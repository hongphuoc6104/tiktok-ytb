import {bundle} from '@remotion/bundler';
import {openBrowser, selectComposition, renderMedia, renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const dir = process.argv[2];
const props = JSON.parse(fs.readFileSync(path.join(dir, 'props.json')));
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

  // Layout check using Playwright
  const checkWidth = is16x9 ? 1920 : 1080;
  const checkHeight = is16x9 ? 1080 : 1920;
  const pw = await chromium.launch({executablePath: '/usr/bin/google-chrome', headless: true});
  const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
  let failures = [];

  for (const seg of props.segments) {
    const scene = props.scenes.find(s => s.id === seg.scene_id) || {title: ''};
    await page.setContent(`
      <div id="title" style="position:absolute;top:48px;left:48px;width:${checkWidth * 0.7}px;font:800 36px/1.25 Arial"></div>
      <div id="subtitle" style="position:absolute;bottom:100px;left:50%;transform:translateX(-50%);width:${checkWidth - 120}px;font:600 32px/46px Arial;padding:14px 24px;box-sizing:border-box;text-align:center"></div>
    `);
    await page.locator('#title').evaluate((e, t) => e.textContent = t, scene.title);
    await page.locator('#subtitle').evaluate((e, t) => e.textContent = t, seg.text);
    const bad = await page.evaluate(([w, h]) => [...document.querySelectorAll('div')].flatMap(e => {
      const r = e.getBoundingClientRect();
      return r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || e.scrollWidth > e.clientWidth || (e.id === 'subtitle' && r.height > 180) ? [e.id] : [];
    }), [checkWidth, checkHeight]);
    if (bad.length) failures.push({text: seg.text, errors: bad});
  }
  await pw.close();

  fs.writeFileSync(path.join(dir, 'layout.json'), JSON.stringify({
    passed: !failures.length,
    checked_frames: props.segments.length,
    method: 'matching text geometry; representative rendered stills require human review',
    failures
  }, null, 2));

  if (failures.length) throw Error('Text overflow');

  // Render representative stills
  const compStills = await selectComposition({
    serveUrl: url,
    id: 'Pilot',
    inputProps: {...props, width: checkWidth, height: checkHeight},
    puppeteerInstance: browser
  });

  for (const scene of props.scenes) {
    await renderStill({
      serveUrl: url,
      composition: compStills,
      inputProps: {...props, width: checkWidth, height: checkHeight},
      puppeteerInstance: browser,
      frame: Math.min(compStills.durationInFrames - 1, Math.round((scene.start + scene.end) / 2 * 30)),
      output: path.join(dir, scene.id + '.png')
    });
  }

  // Render video
  if (isDual) {
    // 1. Render 9:16 Full HD
    const comp916 = await selectComposition({
      serveUrl: url,
      id: 'Pilot',
      inputProps: {...props, width: 1080, height: 1920},
      puppeteerInstance: browser
    });
    await renderMedia({
      serveUrl: url,
      composition: comp916,
      inputProps: {...props, width: 1080, height: 1920},
      puppeteerInstance: browser,
      codec: 'h264',
      hardwareAcceleration: 'if-possible',
      audioCodec: 'aac',
      concurrency: 4,
      outputLocation: path.join(dir, 'video_9x16.mp4')
    });

    // 2. Render 16:9 Full HD
    const comp169 = await selectComposition({
      serveUrl: url,
      id: 'Pilot',
      inputProps: {...props, width: 1920, height: 1080},
      puppeteerInstance: browser
    });
    await renderMedia({
      serveUrl: url,
      composition: comp169,
      inputProps: {...props, width: 1920, height: 1080},
      puppeteerInstance: browser,
      codec: 'h264',
      hardwareAcceleration: 'if-possible',
      audioCodec: 'aac',
      concurrency: 4,
      outputLocation: path.join(dir, 'video_16x9.mp4')
    });

    // Default video is 9:16
    fs.copyFileSync(path.join(dir, 'video_9x16.mp4'), path.join(dir, 'video.mp4'));
  } else {
    const compSingle = await selectComposition({
      serveUrl: url,
      id: 'Pilot',
      inputProps: {...props, width: checkWidth, height: checkHeight},
      puppeteerInstance: browser
    });
    await renderMedia({
      serveUrl: url,
      composition: compSingle,
      inputProps: {...props, width: checkWidth, height: checkHeight},
      puppeteerInstance: browser,
      codec: 'h264',
      hardwareAcceleration: 'if-possible',
      audioCodec: 'aac',
      concurrency: 4,
      outputLocation: path.join(dir, 'video.mp4')
    });
  }
} finally {
  await browser.close({silent: true});
}
