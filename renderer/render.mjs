import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderMedia, renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {outputPlans} from './outputs.mjs';

const dir = process.argv[2];
const props = JSON.parse(fs.readFileSync(path.join(dir, 'props.json')));
const publicDir = path.join(dir, 'public');

const plans = outputPlans(props, fs.existsSync(path.join(publicDir, 'narration_en.wav')));
const url = await bundle({
  entryPoint: fileURLToPath(new URL('./index.tsx', import.meta.url)),
  publicDir: path.join(dir, 'public')
});
const browser = await openBrowser('chrome', {
  browserExecutable: '/usr/bin/google-chrome',
  chromiumOptions: {
    args: ['--enable-gpu', '--ignore-gpu-blocklist', '--no-sandbox']
  }
});

try {
  const isDual = props.aspect_ratio === 'dual';
  const is16x9 = props.aspect_ratio === '16:9';
  // A pure 16:9 output hides subtitles entirely (see outputPlans in
  // outputs.mjs); checking Vietnamese cue geometry against a video that never
  // burns that text in was a check of nothing. Only 9:16/dual carry
  // burned-in subtitles, so only they get a real layout check.
  const hasSubtitles = !is16x9;

  let layoutResult;
  if (!hasSubtitles) {
    layoutResult = {
      passed: true,
      applies: false,
      checked_cues: 0,
      method: '16:9 output hides subtitles; no burned-in text to check',
      failures: []
    };
  } else {
    // Layout check using Playwright. Cues arrive pre-cut from Python
    // (adapters.subtitle_cues) -- this just checks the geometry of each cue
    // exactly as the renderer will show it, with no re-chunking here.
    const checkWidth = 1080;
    const checkHeight = 1920;
    const pw = await chromium.launch({executablePath: '/usr/bin/google-chrome', headless: true});
    const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
    let failures = [];

    for (const cue of props.cues) {
      await page.setContent(`
        <div id="subtitle" style="position:absolute;bottom:100px;left:50%;transform:translateX(-50%);max-width:${checkWidth - 80}px;white-space:nowrap;font:800 32px/44px Arial;padding:10px 24px;box-sizing:border-box;text-align:center"></div>
      `);
      await page.locator('#subtitle').evaluate((e, t) => e.textContent = t, cue.text);
      const bad = await page.evaluate(([w, h]) => [...document.querySelectorAll('div')].flatMap(e => {
        const r = e.getBoundingClientRect();
        return r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || (e.id === 'subtitle' && r.height > 100) ? [e.id] : [];
      }), [checkWidth, checkHeight]);
      if (bad.length) failures.push({text: cue.text, errors: bad});
    }
    await pw.close();

    layoutResult = {
      passed: !failures.length,
      applies: true,
      checked_cues: props.cues.length,
      method: 'matching text geometry; representative rendered stills require human review',
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
      frame: Math.min(compStills.durationInFrames - 1, Math.round((scene.start + scene.end) / 2 * 30)),
      output: path.join(dir, scene.id + '.png')
    });
  }

  for (const plan of plans) {
    const composition = await selectComposition({serveUrl: url, id: 'Pilot', inputProps: plan.props, puppeteerInstance: browser});
    await renderMedia({serveUrl: url, composition, inputProps: plan.props, puppeteerInstance: browser,
      codec: 'h264', hardwareAcceleration: 'if-possible', audioCodec: 'aac',
      concurrency: props.render_concurrency || 2, outputLocation: path.join(dir, plan.file)});
  }
  if (plans[0].file !== 'video.mp4') fs.copyFileSync(path.join(dir, plans[0].file), path.join(dir, 'video.mp4'));

} finally {
  await browser.close({silent: true});
}
