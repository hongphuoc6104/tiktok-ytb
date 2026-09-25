/**
 * FlowPool page operations on an ALREADY RUNNING, user-signed-in Chrome.
 *
 * Hard rules: never launch or sign in, never type a password, never touch a
 * CAPTCHA (detect -> throw CAPTCHA), never read or copy cookies. Only
 * clickStartQueue (images) and FlowPage.submit (clips) can start a generation,
 * and both are called from commit(), after the Python journal fsynced
 * `submitted`.
 */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
export const SYS = path.resolve(here, '..');
const GFLOW = path.join(SYS, 'node_modules/@swissmarley/gflow-cli/dist/src');
const B2 = path.join(SYS, 'experiments/b2_illustrator');

export function coded(code, message = '', extra = {}) {
  const e = new Error(message || code);
  e.code = code;
  Object.assign(e, extra);
  return e;
}

// ----------------------------------------------------------------- detection
const CAPTCHA_TEXT = /(verify (that )?you('|’)?re (not a robot|a human)|unusual traffic from your computer|i'?m not a robot|complete the captcha|xác minh bạn không phải là rô bốt)/i;
const LOGIN_TEXT = /(sign in to continue|choose an account|to continue to (google labs|labs\.google|flow)|verify it'?s you|use your google account|đăng nhập để tiếp tục|chọn tài khoản)/i;

/** Pure classifier over a page snapshot {url, text, frames:[{src,width,height}]}. */
export function classifySnapshot({url = '', text = '', frames = []}) {
  if (/^https:\/\/(www\.)?google\.com\/sorry\//.test(url)) return {state: 'captcha', reason: 'google sorry page'};
  const challenge = frames.find(f => /recaptcha|captcha|challenge/i.test(f.src || '') && !/size=invisible/.test(f.src || '')
    && (f.width || 0) > 60 && (f.height || 0) > 60);
  if (challenge) return {state: 'captcha', reason: 'visible challenge frame'};
  if (CAPTCHA_TEXT.test(text)) return {state: 'captcha', reason: 'challenge text'};
  if (/^https:\/\/accounts\.google\.com\//.test(url)) return {state: 'needs_login', reason: 'accounts.google.com'};
  if (LOGIN_TEXT.test(text)) return {state: 'needs_login', reason: 'sign-in text'};
  return {state: 'ok'};
}

export async function snapshot(page) {
  const dom = await page.evaluate(() => ({
    text: (document.body?.innerText || '').slice(0, 20000),
    frames: [...document.querySelectorAll('iframe')].map(f => {
      const r = f.getBoundingClientRect();
      const style = getComputedStyle(f);
      const shown = style.visibility !== 'hidden' && style.display !== 'none' && Number(style.opacity || 1) > 0.1;
      return {src: f.src || '', title: f.title || '', width: shown ? r.width : 0, height: shown ? r.height : 0};
    }),
  })).catch(() => ({text: '', frames: []}));
  return {url: page.url(), ...dom};
}

export async function assertUsable(page) {
  const verdict = classifySnapshot(await snapshot(page));
  if (verdict.state === 'captcha') throw coded('CAPTCHA', `CAPTCHA shown (${verdict.reason}); solve it yourself, then run flowpool doctor`);
  if (verdict.state === 'needs_login') throw coded('NEEDS_LOGIN', `signed out (${verdict.reason}); sign in yourself, then run flowpool doctor`);
  return verdict;
}

// ----------------------------------------------------------------- credits
const NUM = String.raw`(\d{1,3}(?:[.,\s ]\d{3})+|\d+)`;
const AFTER = new RegExp(NUM + String.raw`\s*(?:AI\s+)?(?:credits?|tín dụng)\b(?!\s*(?:per|\/|each|mỗi|a |an ))`, 'gi');
const BEFORE = new RegExp(String.raw`(?:credits?|tín dụng)\s*(?:left|remaining|còn lại)?\s*[:：]?\s*` + NUM, 'gi');
const toInt = s => Number(String(s).replace(/[^\d]/g, ''));

/** Balance candidates in free text; cost phrases ("20 credits per video") are ignored. */
export function extractCredits(text) {
  const found = [];
  for (const re of [AFTER, BEFORE]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text))) {
      const prefix = text.slice(Math.max(0, m.index - 12), m.index);
      if (/(uses?|costs?|tốn|dùng)\s*$/i.test(prefix)) continue;
      found.push({value: toInt(m[1]), raw: m[0].trim()});
    }
  }
  return found;
}

/** One unambiguous value or null (never guess between several numbers). */
export function pickCredits(texts) {
  const all = texts.flatMap(t => extractCredits(t || ''));
  const values = [...new Set(all.map(c => c.value))];
  return values.length === 1 ? {value: values[0], raw: all.map(c => c.raw)} : {value: null, raw: all.map(c => c.raw)};
}

export async function readCredits(page, probe = {}) {
  const visibleTexts = sel => page.locator(sel).evaluateAll(els => els
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; })
    .map(e => `${e.getAttribute('aria-label') || ''} ${e.innerText || ''}`)).catch(() => []);
  for (const sel of probe.selectors || []) {
    const got = pickCredits(await visibleTexts(sel));
    if (got.value !== null) return {...got, method: `selector:${sel}`};
  }
  for (const sel of probe.open || []) {
    const opener = page.locator(sel).first();
    if (!(await opener.isVisible().catch(() => false))) continue;
    await opener.click({timeout: 3000}).catch(() => undefined);
    await page.waitForTimeout(600);
    const got = pickCredits(await visibleTexts('[role=menu],[role=dialog],[role=listbox],[data-radix-popper-content-wrapper]'));
    await page.keyboard.press('Escape').catch(() => undefined);
    if (got.value !== null) return {...got, method: `open:${sel}`};
  }
  const text = await page.evaluate(() => (document.body?.innerText || '').slice(0, 20000)).catch(() => '');
  const got = pickCredits([text]);
  return {...got, method: got.value === null ? 'unreadable' : 'body-text'};
}

