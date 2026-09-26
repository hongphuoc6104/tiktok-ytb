/**
 * FlowPool page operations on the user's existing signed-in Chrome profiles,
 * reached through the FlowPool daemon's single CDP connection (one tab per profile).
 *
 * Hard rules: the worker never launches Chrome or signs in, never types a password, never touches a
 * CAPTCHA (detect -> throw CAPTCHA), never read or copy cookies. Only
 * clickStartQueue (B-2 images) and FlowPage.submit (Flow images/clips) can start a generation,
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
const AFTER = new RegExp(NUM + String.raw`\s*(?:(?:Google\s+Flow|AI)\s+)?(?:credits?|tín dụng)\b(?!\s*(?:per|\/|each|mỗi|a |an ))`, 'gi');
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
  const balanceSelectors = ['[aria-label*="Google Flow credits" i]', '[aria-label*="tín dụng" i]'];
  const visibleTexts = sel => page.locator(sel).evaluateAll(els => els
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; })
    .map(e => `${e.getAttribute('aria-label') || ''} ${e.innerText || ''}`)).catch(() => []);
  for (const sel of [...balanceSelectors, ...(probe.selectors || [])]) {
    const got = pickCredits(await visibleTexts(sel));
    if (got.value !== null) return {...got, method: `selector:${sel}`};
  }
  // Flow now keeps the balance inside the account panel. This is a menu control,
  // never a generation control; the two labels are the observed English/Vietnamese UI.
  const accountOpener = '[role="button"][aria-label="Account details"],button[aria-label="Account details"],'
    + '[role="button"][aria-label="Thông tin về tài khoản"],button[aria-label="Thông tin về tài khoản"]';
  for (const sel of [...(probe.open || []), accountOpener]) {
    const opener = page.locator(sel).first();
    if (!(await opener.isVisible().catch(() => false))) continue;
    await opener.click({timeout: 3000}).catch(() => undefined);
    await page.waitForTimeout(600);
    let got = {value: null, raw: []};
    for (const balanceSel of balanceSelectors) {
      got = pickCredits(await visibleTexts(balanceSel));
      if (got.value !== null) break;
    }
    if (got.value === null) got = pickCredits(await visibleTexts('[role=menu],[role=dialog],[role=listbox],[data-radix-popper-content-wrapper]'));
    await page.keyboard.press('Escape').catch(() => undefined);
    if (got.value !== null) return {...got, method: `open:${sel}`};
  }
  const text = await page.evaluate(() => (document.body?.innerText || '').slice(0, 20000)).catch(() => '');
  const got = pickCredits([text]);
  return {...got, method: got.value === null ? 'unreadable' : 'body-text'};
}

// ----------------------------------------------------------------- profiles in the shared Chrome
const FLOW_PAGE = /^https:\/\/(flow\.google\.com|labs\.google)\//;
export const markerOf = profile => `flowpool=${profile.slug}`;
/** Exact marker match: `profile-10` must not match `profile-102` (FLOW-008). */
export const hasMarker = (url, profile) => new RegExp(`[#&]${markerOf(profile).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?![\\w-])`).test(url);

async function targetIdOf(page) {
  const s = await page.context().newCDPSession(page);
  try { return (await s.send('Target.getTargetInfo')).targetInfo.targetId; }
  finally { await s.detach().catch(() => undefined); }
}

export async function readAccountEmails(page) {
  return page.evaluate(() => {
    const re = /[\w.+-]+@[\w-]+(\.[\w-]+)+/g, out = new Set();
    for (const e of document.querySelectorAll('[aria-label*="@"],img[alt*="@"],[title*="@"]'))
      for (const v of [e.getAttribute('aria-label'), e.getAttribute('alt'), e.getAttribute('title')])
        for (const m of (v || '').match(re) || []) out.add(m.toLowerCase());
    return [...out];
  }).catch(() => []);
}

/** Find each declared profile's tab among all tabs the one CDP connection sees:
 * 1. the recorded CDP target id, 2. the `#flowpool=<slug>` marker that
 * `flowpool open-profile` puts in the URL, 3. the Flow tab showing the
 * profile's recorded account e-mail. Extra marker tabs are closed when `dedupe`. */
