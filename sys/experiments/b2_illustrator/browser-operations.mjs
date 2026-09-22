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
  if(command==='tool-snapshot:share-copy') {
    await bound.page.getByRole('button',{name:'Copy link',exact:true}).click();
    const link=await Promise.race([bound.page.evaluate(()=>navigator.clipboard.readText()),new Promise((_,reject)=>setTimeout(()=>reject(Error('CLIPBOARD_PERMISSION_PENDING')),3000))]);
    await bound.page.getByRole('button',{name:'Close share dialog',exact:true}).click();
    return {link};
  }
  if(command==='tool-snapshot:share-inspect') {
    await bound.page.getByRole('button',{name:'Share',exact:true}).click();
    return {snapshot:await bound.page.locator('body').ariaSnapshot()};
  }
  if(command.startsWith('tool-snapshot:queue:')) {
    const specs=JSON.parse(fs.readFileSync(command.slice('tool-snapshot:queue:'.length),'utf8'));
    const {runQueue}=await import('./queue-runner.mjs');
    return runQueue(specs,bound);
  }
  if(command === 'tool-snapshot:acceptance-reload') {
    const page=bound.page;let frame=await findToolFrame(page);
    const before=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
    if(before.queue?.length)throw Error('NONEMPTY_QUEUE_DO_NOT_MUTATE');
    await frame.getByRole('textbox').nth(0).fill('RELOAD ACCEPTANCE PROBE - do not generate');
    await frame.getByRole('button',{name:'Initialize Generation',exact:true}).click();
    const queued=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
    if(queued.queue?.length!==1 || queued.queue[0].status!=='QUEUED')throw Error('PROBE_ENQUEUE_FAILED');
    const file=path.join(safeResults(),'acceptance-reload-'+Date.now()+'.json');
    fs.writeFileSync(file,JSON.stringify({queued,generationSubmitted:false},null,2));
    await page.reload({waitUntil:'domcontentloaded'});frame=await findToolFrame(page);
    const restored=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
    const result={queued,restored,pass:restored.queue?.some(i=>i.id===queued.queue[0].id)===true,generationSubmitted:false};
    fs.writeFileSync(file,JSON.stringify(result,null,2));
    return {file,...result};
  }

  if(['tool-snapshot:parallel-smoke-2','tool-snapshot:parallel-smoke-4','tool-snapshot:batch-vocab-4-v2','tool-snapshot:batch-vocab-4-v3'].includes(command)) {
    const count=command.includes('4')?4:2;
    const batchName=command.endsWith('-v3')?'vocab-4-v3':command.endsWith('-v2')?'vocab-4-v2':`parallel-smoke-${count}`;
    const page=bound.page, frame=await findToolFrame(page), folder=safeResults();
    const intent=path.join(folder,`${batchName}-intent.json`);
    if(fs.existsSync(intent)) throw Error('ALREADY_ATTEMPTED_RECONCILE_ONLY');
    const existing=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
    if(existing.queue?.some(i=>!['COMPLETED','ACCEPTED'].includes(i.status))) throw Error('UNRESOLVED_QUEUE');
    const logFile=path.join(folder,`${batchName}-events.ndjson`);
    const record=(event)=>{const fd=fs.openSync(logFile,'a',0o600);try{fs.writeSync(fd,JSON.stringify({at:Date.now(),...event})+'\n');fs.fsyncSync(fd);}finally{fs.closeSync(fd);}};
    const ref={mediaId:canonicalMascotMediaId,base64:fs.readFileSync(canonicalMascotPath).toString('base64'),mimeType:'image/png',name:'canonical-mascot'};
    await frame.evaluate(ref=>{
      const el=document.getElementById('character-selector');
      let f=el[Object.keys(el).find(k=>k.startsWith('__reactFiber$'))];
      while(f && !(typeof f.type==='function' && f.type.name==='App'))f=f.return;
      let h=f?.memoizedState;
      while(h && !(h.memoizedState?.topic && h.queue?.dispatch))h=h.next;
      if(!h?.next?.next?.queue?.dispatch)throw Error('REFERENCE_HOOK_NOT_FOUND');
      h.next.queue.dispatch(null);h.next.next.queue.dispatch(ref);
    },ref);
    await frame.getByRole('button',{name:'Clear Character',exact:true}).waitFor();
    const boxes=frame.getByRole('textbox');
    await boxes.nth(1).fill('Clean minimalist stickman illustration, navy outlines, off-white background.');
    await boxes.nth(2).fill('Match canonical blue shirt #8CCFE8, white head, oval black eyes, coral tongue. One torso, no teeth or eyebrows.');
    await boxes.nth(3).fill('');await boxes.nth(4).fill('');
    await frame.getByRole('button',{name:'9:16',exact:true}).click();
    const combos=frame.getByRole('combobox');
    await combos.nth(2).selectOption({label:'🍌 Nano Banana Pro'});
    await combos.nth(3).selectOption({label:`${count} Workers`});
    for(const topic of ['The canonical mascot borrows a red book from a friend in a library. Show book passing toward mascot. No text.','The canonical mascot borrows a yellow umbrella from a friend beside a doorway on a rainy day. Show umbrella passing toward mascot. No text.',...(count===4?['The canonical mascot borrows a blue pen from a friend at a desk. Show pen passing toward mascot. No text.','The canonical mascot borrows a green watering can from a friend in a garden. Show watering can passing toward mascot. No text.']:[])]) {
      await boxes.nth(0).fill(topic+' STRICT CHARACTER LOCK: CH01 must exactly match the attached reference. Round white head, thick navy outline, two solid black vertical oval eyes, open happy mouth with a visible coral-pink tongue. Exactly one light-blue short-sleeve T-shirt #8CCFE8, two navy stick arms and two navy stick legs. No teeth, eyebrows or white pupils. Preserve the same bold stroke weight and head/body proportions. Wide full-body two-person shot: both heads, hands, torsos and feet entirely inside the image with generous 15 percent margins on every side. Small characters centered in the middle 60 percent of the frame. No close-up, no cropped heads or bodies. For the desk scene show both people standing beside a small desk, not sitting behind it. Do not simplify the mascot face.');
      await frame.getByRole('button',{name:'Initialize Generation',exact:true}).click();
    }
    const prepared=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
    const pending=prepared.queue.filter(i=>i.status==='QUEUED');
    if(pending.length!==count || pending.some(i=>i.characterRefMediaId!==ref.mediaId || i.config.aspectRatio!=='9:16'))throw Error('QUEUE_MAPPING_INVALID');
    fs.writeFileSync(intent,JSON.stringify({at:Date.now(),prepared},null,2),{flag:'wx'});
    record({state:'submitting',prepared});
    const start=Date.now();await frame.getByRole('button',{name:'Start Queue',exact:true}).click();
    let state;const captured=new Set();
    for(let n=0;n<120;n++) {
      await page.waitForTimeout(1000);
      state=await frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
      if(!Array.isArray(state.queue) || !pending.every(p=>state.queue.some(i=>i.id===p.id))) {record({state:'unknown',reason:'QUEUE_DISAPPEARED'});throw Error('QUEUE_DISAPPEARED_RECONCILE_NO_RESUBMIT');}
      for(const item of state.queue.filter(i=>pending.some(p=>p.id===i.id))) {
        if(item.mediaId && !captured.has(item.id)) {record({state:'generated',item});captured.add(item.id);}
      }
      if(state.status==='UNKNOWN'||state.queue.filter(i=>pending.some(p=>p.id===i.id)).every(i=>['COMPLETED','ACCEPTED'].includes(i.status)))break;
    }
    record({state:state.status==='IDLE'?'finished':'unknown',snapshot:state});
    const result={elapsedSeconds:(Date.now()-start)/1000,state};
    const file=path.join(folder,`${batchName}-result.json`);fs.writeFileSync(file,JSON.stringify(result,null,2));
    for(const i of state.queue.filter(i=>pending.some(p=>p.id===i.id))) {
      if(i.result?.base64) fs.writeFileSync(path.join(folder,i.id+(i.result.mimeType==='image/jpeg'?'.jpg':'.png')),Buffer.from(i.result.base64,'base64'));
    }
    return {file,elapsedSeconds:result.elapsedSeconds,items:state.queue.map(({id,status,mediaId,timestamps})=>({id,status,mediaId,timestamps}))};
  }

  if(['tool-snapshot:repair-queue','tool-snapshot:repair-queue-02'].includes(command)) {
    const page=bound?.page;
    if(!page || page.isClosed() || !page.url().startsWith(toolUrl)) throw Error('BOUND_TAB_UNAVAILABLE');
    const audit=path.join(safeResults(),command.endsWith('-02') ? 'queue-repair-02.json' : 'queue-repair-01.json');
    if(fs.existsSync(audit)) throw Error('REPAIR_ALREADY_SUBMITTED');
    await page.getByRole('radio',{name:'Edit',exact:true}).click();
    const prompt=`Fix V2.2.0 source defects only; do not generate images. syncState must save successfully BEFORE publishing stateRef/UI, return boolean, and set an in-memory dispatchBlocked latch on storage failure (retain raw returned results in memory for export). Every caller must honor failure before SDK invocation. updateItem must merge timestamps with the latest stored item, ignoring undefined fields. processItem must use submitTime, never stale item.timestamps.submit. Persist mediaId/result before decoding. On ANY post-submit error set item UNKNOWN and global UNKNOWN, latch dispatchBlocked. checkIdle must never overwrite UNKNOWN/PAUSED/storage failure. Scheduler and Start button must reject dispatch when any item UNKNOWN, even after reload. Each item callback checks the latest latch before invocation so a forEach cannot dispatch after sibling failure. On load handle legacy VP_LAB_STATE_V2 safely: queue may be absent; retain legacy history and pendingRequest, migrate without erasing keys, unresolved legacy must block. Preserve source-backed old outputs. Restore Export Journal JSON with full queue, refs, mediaId, timing, journal and legacy history using UTF8. Add accessible labels Topic / Prompt, Style, Preserve, Change, Literal Text Overlay, Font, Color, Placement, Model, Concurrency, Start Queue. Initialize Generation should enqueue exactly one item; Start Queue explicit only. Keep references, all controls, defaults concurrency1 and 9:16, image-only. No automatic generation or publishing. Apply these exact corrections.`;
    await page.getByRole('textbox',{name:'Ask applet agent to make changes',exact:true}).fill(prompt);
    fs.writeFileSync(audit,JSON.stringify({at:new Date().toISOString(),prompt}),{flag:'wx'});
    await page.getByRole('button',{name:'Send message',exact:true}).click();
    return {status:'repair_requested',audit,generationSubmitted:false};
  }
  if(command === 'tool-snapshot:read-only') {
    const page=bound?.page;
    if(!page || page.isClosed() || !page.url().startsWith(toolUrl)) throw Error('BOUND_TAB_UNAVAILABLE');
    await page.getByRole('radio',{name:'Tool',exact:true}).click();
    const frames=[];
    for(const f of page.frames()) {
      frames.push({url:f.url(),snapshot:await f.locator('body').ariaSnapshot().catch(()=>''),scripts:await f.locator('script').allTextContents().catch(()=>[])});
    }
    const file=path.join(safeResults(),`readonly-${Date.now()}.json`);
    fs.writeFileSync(file,JSON.stringify({frames},null,2));
    return {file,frames:frames.map(({url,snapshot})=>({url,snapshot})),generationSubmitted:false};
  }
  if(command === 'tool-snapshot:upgrade-queue') {
    const page=bound?.page;
    if(!page || page.isClosed() || !page.url().startsWith(toolUrl)) throw Error('BOUND_TAB_UNAVAILABLE');
    const prompt=`Upgrade this existing experimental still-image tool for measurable parallel generation. Preserve every existing control, model, references, journal, single-image button accessible name Initialize Generation, and existing saved results. Do not generate any images automatically. Add separate outputs-per-request and concurrent-requests controls, both default 1. Only expose native output counts supported by the actual Flow SDK; otherwise show output count 1 with an honest unsupported explanation, never fake a batch with multiple SDK calls. Add a queue accepting independent prompt items, each immutable snapshot with sceneId, beatId, ratio, config and actual character/base mediaIds. Concurrency selectable 1,2,3,4 with default 1. Each worker uses its own immutable snapshot, never shared mutable form state. based_on items wait for an explicitly accepted parent and its real mediaId. Persist request ID and submitting status BEFORE SDK call, persist returned mediaId immediately BEFORE image dimension measurement or downloads. Any ambiguous error becomes UNKNOWN and blocks further dispatch; never retry generation automatically or clear unresolved state. On authentication, CAPTCHA, quota, rate-limit or persistence errors pause queue. Downloads may retry only an existing mediaId. Add enqueue-current-input and explicit Start Queue buttons. Track monotonic timestamps for prepare, submit, first result, all results, validation and download separately. Display outputs linked to their request IDs and export all metadata as UTF8 JSON. Keep generation image-only, model Nano Banana Pro selectable, correct references and 9:16. Never claim zero cost without real billing evidence. Do not publish. Implement code only and wait for manual testing.`;
    const audit=path.join(safeResults(),'queue-upgrade-submitted.json');
    if(fs.existsSync(audit)) throw Error('UPGRADE_ALREADY_SUBMITTED: inspect instead of resending');
    await page.getByRole('textbox',{name:'Ask applet agent to make changes',exact:true}).fill(prompt);
    fs.writeFileSync(audit,JSON.stringify({submittedAt:new Date().toISOString(),prompt}),{flag:'wx'});
    await page.getByRole('button',{name:'Send message',exact:true}).click();
    return {status:'upgrade_requested',audit,generationSubmitted:false};
  }
  if(command === 'tool-snapshot:cost-inspect') {
    const page=bound?.page;
    if(!page || page.isClosed()) throw Error('BOUND_TAB_UNAVAILABLE');
    const frame=await findToolFrame(page);
    const state=await frame.locator('body').innerText();
    if(!/\bIDLE\b/.test(state) || /\bUNKNOWN\b/.test(state)) throw Error('TOOL_NOT_IDLE');
    const folder=safeResults();
    const stamp=Date.now();
    const source=await frame.locator('script').allTextContents();
    fs.writeFileSync(path.join(folder,`source-before-${stamp}.json`),JSON.stringify({url:page.url(),state,scripts:source},null,2));
    try {
      await page.goto(toolUrl.split('/tool/')[0],{waitUntil:'domcontentloaded'});
      await page.getByRole('button',{name:'Account details',exact:true}).click({timeout:20000});
      const snapshot=await page.locator('body').ariaSnapshot();
      const screenshot=path.join(folder,`cost-settings-${stamp}.png`);
      await page.screenshot({path:screenshot});
      const result={observedAt:new Date().toISOString(),snapshot,screenshot,generationSubmitted:false,chargedCredits:null};
      fs.writeFileSync(path.join(folder,`cost-settings-${stamp}.json`),JSON.stringify(result,null,2));
      return result;
    } finally {await page.goto(toolUrl,{waitUntil:'domcontentloaded'});}
  }
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
  if(frame && command.startsWith('tool-snapshot:') && await frame.getByRole('button',{name:'Start Queue',exact:true}).isVisible()) {
    throw Error('B2_QUEUE_ADAPTER_NOT_ACCEPTED: the legacy single-image adapter cannot operate the queue tool; use the isolated acceptance runner');
  }
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

    // Preserve ambiguous submissions for reconciliation; clearing state can cause duplicate generation.
    const isStuck = await frame.evaluate(() => {
      return document.body.innerText.includes('STATE: UNKNOWN') || document.body.innerText.includes('STABILITY ALERT');
    }).catch(() => false);

    if (isStuck) {
      throw new Error('FLOW_RECONCILIATION_REQUIRED: Tool state is UNKNOWN or has a stability alert. Preserve the journal and reconcile existing media with real UI evidence before submitting another request.');
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
    await frame.getByRole('combobox',{name:'Model',exact:true}).selectOption({label:'🍌 Nano Banana Pro'});
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
    if(!refUpdateRes.success || (charRefPath && !refUpdateRes.charSet)) throw Error('REFERENCE_SETUP_FAILED');
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
    const intentPath=path.join(safeResults(),`submission-${testConfig.testCase}.json`);
    fs.writeFileSync(intentPath,JSON.stringify({state:'submitting',startedAt:startTime,request:testConfig,model:'🍌 Nano Banana Pro'},null,2),{flag:'wx'});
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