// ----------------------------------------------------------------- binding
export async function readAccountEmails(page) {
  return page.evaluate(() => {
    const re = /[\w.+-]+@[\w-]+(\.[\w-]+)+/g, out = new Set();
    for (const e of document.querySelectorAll('[aria-label*="@"],img[alt*="@"],[title*="@"]'))
      for (const v of [e.getAttribute('aria-label'), e.getAttribute('alt'), e.getAttribute('title')])
        for (const m of (v || '').match(re) || []) out.add(m.toLowerCase());
    return [...out];
  }).catch(() => []);
}

async function targetInfo(page) {
  const s = await page.context().newCDPSession(page);
  try { return (await s.send('Target.getTargetInfo')).targetInfo; }
  finally { await s.detach().catch(() => undefined); }
}

/** Find the tab that belongs to `profile`: the recorded CDP target, else the
 * one tab whose URL carries `#flowpool=<slug>` (opened by `flowpool open-profile`). */
export async function bindPage(browser, profile, info = targetInfo) {
  const marker = `flowpool=${profile.slug}`;
  let byTarget = null;
  const byMarker = [];
  for (const page of browser.contexts().flatMap(c => c.pages())) {
    if (page.isClosed()) continue;
    let t;
    try { t = await info(page); } catch { continue; }
    if (profile.binding?.target_id && t.targetId === profile.binding.target_id) byTarget = {page, t};
    if (page.url().includes(marker)) byMarker.push({page, t});
  }
  if (!byTarget && byMarker.length > 1) throw coded('PROFILE_TAB_NOT_FOUND', `${byMarker.length} tabs carry ${marker}; close the extras`);
  const found = byTarget || byMarker[0];
  if (!found) throw coded('PROFILE_TAB_NOT_FOUND', `no tab bound to ${profile.name}; run: python3 -m flowpool open-profile "${profile.name}"`);
  const ctx = found.t.browserContextId || null;
  if (ctx && (profile._other_context_ids || []).includes(ctx)) throw coded('PROFILE_MISMATCH', 'tab belongs to another bound profile');
  return {page: found.page, binding: {target_id: found.t.targetId, browser_context_id: ctx, at: Date.now()}};
}

export async function verifyAccount(page, profile) {
  if (!profile.account_hint) return null;
  const emails = await readAccountEmails(page);
  if (!emails.length) return null;
  if (!emails.includes(profile.account_hint.toLowerCase())) throw coded('PROFILE_MISMATCH', `tab shows ${emails.join(', ')}, expected ${profile.account_hint}`);
  return true;
}

// ----------------------------------------------------------------- images (B-2 queue tool)
let b2;
async function loadB2() {
  if (!b2) b2 = {...await import(path.join(B2, 'queue-runner.mjs')), ...await import(path.join(B2, 'controller.mjs'))};
  return b2;
}

