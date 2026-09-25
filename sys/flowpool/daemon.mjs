/**
 * FlowPool daemon: holds the ONE CDP connection to the user's own Chrome
 * (remote debugging enabled at chrome://inspect/#remote-debugging; Chrome asks
 * the user to "Allow" every new CDP client, so there must be exactly one).
 *
 * - unix socket (sys/flowpool/daemon.sock): line-delimited JSON RPC used by
 *   flowpool/driver.py (status, reconnect, locate, open, probe, credits,
 *   prepare, commit, release, shutdown). Work is serialized per profile tab;
 *   different profiles run in parallel.
 * - http://127.0.0.1:<flowpool_ui_port>: the Vietnamese dashboard.
 *
 * On a lost connection it tries to reconnect once; after that it reports
 * NEEDS_ALLOW and waits for `python3 -m flowpool daemon reconnect`. It never
 * launches Chrome, signs in, solves CAPTCHAs or reads cookies.
 */
import fs from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import * as ops from './flow-ops.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const SYS = path.resolve(here, '..');

export function debugEndpoint(contents) {
  const [rawPort, rawPath] = String(contents).trim().split(/\r?\n/);
  const port = Number(rawPort);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw ops.coded('NO_CDP', 'invalid DevToolsActivePort');
  if (!rawPath || !/^\/devtools\/browser\/[a-zA-Z0-9-]+$/.test(rawPath.trim())) throw ops.coded('NO_CDP', 'invalid browser WebSocket path');
  return `ws://127.0.0.1:${port}${rawPath.trim()}`;
}

/** ws endpoint of the user's Chrome, re-read on every (re)connect: Chrome rewrites the file on restart. */
export function endpointFromDir(userDataDir) {
  const file = path.join(userDataDir, 'DevToolsActivePort');
  if (!fs.existsSync(file)) {
    throw ops.coded('NEEDS_ALLOW', `${file} missing: enable remote debugging at chrome://inspect/#remote-debugging in the user's Chrome`);
  }
  return debugEndpoint(fs.readFileSync(file, 'utf8'));
}

const ALLOW_HINT = 'click "Allow" in Chrome, then run: python3 -m flowpool daemon reconnect';

