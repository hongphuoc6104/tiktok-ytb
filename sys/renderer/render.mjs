import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderMedia, renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {outputPlans} from './outputs.mjs';
import {captionStyle, captionMaxHeight} from './captions.mjs';

const dir = path.resolve(process.argv[2]);
const props = JSON.parse(fs.readFileSync(path.join(dir, 'props.json')));
const publicDir = path.join(dir, 'public');

// Clip beats (MP4 delivered by the image stage) loop inside their beat; the
// composition needs each clip's length to know where to loop.
const clipSeconds = {};
for (const list of [props.scenes, props.en_scenes, props.horizontal_scenes]) {
  for (const beat of (list || []).flatMap((s) => s.images || [])) {
    if (!/\.mp4$/i.test(beat.src) || beat.clip_seconds) continue;
    clipSeconds[beat.src] ??= Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
      path.join(publicDir, beat.src)], {encoding: 'utf8'}).trim());
    beat.kind = 'clip';
    beat.clip_seconds = clipSeconds[beat.src];
  }
}

const plans = outputPlans(props, fs.existsSync(path.join(publicDir, 'narration_en.wav')));
const url = await bundle({
  entryPoint: fileURLToPath(new URL('./index.tsx', import.meta.url)),
  publicDir: path.join(dir, 'public'),
  // Fonts become data URLs inside the bundle: with several render tabs a
  // per-tab font request could stall past the delayRender timeout.
  webpackOverride: (config) => ({...config, module: {...config.module, rules: config.module.rules.map((rule) =>
    rule && rule.test instanceof RegExp && rule.test.test('x.ttf') ? {...rule, type: 'asset/inline'} : rule)}})
});
const browser = await openBrowser('chrome', {
  browserExecutable: '/usr/bin/google-chrome',
  chromiumOptions: {
    // config.render_gl (e.g. "angle", "vulkan") picks Chrome's GL backend;
    // unset keeps Chrome's own default, as before.
    ...(props.render_gl ? {gl: props.render_gl} : {}),
    args: ['--enable-gpu', '--ignore-gpu-blocklist', '--no-sandbox']
  }
});

try {
  // Only outputs that burn Vietnamese subtitles in get a geometry check, at
  // their own frame size (a 16:9 Vietnamese track is checked at 1920x1080).
  // English 16:9 hides subtitles, so checking it would be a check of nothing.
  const subtitled = plans.filter((plan) => !plan.props.hideSubtitles);

  let layoutResult;
  if (!subtitled.length) {
    layoutResult = {
      passed: true,
      applies: false,
      checked_cues: 0,
      method: 'no output burns subtitles in (English 16:9 or subtitles off); no burned-in text to check',
      failures: []
    };
  } else {
    // Layout check using Playwright. Cues arrive pre-cut from Python
    // (adapters.subtitle_cues) -- this just checks the geometry of each cue
    // exactly as the renderer will show it, with no re-chunking here.
    const pw = await chromium.launch({executablePath: '/usr/bin/google-chrome', headless: true});
    const failures = [];
    let checked = 0;
    for (const plan of subtitled) {
      const checkWidth = plan.props.width;
      const checkHeight = plan.props.height;
      const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
      for (const cue of props.cues) {
        await page.setContent('<div id="subtitle"></div>');
        const style = captionStyle(checkWidth, checkHeight);
        await page.locator('#subtitle').evaluate((e, {text, style}) => {
          for (const [key, value] of Object.entries(style)) {
            e.style[key] = typeof value === 'number' && !['fontWeight', 'lineHeight'].includes(key) ? `${value}px` : String(value);
          }
          e.textContent = text;
        }, {text: cue.text, style});
        const bad = await page.evaluate(([w, h, maxHeight]) => {
          const e = document.querySelector('#subtitle');
          const r = e.getBoundingClientRect();
          return r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || r.height > maxHeight || e.scrollWidth > e.clientWidth
            ? ['subtitle'] : [];
        }, [checkWidth, checkHeight, captionMaxHeight(checkWidth, checkHeight)]);
        if (bad.length) failures.push({text: cue.text, output: plan.file, errors: bad});
        checked++;
      }
      await page.close();
    }
    await pw.close();

    layoutResult = {
      passed: !failures.length,
      applies: true,
      checked_cues: checked,
      outputs: subtitled.map((plan) => `${plan.file} ${plan.props.width}x${plan.props.height}`),
      method: 'shared composition style; at most two lines; actual playback/readability still requires review',
      failures
    };
  }

  fs.writeFileSync(path.join(dir, 'layout.json'), JSON.stringify(layoutResult, null, 2));

  if (layoutResult.failures.length) throw Error('Text overflow');

  // Render representative stills
  const compStills = await selectComposition({
    serveUrl: url,
    id: 'Pilot',
    inputProps: plans[0].props,
    puppeteerInstance: browser
  });

  for (const scene of plans[0].props.scenes) {
    await renderStill({
      serveUrl: url,
      composition: compStills,
      inputProps: plans[0].props,
      puppeteerInstance: browser,
      frame: Math.min(compStills.durationInFrames - 1, Math.round((scene.start + scene.end) / 2 * compStills.fps)),
      output: path.join(dir, scene.id + '.png')
    });
  }

  const timings = [];
  for (const plan of plans) {
    const composition = await selectComposition({serveUrl: url, id: 'Pilot', inputProps: plan.props, puppeteerInstance: browser});
    const started = Date.now();
    const output = path.join(dir, plan.file);
    // hardwareAcceleration 'if-possible' encodes with h264_nvenc on this laptop,
    // so an x264 preset must not be passed here (nvenc rejects it).
    // Cheaper long-form path: render_fps < 30 screenshots fewer frames, then
    // ffmpeg repeats frames up to the 30 fps the video gate requires.
    const lowFps = composition.fps < 30;
    await renderMedia({serveUrl: url, composition, inputProps: plan.props, puppeteerInstance: browser,
      codec: 'h264', hardwareAcceleration: 'if-possible', audioCodec: 'aac',
      concurrency: props.render_concurrency || 4, outputLocation: lowFps ? output + '.low.mp4' : output});
    if (lowFps) {
      const retime = (codec) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', output + '.low.mp4', '-vf', 'fps=30',
        ...codec, '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', output]);
      try {
        retime(['-c:v', 'h264_nvenc', '-preset', 'p5', '-rc', 'vbr', '-cq', '21']);
      } catch {
        retime(['-c:v', 'libx264', '-preset', props.render_x264_preset || 'veryfast', '-crf', '20']);
      }
      fs.rmSync(output + '.low.mp4');
    }
    const seconds = (Date.now() - started) / 1000;
    const videoSeconds = composition.durationInFrames / composition.fps;
    timings.push({file: plan.file, video_seconds: videoSeconds, render_fps: composition.fps, render_seconds: seconds,
      ratio: +(seconds / videoSeconds).toFixed(3)});
    console.log('render timing', JSON.stringify(timings.at(-1)));
  }
  fs.writeFileSync(path.join(dir, 'render-timing.json'), JSON.stringify(timings, null, 2));
  if (plans[0].file !== 'video.mp4') fs.copyFileSync(path.join(dir, plans[0].file), path.join(dir, 'video.mp4'));

} finally {
  await browser.close({silent: true});
}