export async function imagePrepare(session, items, lib = null) {
  const q = lib || await loadB2();
  const {page, profile} = session;
  if (!profile.tool_url) throw coded('TOOL_NOT_READY', `${profile.name} has no tool_url (remix the B-2 tool in this account)`);
  if (new Set(items.map(i => i.model)).size !== 1) throw coded('INVALID_BATCH', 'one model per queue batch');
  if (!page.url().startsWith(profile.tool_url)) await page.goto(profile.tool_url, {waitUntil: 'domcontentloaded', timeout: 30000});
  await assertUsable(page);
  let frame;
  try { frame = await q.findToolFrame(page); } catch (e) { throw coded('TOOL_NOT_READY', e.message); }
  const specs = items.map(it => ({testCase: it.id, prompt: it.prompt, ratio: it.ratio, outDir: it.out_dir,
    characterRefPath: it.refs[0], charMediaId: it.ref_media_ids[0], baseRefPath: it.refs[1] || null,
    baseMediaId: it.ref_media_ids[1] || null}));
  let requests;
  try { requests = q.prepareRequests(specs, {tool: profile.tool_url, model: items[0].model}); }
  catch (e) { throw coded('INVALID_BATCH', e.message); }
  try { await q.assertQueueIdle(frame); } catch (e) { throw coded('UNRESOLVED_FLOW_QUEUE', e.message); }
  const ids = await q.enqueueRequests(frame, requests, {label: q.modelLabelFor(items[0].model)});
  await q.selectWorkers(frame, ids);
  session.pending = {kind: 'image', frame, ids, items};
  return ids;
}

function writeImage(item, queued, profile) {
  const ext = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}[queued.result?.mimeType];
  if (!ext) throw coded('OUTPUT_FORMAT_UNSUPPORTED', String(queued.result?.mimeType), {submitted: true});
  fs.mkdirSync(item.out_dir, {recursive: true});
  const file = path.join(item.out_dir, `${item.id}-1${ext}`);
  fs.writeFileSync(file, Buffer.from(queued.result.base64, 'base64'));
  // Evidence for reconciliation even if the Python side dies before journaling.
  fs.writeFileSync(path.join(item.out_dir, `${item.id}-1.flowpool.json`), JSON.stringify({mediaId: queued.mediaId,
    queueId: queued.id, profile: profile.name, timestamps: queued.timestamps || null, at: new Date().toISOString()}, null, 2));
  return file;
}

export async function imageCommit(session, timeoutMs, lib = null) {
  const q = lib || await loadB2();
  const {frame, ids, items} = session.pending;
  session.pending = null;
  const out = items.map(it => ({id: it.id, files: [], media_ids: []}));
  await q.clickStartQueue(frame);
  try {
    await q.pollQueue(frame, ids, {timeoutMs, onGenerated: (i, item) => {
      out[i].files.push(writeImage(items[i], item, session.profile));
      out[i].media_ids.push(item.mediaId);
    }});
  } catch (e) {
    const v = classifySnapshot(await snapshot(session.page));
    const code = v.state === 'captcha' ? 'CAPTCHA' : v.state === 'needs_login' ? 'NEEDS_LOGIN' : /TIMEOUT/.test(e.message) ? 'TIMEOUT' : 'RECONCILE_REQUIRED';
    throw coded(code, e.message, {submitted: true, partial: out});
  }
  return out;
}

// ----------------------------------------------------------------- clips (Flow frames-to-video)
let gflow;
async function loadGflow() {
  if (!gflow) gflow = {...await import(path.join(GFLOW, 'flow/page.js')), ...await import(path.join(GFLOW, 'flow/ui.js')),
    ...await import(path.join(GFLOW, 'flow/download.js')), ...await import(path.join(GFLOW, 'flow/locators.js'))};
  return gflow;
}
const RATIO_ICON = {'16:9': 'crop_16_9', '9:16': 'crop_9_16'};
const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

export async function openProject(page, profile, g) {
  if (profile.project_url) {
    if (!page.url().startsWith(profile.project_url)) await page.goto(profile.project_url, {waitUntil: 'domcontentloaded', timeout: 30000});
  } else {
    await assertUsable(page);
    try { await g.navigateToProject(page, profile.project); } catch (e) { throw coded('PROJECT_NOT_FOUND', e.message); }
  }
  await assertUsable(page);
}