export function createDaemon({connect, endpoint, operations = ops, onShutdown = () => {}, now = Date.now}) {
  const st = {browser: null, everConnected: false, reconnectUsed: false, needsAllow: false,
    sessions: new Map(), chains: new Map(), activity: {}};

  async function doConnect() {
    let browser;
    try { browser = await connect(endpoint()); }
    catch (e) { st.needsAllow = true; throw ops.coded('NEEDS_ALLOW', `CDP connection refused or not approved (${e.message}); ${ALLOW_HINT}`); }
    st.browser = browser;
    st.everConnected = true;
    st.needsAllow = false;
    browser.on?.('disconnected', () => { st.sessions.clear(); });
  }
  const connected = () => Boolean(st.browser && (st.browser.isConnected ? st.browser.isConnected() : true));
  async function ensure() {
    if (connected()) return;
    if (!st.everConnected) throw ops.coded('NOT_CONNECTED', `daemon has no Chrome connection yet; ${ALLOW_HINT}`);
    if (st.needsAllow || st.reconnectUsed) { st.needsAllow = true; throw ops.coded('NEEDS_ALLOW', `Chrome connection lost; ${ALLOW_HINT}`); }
    st.reconnectUsed = true; // exactly one automatic attempt per lost connection
    await doConnect();
  }
  function serial(name, fn) {
    const prev = st.chains.get(name) || Promise.resolve();
    const run = prev.catch(() => undefined).then(fn);
    st.chains.set(name, run.catch(() => undefined));
    return run;
  }
  async function sessionFor(profile) {
    await ensure();
    let s = st.sessions.get(profile.name);
    if (s && !s.page.isClosed()) { s.profile = {...s.profile, ...profile}; return s; }
    const found = (await operations.locateProfiles(st.browser, [profile]))[profile.name];
    if (!found) throw ops.coded('PROFILE_TAB_NOT_FOUND', `no tab of ${profile.name}; run: python3 -m flowpool open-profile "${profile.name}"`);
    s = {page: found.page, profile, pending: null, projectUrl: profile.project_url || null, targetId: found.target_id};
    st.sessions.set(profile.name, s);
    return s;
  }
  const perProfile = {
    async open(s) {
      await operations.assertUsable(s.page);
      const account = await operations.verifyAccount(s.page, s.profile);
      return {binding: {target_id: s.targetId}, url: s.page.url(), email: account.email, account_verified: account.verified};
    },
    async probe(s, msg) { return operations.probe(s, msg.kinds || [], msg.cfg || {}); },
    async credits(s, msg) { return {credits: await operations.readCredits(s.page, (msg.cfg || {}).flowpool_credit_probe || {})}; },
    async prepare(s, msg) {
      if (s.pending) throw ops.coded('INVALID_STATE', 'a prepared batch is waiting for commit');
      const b2 = msg.kind === 'image' && msg.items?.[0]?.engine === 'b2';
      return {prepared: b2 ? await operations.imagePrepare(s, msg.items) : await operations.flowPrepare(s, msg.items, msg.cfg || {})};
    },
    async commit(s, msg) {
      if (!s.pending) throw ops.coded('INVALID_STATE', 'nothing prepared', {submitted: false});
      const items = s.pending.kind === 'b2' ? await operations.imageCommit(s, msg.timeout_ms) : await operations.flowCommit(s, msg.timeout_ms);
      return {items};
    },
    async release(s) { s.pending = null; return {}; },
  };
  const global = {
    async status() {
      return {connected: connected(), needs_allow: st.needsAllow, ever_connected: st.everConnected,
        sessions: [...st.sessions.keys()], activity: st.activity};
    },
    async reconnect() {
      if (connected()) return {connected: true, reused: true};
      st.reconnectUsed = false;
      st.needsAllow = false;
      await doConnect();
      return {connected: true};
    },
    async locate(msg) {
      await ensure();
      const found = await operations.locateProfiles(st.browser, msg.profiles || [], {dedupe: Boolean(msg.dedupe)});
      return {located: Object.fromEntries(Object.entries(found).map(([n, f]) => [n, {target_id: f.target_id, url: f.url, via: f.via, closed: f.closed}]))};
    },
    async shutdown() {
      // Disconnect only: for a CDP-attached browser this never closes the user's Chrome or tabs.
      if (st.browser) await st.browser.close().catch(() => undefined);
      st.browser = null;
      setTimeout(onShutdown, 10);
      return {stopped: true};
    },
  };

  return async function handle(msg) {
    const op = msg?.op;
    const name = msg?.profile?.name;
    try {
      if (global[op]) return {ok: true, ...(await global[op](msg))};
      if (!perProfile[op]) return {ok: false, code: 'PROTOCOL', error: `unknown op ${op}`};
      if (!name) return {ok: false, code: 'PROTOCOL', error: `${op} needs a profile`};
      return await serial(name, async () => {
        st.activity[name] = {...(st.activity[name] || {}), task: op, since: now()};
        let s;
        try {
          s = await sessionFor(msg.profile);
          const reply = await perProfile[op](s, msg);
          return {ok: true, ...reply, ...(s.projectUrl ? {project_url: s.projectUrl} : {})};
        } catch (e) {
          if (e.code === 'PROFILE_TAB_NOT_FOUND' || e.code === 'PROFILE_MISMATCH') st.sessions.delete(name);
          st.activity[name] = {...st.activity[name], last_error: {code: e.code || 'WORKER_ERROR', message: e.message, at: now()}};
          throw Object.assign(e, {projectUrl: s?.projectUrl});
        } finally {
          st.activity[name] = {...st.activity[name], task: null, since: now()};
        }
      });
    } catch (e) {
      const submitted = op === 'commit' ? e.submitted !== false : Boolean(e.submitted);
      return {ok: false, code: e.code || (op === 'commit' ? 'RECONCILE_REQUIRED' : 'WORKER_ERROR'), error: e.message,
        submitted, partial: e.partial || null, ...(e.projectUrl ? {project_url: e.projectUrl} : {})};
    }
  };
}

// ----------------------------------------------------------------- dashboard (HTTP)
function readBody(req, limit = 65536) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', c => { data += c; if (data.length > limit) { reject(new Error('body too large')); req.destroy(); } });
    req.on('end', () => { try { resolve(data ? JSON.parse(data) : {}); } catch (e) { reject(e); } });
    req.on('error', reject);
  });
}

const MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.mp4': 'video/mp4'};

/** HTTP handler. Data comes from `python3 -m flowpool ui-state|decide` (runPython), so
 * the dashboard shows exactly what the CLI/pipeline see. Media are served only when
 * they are listed in the latest state's gallery. */
