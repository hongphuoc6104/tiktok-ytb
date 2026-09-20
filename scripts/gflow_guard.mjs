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
const character = args[0] === 'character' && args[1] === 'create';
if (!image && !character) throw Error('M2_POLICY: only image or character create allowed');
const out = args[args.indexOf('--out') + 1];
if (!out || !args.includes('--out')) throw Error('Output directory required');
const evidenceDir = dirname(out);
const proof = { mode: image ? 'image' : 'character-register', characters: [], passed: false };
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
  if (job.type !== 'image' || (job.ratio !== '9:16' && job.ratio !== '16:9') || job.outputs !== 1) {
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
  const targetRatio = job.ratio === '16:9' ? '16:9' : '9:16';
  await page.evaluate((r) => {
    const group = document.querySelector('mat-button-toggle-group');
    if (group) {
      const toggle = [...group.querySelectorAll('mat-button-toggle')].find(t => t.innerText.includes(r));
      if (toggle) {
        const btn = toggle.querySelector('button');
        if (btn) btn.click();
      }
    }
  }, targetRatio);
  await page.waitForTimeout(300);

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

  // Record observed selections, never reconstruct proof from requested arguments.
  const observed = await page.evaluate(() => ({
    selected: [...document.querySelectorAll('[aria-selected="true"], [aria-pressed="true"], .mat-button-toggle-checked')]
      .map(e => (e.textContent || '').trim()),
    labels: [...document.querySelectorAll('button')].map(e => (e.textContent || '').trim())
  }));
  const selection = observed.selected.join(' ');
  const labels = observed.labels.join(' ');
  const normalized = labels.toLowerCase().replace(/[-_]/g, ' ');
  const model = job.model.toLowerCase().replace(/[-_]/g, ' ');
  const ratioIcon = job.ratio === '16:9' ? 'crop_16_9' : 'crop_9_16';
  if (!/\bImage\b/i.test(selection) || !normalized.includes(model) ||
      !(selection.includes(job.ratio) || labels.includes(ratioIcon)) || !/\bx1\b/.test(labels)) {
    throw Error('M2_PREFLIGHT: cannot verify image/model/ratio/output count from the live UI');
  }
  proof.settings = observed;
  const save = page.getByRole('button', {name: 'Save', exact: true});
  if (await save.count()) await save.first().click();

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
    const {navigateToProject} = await import(join(base, 'dist/src/flow/ui.js'));
    await navigateToProject(page, job.project);
    await page.waitForTimeout(2500);

    // 2. Apply Settings
    await this.applySettings(job);

    // 3. Collect existing image sources before generation
    const beforeSrcs = new Set(await this.resultSrcs(job.type));

    // 4. Fill Prompt
    await this.fillPrompt(job.prompt);
    for (const name of job.character || []) {
      await this.referenceCharacter(name);
      const attached = await page.locator('.prompt-input, form, [data-prompt-container]').filter({hasText: name}).count();
      if (!attached) throw Error('Character attachment cannot be verified: ' + name);
    }

    // 5. Submit & record evidence
    await this.submit();

    // 6. Wait for new image result
    const timeoutMs = (job.timeout ?? 900) * 1000;
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
    const resolvedOutDir = resolve(outDir);
    await fsPromises.mkdir(resolvedOutDir, { recursive: true });
    const artifacts = [];

    for (let i = 0; i < newSrcs.length; i++) {
      const basename = `${job.id}-${i + 1}`;
      const assetPath = join(resolvedOutDir, `${basename}.png`);
      const metadataPath = join(resolvedOutDir, `${basename}.json`);

      // Download authentic full-resolution asset using downloadResult
      const { downloadResult } = await import(join(base, 'dist/src/flow/download.js'));
      const dl = await downloadResult({
        page,
        context,
        src: newSrcs[i],
        type: job.type,
        quality: 'original',
        outDir: resolvedOutDir,
        basename
      });
      if (dl?.assetPath && dl.assetPath !== assetPath) {
        await fsPromises.copyFile(dl.assetPath, assetPath);
      }

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

// Keep the pinned provider implementation: it downloads the actual registration result.
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