export async function clipPrepare(session, items, cfg, lib = null) {
  const g = lib || await loadGflow();
  if (items.length !== 1) throw coded('INVALID_BATCH', 'one clip request per submission');
  const it = items[0];
  const {page, profile} = session;
  await openProject(page, profile, g);
  const fp = new g.FlowPage(page);
  try { await fp.assertReady(); } catch (e) { throw coded('NEEDS_LOGIN', e.message); }
  const label = (cfg.flowpool_model_labels || {})[it.model] || it.model;
  try {
    await fp.applySettings({type: 'video', ratio: it.ratio, duration: it.seconds, outputs: it.variants, model: label, startFrame: it.start_frame});
  } catch (e) { throw coded('MODEL_NOT_SELECTABLE', e.message); }
  const pill = await g.flowLocators(page).settingsButton.first().innerText().catch(() => '');
  if (!pill.includes(RATIO_ICON[it.ratio]) || !norm(pill).includes(norm(label))) throw coded('MODEL_NOT_SELECTABLE', `settings show "${pill}"`);
  await fp.uploadFrame('Start', it.start_frame);
  if (await page.getByText('Start', {exact: true}).count().catch(() => 1)) throw coded('FRAME_NOT_ATTACHED', 'Start frame slot is still empty');
  const before = new Set(await fp.resultSrcs('video'));
  await fp.fillPrompt(it.prompt);
  session.pending = {kind: 'clip', fp, before, item: it};
  return [null];
}

const CLIP_ERRORS = {RateLimitedError: 'RATE_LIMITED', CreditLimitError: 'CREDIT_LIMIT', GenerationBlockedError: 'POLICY_BLOCKED'};

export async function clipCommit(session, timeoutMs, lib = null) {
  const g = lib || await loadGflow();
  const {fp, before, item} = session.pending;
  session.pending = null;
  await fp.submit();
  let srcs;
  try { srcs = await fp.waitForResults(before, item.variants, timeoutMs, 'video'); }
  catch (e) {
    const v = classifySnapshot(await snapshot(session.page));
    const code = v.state === 'captcha' ? 'CAPTCHA' : v.state === 'needs_login' ? 'NEEDS_LOGIN'
      : CLIP_ERRORS[e.name] || (/timed out/i.test(e.message) ? 'TIMEOUT' : e.name === 'GenerationFailedError' ? 'GENERATION_FAILED' : 'RECONCILE_REQUIRED');
    throw coded(code, e.message, {submitted: true});
  }
  const out = {id: item.id, files: [], media_ids: []};
  try {
    for (let i = 0; i < srcs.length; i++) {
      const {assetPath} = await g.downloadResult({page: session.page, context: session.page.context(), src: srcs[i],
        type: 'video', quality: 'original', outDir: item.out_dir, basename: `${item.id}-${i + 1}`});
      out.files.push(assetPath);
      out.media_ids.push(g.mediaIdFromSrc(srcs[i]) || null);
    }
  } catch (e) { throw coded('DOWNLOAD_FAILED', e.message, {submitted: true, partial: [out]}); }
  return [out];
}

// ----------------------------------------------------------------- doctor
export async function probe(session, kinds, cfg, libs = {}) {
  const {page, profile} = session;
  const out = {logged_in: false, flow_reachable: false, credits: null, clip_model_selectable: null,
    image_tool: null, image_model_selectable: null, image_queue_idle: null};
  if (kinds.includes('clip')) {
    const g = libs.gflow || await loadGflow();
    await openProject(page, profile, g);
    const fp = new g.FlowPage(page);
    try { await fp.assertReady(); out.logged_in = out.flow_reachable = true; } catch (e) { throw coded('NEEDS_LOGIN', e.message); }
    out.credits = await readCredits(page, cfg.flowpool_credit_probe);
    // Read-only look at the settings popover: report the Veo label only if it is listed.
    const label = (cfg.flowpool_model_labels || {})[cfg.veo_model || 'veo-fast'] || 'Veo';
    const settings = g.flowLocators(page).settingsButton.first();
    if (await settings.count()) {
      await settings.click({timeout: 3000}).catch(() => undefined);
      await page.waitForTimeout(700);
      const text = await page.evaluate(() => document.body.innerText).catch(() => '');
      out.clip_model_selectable = norm(text).includes(norm(label)) ? true : null;
      await g.dismissOpenLayers(page);
    }
  }
  if (kinds.includes('image') && profile.tool_url) {
    const q = libs.b2 || await loadB2();
    if (!page.url().startsWith(profile.tool_url)) await page.goto(profile.tool_url, {waitUntil: 'domcontentloaded', timeout: 30000});
    await assertUsable(page);
    out.logged_in = out.flow_reachable = true;
    try {
      const frame = await q.findToolFrame(page);
      out.image_tool = true;
      const options = await frame.getByRole('combobox').nth(2).evaluate(s => [...s.options].map(o => o.label || o.text));
      out.image_model_selectable = options.includes(q.modelLabelFor(cfg.flow_model || 'Nano Banana 2'));
      out.image_queue_idle = await q.assertQueueIdle(frame).then(() => true, () => false);
    } catch (e) { out.image_tool = false; out.image_error = e.message; }
    if (!out.credits || out.credits.value === null) out.credits = await readCredits(page, cfg.flowpool_credit_probe);
  }
  return out;
}
