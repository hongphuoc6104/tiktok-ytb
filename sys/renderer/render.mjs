import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderMedia, renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {cpus} from 'node:os';
import {fileURLToPath} from 'node:url';
import {outputPlans, renderConcurrency} from './outputs.mjs';
import {captionStyle, captionMaxHeight} from './captions.mjs';

const dir = path.resolve(process.argv[2]);
const props = JSON.parse(fs.readFileSync(path.join(dir, 'props.json')));
const publicDir = path.join(dir, 'public');

const plans = outputPlans(props, fs.existsSync(path.join(publicDir, 'narration_en.wav')));
const url = await bundle({
  entryPoint: fileURLToPath(new URL('./index.tsx', import.meta.url)),
  publicDir: path.join(dir, 'public')
});
function resolveChromePath() {
  if (process.env.VP_CHROME_PATH && fs.existsSync(process.env.VP_CHROME_PATH)) {
    return process.env.VP_CHROME_PATH;
  }
  try {
    const pwPath = chromium.executablePath();
    if (fs.existsSync(pwPath)) return pwPath;
  } catch {}
  for (const p of ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser']) {
    if (fs.existsSync(p)) return p;
  }
  return chromium.executablePath();
}
const chromePath = resolveChromePath();

process.env.DISABLE_FROM_SURFACE = 'true';

const browser = await openBrowser('chrome', {
  browserExecutable: chromePath,
  chromiumOptions: {
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--run-all-compositor-stages-before-draw',
      '--disable-gpu-rasterization',
      '--enable-gpu',
      '--ignore-gpu-blocklist'
    ]
  }
});

try {
  const captionPlans = plans.filter(plan => !plan.props.hideSubtitles);
  let failures = [];
  let checked = 0;
  if (captionPlans.length) {
    const pw = await chromium.launch({executablePath: chromePath, headless: true});
    try {
      for (const plan of captionPlans) {
        const checkWidth = plan.props.width;
        const checkHeight = plan.props.height;
        const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
        for (const cue of plan.props.cues) {
          checked++;
          await page.setContent('<div id="subtitle"></div>');
          const style = captionStyle(checkWidth, checkHeight);
          await page.locator('#subtitle').evaluate((e, {text, style}) => {
            for (const [key, value] of Object.entries(style)) {
              e.style[key] = typeof value === 'number' && !['fontWeight', 'lineHeight', 'zIndex'].includes(key) ? `${value}px` : String(value);
            }
            e.textContent = text;
          }, {text: cue.text, style});
          const bad = await page.evaluate(([w, h, maxHeight]) => {
            const e = document.querySelector('#subtitle');
            const r = e.getBoundingClientRect();
            return r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || r.height > maxHeight || e.scrollWidth > e.clientWidth
              ? ['subtitle'] : [];
          }, [checkWidth, checkHeight, captionMaxHeight(checkWidth, checkHeight)]);
          if (bad.length) failures.push({file: plan.file, language: plan.props.language, text: cue.text, errors: bad});
        }
        await page.close();
      }
    } finally { await pw.close(); }
  }
  const layoutResult = {passed: !failures.length, applies: captionPlans.length > 0, checked_cues: checked,
    method: 'actual requested language/aspect caption styles; two lines; no quality approval', failures};

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
    await renderMedia({
      serveUrl: url,
      composition,
      inputProps: plan.props,
      puppeteerInstance: browser,
      codec: 'h264',
      hardwareAcceleration: 'if-possible',
      audioCodec: 'aac',
      concurrency: renderConcurrency(props.render_concurrency, cpus().length),
      outputLocation: path.join(dir, plan.file),
      onProgress: ({renderedFrames}) => {
        if (renderedFrames % 150 === 0) {
          console.log(`Render progress: ${renderedFrames}/${composition.durationInFrames} frames`);
        }
      }
    });
  }
  if (plans[0].file !== 'video.mp4') fs.copyFileSync(path.join(dir, plans[0].file), path.join(dir, 'video.mp4'));

} finally {
  await browser.close({silent: true});
}