export function createDashboard({handle, runPython, html}) {
  let allowed = new Map();
  const send = (res, code, body, type = 'application/json; charset=utf-8') => {
    res.writeHead(code, {'content-type': type, 'cache-control': 'no-store'});
    res.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
  };
  return async function (req, res) {
    const url = new URL(req.url, 'http://127.0.0.1');
    try {
      if (req.method === 'GET' && url.pathname === '/') return send(res, 200, html(), 'text/html; charset=utf-8');
      if (req.method === 'GET' && url.pathname === '/api/state') {
        const state = await runPython(['ui-state']);
        state.daemon = await handle({op: 'status'});
        allowed = new Map();
        for (const g of state.gallery || []) for (const v of g.variants || []) allowed.set(`${g.key}:${v.index}`, v.path);
        return send(res, 200, state);
      }
      if (req.method === 'GET' && url.pathname === '/media') {
        const file = allowed.get(`${url.searchParams.get('key')}:${url.searchParams.get('i')}`);
        if (!file || !fs.existsSync(file)) return send(res, 404, {error: 'not in gallery'});
        return send(res, 200, fs.readFileSync(file), MIME[path.extname(file).toLowerCase()] || 'application/octet-stream');
      }
      if (req.method === 'POST' && ['/api/pick', '/api/regenerate'].includes(url.pathname)) {
        if (!/^application\/json/.test(req.headers['content-type'] || '')) return send(res, 415, {error: 'json only'});
        const body = await readBody(req);
        const key = String(body.key || '');
        if (!/^[a-f0-9]{12,64}$/.test(key)) return send(res, 400, {error: 'bad key'});
        const args = url.pathname === '/api/pick'
          ? ['decide', 'pick', key, '--index', String(Number.parseInt(body.index, 10))]
          : ['decide', 'regenerate', key, ...(body.note ? ['--note', String(body.note).slice(0, 2000)] : [])];
        return send(res, 200, await runPython(args));
      }
      return send(res, 404, {error: 'not found'});
    } catch (e) {
      return send(res, 500, {error: e.message});
    }
  };
}

export function pythonRunner(python = process.env.FLOWPOOL_PYTHON || 'python3') {
  return args => new Promise((resolve, reject) => {
    const child = spawn(python, ['-m', 'flowpool', ...args], {cwd: SYS});
    let out = '', err = '';
    child.stdout.on('data', d => { out += d; });
    child.stderr.on('data', d => { err += d; });
    child.on('close', () => { try { resolve(JSON.parse(out)); } catch { reject(new Error((err || out).slice(-500))); } });
  });
}

function readJson(file, fallback = {}) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return fallback; }
}

async function serve() {
  const {chromium} = await import('playwright');
  const cfg = readJson(path.join(SYS, 'config.json'));
  const b2 = path.join(SYS, 'experiments/b2_illustrator');
  const profiles = {...readJson(path.join(b2, 'browser-profiles.json')), ...readJson(path.join(b2, 'machine.local.json'))};
  const userDataDir = profiles.flow_user_data_dir;
  const socketPath = cfg.flowpool_daemon_socket || path.join(here, 'daemon.sock');
  const port = Number(cfg.flowpool_ui_port || 8765);
  if (fs.existsSync(socketPath)) {
    const alive = await new Promise(r => { const c = net.createConnection(socketPath, () => { c.end(); r(true); }); c.on('error', () => r(false)); });
    if (alive) throw Error('FlowPool daemon already running');
    fs.unlinkSync(socketPath);
  }
  let rpc, web;
  const handle = createDaemon({
    connect: ep => chromium.connectOverCDP(ep, {timeout: 120000}),
    endpoint: () => endpointFromDir(userDataDir),
    onShutdown: () => { rpc?.close(); web?.close(); process.exit(0); },
  });
  rpc = net.createServer(client => {
    let data = '';
    client.on('error', () => {});
    client.on('data', chunk => {
      data += chunk;
      if (data.length > 4 * 1024 * 1024) return client.destroy();
      if (!data.includes('\n')) return;
      client.removeAllListeners('data');
      let msg;
      try { msg = JSON.parse(data.split('\n')[0]); } catch { return client.end(JSON.stringify({ok: false, code: 'PROTOCOL', error: 'bad json'}) + '\n'); }
      handle(msg).then(reply => client.end(JSON.stringify(reply) + '\n'));
    });
  });
  rpc.listen(socketPath, () => fs.chmodSync(socketPath, 0o600));
  rpc.on('close', () => { try { fs.unlinkSync(socketPath); } catch {} });
  const html = () => fs.readFileSync(path.join(here, 'dashboard.html'), 'utf8');
  web = http.createServer(createDashboard({handle, runPython: pythonRunner(), html}));
  web.listen(port, '127.0.0.1', () => console.log(`FlowPool dashboard: http://127.0.0.1:${port}`));
  for (const sig of ['SIGTERM', 'SIGINT']) process.on(sig, () => handle({op: 'shutdown'}));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url) && process.argv[2] === 'serve') {
  serve().catch(e => { console.error(e.message); process.exit(2); });
}
