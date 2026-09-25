import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import * as ops from './flow-ops.mjs';
import {createWorker, debugEndpoint} from './worker.mjs';
import {pollQueue} from '../experiments/b2_illustrator/queue-runner.mjs';

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'flowpool-'));
const fakePage = (url = 'https://flow.test/tool', text = '') => ({
  url: () => url, goto: async u => { url = u; }, isClosed: () => false,
  evaluate: async () => ({text, frames: []}), context: () => ({}),
});

test('CAPTCHA and sign-in walls are detected, invisible reCAPTCHA is not', () => {
  assert.equal(ops.classifySnapshot({url: 'https://www.google.com/sorry/index'}).state, 'captcha');
  assert.equal(ops.classifySnapshot({url: 'https://labs.google/fx/tools/flow', text: "Verify you're not a robot"}).state, 'captcha');
  assert.equal(ops.classifySnapshot({frames: [{src: 'https://www.google.com/recaptcha/api2/bframe?k=1', width: 400, height: 580}]}).state, 'captcha');
  assert.equal(ops.classifySnapshot({frames: [{src: 'https://www.google.com/recaptcha/enterprise/anchor?size=invisible', width: 256, height: 60}]}).state, 'ok');
  assert.equal(ops.classifySnapshot({url: 'https://accounts.google.com/v3/signin/identifier'}).state, 'needs_login');
  assert.equal(ops.classifySnapshot({text: 'Choose an account to continue'}).state, 'needs_login');
  assert.equal(ops.classifySnapshot({url: 'https://labs.google/fx/tools/flow/project/1', text: 'New project'}).state, 'ok');
});

test('assertUsable throws coded errors and never interacts', async () => {
  await assert.rejects(ops.assertUsable(fakePage('https://accounts.google.com/x')), e => e.code === 'NEEDS_LOGIN');
  await assert.rejects(ops.assertUsable(fakePage('https://x', 'unusual traffic from your computer network')), e => e.code === 'CAPTCHA');
});

test('credit balances are parsed; cost phrases and ambiguity give null', () => {
  assert.equal(ops.pickCredits(['1.050 credits']).value, 1050);
  assert.equal(ops.pickCredits(['AI credits: 1,050']).value, 1050);
  assert.equal(ops.pickCredits(['Còn lại 980 tín dụng']).value, 980);
  assert.equal(ops.pickCredits(['Veo 3.1 - Fast uses 20 credits', '20 credits per video']).value, null);
  assert.equal(ops.pickCredits(['1,050 credits', '900 credits']).value, null);
  assert.equal(ops.pickCredits(['no numbers here']).value, null);
});

test('tabs bind by recorded target, else by the open-profile marker', async () => {
  const pages = [fakePage('https://labs.google/fx/tools/flow#flowpool=profile-13'), fakePage('https://labs.google/fx/tools/flow')];
  const infos = new Map([[pages[0], {targetId: 'T13', browserContextId: 'C13'}], [pages[1], {targetId: 'T10', browserContextId: 'C10'}]]);
  const browser = {contexts: () => [{pages: () => pages}]};
  const info = async p => infos.get(p);
  const p13 = {name: 'Profile 13', slug: 'profile-13'};
  assert.equal((await ops.bindPage(browser, p13, info)).binding.target_id, 'T13');
  const p10 = {name: 'Profile 10', slug: 'profile-10', binding: {target_id: 'T10'}};
  assert.equal((await ops.bindPage(browser, p10, info)).page, pages[1]);
  await assert.rejects(ops.bindPage(browser, {name: 'Profile 14', slug: 'profile-14'}, info), e => e.code === 'PROFILE_TAB_NOT_FOUND');
  await assert.rejects(ops.bindPage(browser, {...p13, _other_context_ids: ['C13']}, info), e => e.code === 'PROFILE_MISMATCH');
  pages.push(fakePage('https://x#flowpool=profile-13'));
  infos.set(pages[2], {targetId: 'T99'});
  await assert.rejects(ops.bindPage(browser, p13, info), /2 tabs/);
});