export async function locateProfiles(browser, profiles, {dedupe = false, info = targetIdOf, emails = readAccountEmails} = {}) {
  const entries = [];
  for (const page of browser.contexts().flatMap(c => c.pages())) {
    if (page.isClosed()) continue;
    try { entries.push({page, id: await info(page)}); } catch { /* tab went away */ }
  }
  const claimed = new Set(), out = {};
  const take = (p, e, via) => { out[p.name] = {page: e.page, target_id: e.id, url: e.page.url(), via, closed: 0}; claimed.add(e.id); };
  for (const p of profiles) {
    const e = p.binding?.target_id && entries.find(x => x.id === p.binding.target_id);
    if (e) take(p, e, 'target');
  }
  for (const p of profiles) {
    const marked = entries.filter(x => !claimed.has(x.id) && hasMarker(x.page.url(), p));
    if (!marked.length) continue;
    if (!out[p.name]) take(p, marked.shift(), 'marker');
    for (const extra of marked) {
      if (!dedupe) continue;
      await extra.page.close().catch(() => undefined);
      out[p.name].closed += 1;
    }
  }
  const waiting = profiles.filter(p => !out[p.name] && p.account_email);
  for (const e of entries.filter(x => waiting.length && !claimed.has(x.id) && FLOW_PAGE.test(x.page.url()))) {
    const shown = await emails(e.page);
    const p = waiting.find(q => !out[q.name] && shown.includes(q.account_email.toLowerCase()));
    if (p) take(p, e, 'email');
  }
  return out;
}

/** The account the tab shows. With a recorded e-mail, another visible account is a mismatch. */
export async function verifyAccount(page, profile) {
  const shown = await readAccountEmails(page);
  const expected = (profile.account_email || '').toLowerCase();
  if (expected && shown.length && !shown.includes(expected)) {
    throw coded('PROFILE_MISMATCH', `tab shows ${shown.join(', ')}, expected ${expected} for ${profile.name}`);
  }
  return {email: shown.length === 1 ? shown[0] : null, verified: expected ? (shown.length ? true : null) : null};
}

// ----------------------------------------------------------------- Flow project
let gflow;
async function loadGflow() {
  if (!gflow) gflow = {...await import(path.join(GFLOW, 'flow/page.js')), ...await import(path.join(GFLOW, 'flow/ui.js')),
    ...await import(path.join(GFLOW, 'flow/download.js')), ...await import(path.join(GFLOW, 'flow/locators.js'))};
  return gflow;
}
const RATIO_ICON = {'16:9': 'crop_16_9', '9:16': 'crop_9_16'};
const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
const RADIO_SELECTOR = 'button[role="radio"]:visible,[role="radio"]:visible';
const MODEL_TRIGGER = 'button[aria-label="Chọn nhóm mô hình"]:visible,button[aria-label="Select model group"]:visible,'
  + 'button[aria-label="Choose model group"]:visible,button:has-text("arrow_drop_down"):visible';

async function radioOptions(page) {
  return page.locator(RADIO_SELECTOR).evaluateAll(els => els.map((el, index) => ({
    index, text: (el.textContent || '').trim().toLowerCase().replace(/\s+/g, ''),
    checked: el.getAttribute('aria-checked') === 'true',
  })));
}

function radioOption(options, token) {
  return options.find(o => o.text.startsWith(token) &&
    (!/^x\d+$/.test(token) || !/\d/.test(o.text[token.length] || '')));
}

/** Select the actual Flow radio control and verify aria-checked after React updates.
 * Icon ligatures are stable across the English and Vietnamese Flow labels. */
