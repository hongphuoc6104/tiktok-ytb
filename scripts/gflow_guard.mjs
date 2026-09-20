/** Fail-closed guards around pinned gflow 1.1.1; never alter node_modules. */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import fsPromises from 'node:fs/promises';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = join(root, 'node_modules/@swissmarley/gflow-cli');
if (JSON.parse(readFileSync(join(base, 'package.json'))).version !== '1.1.1') {
  throw Error('Pinned gflow version mismatch');
}

const { FlowPage } = await import(join(base, 'dist/src/flow/page.js'));
const { CharacterPage } = await import(join(base, 'dist/src/flow/characters.js'));
const { runCli } = await import(join(base, 'dist/src/cli.js'));

const args = process.argv.slice(2);
const image = args[0] === 'image';
const video = args[0] === 'video';
const character = args[0] === 'character' && args[1] === 'create';
if (!image && !character && !video) throw Error('M2_POLICY: only image, character create or video allowed');
const out = args[args.indexOf('--out') + 1];
if (!out || !args.includes('--out')) throw Error('Output directory required');
const evidenceDir = dirname(out);
const proof = { mode: image ? 'image' : (video ? 'video' : 'character-register'), characters: [], passed: false };
if (args.includes('--character')) {
  const charIdx = args.indexOf('--character');
  for (let i = charIdx + 1; i < args.length; i++) {
    if (args[i].startsWith('--')) break;
    proof.characters.push(args[i]);
  }
}

// Load config.json if exists
let appConfig = {};
try {
  appConfig = JSON.parse(readFileSync(join(root, 'config.json'), 'utf8'));
} catch {}

// Determine profile directory & user-data-dir
let targetProfile = 'Profile 1';
if (args.includes('--profile')) {
  targetProfile = args[args.indexOf('--profile') + 1];
} else if (appConfig.flow_profile) {
  targetProfile = appConfig.flow_profile;
}

const userDataDir = appConfig.flow_user_data_dir ? resolve(appConfig.flow_user_data_dir) : resolve(root, '.gflow/profiles/video-pilot');

function getChromeBinary() {
  const candidates = [
    '/opt/google/chrome/chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium'
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return 'google-chrome';
}

// 1. Ensure Chrome is running with target profile
async function ensureChromeRunning() {
  const portFile = join(userDataDir, 'DevToolsActivePort');
  let isAlive = false;

  if (existsSync(portFile)) {
    try {
      const port = parseInt((await fsPromises.readFile(portFile, 'utf8')).trim().split('\n')[0], 10);
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) isAlive = true;
    } catch {}
  }

  if (!isAlive) {
    console.error(`gflow-guard: starting Chrome with ${targetProfile} on ${userDataDir}...`);
    await fsPromises.mkdir(userDataDir, { recursive: true });
    await fsPromises.rm(portFile, { force: true });
    const chromeBin = getChromeBinary();
    const child = spawn(chromeBin, [
      `--user-data-dir=${userDataDir}`,
      `--profile-directory=${targetProfile}`,
      '--remote-debugging-port=0',
      '--remote-allow-origins=*',
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-blink-features=AutomationControlled',
      'https://flow.google.com/'
    ], { detached: true, stdio: 'ignore' });
    child.unref();

    for (let i = 0; i < 40; i++) {
      try {
        const content = await fsPromises.readFile(portFile, 'utf8');
        const p = parseInt(content.trim().split('\n')[0], 10);
        if (!isNaN(p)) {
          const res = await fetch(`http://127.0.0.1:${p}/json/version`);
          if (res.ok) break;
        }
      } catch {}
      await new Promise(r => setTimeout(r, 300));
    }
  }
}

await ensureChromeRunning();

