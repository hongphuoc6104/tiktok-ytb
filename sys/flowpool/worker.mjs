/**
 * FlowPool worker: one process per active profile, driven by flowpool/driver.py
 * over line-delimited JSON on stdin/stdout. It attaches over CDP to the Chrome
 * that already runs the profile's user-data-dir (DevToolsActivePort, exactly
 * like the B-2 session) and never launches a browser itself.
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

export function createWorker({connect, operations = ops} = {}) {
  const state = {browser: null, session: null, cfg: {}};
  const handlers = {
    async open(msg) {
      state.cfg = msg.cfg || {};
      const profile = msg.profile;
      const portFile = path.join(profile.user_data_dir, 'DevToolsActivePort');
      if (!fs.existsSync(portFile)) throw ops.coded('NO_CDP', `Chrome for ${profile.user_data_dir} is not running with remote debugging (DevToolsActivePort missing)`);
      state.browser = await connect(debugEndpoint(fs.readFileSync(portFile, 'utf8')));
      const {page, binding} = await operations.bindPage(state.browser, profile);
      state.session = {page, profile, pending: null};
      await operations.assertUsable(page);
      const accountVerified = await operations.verifyAccount(page, profile);
      return {binding, url: page.url(), account_verified: accountVerified};
    },
    async probe(msg) { return operations.probe(state.session, msg.kinds || [], state.cfg); },
    async credits() { return {credits: await operations.readCredits(state.session.page, state.cfg.flowpool_credit_probe || {})}; },
    async prepare(msg) {
      if (state.session.pending) throw ops.coded('INVALID_STATE', 'a prepared batch is waiting for commit');
      const prepared = msg.kind === 'clip' ? await operations.clipPrepare(state.session, msg.items, state.cfg)
        : await operations.imagePrepare(state.session, msg.items);
      return {prepared};
    },
    async commit(msg) {
      const pending = state.session?.pending;
      if (!pending) throw ops.coded('INVALID_STATE', 'nothing prepared', {submitted: false});
      const items = pending.kind === 'clip' ? await operations.clipCommit(state.session, msg.timeout_ms)
        : await operations.imageCommit(state.session, msg.timeout_ms);
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
    try {
      return {ok: true, ...(await op(msg))};
    } catch (e) {
      const submitted = msg.op === 'commit' ? e.submitted !== false : Boolean(e.submitted);
      return {ok: false, code: e.code || (msg.op === 'commit' ? 'RECONCILE_REQUIRED' : 'WORKER_ERROR'), error: e.message,
        submitted, partial: e.partial || null};
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