export async function applyFlowSettings(page, job, g) {
  // The current Angular Flow page has a dedicated trigger. The bundled
  // gflow-cli text filter can also match a radio inside an open settings pane.
  const currentTrigger = page.locator('button.settings-trigger-button:visible').first();
  const settings = await currentTrigger.isVisible().catch(() => false)
    ? currentTrigger : g.flowLocators(page).settingsButton.first();
  const radios = page.locator(RADIO_SELECTOR);
  const clearObstructions = async () => {
    await g.dismissOpenLayers(page);
    const account = page.locator('.cdk-overlay-pane.flow-account-panel-overlay:visible').first();
    if (await account.isVisible().catch(() => false)) {
      const close = account.locator('button[aria-label="Đóng bảng điều khiển tài khoản"]').first();
      if (await close.isVisible().catch(() => false)) await close.click({timeout: 3000});
      else await page.keyboard.press('Escape');
      await account.waitFor({state: 'hidden', timeout: 2000});
    }
    if (await radios.count()) return;
    const stale = page.locator('.cdk-overlay-pane:visible').first();
    if (await stale.isVisible().catch(() => false)) {
      await page.keyboard.press('Escape');
      await stale.waitFor({state: 'hidden', timeout: 2000});
    }
  };
  const open = async () => {
    await clearObstructions();
    if (await radios.count()) return;
    let lastError;
    for (let attempt = 0; attempt < 2; attempt++) {
      try {
        await settings.click({timeout: 3000});
        await radios.first().waitFor({state: 'visible', timeout: 2500});
        return;
      } catch (e) {
        lastError = e;
        if (attempt === 0) {
          await clearObstructions();
          if (await radios.count()) return;
        }
      }
    }
    throw coded('MODEL_NOT_SELECTABLE', `Flow settings radios did not open: ${lastError?.message || 'unknown error'}`);
  };
  const select = async (tokens, name) => {
    tokens = Array.isArray(tokens) ? tokens : [tokens];
    const find = options => tokens.map(token => radioOption(options, token)).find(Boolean);
    await open();
    const chosen = find(await radioOptions(page));
    if (!chosen) throw coded('MODEL_NOT_SELECTABLE', `Flow has no ${name} option (${tokens.join('/')})`);
    if (!chosen.checked) {
      await page.locator(RADIO_SELECTOR).nth(chosen.index).click({force: true, timeout: 5000});
      await page.waitForTimeout(350);
    }
    await open();
    if (!find(await radioOptions(page))?.checked)
      throw coded('MODEL_NOT_SELECTABLE', `Flow did not select ${name} (${tokens.join('/')})`);
  };
  const modeTokens = job.type === 'video' ? ['videocam', 'video'] : ['image', 'hìnhảnh', 'ảnh'];
  await select(modeTokens, 'mode');
  if (job.type === 'video') {
    await select(job.startFrame ? ['crop_free', 'frames', 'khunghình'] : ['chrome_extension', 'ingredients', 'thànhphần'], 'video input');
    if (job.duration) await select([`${job.duration}giây`, `${job.duration}s`], 'duration');
  }
  await select(RATIO_ICON[job.ratio], 'aspect ratio');
  const outputTokens = [`x${job.outputs}`, `${job.outputs}x`];
  await select(outputTokens, 'output count');
  await open();
  const modelTrigger = page.locator(MODEL_TRIGGER).first();
  if (!(await modelTrigger.isVisible().catch(() => false)))
    throw coded('MODEL_NOT_SELECTABLE', 'Flow model selector is missing');
  if (!norm(await modelTrigger.innerText()).includes(norm(job.model))) {
    await modelTrigger.click({force: true, timeout: 5000});
    await g.selectModelOption(page, job.model);
    await open();
  }
  if (!norm(await page.locator(MODEL_TRIGGER).first().innerText()).includes(norm(job.model)))
    throw coded('MODEL_NOT_SELECTABLE', `Flow did not select model "${job.model}"`);
  const expected = [[modeTokens, 'mode'], [RATIO_ICON[job.ratio], 'aspect ratio'], [outputTokens, 'output count']];
  if (job.type === 'video') {
    expected.push([job.startFrame ? ['crop_free', 'frames', 'khunghình'] : ['chrome_extension', 'ingredients', 'thànhphần'], 'video input']);
    if (job.duration) expected.push([[`${job.duration}giây`, `${job.duration}s`], 'duration']);
  }
  for (const [tokens, name] of expected) {
    const candidates = Array.isArray(tokens) ? tokens : [tokens];
    const options = await radioOptions(page);
    if (!candidates.some(token => radioOption(options, token)?.checked))
      throw coded('MODEL_NOT_SELECTABLE', `Flow changed ${name} after model selection`);
  }
  const pill = await settings.innerText();
  if (!pill.includes(RATIO_ICON[job.ratio]) || !outputTokens.some(token => pill.includes(token)))
    throw coded('MODEL_NOT_SELECTABLE', `settings show "${pill}"`);
  // Close the Angular CDK settings panel before focusing the prompt composer.
  for (let attempt = 0; attempt < 2 && await radios.count(); attempt++) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(200);
  }
  if (await radios.count()) throw coded('MODEL_NOT_SELECTABLE', 'Flow settings panel stayed open over the prompt');
  await g.dismissOpenLayers(page);
}