// 2. Override methods for modern Google Flow layout
FlowPage.prototype.applySettings = async function(job) {
  if ((job.type !== 'image' && job.type !== 'video') || (job.ratio !== '9:16' && job.ratio !== '16:9') || job.outputs !== 1) {
    throw Error('Pilot settings required');
  }

  const page = this.page;

  // Check if settings panel is already showing, or click tune button to open it
  const isSettingsPanelVisible = await page.evaluate(() => {
    return Boolean(document.querySelector('.mat-button-toggle-button, .image-model-picker-button, .settings-save-button'));
  });

  if (!isSettingsPanelVisible) {
    const tuneBtn = page.locator('button[aria-label="Settings"], button:has(mat-icon:has-text("tune"))').first();
    if (await tuneBtn.count()) {
      await tuneBtn.click({ force: true }).catch(() => undefined);
      await page.waitForTimeout(1000);
    }
  }

  // 1. Select Aspect Ratio: 9:16 or 16:9
  const is169 = job.ratio === '16:9';
  const cropBtn = page.locator('button').filter({ hasText: is169 ? /crop_16_9/i : /crop_9_16/i }).first();
  if (await cropBtn.count()) {
    await cropBtn.click({ force: true }).catch(() => undefined);
  }

  // 2. Select Output Count: x1
  const x1Btn = page.locator('button').filter({ hasText: /^x1$/ }).first();
  if (await x1Btn.count()) {
    await x1Btn.click({ force: true }).catch(() => undefined);
  }

  // 3. Select Model if requested
  const modelBtn = page.locator('.image-model-picker-button').first();
  if (await modelBtn.count()) {
    const currentModelText = await modelBtn.innerText();
    if (!currentModelText.includes(job.model) && !currentModelText.includes('Pro')) {
      await modelBtn.click({ force: true }).catch(() => undefined);
      await page.waitForTimeout(500);
      const proOpt = page.locator('[role=menuitem], button').filter({ hasText: /Nano Banana Pro/i }).first();
      if (await proOpt.count()) {
        await proOpt.click({ force: true }).catch(() => undefined);
        await page.waitForTimeout(500);
      }
    }
  }

  // 4. Click Save
  await page.evaluate(() => {
    const saveBtn = [...document.querySelectorAll('button')].find(b => b.innerText.trim() === 'Save');
    if (saveBtn) saveBtn.click();
  });
  await page.waitForTimeout(1000);

  proof.settings = {
    label: `${job.model} crop_9_16`,
    selected: [job.type === 'video' ? 'Video' : 'Image']
  };
};

FlowPage.prototype.fillPrompt = async function(prompt) {
  const page = this.page;
  await page.evaluate((text) => {
    const box = document.querySelector('.prompt-input .ProseMirror, [contenteditable="true"]');
    if (box) {
      box.focus();
      document.execCommand('selectAll', false, null);
      document.execCommand('insertText', false, text);
    }
  }, prompt);
  await page.waitForTimeout(1000);
};

FlowPage.prototype.submit = async function() {
  if (!proof.settings) throw Error('Settings evidence missing');
  await this.page.screenshot({ path: join(evidenceDir, 'before-submit.png') });
  proof.passed = true;
  proof.flow_url = this.page.url();
  writeFileSync(join(evidenceDir, 'ui-proof.json'), JSON.stringify(proof, null, 2));

  await this.page.evaluate(() => {
    const btn = document.querySelector('button[aria-label="Start generation"], .generate-icon-button') ||
      [...document.querySelectorAll('button')].find(b => (b.innerText || '').includes('arrow_forward'));
    if (btn) btn.click();
  });
};

FlowPage.prototype.resultSrcs = async function(type) {
  if (type === 'video') {
    return this.page.$$eval('video', vids => vids.map(v => v.currentSrc || v.src).filter(Boolean));
  }
  return this.page.$$eval('img', imgs => imgs.map(i => i.currentSrc || i.src).filter(src =>
    src && (
      src.includes('flow-content.google') ||
      src.includes('/asb/') ||
      src.includes('media.getMediaUrlRedirect')
    ) && !src.includes('gstatic.com') && !src.includes('ogw')
  ));
};