function fakeB2(calls, {pollError = null, queued = []} = {}) {
  return {
    findToolFrame: async () => ({frame: true}),
    prepareRequests: (specs, opts) => { calls.push(['prepareRequests', opts]); return specs.map(s => ({spec: s})); },
    assertQueueIdle: async () => { calls.push(['assertQueueIdle']); },
    enqueueRequests: async (f, reqs) => { calls.push(['enqueue', reqs.length]); return reqs.map((_, i) => `q${i}`); },
    selectWorkers: async () => { calls.push(['selectWorkers']); },
    clickStartQueue: async () => { calls.push(['START']); },
    modelLabelFor: m => `🍌 ${m}`,
    pollQueue: async (frame, ids, {onGenerated}) => {
      queued.forEach((item, i) => onGenerated(i, item));
      if (pollError) throw new Error(pollError);
    },
  };
}
const item = (id, extra = {}) => ({id, prompt: 'p', ratio: '16:9', out_dir: path.join(tmp, id), refs: ['/r.png'],
  ref_media_ids: ['M'], model: 'Nano Banana 2', ...extra});
const png = Buffer.from('iVBORw0KGgo=', 'base64').toString('base64');

test('image prepare fills the local queue only; commit is the single start', async () => {
  const calls = [];
  const session = {page: fakePage('https://flow.test/tool'), profile: {name: 'P', tool_url: 'https://flow.test/tool'}};
  const lib = fakeB2(calls, {queued: [{id: 'q0', mediaId: 'MID', result: {mimeType: 'image/png', base64: png}}]});
  assert.deepEqual(await ops.imagePrepare(session, [item('a')], lib), ['q0']);
  assert.ok(!calls.some(c => c[0] === 'START'));
  assert.deepEqual(calls[0][1], {tool: 'https://flow.test/tool', model: 'Nano Banana 2'});
  const out = await ops.imageCommit(session, 1000, lib);
  assert.equal(calls.filter(c => c[0] === 'START').length, 1);
  assert.deepEqual(out[0].media_ids, ['MID']);
  assert.ok(fs.existsSync(out[0].files[0]));
  assert.equal(JSON.parse(fs.readFileSync(path.join(tmp, 'a', 'a-1.flowpool.json'))).mediaId, 'MID');
  await assert.rejects(ops.imagePrepare({...session, profile: {name: 'P'}}, [item('b')], lib), e => e.code === 'TOOL_NOT_READY');
  await assert.rejects(ops.imagePrepare(session, [item('b'), item('c', {model: 'Other'})], lib), e => e.code === 'INVALID_BATCH');
});

test('queue failure after start is submitted, keeps partial outputs', async () => {
  const calls = [];
  const lib = fakeB2(calls, {pollError: 'FLOW_TIMEOUT_RECONCILE_NO_RESUBMIT',
    queued: [{id: 'q0', mediaId: 'M0', result: {mimeType: 'image/png', base64: png}}]});
  const session = {page: fakePage('https://flow.test/tool'), profile: {name: 'P', tool_url: 'https://flow.test/tool'}};
  await ops.imagePrepare(session, [item('d'), item('e')], lib);
  await assert.rejects(ops.imageCommit(session, 1000, lib), e => e.code === 'TIMEOUT' && e.submitted && e.partial[0].files.length === 1 && !e.partial[1].files.length);
  const busy = {...session, page: fakePage('https://flow.test/tool')};
  busy.page.evaluate = async () => ({text: "I'm not a robot", frames: []});
  await ops.imagePrepare({...session}, [item('f')], fakeB2([])).catch(() => {});
  const s2 = {page: busy.page, profile: session.profile, pending: {kind: 'image', frame: {}, ids: ['q0'], items: [item('f')]}};
  await assert.rejects(ops.imageCommit(s2, 10, fakeB2([], {pollError: 'FLOW_RECONCILIATION_REQUIRED'})), e => e.code === 'CAPTCHA' && e.submitted);
});

