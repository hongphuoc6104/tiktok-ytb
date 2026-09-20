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

// Auto-enrich scenes with dedicated 9:16 and 16:9 images and multi-beat illustrations
for (const scene of props.scenes) {
  const p916 = `${scene.id}_9x16.png`;
  const p169 = `${scene.id}_16x9.png`;
  if (fs.existsSync(path.join(publicDir, p916))) scene.image_9x16 = p916;
  if (fs.existsSync(path.join(publicDir, p169))) scene.image_16x9 = p169;

  const beats916 = [];
  if (fs.existsSync(path.join(publicDir, `${scene.id}_a_9x16.png`))) {
    beats916.push({src: `${scene.id}_a_9x16.png`, at: 0});
  } else if (scene.image_9x16) {
    beats916.push({src: scene.image_9x16, at: 0});
  }
  if (fs.existsSync(path.join(publicDir, `${scene.id}_b_9x16.png`))) {
    beats916.push({src: `${scene.id}_b_9x16.png`, at: 4.5});
  }
  if (beats916.length > 1) scene.images_9x16 = beats916;

  const beats169 = [];
  if (fs.existsSync(path.join(publicDir, `${scene.id}_a_16x9.png`))) {
    beats169.push({src: `${scene.id}_a_16x9.png`, at: 0});
  } else if (scene.image_16x9) {
    beats169.push({src: scene.image_16x9, at: 0});
  }
  if (fs.existsSync(path.join(publicDir, `${scene.id}_b_16x9.png`))) {
    beats169.push({src: `${scene.id}_b_16x9.png`, at: 4.5});
  }
  if (beats169.length > 1) scene.images_16x9 = beats169;
}
if (props.en_scenes) {
  const spans = new Map(props.en_scenes.map(s => [s.id, s]));
  props.en_scenes = props.scenes.map(s => ({...s, start: spans.get(s.id).start, end: spans.get(s.id).end}));
}
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

  // Layout check using Playwright
  const checkWidth = is16x9 ? 1920 : 1080;
  const checkHeight = is16x9 ? 1080 : 1920;
  const pw = await chromium.launch({executablePath: '/usr/bin/google-chrome', headless: true});
  const page = await pw.newPage({viewport: {width: checkWidth, height: checkHeight}});
  let failures = [];

function splitIntoPhrases(text, maxLen = 32) {
  if (!text || text.length <= maxLen) return [text || ''];
  const rawParts = text.split(/([,?!;:\.—])/).filter(Boolean);
  const clauses = [];
  let curr = '';
  for (const p of rawParts) {
    if (['.', ',', '?', '!', ';', ':', '—'].includes(p)) {
      curr += p;
    } else {
      if (curr.trim()) clauses.push(curr.trim());
      curr = p;
    }
  }
  if (curr.trim()) clauses.push(curr.trim());

  const result = [];
  for (const clause of clauses) {
    if (clause.length <= maxLen) {
      result.push(clause);
    } else {
      const words = clause.split(/\s+/);
      let buf = '';
      for (const w of words) {
        if ((buf ? buf + ' ' + w : w).length <= maxLen) {
          buf = buf ? buf + ' ' + w : w;
        } else {
          if (buf) result.push(buf);
          buf = w;
        }
      }
      if (buf) result.push(buf);
    }
  }
  return result.length > 0 ? result : [text];
}

  for (const seg of props.segments) {
    const chunks = splitIntoPhrases(seg.text, 32);
    for (const chunk of chunks) {
      await page.setContent(`
        <div id="subtitle" style="position:absolute;bottom:100px;left:50%;transform:translateX(-50%);max-width:${checkWidth - 80}px;white-space:nowrap;font:800 32px/44px Arial;padding:10px 24px;box-sizing:border-box;text-align:center"></div>
      `);
      await page.locator('#subtitle').evaluate((e, t) => e.textContent = t, chunk);
      const bad = await page.evaluate(([w, h]) => [...document.querySelectorAll('div')].flatMap(e => {
        const r = e.getBoundingClientRect();
        return r.left < 0 || r.right > w || r.top < 0 || r.bottom > h || (e.id === 'subtitle' && r.height > 100) ? [e.id] : [];
      }), [checkWidth, checkHeight]);
      if (bad.length) failures.push({text: chunk, errors: bad});
    }
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