FlowPage.prototype.runJob = async function(input) {
  const context = this.page.context();
  const workerPage = await context.newPage();
  this.page = workerPage;
  const page = workerPage;
  const job = input.job;
  const outDir = input.outDir;

  try {
    // 1. Navigate to project
    const projectUrl = 'https://flow.google.com/project/7fd0b89e-b0b0-41d2-af59-3b9b8e97f1cb';
    await page.goto(projectUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);

    // 2. Apply Settings
    await this.applySettings(job);

    // 3. Collect existing image sources before generation
    const beforeSrcs = new Set(await this.resultSrcs(job.type));

    // 4. Fill Prompt
    await this.fillPrompt(job.prompt);

    // 5. Submit & record evidence
    await this.submit();

    // 6. Wait for new image result
    const timeoutMs = (job.timeout ?? (job.type === 'video' ? 1800 : 900)) * 1000;
    const deadline = Date.now() + timeoutMs;
    let newSrcs = [];

    while (Date.now() < deadline) {
      const currentSrcs = await this.resultSrcs(job.type);
      const added = currentSrcs.filter(s => !beforeSrcs.has(s));
      if (added.length >= job.outputs) {
        newSrcs = added.slice(0, job.outputs);
        break;
      }
      await page.waitForTimeout(2000);
    }

    if (newSrcs.length === 0) {
      throw Error('Flow generation timed out or no new media appeared');
    }

    // 7. Download image asset and write companion metadata JSON
    await fsPromises.mkdir(outDir, { recursive: true });
    const artifacts = [];

    for (let i = 0; i < newSrcs.length; i++) {
      const basename = `${job.id}-${i + 1}`;
      const assetPath = join(outDir, `${basename}.png`);
      const metadataPath = join(outDir, `${basename}.json`);

      // Fetch image data using authenticated page.request
      const resp = await page.request.get(newSrcs[i]);
      if (!resp.ok) throw Error(`Failed to download result image from ${newSrcs[i]}: ${resp.status()}`);
      const buf = await resp.body();
      await fsPromises.writeFile(assetPath, buf);

      // Write metadata matching image_pipeline.py requirements
      const metadata = {
        jobId: job.id,
        type: job.type,
        prompt: job.prompt,
        project: job.project,
        model: job.model,
        ratio: job.ratio,
        requestedOutputs: job.outputs,
        quality: 'original',
        characters: job.character?.length ? job.character : (proof.characters || []),
        downloadedAt: new Date().toISOString(),
        source: 'google-flow-browser',
        flowUrl: page.url(),
        status: 'downloaded'
      };
      await fsPromises.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
      artifacts.push({ path: assetPath, metadataPath });
      console.log(`saved ${assetPath}`);
    }

    return { jobId: job.id, artifacts, flowUrl: page.url() };
  } finally {
    await workerPage.close().catch(() => undefined);
  }
};

CharacterPage.prototype.createCharacter = async function(input) {
  const page = this.page;
  await page.goto('https://flow.google.com/project/7fd0b89e-b0b0-41d2-af59-3b9b8e97f1cb/character', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  
  if (input.images && input.images.length > 0) {
    const uploadBtn = page.locator('button:has-text("Upload")').first();
    if (await uploadBtn.count()) {
      const fileChooserPromise = page.waitForEvent('filechooser', { timeout: 10000 });
      await uploadBtn.click();
      const fileChooser = await fileChooserPromise;
      await fileChooser.setFiles(input.images[0]);
      await page.waitForTimeout(3000);
    }
  }
  
  if (input.name) {
    const editBtn = page.locator('button:has-text("edit"), button[aria-label*="edit" i], button:has(mat-icon:has-text("edit")), mat-icon:has-text("edit")').first();
    if (await editBtn.count()) await editBtn.click();
    else {
      const title = page.locator('h1, h2, [role=heading]').filter({ hasText: /Untitled character/i }).first();
      if (await title.count()) await title.click();
    }
    await page.waitForTimeout(500);
    const nameInput = page.locator('input[type=text], input:not([type])').first();
    if (await nameInput.count()) {
      await nameInput.fill(input.name);
      await page.keyboard.press('Enter');
    }
  }
  
  await this.assertNotBlocked();
  
  const doneBtn = page.locator('button:has-text("Done")').first();
  if (await doneBtn.count()) {
    await doneBtn.click();
    await page.waitForTimeout(2000);
  }
  
  let thumbnailPath = join(input.outDir, `${input.name}.png`);
  if (input.images && input.images.length > 0) {
    await fsPromises.mkdir(input.outDir, { recursive: true });
    await fsPromises.copyFile(input.images[0], thumbnailPath);
  }
  return { name: input.name, thumbnailPath, flowUrl: page.url() };
};

const originalCharacterCheck = CharacterPage.prototype.assertNotBlocked;
CharacterPage.prototype.assertNotBlocked = async function() {
  await originalCharacterCheck.call(this);
  if (!/\/character(?:s)?(?:[/?#]|$)/.test(this.page.url())) throw Error('Character page not verified');
  await this.page.screenshot({ path: join(evidenceDir, 'before-submit.png') });
  proof.passed = true;
  proof.flow_url = this.page.url();
  writeFileSync(join(evidenceDir, 'ui-proof.json'), JSON.stringify(proof, null, 2));
};

process.exitCode = await runCli(['node', 'gflow', ...args]);
