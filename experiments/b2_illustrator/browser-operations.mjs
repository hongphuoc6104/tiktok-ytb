/** Fixed, bounded experimental UI operations; generates baseline image and harvests output. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { findToolFrame, safeResults, toolUrl } from './controller.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const canonicalMascotPath = path.resolve(here, '../../assets/characters/channel-mascot/reference-v1.png');
const canonicalMascotMediaId = 'de94a39b-155f-4afe-acbb-d9d4b59ad532';

export async function runOperation(command, bound) {
  if(command.startsWith('tool-snapshot:mascot-')) {
    const helper=await import('./channel-character-flow.mjs?revision='+Date.now());
    return helper.runCharacterOperation(command,bound);
  }
  const page = bound?.page;
  if (!page || page.isClosed()) throw Error('BOUND_TAB_UNAVAILABLE');
  if (!page.url().startsWith(toolUrl)) {
    if (page.url().startsWith('https://flow.google.com/project/')) {
      await page.goto(toolUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
    } else {
      throw Error(`BOUND_TAB_NAVIGATED: expected ${toolUrl}, got ${page.url()}`);
    }
  }

  if (command === 'editor-inspect') {
    const editRadio = page.getByRole('radio', { name: 'Edit', exact: true });
    if (await editRadio.isVisible({ timeout: 2000 }).catch(() => false)) {
      await editRadio.click().catch(() => {});
    }
  } else if (command === 'reference-inspect' || command === 'tool-snapshot' || command.startsWith('tool-snapshot:')) {
    const toolRadio = page.getByRole('radio', { name: 'Tool', exact: true });
    if (await toolRadio.isVisible({ timeout: 2000 }).catch(() => false)) {
      const checked = await toolRadio.isChecked().catch(() => false);
      if (!checked) await toolRadio.click().catch(() => {});
    }
  } else throw Error('Unsupported fixed operation');

  let frame = await findToolFrame(page).catch(() => null);
  const step2Execution = { executed: false };

  if (frame && command === 'reference-inspect') {
    // Deep DOM audit using Playwright locators and frame evaluation
    const baseBtnLocator = frame.getByRole('button', { name: /Select Base Scene/i });
    const charBtnLocator = frame.getByRole('button', { name: /Select Character/i });

    const baseBtnInfo = {
      visible: await baseBtnLocator.isVisible().catch(() => false),
      enabled: await baseBtnLocator.isEnabled().catch(() => false),
      html: await baseBtnLocator.evaluate(el => el.outerHTML).catch(e => e.message)
    };

    const charBtnInfo = {
      visible: await charBtnLocator.isVisible().catch(() => false),
      enabled: await charBtnLocator.isEnabled().catch(() => false),
      html: await charBtnLocator.evaluate(el => el.outerHTML).catch(e => e.message)
    };

    // Inspect React Fiber parent component full source and Flow SDK
    const componentAudit = await frame.evaluate(async () => {
      const el = document.getElementById('base-scene-selector');
      if (!el) return { found: false };
      const fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
      const fiber = el[fiberKey];
      
      let curr = fiber;
      let parentComp = null;
      let depth = 0;
      let hooksInfo = [];
      let appFiber = null;
      while (curr && depth < 20) {
        if (curr.type && typeof curr.type === 'function' && curr.type.name !== 'ReferenceSlot') {
          parentComp = {
            name: curr.type.name,
            source: curr.type.toString()
          };
          appFiber = curr;
          break;
        }
        curr = curr.return;
        depth++;
      }

      if (appFiber && appFiber.memoizedState) {
        let hook = appFiber.memoizedState;
        let idx = 0;
        while (hook && idx < 12) {
          hooksInfo.push({
            index: idx,
            hasDispatch: typeof hook.queue?.dispatch === 'function',
            valueType: typeof hook.memoizedState,
            isNull: hook.memoizedState === null,
            preview: typeof hook.memoizedState === 'object' && hook.memoizedState ? Object.keys(hook.memoizedState) : String(hook.memoizedState).substring(0, 50)
          });
          hook = hook.next;
          idx++;
        }
      }

      let scriptsData = [];
      try {
        const scripts = Array.from(document.querySelectorAll('script'));
        for (let i = 0; i < scripts.length; i++) {
          const s = scripts[i];
          if (s.src) scriptsData.push({ type: 'src', src: s.src });
          else {
            scriptsData.push({ type: 'inline', index: i, length: s.innerText.length });
          }
        }
      } catch (e) {
        scriptsData = [{ error: e.message }];
      }

      // Return the content of the main bundled inline script (length > 10000)
      let mainBundle = null;
      try {
        const scripts = Array.from(document.querySelectorAll('script'));
        const main = scripts.find(s => !s.src && s.innerText.length > 10000);
        if (main) mainBundle = main.innerText;
      } catch (e) {
        mainBundle = e.message;
      }

      // Storyboard component
      const storyboardEl = Array.from(document.querySelectorAll('h3')).find(h => /Sequential Narrative Plan/i.test(h.innerText));
      let storyboardComp = null;
      if (storyboardEl) {
        const k = Object.keys(storyboardEl).find(k => k.startsWith('__reactFiber$'));
        let curr = storyboardEl ? storyboardEl[k] : null;
        while (curr) {
          if (curr.type && typeof curr.type === 'function') {
            storyboardComp = { name: curr.type.name, source: curr.type.toString() };
            break;
          }
          curr = curr.return;
        }
      }

      let storageState = null;
      try {
        storageState = JSON.parse(localStorage.getItem('VP_LAB_STATE_V2') || 'null');
      } catch (e) {
        storageState = { error: e.message };
      }

      return {
        parentCompName: parentComp?.name,
        hooksInfo,
        storageState,
        scriptsCount: scriptsData.length,
        scriptsInfo: scriptsData,
        mainBundle,
        storyboardComp
      };
    }).catch(e => ({ error: e.message }));

    if (componentAudit?.mainBundle) {
      const bundlePath = path.join(safeResults(), 'applet-main-bundle.js');
      fs.writeFileSync(bundlePath, componentAudit.mainBundle);
      componentAudit.bundleSavedPath = bundlePath;
      componentAudit.bundleLength = componentAudit.mainBundle.length;
      delete componentAudit.mainBundle;
    }

    let fileChooserInfo = { note: 'Not triggered - using Flow2.media.select internal picker' };

    const tapElements = await frame.evaluate(() => {
      return Array.from(document.querySelectorAll('*'))
        .filter(el => (el.innerText || '').includes('Tap to Upload') && el.children.length <= 2)
        .map(el => ({
          tagName: el.tagName,
          className: el.className,
          outerHTML: el.outerHTML.substring(0, 300)
        }));
    });

    // Check all inputs across frames
    const allFramesInputs = [];
    for (const f of page.frames()) {
      const inputs = await f.evaluate(() => {
        return Array.from(document.querySelectorAll('input')).map(i => ({
          type: i.type,
          name: i.name,
          id: i.id,
          accept: i.accept,
          outerHTML: i.outerHTML.substring(0, 150)
        }));
      }).catch(() => []);
      if (inputs.length) allFramesInputs.push({ frameUrl: f.url(), inputs });
    }

    // Evaluate Narrative Plan and DOM details inside frame
    const narrativePlanAudit = await frame.evaluate(() => {
      const planHeading = Array.from(document.querySelectorAll('*')).find(el => /Sequential Narrative Plan/i.test(el.innerText || ''));
      const planCards = Array.from(document.querySelectorAll('*')).filter(el => {
        const t = el.innerText || '';
        return (t.includes('STEP 01') || t.includes('STEP 02') || t.includes('STEP 03') || t.includes('STEP 04')) && el.children.length > 2;
      }).map(card => ({
        text: card.innerText.substring(0, 150),
        inputs: Array.from(card.querySelectorAll('input, textarea')).map(i => ({
          type: i.type,
          placeholder: i.placeholder,
          value: i.value,
          ariaLabel: i.getAttribute('aria-label')
        })),
        buttons: Array.from(card.querySelectorAll('button')).map(b => ({
          text: b.innerText,
          ariaLabel: b.getAttribute('aria-label'),
          disabled: b.disabled
        })),
        images: Array.from(card.querySelectorAll('img, svg')).map(im => ({
          tag: im.tagName,
          src: im.getAttribute('src') || null,
          alt: im.getAttribute('alt') || null
        }))
      }));

      return {
        headingFound: !!planHeading,
        cardCount: planCards.length,
        planCards
      };
    }).catch(err => ({ error: err.message }));

    // Optional Phase 2 test: Injection or Upload interaction based on current-test.json
    let referenceAction = null;
    let referenceActionResult = null;
    const configPath = path.join(here, 'current-test.json');
    if (fs.existsSync(configPath)) {
      try {
        const cfg = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        referenceAction = cfg.referenceAction || null;
      } catch {}
    }

    if (referenceAction === 'inject-reference') {
      const basePosePath = path.join(safeResults(), 'EXP-BASE-POSE-1789982107162.jpg');
      if (fs.existsSync(basePosePath)) {
        const b64 = fs.readFileSync(basePosePath).toString('base64');
        const injectRes = await frame.evaluate(async ({ mediaId, base64, mimeType, name, slot }) => {
          const el = document.getElementById(slot === 'base' ? 'base-scene-selector' : 'character-selector');
          if (!el) return { success: false, error: 'Element not found' };
          const fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
          const fiber = el[fiberKey];
          let curr = fiber;
          let appFiber = null;
          while (curr) {
            if (curr.type && typeof curr.type === 'function' && curr.type.name === 'App') {
              appFiber = curr;
              break;
            }
            curr = curr.return;
          }
          if (!appFiber) return { success: false, error: 'App fiber not found' };

          const targetHook = slot === 'base' ? appFiber.memoizedState.next : appFiber.memoizedState.next.next;
          if (!targetHook || !targetHook.queue?.dispatch) {
            return { success: false, error: 'Hook dispatch not found' };
          }

          targetHook.queue.dispatch({
            mediaId,
            base64,
            mimeType,
            name
          });
          return { success: true, slot, mediaId, name };
        }, {
          mediaId: '2c03a91f-80b6-4579-8261-3177f7182655',
          base64: b64,
          mimeType: 'image/jpeg',
          name: 'EXP-BASE-POSE',
          slot: 'character'
        }).catch(e => ({ success: false, error: e.message }));

        await page.waitForTimeout(600);

        // Verify slot DOM after injection
        const slotStatus = await frame.evaluate(() => {
          const charEl = document.getElementById('character-selector');
          const baseEl = document.getElementById('base-scene-selector');
          return {
            characterSlot: {
              hasImg: !!charEl?.querySelector('img'),
              imgSrcLength: charEl?.querySelector('img')?.src?.length || 0,
              hasClearBtn: !!charEl?.querySelector('button[aria-label*="Clear"]'),
              classList: Array.from(charEl?.classList || [])
            },
            baseSlot: {
              hasImg: !!baseEl?.querySelector('img'),
              imgSrcLength: baseEl?.querySelector('img')?.src?.length || 0,
              hasClearBtn: !!baseEl?.querySelector('button[aria-label*="Clear"]'),
              classList: Array.from(baseEl?.classList || [])
            }
          };
        }).catch(e => ({ error: e.message }));

        await frame.evaluate(() => {
          const el = document.getElementById('character-selector') || document.getElementById('base-scene-selector');
          if (el) el.scrollIntoView({ behavior: 'instant', block: 'center' });
        });
        await page.waitForTimeout(400);

        // Screenshot after injection
        const refScreenshotPath = path.join(safeResults(), `reference-injected-${Date.now()}.png`);
        await page.screenshot({ path: refScreenshotPath });

        referenceActionResult = {
          action: 'inject-reference',
          injectRes,
          slotStatus,
          screenshot: refScreenshotPath
        };
      }
    } else if (referenceAction === 'clear-reference') {
      const clearRes = await frame.evaluate(() => {
        const charClear = document.querySelector('#character-selector button[aria-label*="Clear"]');
        if (charClear) {
          charClear.click();
          return { clicked: 'character' };
        }
        const baseClear = document.querySelector('#base-scene-selector button[aria-label*="Clear"]');
        if (baseClear) {
          baseClear.click();
          return { clicked: 'base' };
        }
        return { clicked: null, note: 'No clear button found' };
      }).catch(e => ({ error: e.message }));

      await page.waitForTimeout(500);
      const clearScreenshotPath = path.join(safeResults(), `reference-cleared-${Date.now()}.png`);
      await page.screenshot({ path: clearScreenshotPath });
      referenceActionResult = { action: 'clear-reference', clearRes, screenshot: clearScreenshotPath };
    }

    const audit = {
      baseBtnInfo,
      charBtnInfo,
      componentAudit,
      fileChooserInfo,
      tapElements,
      allFramesInputs,
      narrativePlan: narrativePlanAudit,
      referenceActionResult
    };

    const auditFile = path.join(safeResults(), `dom-audit-${Date.now()}.json`);
    fs.writeFileSync(auditFile, JSON.stringify(audit, null, 2));

    return {
      command: 'reference-inspect',
      observedAt: new Date().toISOString(),
      audit,
      auditFile
    };
  }

  if (frame && (command === 'tool-snapshot' || command.startsWith('tool-snapshot:'))) {
    step2Execution.executed = true;
    step2Execution.steps = [];

    // Load test configuration (defaults to TC-16x9-03 Multi-Character or custom spec)
    let specPath = null;
    if (command.startsWith('tool-snapshot:')) {
      specPath = command.slice('tool-snapshot:'.length).trim();
    }
    let testConfig = {
      testCase: 'TC-16x9-03',
      testName: 'Level 3: Multi-Character Interaction (Two Stickmen Agreement)',
      prompt: 'Two clean minimal stickmen standing together shaking hands in friendly agreement',
      preserve: 'Clean black stickman line weight, minimal ink on light paper background',
      change: '',
      literalText: 'AGREED',
      ratio: '16:9'
    };
    const configPath = specPath || path.join(here, 'current-test.json');
    if (fs.existsSync(configPath)) {
      try {
        testConfig = { ...testConfig, ...JSON.parse(fs.readFileSync(configPath, 'utf8')) };
      } catch {}
    }

    // Auto-recovery: If frame is stuck in UNKNOWN or has alert, clear localStorage and reload tab
    const isStuck = await frame.evaluate(() => {
      return document.body.innerText.includes('STATE: UNKNOWN') || document.body.innerText.includes('STABILITY ALERT');
    }).catch(() => false);

    if (isStuck) {
      await frame.evaluate(() => localStorage.clear()).catch(() => {});
      await page.reload({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(2500);
      frame = await findToolFrame(page);
    }

    // 1. Setup parameters
    const promptInput = frame.getByRole('textbox', { name: 'Topic / Prompt' });
    const preserveInput = frame.getByRole('textbox', { name: 'Preserve' });
    const changeInput = frame.getByRole('textbox', { name: 'Change' });
    const textInput = frame.getByRole('textbox', { name: 'Literal Text Overlay' });

    await promptInput.fill(testConfig.prompt);
    await preserveInput.fill(testConfig.preserve || '');
    await changeInput.fill(testConfig.change || '');
    await textInput.fill(testConfig.literalText || '');
    step2Execution.steps.push({ step: 'fill_params', ...testConfig });

    // Select ratio
    if (testConfig.ratio === '9:16') {
      await frame.getByRole('button', { name: '9:16', exact: true }).click();
    } else {
      await frame.getByRole('button', { name: '16:9', exact: true }).click();
    }
    await page.waitForTimeout(400);

    // Inject or clear references based on testConfig
    const basePoseDefault = path.join(safeResults(), 'EXP-BASE-POSE-1789982107162.jpg');
    const defaultMascot = fs.existsSync(canonicalMascotPath) ? canonicalMascotPath : basePoseDefault;
    const baseRefPath = testConfig.baseRefPath ? path.resolve(testConfig.baseRefPath) : (testConfig.useBaseSceneRef ? basePoseDefault : null);
    const charRefPath = testConfig.characterRefPath ? path.resolve(testConfig.characterRefPath) : (testConfig.useCharacterRef !== false ? defaultMascot : null);

    const refUpdateRes = await frame.evaluate(async ({ baseData, charData }) => {
      const el = document.getElementById('base-scene-selector');
      if (!el) return { success: false, error: 'Element not found' };
      const fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
      const fiber = el[fiberKey];
      let curr = fiber;
      let appFiber = null;
      while (curr) {
        if (curr.type && typeof curr.type === 'function' && curr.type.name === 'App') {
          appFiber = curr;
          break;
        }
        curr = curr.return;
      }
      if (!appFiber) return { success: false, error: 'App fiber not found' };

      const baseHook = appFiber.memoizedState.next;
      const charHook = appFiber.memoizedState.next.next;

      if (baseHook?.queue?.dispatch) {
        baseHook.queue.dispatch(baseData || null);
      }
      if (charHook?.queue?.dispatch) {
        charHook.queue.dispatch(charData || null);
      }

      return {
        success: true,
        baseSet: !!baseData,
        charSet: !!charData
      };
    }, {
      baseData: baseRefPath && fs.existsSync(baseRefPath) ? {
        mediaId: testConfig.baseMediaId || '2c03a91f-80b6-4579-8261-3177f7182655',
        base64: fs.readFileSync(baseRefPath).toString('base64'),
        mimeType: baseRefPath.endsWith('.png') ? 'image/png' : baseRefPath.endsWith('.webp') ? 'image/webp' : 'image/jpeg',
        name: path.basename(baseRefPath)
      } : null,
      charData: charRefPath && fs.existsSync(charRefPath) ? {
        mediaId: testConfig.charMediaId || (charRefPath === canonicalMascotPath ? canonicalMascotMediaId : 'de94a39b-155f-4afe-acbb-d9d4b59ad532'),
        base64: fs.readFileSync(charRefPath).toString('base64'),
        mimeType: charRefPath.endsWith('.png') ? 'image/png' : charRefPath.endsWith('.webp') ? 'image/webp' : 'image/jpeg',
        name: path.basename(charRefPath)
      } : null
    }).catch(e => ({ success: false, error: e.message }));

    step2Execution.steps.push({ step: 'configured_references', refUpdateRes });
    await page.waitForTimeout(600);

    // 2. Capture existing images and existing Forge ID to ensure we harvest the NEW image
    const existingSrcs = new Set();
    const existingImgs = await frame.locator('img').all();
    for (const im of existingImgs) {
      const s = await im.getAttribute('src').catch(() => null);
      if (s) existingSrcs.add(s);
    }
    const prevBodyText = await frame.locator('body').innerText().catch(() => '');
    const prevForgeIdMatch = prevBodyText.match(/Forge ID\s+([A-Z0-9_-]+)/i);
    const prevForgeId = prevForgeIdMatch ? prevForgeIdMatch[1] : null;
    step2Execution.prevForgeId = prevForgeId;

    // 3. Locate Initialize Generation button
    const genBtn = frame.getByRole('button', { name: /Initialize Generation/ });
    if (!(await genBtn.isVisible()) || !(await genBtn.isEnabled())) {
      throw Error('GENERATE_BUTTON_NOT_READY: button is hidden or disabled');
    }

    // 4. Click Initialize Generation and record start time
    const startTime = Date.now();
    await genBtn.click();
    step2Execution.steps.push({ step: 'clicked_initialize_generation', timestamp: new Date(startTime).toISOString() });

    // 5. Poll for generation completion (up to 90 seconds)
    let harvestedImage = null;
    let pollAttempts = 0;
    const maxPollAttempts = 60; // 60 * 1.5s = 90s

    while (pollAttempts < maxPollAttempts) {
      await page.waitForTimeout(1500);
      pollAttempts++;

      const currentBodyText = await frame.locator('body').innerText().catch(() => '');
      const newForgeIdMatch = currentBodyText.match(/Forge ID\s+([A-Z0-9_-]+)/i);
      const newForgeId = newForgeIdMatch ? newForgeIdMatch[1] : null;
      const isCommitted = /COMMITTED|STATE:\s*IDLE/i.test(currentBodyText);

      // Check if Forge ID updated to a new ID and status is committed
      if (newForgeId && newForgeId !== prevForgeId && isCommitted) {
        // Try getting Forge Output image specifically first
        const forgeOutputImg = frame.locator('img[alt="Forge Output"]').first();
        let candidateSrc = await forgeOutputImg.getAttribute('src').catch(() => null);

        if (!candidateSrc) {
          const imgs = await frame.locator('img').all();
          for (let i = imgs.length - 1; i >= 0; i--) {
            const s = await imgs[i].getAttribute('src').catch(() => null);
            if (s && (s.startsWith('data:image') || s.startsWith('blob:') || s.startsWith('http'))) {
              candidateSrc = s;
              break;
            }
          }
        }

        if (candidateSrc) {
          harvestedImage = { src: candidateSrc, forgeId: newForgeId };
          break;
        }
      }

      // Check for error text in frame
      if (/generation failed|error occurred|insufficient credits|rate limit/i.test(currentBodyText)) {
        step2Execution.errorObserved = currentBodyText.substring(0, 300);
        break;
      }
    }

    const endTime = Date.now();
    step2Execution.testCase = testConfig.testCase;
    step2Execution.testName = testConfig.testName;
    step2Execution.latencySeconds = (endTime - startTime) / 1000;
    step2Execution.generationCompleted = !!harvestedImage;
    if (harvestedImage) step2Execution.forgeId = harvestedImage.forgeId;

    // 6. Harvest and save image file
    if (harvestedImage) {
      let imageBuffer;
      let ext = '.png';

      if (harvestedImage.src.startsWith('data:image')) {
        const mime = harvestedImage.src.split(';')[0].replace('data:', '');
        ext = mime === 'image/jpeg' ? '.jpg' : mime === 'image/webp' ? '.webp' : '.png';
        const base64Data = harvestedImage.src.split(',')[1];
        imageBuffer = Buffer.from(base64Data, 'base64');
      } else {
        // Fetch blob/http inside frame context
        const base64Data = await frame.evaluate(async (url) => {
          const resp = await fetch(url);
          const blob = await resp.blob();
          return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.readAsDataURL(blob);
          });
        }, harvestedImage.src);
        imageBuffer = Buffer.from(base64Data, 'base64');
        ext = '.png';
      }

      const targetDir = testConfig.outDir ? path.resolve(testConfig.outDir) : safeResults();
      if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
      const savedPath = path.join(targetDir, `${testConfig.testCase}-${Date.now()}${ext}`);
      fs.writeFileSync(savedPath, imageBuffer);
      step2Execution.savedImagePath = savedPath;
      step2Execution.imageBytes = imageBuffer.length;

      // 7. Run automated technical validation via validate_asset.py
      try {
        const pyScript = path.join(here, 'validate_asset.py');
        const validationOutput = execFileSync('python3', [pyScript, savedPath, '--ratio', testConfig.ratio], { encoding: 'utf8' });
        step2Execution.technicalValidation = JSON.parse(validationOutput);
      } catch (valErr) {
        step2Execution.technicalValidation = { status: 'failed', error: valErr.message, stderr: valErr.stderr };
      }
    }

    // 8. Test Export Journal JSON if button visible
    try {
      const journalBtn = frame.getByRole('button', { name: /Export Journal JSON/i });
      if (await journalBtn.isVisible()) {
        const downloadPromise = page.waitForEvent('download', { timeout: 4000 }).catch(() => null);
        await journalBtn.click();
        const download = await downloadPromise;
        if (download) {
          const dlPath = path.join(safeResults(), `exported-journal-${Date.now()}.json`);
          await download.saveAs(dlPath);
          step2Execution.exportedJournalPath = dlPath;
        }
      }
    } catch (jErr) {
      step2Execution.journalExportNote = jErr.message;
    }
  }

  const screenshotPath = path.join(safeResults(), `step2-result-${Date.now()}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: false }).catch(() => {});

  const snapshot = await page.locator('body').ariaSnapshot();
  const frames = [];
  for (const f of page.frames().filter(f => f !== page.mainFrame())) {
    try { frames.push({ url: f.url(), snapshot: await f.locator('body').ariaSnapshot({ timeout: 3000 }) }); } catch {}
  }

  const record = {
    command,
    observedAt: new Date().toISOString(),
    profile: bound.identity.observedProfile,
    url: page.url(),
    step2Execution,
    screenshot: screenshotPath,
    snapshot,
    frames,
    generationSubmitted: step2Execution.executed && step2Execution.generationCompleted
  };

  const destination = path.join(safeResults(), `step2-baseline-${Date.now()}.json`);
  fs.writeFileSync(destination, JSON.stringify(record, null, 2), { flag: 'wx' });
  return { status: 'executed', evidence: destination, ...record };
}
