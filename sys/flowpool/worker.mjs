/**
 * FlowPool worker: one process per active instance, driven by flowpool/driver.py
 * over line-delimited JSON on stdin/stdout. It attaches over CDP to the
 * instance's own Chrome (started by `python3 -m flowpool launch`, one account
 * per user-data-dir and port) and never launches a browser itself.
 */
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import {fileURLToPath} from 'node:url';
import * as ops from './flow-ops.mjs';

export function debugEndpoint(contents) {
  const [rawPort, rawPath] = contents.trim().split(/\r?\n/);
  const port = Number(rawPort);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw ops.coded('NO_CDP', 'invalid DevToolsActivePort');
  if (!rawPath || !/^\/devtools\/browser\/[a-zA-Z0-9-]+$/.test(rawPath.trim())) throw ops.coded('NO_CDP', 'invalid browser WebSocket path');
  return `ws://127.0.0.1:${port}${rawPath.trim()}`;
}

/** The instance's own debugging port; DevToolsActivePort in its data dir as a fallback. */
export function endpointFor(profile) {
  if (profile.port) return `http://127.0.0.1:${Number(profile.port)}`;
  const portFile = path.join(profile.user_data_dir || '', 'DevToolsActivePort');
  if (!profile.user_data_dir || !fs.existsSync(portFile)) throw ops.coded('NO_CDP', `instance ${profile.name} has no debugging port`);
  return debugEndpoint(fs.readFileSync(portFile, 'utf8'));
}

export function createWorker({connect, operations = ops} = {}) {
  const state = {browser: null, session: null, cfg: {}};
  const handlers = {
    async open(msg) {
      state.cfg = msg.cfg || {};
      const profile = msg.profile;
      state.browser = await connect(endpointFor(profile)).catch(e => {
        throw ops.coded('NO_CDP', `instance ${profile.name} is not reachable (${e.message}); run: python3 -m flowpool launch ${profile.name}`);
      });
      const page = await operations.pickPage(state.browser);
      state.session = {page, profile, pending: null, projectUrl: profile.project_url || null};
      await operations.assertUsable(page);
      const accountVerified = await operations.verifyAccount(page, profile);
      return {url: page.url(), account_verified: accountVerified};
    },
    async probe(msg) { return operations.probe(state.session, msg.kinds || [], state.cfg); },
    async credits() { return {credits: await operations.readCredits(state.session.page, state.cfg.flowpool_credit_probe || {})}; },
    async prepare(msg) {
      if (state.session.pending) throw ops.coded('INVALID_STATE', 'a prepared batch is waiting for commit');
      const b2 = msg.kind === 'image' && msg.items?.[0]?.engine === 'b2';
      const prepared = b2 ? await operations.imagePrepare(state.session, msg.items)
        : await operations.flowPrepare(state.session, msg.items, state.cfg);
      return {prepared};
    },
    async commit(msg) {
      const pending = state.session?.pending;
      if (!pending) throw ops.coded('INVALID_STATE', 'nothing prepared', {submitted: false});
      const items = pending.kind === 'b2' ? await operations.imageCommit(state.session, msg.timeout_ms)
        : await operations.flowCommit(state.session, msg.timeout_ms);
      return {items};
    },
    async close() {
      // Disconnect only: for a CDP-attached browser this never closes the user's Chrome or tabs.
      if (state.browser) await state.browser.close().catch(() => undefined);
      state.browser = null;
      return {};
    },
  };
  return async function handle(msg) {
    const op = handlers[msg?.op];
    if (!op) return {ok: false, code: 'PROTOCOL', error: `unknown op ${msg?.op}`};
    const project = () => state.session?.projectUrl ? {project_url: state.session.projectUrl} : {};
    try {
      const reply = await op(msg);
      return {ok: true, ...reply, ...project()};
    } catch (e) {
      const submitted = msg.op === 'commit' ? e.submitted !== false : Boolean(e.submitted);
      return {ok: false, code: e.code || (msg.op === 'commit' ? 'RECONCILE_REQUIRED' : 'WORKER_ERROR'), error: e.message,
        submitted, partial: e.partial || null, ...project()};
    }
  };
}

async function main() {
  const {chromium} = await import('playwright');
  const handle = createWorker({connect: endpoint => chromium.connectOverCDP(endpoint, {timeout: 60000})});
  const rl = readline.createInterface({input: process.stdin});
  for await (const line of rl) {
    if (!line.trim()) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { process.stdout.write(JSON.stringify({ok: false, code: 'PROTOCOL', error: 'bad json'}) + '\n'); continue; }
    const reply = await handle(msg);
    process.stdout.write(JSON.stringify(reply) + '\n');
    if (msg.op === 'close') break;
  }
  process.exit(0);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