/** Canonical project URL (".../project/<id>") or null. */
export function projectUrlOf(url) {
  const m = String(url || '').match(/^(https:\/\/[^/]+(?:\/[^?#]*?)?\/project\/[0-9a-f][0-9a-f-]{7,})/i);
  return m ? m[1] : null;
}

// The bundled gflow-cli still expects role=textbox. Current Flow exposes a
// ProseMirror contenteditable without that role; keep both editor generations.
export const PROMPT_EDITOR = 'div.ProseMirror[contenteditable="true"]:visible,[role="textbox"][contenteditable="true"]:visible';

export async function readyProjectEditor(page) {
  await assertUsable(page);
  const editor = page.locator(PROMPT_EDITOR).first();
  await editor.waitFor({state: 'visible', timeout: 20000}).catch(() => undefined);
  await assertUsable(page);
  if (!(await editor.isVisible().catch(() => false))) {
    throw coded('EDITOR_NOT_FOUND', `Flow project is open but its prompt editor is missing at ${page.url()}`);
  }
  return editor;
}

export async function fillFlowPrompt(page, prompt, g) {
  const box = await readyProjectEditor(page);
  await g.dismissOpenLayers(page);
  await box.click({timeout: 2000}).catch(async () => {
    await g.dismissOpenLayers(page);
    await box.click({timeout: 5000}).catch(() => box.evaluate(el => el.focus()));
  });
  await box.press('ControlOrMeta+a');
  await box.press('Backspace');
  await box.pressSequentially(prompt, {delay: 8});
}

/** Absolute URL of the dashboard card whose label contains `name`. Resolved
 * against the CURRENT page URL: gflow-cli resolves against labs.google, which
 * now redirects to flow.google.com. */
export async function findProjectUrl(page, name) {
  const href = await page.evaluate(n => {
    const sel = 'a[href*="/project/"]';
    for (const a of document.querySelectorAll(sel)) {
      let card = a;
      while (card.parentElement && card.parentElement.querySelectorAll(sel).length === 1) card = card.parentElement;
      if ((card.textContent || '').includes(n)) return a.getAttribute('href');
    }
    return null;
  }, name).catch(() => null);
  return href ? new URL(href, page.url()).toString() : null;
}

/** Reuse the current/recorded/named project; only production preparation may
 * create one when none exists. Doctor passes create=false and remains read-only. */
export async function ensureProject(session, cfg, g, {create = true} = {}) {
  const {page, profile} = session;
  const known = session.projectUrl || profile.project_url;
  if (known) {
    if (projectUrlOf(page.url()) !== known) await page.goto(known, {waitUntil: 'domcontentloaded', timeout: 30000});
    await assertUsable(page);
    if (projectUrlOf(page.url()) === known) return (session.projectUrl = known);
    throw coded('PROJECT_NOT_FOUND', `recorded Flow project ${known} did not open in ${profile.name}`);
  }
  const current = projectUrlOf(page.url());
  if (current) {
    await assertUsable(page);
    return (session.projectUrl = current);
  }
  await page.goto(cfg.flowpool_flow_url || 'https://flow.google.com/', {waitUntil: 'domcontentloaded', timeout: 30000});
  await assertUsable(page);
  const newProject = g.flowLocators(page).newProjectButton.first();
  await page.locator('a[href*="/project/"]').first().or(newProject).waitFor({state: 'visible', timeout: 20000}).catch(() => undefined);
  await assertUsable(page);
  const found = profile.project ? await findProjectUrl(page, profile.project) : null;
  if (found) {
    await page.goto(found, {waitUntil: 'domcontentloaded', timeout: 30000});
  } else {
    if (!create) throw coded('PROJECT_NOT_FOUND', `no recorded or named Flow project for ${profile.name}; doctor will not create one`);
    if (!(await newProject.isVisible().catch(() => false))) {
      throw coded('PROJECT_NOT_FOUND', `Flow shows no projects and no "New project" button in ${profile.name}`);
    }
    await newProject.click({timeout: 5000});
    await page.waitForURL(/\/project\/[0-9a-f-]+/i, {timeout: 30000}).catch(() => undefined);
  }
  await assertUsable(page);
  const url = projectUrlOf(page.url());
  if (!url) throw coded('PROJECT_NOT_FOUND', `could not open or create Flow project "${profile.project}"`);
  return (session.projectUrl = url);
}

// ----------------------------------------------------------------- images (B-2 queue tool, optional per-account remix)
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
  session.pending = {kind: 'b2', frame, ids, items};
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

// ----------------------------------------------------------------- plain Flow UI: images and frames-to-video clips
/** Count images in the prompt composer (the prompt box's nearest ancestor that also holds the submit arrow). */
async function composerImageCount(page) {
  return page.evaluate(() => {
    let c = document.querySelector('[role="textbox"][contenteditable="true"],div.ProseMirror[contenteditable="true"]');
    for (let i = 0; c && i < 8; i++, c = c.parentElement)
      if ([...c.querySelectorAll('button')].some(b => /arrow_forward/.test(b.textContent || ''))) break;
    return c ? c.querySelectorAll('img').length : -1;
  }).catch(() => -1);
}

/** Upload one reference image as a prompt ingredient ("add_2" picker -> Upload -> Add to prompt). */
export async function attachReference(page, file, g) {
  const before = await composerImageCount(page);
  const trigger = page.locator('button[aria-haspopup="dialog"]').filter({hasText: /add_2/i}).first();
  if (!(await trigger.isVisible().catch(() => false))) throw coded('REFERENCE_NOT_ATTACHED', 'no ingredient ("add_2") button in the prompt bar');
  await trigger.click({timeout: 5000});
  const dialog = page.locator('[role=dialog],[aria-modal=true]').first();
  await dialog.waitFor({state: 'visible', timeout: 10000}).catch(() => undefined);
  const upload = dialog.locator('button').filter({hasText: /upload/i}).first();
  try {
    const [chooser] = await Promise.all([page.waitForEvent('filechooser', {timeout: 15000}), upload.click()]);
    await chooser.setFiles(file);
    await dialog.locator('[role=option][aria-selected="true"]').first().waitFor({state: 'visible', timeout: 30000});
    await g.confirmPicker(page, dialog);
  } catch (e) {
    await g.dismissOpenLayers(page).catch(() => undefined);
    throw coded('REFERENCE_NOT_ATTACHED', `${path.basename(file)}: ${e.message}`);
  }
  if (before >= 0 && (await composerImageCount(page)) <= before) throw coded('REFERENCE_NOT_ATTACHED', `${path.basename(file)} not visible in the prompt bar`);
}

/** Attach the Start frame in Frames mode. The empty slot and upload button
 * have observed English/Vietnamese names; an unknown confirm control is a
 * pre-submit failure, never evidence that a frame was attached. */
export async function attachStartFrame(page, file, g) {
  const empty = page.getByRole('button', {name: /^(Start|Bắt đầu)$/i}).first();
  if (!(await empty.isVisible().catch(() => false)))
    throw coded('FRAME_NOT_ATTACHED', 'Start/Bắt đầu frame slot is not visible');
  try {
    await empty.click({timeout: 5000});
    const dialog = page.locator('[role=dialog],[aria-modal=true]').first();
    await dialog.waitFor({state: 'visible', timeout: 10000});
    const upload = dialog.getByRole('button', {name: /^(Upload media|Tải nội dung nghe nhìn lên)$/i}).first();
    if (!(await upload.isVisible().catch(() => false)))
      throw new Error('Upload media/Tải nội dung nghe nhìn lên button is missing');
    const [chooser] = await Promise.all([page.waitForEvent('filechooser', {timeout: 15000}), upload.click({timeout: 5000})]);
    await chooser.setFiles(file);
    await dialog.locator('[role=option][aria-selected="true"]').first().waitFor({state: 'visible', timeout: 30000});
    // The only confirmed action text is the English Flow control. If Flow
    // localizes it differently, stop so a human can identify the real button.
    const confirm = dialog.getByRole('button', {name: /\bAdd to (Prompt|Scene)\b/i}).first();
    if (!(await confirm.isVisible().catch(() => false))) throw new Error('Add to Prompt/Scene control is unverified');
    await confirm.click({timeout: 5000});
    await dialog.waitFor({state: 'hidden', timeout: 10000});
    await empty.waitFor({state: 'hidden', timeout: 10000});
    await assertUsable(page);
    if (await empty.isVisible().catch(() => true)) throw new Error('Start/Bắt đầu frame slot is still empty');
  } catch (e) {
    await assertUsable(page); // preserve real CAPTCHA/sign-in errors
    await g.dismissOpenLayers(page).catch(() => undefined);
    throw coded('FRAME_NOT_ATTACHED', `${path.basename(file)}: ${e.message}`);
  }
}

export async function flowPrepare(session, items, cfg, lib = null) {
  const g = lib || await loadGflow();
  if (items.length !== 1) throw coded('INVALID_BATCH', 'one request per plain-Flow submission');
  const it = items[0];
  const video = it.kind === 'clip';
  const {page} = session;
  await ensureProject(session, cfg, g);
  const fp = new g.FlowPage(page);
  // Real gflow-cli only waits for an English "Create" button (FLOW-009).
  if (!lib) fp.submit = () => submitFlowPrompt(page);
  await readyProjectEditor(page);
  const label = (cfg.flowpool_model_labels || {})[it.model] || it.model;
  const job = video ? {type: 'video', ratio: it.ratio, duration: it.seconds, outputs: it.variants, model: label, startFrame: it.start_frame}
    : {type: 'image', ratio: it.ratio, outputs: it.variants || 1, model: label};
  try { await (g.applyFlowSettings || applyFlowSettings)(page, job, g); }
  catch (e) { if (e.code) throw e; throw coded('MODEL_NOT_SELECTABLE', e.message); }
  if (video) {
    await attachStartFrame(page, it.start_frame, g);
  } else {
    for (const ref of it.refs || []) await attachReference(page, ref, g);
  }
  const type = video ? 'video' : 'image';
  const before = new Set(await fp.resultSrcs(type));
  await fillFlowPrompt(page, it.prompt, g);
  session.pending = {kind: 'flow', type, fp, before, item: it, expected: it.variants || 1};
  return [null];
}

const FLOW_ERRORS = {RateLimitedError: 'RATE_LIMITED', CreditLimitError: 'CREDIT_LIMIT', GenerationBlockedError: 'POLICY_BLOCKED'};

/** Locale-independent submit (FLOW-009): gflow-cli waits for an English "Create"
 * button; the Vietnamese UI labels it "Tạo". Match the arrow_forward icon and exclude
 * the sibling "add_2" button. Failing before the click is provably not submitted. */
export async function submitFlowPrompt(page) {
  // Live UI 26/09 (vi): icon-only <button aria-label="Bắt đầu tạo">arrow_forward</button>.
  const byLabel = page.locator('button[aria-label="Bắt đầu tạo"]:visible,button[aria-label="Create"]:visible,button[aria-label="Start creating"]:visible,button[aria-label="Generate"]:visible');
  const iconOnly = page.locator('button:visible').filter({hasText: /^\s*arrow_forward\s*$/});
  const labelled = page.locator('button:visible').filter({hasText: /arrow_forward/}).filter({hasNotText: /add_2/}).filter({hasText: /Create|Tạo/i});
  const btn = byLabel.or(iconOnly).or(labelled).first();
  try { await btn.waitFor({state: 'visible', timeout: 15000}); }
  catch (e) { throw coded('SUBMIT_NOT_FOUND', `submit button not visible: ${e.message}`, {submitted: false}); }
  const deadline = Date.now() + 15000;
  let enabled = false;
  while (Date.now() < deadline) {
    enabled = await btn.evaluate(b => !(b.disabled || b.getAttribute('aria-disabled') === 'true')).catch(() => false);
    if (enabled) break;
    await page.waitForTimeout(300);
  }
  if (!enabled) throw coded('SUBMIT_DISABLED', 'submit button stayed disabled', {submitted: false});
  try { await btn.click({timeout: 3000}); }
  catch (e) {
    await page.keyboard.press('Escape').catch(() => undefined);
    try { await btn.click({timeout: 3000}); }
    catch (e2) { throw coded('SUBMIT_CLICK_FAILED', e2.message, {submitted: false}); }
  }
}

export async function flowCommit(session, timeoutMs, lib = null) {
  const g = lib || await loadGflow();
  const {fp, before, item, type, expected} = session.pending;
  session.pending = null;
  await fp.submit();
  let srcs;
  try { srcs = await fp.waitForResults(before, expected, timeoutMs, type); }
  catch (e) {
    const v = classifySnapshot(await snapshot(session.page));
    const code = v.state === 'captcha' ? 'CAPTCHA' : v.state === 'needs_login' ? 'NEEDS_LOGIN'
      : FLOW_ERRORS[e.name] || (/timed out/i.test(e.message) ? 'TIMEOUT' : e.name === 'GenerationFailedError' ? 'GENERATION_FAILED' : 'RECONCILE_REQUIRED');
    throw coded(code, e.message, {submitted: true});
  }
  const out = {id: item.id, files: [], media_ids: []};
  try {
    for (let i = 0; i < srcs.length; i++) {
      const {assetPath} = await g.downloadResult({page: session.page, context: session.page.context(), src: srcs[i],
        type, quality: 'original', outDir: item.out_dir, basename: `${item.id}-${i + 1}`});
      out.files.push(assetPath);
      out.media_ids.push(g.mediaIdFromSrc(srcs[i]) || null);
    }
  } catch (e) { throw coded('DOWNLOAD_FAILED', e.message, {submitted: true, partial: [out]}); }
  return [out];
}

// ----------------------------------------------------------------- doctor
export async function probe(session, kinds, cfg, libs = {}) {
  const {page, profile} = session;
  const out = {logged_in: false, flow_reachable: false, project_url: null, credits: null,
    image_model_visible: null, clip_model_visible: null, image_tool: null, image_model_selectable: null, image_queue_idle: null};
  const g = libs.gflow || await loadGflow();
  out.project_url = await ensureProject(session, cfg, g, {create: false});
  await readyProjectEditor(page);
  out.logged_in = out.flow_reachable = true;
  out.credits = await readCredits(page, cfg.flowpool_credit_probe);
  // Look (without selecting) at the settings popover: which model labels are listed right now.
  const settings = g.flowLocators(page).settingsButton.first();
  if (await settings.count()) {
    await settings.click({timeout: 3000}).catch(() => undefined);
    await page.waitForTimeout(700);
    const text = norm(await page.evaluate(() => document.body.innerText).catch(() => ''));
    const labels = cfg.flowpool_model_labels || {};
    if (kinds.includes('image')) out.image_model_visible = text.includes(norm(labels[cfg.flow_model] || cfg.flow_model || 'Nano Banana')) || null;
    if (kinds.includes('clip')) out.clip_model_visible = text.includes(norm(labels[cfg.veo_model || 'veo-fast'] || 'Veo')) || null;
    await g.dismissOpenLayers(page);
  }
  if (kinds.includes('image') && profile.tool_url) {
    const q = libs.b2 || await loadB2();
    await page.goto(profile.tool_url, {waitUntil: 'domcontentloaded', timeout: 30000});
    await assertUsable(page);
    try {
      const frame = await q.findToolFrame(page);
      out.image_tool = true;
      const options = await frame.getByRole('combobox').nth(2).evaluate(s => [...s.options].map(o => o.label || o.text));
      out.image_model_selectable = options.includes(q.modelLabelFor(cfg.flow_model || 'Nano Banana 2'));
      out.image_queue_idle = await q.assertQueueIdle(frame).then(() => true, () => false);
    } catch (e) { out.image_tool = false; out.image_error = e.message; }
  }
  return out;
}
