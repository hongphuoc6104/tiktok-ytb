/**
 * flowctl runner: one CDP connection to the user's own Chrome (Chrome asks "Allow" once),
 * then executes step batches dropped as JSON files into <dir>/in/ and writes results to <dir>/out/.
 * Tabs are chosen by the `#flowpool=<slug>` marker that `flowpool open-profile` put in the URL.
 * Never signs in, never touches CAPTCHAs (a detected challenge stops the batch), never reads cookies.
 *
 * Usage (from sys/): node flowctl/runner.mjs <dir>
 * Step: {op, tab, ...}. ops: goto, click, fill, type, press, upload, wait, waitFor, eval, shot, list, text, save
 */
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';

const dir = path.resolve(process.argv[2] || 'scratch/flowctl');
for (const d of ['in', 'out', 'shots']) fs.mkdirSync(path.join(dir, d), {recursive: true});
const log = m => fs.appendFileSync(path.join(dir, 'runner.log'), `${new Date().toISOString()} ${m}\n`);

const portFile = path.join(process.env.HOME, '.config/google-chrome/DevToolsActivePort');
const [port, wsPath] = fs.readFileSync(portFile, 'utf8').trim().split(/\r?\n/);
const browser = await chromium.connectOverCDP(`ws://127.0.0.1:${port}${wsPath}`);
log('connected');
fs.writeFileSync(path.join(dir, 'ready'), String(process.pid));

const CAPTCHA = /(i'?m not a robot|unusual traffic|xác minh bạn không phải là rô bốt|verify you('|’)?re (not a robot|a human))/i;

function pages() { return browser.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()); }
function tabOf(slug) {
  const re = new RegExp(`[#&]flowpool=${slug}(?![\\w-])`);
  const p = pages().find(x => re.test(x.url()));
  if (!p) throw new Error(`no tab for ${slug}`);
  return p;
}
function loc(page, s) {
  if (s.sel) return page.locator(s.sel).nth(s.nth || 0);
  if (s.role) return page.getByRole(s.role, {name: s.name, exact: !!s.exact}).nth(s.nth || 0);
  if (s.text) return page.getByText(s.text, {exact: !!s.exact}).nth(s.nth || 0);
  throw new Error('no locator');
}

async function listControls(page) {
  return page.evaluate(() => [...document.querySelectorAll('button,[role=button],[role=radio],[role=option],[role=menuitem],[role=menuitemradio],[role=tab],input,textarea,[contenteditable=true],a,video,img')]
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 4 && r.height > 4 && r.bottom > 0 && r.top < innerHeight; })
    .map(e => { const r = e.getBoundingClientRect(); return {tag: e.tagName.toLowerCase(), role: e.getAttribute('role'),
      text: (e.innerText || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 80), aria: e.getAttribute('aria-label'),
      checked: e.getAttribute('aria-checked') || e.getAttribute('aria-selected'), disabled: e.disabled || e.getAttribute('aria-disabled') === 'true',
      src: (e.currentSrc || e.src || '').slice(0, 120), x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2), w: Math.round(r.width), h: Math.round(r.height)}; }));
}