test('clip refusals map to declined codes; timeouts stay unknown', async () => {
  class RateLimitedError extends Error { constructor(m) { super(m); this.name = 'RateLimitedError'; } }
  const run = async err => {
    const fp = {submit: async () => {}, waitForResults: async () => { throw err; }};
    const session = {page: fakePage('https://labs.google/fx/tools/flow/project/1'), pending: {kind: 'clip', fp, before: new Set(), item: item('c', {variants: 2})}};
    return ops.clipCommit(session, 10, {}).catch(e => e);
  };
  assert.equal((await run(new RateLimitedError('slow down'))).code, 'RATE_LIMITED');
  const failed = new Error('Flow displayed a generation failed message.'); failed.name = 'GenerationFailedError';
  assert.equal((await run(failed)).code, 'GENERATION_FAILED');
  const timeout = new Error('Timed out waiting for 2 result(s).'); timeout.name = 'GenerationFailedError';
  const e = await run(timeout);
  assert.equal(e.code, 'TIMEOUT');
  assert.equal(e.submitted, true);
});

test('worker protocol: no CDP, commit semantics, disconnect only', async () => {
  const dir = fs.mkdtempSync(path.join(tmp, 'udd-'));
  let closed = 0;
  const operations = {
    ...ops,
    bindPage: async () => ({page: fakePage('https://labs.google/fx/tools/flow'), binding: {target_id: 'T'}}),
    assertUsable: async () => ({state: 'ok'}), verifyAccount: async () => null,
    imagePrepare: async s => { s.pending = {kind: 'image'}; return ['q0']; },
    imageCommit: async () => { throw Object.assign(new Error('boom'), {code: 'TIMEOUT'}); },
  };
  const handle = createWorker({connect: async () => ({close: async () => { closed++; }}), operations});
  const profile = {name: 'P', slug: 'p', user_data_dir: dir};
  assert.equal((await handle({op: 'open', profile})).code, 'NO_CDP');
  fs.writeFileSync(path.join(dir, 'DevToolsActivePort'), '9222\n/devtools/browser/abc-123\n');
  assert.equal((await handle({op: 'open', profile, cfg: {}})).ok, true);
  const early = await handle({op: 'commit', timeout_ms: 5});
  assert.deepEqual([early.ok, early.code, early.submitted], [false, 'INVALID_STATE', false]);
  assert.deepEqual((await handle({op: 'prepare', kind: 'image', items: []})).prepared, ['q0']);
  const late = await handle({op: 'commit', timeout_ms: 5});
  assert.deepEqual([late.code, late.submitted], ['TIMEOUT', true]);
  assert.equal((await handle({op: 'close'})).ok, true);
  assert.equal(closed, 1);
  assert.equal((await handle({op: 'launch'})).code, 'PROTOCOL');
  assert.throws(() => debugEndpoint('abc'), e => e.code === 'NO_CDP');
});

test('B-2 pollQueue captures each result once and stops on a vanished queue', async () => {
  const states = [
    {queue: [{id: 'a', status: 'RUNNING'}, {id: 'b', status: 'RUNNING'}]},
    {queue: [{id: 'a', status: 'COMPLETED', mediaId: 'A', result: {base64: 'x'}}, {id: 'b', status: 'RUNNING'}]},
    {queue: [{id: 'a', status: 'COMPLETED', mediaId: 'A', result: {base64: 'x'}}, {id: 'b', status: 'COMPLETED', mediaId: 'B', result: {base64: 'y'}}]},
  ];
  let n = 0;
  const frame = {evaluate: async () => states[Math.min(n++, states.length - 1)]};
  const seen = [];
  await pollQueue(frame, ['a', 'b'], {timeoutMs: 5000, sleep: async () => {}, onGenerated: (i, it) => seen.push(it.mediaId)});
  assert.deepEqual(seen, ['A', 'B']);
  const gone = {evaluate: async () => ({queue: []})};
  await assert.rejects(pollQueue(gone, ['a'], {sleep: async () => {}}), /QUEUE_DISAPPEARED/);
});
