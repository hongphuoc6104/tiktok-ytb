// Legacy CLI guard: retained for compatibility tests; v3 uses b2_bridge and queue-runner.
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
let baseImage;
if (args.includes('--base-image')) {
  const index = args.indexOf('--base-image');
  baseImage = resolve(args[index + 1]);
  args.splice(index, 2);
}
const image = args[0] === 'image';
const character = args[0] === 'character' && args[1] === 'create';
const batchMode = args[0] === 'batch';
// `auth login` opens the sign-in window. It goes through this guard rather than
// the bundled CLI because gflow's own login resolves only a --user-data-dir and
// lets Chrome fall back to the `Default` profile inside it, while every image
// runs with an explicit --profile-directory. Signing in there would have stored
// the session in a different profile than the one that generates the images.
const authMode = args[0] === 'auth' && args[1] === 'login';
if (!image && !character && !batchMode && !authMode) throw Error('M2_POLICY: only image, character create, batch, or auth login allowed');
const out = authMode ? null : args[args.indexOf('--out') + 1];
if (!authMode && (!out || !args.includes('--out'))) throw Error('Output directory required');

// Single-job invocations (image / character create) are today's only
// production path: one fixed evidence location, exactly as before. `batch`
// runs many jobs through this same process against one shared --out, so
// each job needs its own evidence subdirectory instead -- `current` is
// reassigned per job at the top of runJob() in that case (never null once a
// job starts). Every place that used to read the old module-level `proof`/
// `evidenceDir` now reads `current.proof`/`current.evidenceDir`.
let current = (batchMode || authMode) ? null : {
  proof: { mode: image ? 'image' : 'character-register', characters: [], passed: false },
  evidenceDir: dirname(out),
};
if (!batchMode && !authMode && args.includes('--character')) {
  const charIdx = args.indexOf('--character');
  for (let i = charIdx + 1; i < args.length; i++) {
    if (args[i].startsWith('--')) break;
    current.proof.characters.push(args[i]);
  }
}

// Load config.json if exists
let appConfig = {};
try {
  appConfig = JSON.parse(readFileSync(join(root, 'config.json'), 'utf8'));
} catch {}

// `--profile` means what it means in gflow itself: the name of the
// user-data-dir under .gflow/profiles, NOT a Chrome --profile-directory.
// This guard used to pass it straight through as --profile-directory, so
// `gflow auth login --profile video-pilot` signed in to
// .gflow/profiles/video-pilot/Default while every image ran from
// .gflow/profiles/video-pilot/video-pilot -- two different profiles, and the
// generating one was never signed in. Which Chrome profile inside the
// user-data-dir to use is now its own config key, defaulting to `Default`
// exactly as Chrome (and therefore gflow's own login) does.
let flowProfile = 'video-pilot';
if (args.includes('--profile')) {
  flowProfile = args[args.indexOf('--profile') + 1];
} else if (appConfig.flow_profile) {
  flowProfile = appConfig.flow_profile;
}

const userDataDir = appConfig.flow_user_data_dir ? resolve(appConfig.flow_user_data_dir) : resolve(root, '.gflow/profiles', flowProfile);
const profileDirectory = appConfig.flow_profile_directory || 'Default';

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

// `auth login`: a plain sign-in window on the same user-data-dir AND the same
// profile-directory the image path uses. No debugging port and no automation
// flag -- Google rejects sign-in from automation-flagged browsers, which is why
// gflow opens a plain window for this too.
if (authMode) {
  await fsPromises.mkdir(userDataDir, { recursive: true });
  await fsPromises.rm(join(userDataDir, 'DevToolsActivePort'), { force: true });
  const child = spawn(getChromeBinary(), [
    `--user-data-dir=${userDataDir}`,
    `--profile-directory=${profileDirectory}`,
    '--no-first-run',
    '--no-default-browser-check',
    'https://flow.google.com/'
  ], { detached: true, stdio: 'ignore' });
  child.unref();
  console.log(JSON.stringify({ opened: true, user_data_dir: userDataDir, profile_directory: profileDirectory }));
  process.exit(0);
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
    console.error(`gflow-guard: starting Chrome with profile-directory ${profileDirectory} on ${userDataDir}...`);
    await fsPromises.mkdir(userDataDir, { recursive: true });
    await fsPromises.rm(portFile, { force: true });
    const chromeBin = getChromeBinary();
    const child = spawn(chromeBin, [
      `--user-data-dir=${userDataDir}`,
      `--profile-directory=${profileDirectory}`,
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
  current.proof.settings = observed;
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
  if (!current.proof.settings) throw Error('Settings evidence missing');
  await this.page.screenshot({ path: join(current.evidenceDir, 'before-submit.png') });
  current.proof.passed = true;
  current.proof.flow_url = this.page.url();
  writeFileSync(join(current.evidenceDir, 'ui-proof.json'), JSON.stringify(current.proof, null, 2));

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
  const job = input.job;
  const outDir = input.outDir;

  // Batch jobs run strictly sequentially (see gflow-cli's runJobs: a plain
  // for-await loop), so it is safe to give each job its own evidence
  // directory by simply reassigning this shared, module-level pointer right
  // before the job starts -- the previous job's submit()/applySettings()
  // calls have already fully completed and written their files by now.
  // image_pipeline.py's batch path reads a job's evidence at
  // <outDir>/.evidence/<job.id>/ (a `--base-image` equivalent for a batched
  // job is carried in `ingredients[0]`, resolved to an absolute path by
  // Python before the job is written to the jobs file).
  if (batchMode) {
    const jobEvidenceDir = resolve(outDir, '.evidence', job.id);
    await fsPromises.mkdir(jobEvidenceDir, { recursive: true });
    current = { proof: { mode: 'image', characters: job.character || [], passed: false }, evidenceDir: jobEvidenceDir };
  }
  const jobBaseImage = batchMode ? (job.ingredients && job.ingredients[0] ? resolve(job.ingredients[0]) : null) : baseImage;

  const context = this.page.context();
  const workerPage = await context.newPage();
  this.page = workerPage;
  const page = workerPage;

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

    if (jobBaseImage) {
      const {uploadMedia} = await import(join(base, 'dist/src/flow/ui.js'));
      await uploadMedia(page, /upload|add/i, jobBaseImage);
      // Require an observed attachment; never infer success from the requested path.
      const fileName = jobBaseImage.split('/').pop();
      const attached = page.locator('.prompt-input, form, [data-prompt-container]').getByText(fileName, {exact: true});
      if (!await attached.count()) throw Error('M2_BASE_IMAGE: cannot verify uploaded image in prompt UI');
      for (const name of job.character || []) {
        const characterStillAttached = await page.locator('.prompt-input, form, [data-prompt-container]').filter({hasText: name}).count();
        if (!characterStillAttached) throw Error('Character reference lost after base image upload: ' + name);
      }
      current.proof.base_image = jobBaseImage;
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
        characters: job.character?.length ? job.character : (current.proof.characters || []),
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
  // Character creation is never part of a batch (imageJobSchema only), so
  // `current` is always the single-job context here.
  await this.page.screenshot({ path: join(current.evidenceDir, 'before-submit.png') });
  current.proof.passed = true;
  current.proof.flow_url = this.page.url();
  writeFileSync(join(current.evidenceDir, 'ui-proof.json'), JSON.stringify(current.proof, null, 2));
};

process.exitCode = await runCli(['node', 'gflow', ...args]);