async function step(s) {
  if (s.op === 'tabs') return pages().map(p => p.url());
  if (s.op === 'bind') { // tag an existing tab (found by URL prefix, optional nth) with a lane marker
    const p = pages().filter(x => x.url().startsWith(s.prefix))[s.nth || 0];
    if (!p) throw new Error('no tab with prefix ' + s.prefix);
    const u = p.url().split('#')[0] + `#flowpool=${s.tab}`;
    await p.evaluate(h => { location.hash = h; }, `flowpool=${s.tab}`);
    return u;
  }
  const page = tabOf(s.tab);
  const t = s.timeout || 15000;
  switch (s.op) {
    case 'goto': await page.goto(s.url, {waitUntil: 'domcontentloaded', timeout: 45000}); return page.url();
    case 'click': if (s.x !== undefined) { await page.mouse.click(s.x, s.y); return true; } await loc(page, s).click({timeout: t, force: !!s.force}); return true;
    case 'hover': await loc(page, s).hover({timeout: t}); return true;
    case 'fill': await loc(page, s).fill(s.value, {timeout: t}); return true;
    case 'type': await loc(page, s).click({timeout: t}); await page.keyboard.press('ControlOrMeta+a'); await page.keyboard.press('Backspace');
      await page.keyboard.insertText(s.value); return true;
    case 'press': await page.keyboard.press(s.key); return true;
    case 'upload': {
      if (s.sel) { await page.locator(s.sel).nth(s.nth || 0).setInputFiles(s.files); return true; }
      const [ch] = await Promise.all([page.waitForEvent('filechooser', {timeout: t}), loc(page, s.trigger).click({timeout: t})]);
      await ch.setFiles(s.files); return true;
    }
    case 'wait': await page.waitForTimeout(s.ms || 1000); return true;
    case 'waitFor': await loc(page, s).waitFor({state: s.state || 'visible', timeout: t}); return true;
    case 'eval': return await page.evaluate(new Function(`return (async () => { ${s.js} })()`));
    case 'shot': { const f = path.join(dir, 'shots', `${s.name || Date.now()}.png`); await page.screenshot({path: f, fullPage: !!s.full}); return f; }
    case 'list': return await listControls(page);
    case 'text': return (await page.evaluate(() => document.body.innerText)).slice(0, s.max || 6000);
    case 'save': { // save a media src (http via the profile's session; blob/data inside the page)
      let buf;
      if (/^https?:/.test(s.src)) { const r = await page.context().request.get(s.src, {timeout: 180000}); if (!r.ok()) throw new Error('HTTP ' + r.status()); buf = await r.body(); }
      else { const b64 = await page.evaluate(async u => { const b = await (await fetch(u)).blob(); return await new Promise(res => { const f = new FileReader(); f.onload = () => res(String(f.result)); f.readAsDataURL(b); }); }, s.src);
        buf = Buffer.from(b64.slice(b64.indexOf(',') + 1), 'base64'); }
      fs.mkdirSync(path.dirname(s.path), {recursive: true}); fs.writeFileSync(s.path, buf); return {path: s.path, bytes: buf.length};
    }
    case 'scroll': await page.mouse.move(s.x || 800, s.y || 500); await page.mouse.wheel(s.dx || 0, s.dy || 600); return true;
    case 'keys': await page.keyboard.type(s.value, {delay: s.delay || 10}); return true;
    case 'frameEval': {
      let f = null;
      if (s.frameHas) { for (const x of page.frames()) { if (await x.evaluate(t => (document.body?.innerText || '').includes(t), s.frameHas).catch(() => false)) { f = x; break; } } }
      else f = page.frames().find(x => x.url().includes(s.frame));
      if (!f) throw new Error('no frame ' + (s.frame || s.frameHas));
      return await f.evaluate(new Function(`return (async () => { ${s.js} })()`)); }
    case 'frames': return page.frames().map(f => f.url());
    case 'close': await page.close(); return true;
    case 'reload': await page.reload({waitUntil: 'domcontentloaded', timeout: 45000}); return page.url();
    default: throw new Error('unknown op ' + s.op);
  }
}

async function runBatch(file) {
  const name = path.basename(file, '.json');
  const steps = JSON.parse(fs.readFileSync(file, 'utf8'));
  fs.unlinkSync(file);
  const results = [];
  for (const s of steps) {
    try {
      const r = await step(s);
      results.push({op: s.op, ok: true, r});
      if (s.op !== 'eval' && s.tab && s.captchaCheck !== false) {
        const txt = await tabOf(s.tab).evaluate(() => document.body.innerText.slice(0, 20000)).catch(() => '');
        if (CAPTCHA.test(txt)) { results.push({op: 'captcha', ok: false, error: 'CAPTCHA'}); break; }
      }
    } catch (e) {
      results.push({op: s.op, ok: false, error: String(e.message || e).slice(0, 1500)});
      if (!s.optional) break;
    }
  }
  fs.writeFileSync(path.join(dir, 'out', name + '.json'), JSON.stringify(results, null, 1));
  log(`done ${name}`);
}

browser.on('disconnected', () => { log('disconnected'); fs.rmSync(path.join(dir, 'ready'), {force: true}); process.exit(3); });
const busy = new Set();
setInterval(() => {
  for (const f of fs.readdirSync(path.join(dir, 'in')).filter(f => f.endsWith('.json')).sort()) {
    const lane = f.split('__')[0]; // batches for different lanes (tabs) run in parallel, same lane serial
    if (busy.has(lane)) continue;
    busy.add(lane);
    runBatch(path.join(dir, 'in', f)).catch(e => log('batch error ' + e.message)).finally(() => busy.delete(lane));
  }
}, 300);
