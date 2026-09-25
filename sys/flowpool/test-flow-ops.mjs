import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import * as ops from './flow-ops.mjs';
import {createWorker, debugEndpoint, endpointFor} from './worker.mjs';
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

test('one instance = one account: reuse its Flow tab, else a plain tab, else open one', async () => {
  const other = fakePage('chrome://newtab/'), flow = fakePage('https://flow.google.com/project/abc');
  const browser = pages => ({contexts: () => [{pages: () => pages, newPage: async () => 'NEW'}]});
  assert.equal(await ops.pickPage(browser([other, flow])), flow);
  const plain = fakePage('https://example.org/');
  assert.equal(await ops.pickPage(browser([other, plain])), plain);
  assert.equal(await ops.pickPage(browser([other])), 'NEW');
  await assert.rejects(ops.pickPage({contexts: () => []}), e => e.code === 'NO_CDP');
});

test('project URLs are canonical and resolved on the current (flow.google.com) host', async () => {
  assert.equal(ops.projectUrlOf('https://flow.google.com/project/7c815425-4625-4afb?x=1#flowpool=a'), 'https://flow.google.com/project/7c815425-4625-4afb');
  assert.equal(ops.projectUrlOf('https://labs.google/fx/tools/flow/project/41d3d574-907c/tool/2791'), 'https://labs.google/fx/tools/flow/project/41d3d574-907c');
  assert.equal(ops.projectUrlOf('https://flow.google.com/'), null);
  const page = {url: () => 'https://flow.google.com/', evaluate: async () => '/project/0123abcd-ef'};
  assert.equal(await ops.findProjectUrl(page, 'Video Pilot'), 'https://flow.google.com/project/0123abcd-ef');
});

function fakeFlow({cards = {}, canCreate = true, url = 'https://flow.google.com/'} = {}) {
  const calls = [];
  const loc = (visible, onClick) => ({first: () => loc(visible, onClick), or: () => loc(visible, onClick),
    waitFor: async () => {}, isVisible: async () => visible, click: async () => onClick && onClick()});
  const page = {
    url: () => url, goto: async u => { calls.push(['goto', u]); url = u; },
    evaluate: async (fn, arg) => typeof arg === 'string' ? (cards[arg] || null) : {text: '', frames: []},
    locator: () => loc(Object.keys(cards).length > 0),
    waitForURL: async () => {},
  };
  const newProject = loc(canCreate, () => { calls.push(['new-project']); url = 'https://flow.google.com/project/beef0001-aaaa'; });
  const g = {flowLocators: () => ({newProjectButton: newProject})};
  return {page, g, calls};
}

test('ensureProject: recorded URL, else named card, else creates one (no generation)', async () => {
  let f = fakeFlow();
  const cfg = {flowpool_flow_url: 'https://flow.google.com/'};
  let session = {page: f.page, profile: {name: 'acc1', project: 'Video Pilot'}};
  assert.equal(await ops.ensureProject(session, cfg, f.g), 'https://flow.google.com/project/beef0001-aaaa');
  assert.deepEqual(f.calls.map(c => c[0]), ['goto', 'new-project']);
  f = fakeFlow({cards: {'Video Pilot': '/project/cafe0002-bbbb'}});
  session = {page: f.page, profile: {name: 'acc1', project: 'Video Pilot'}};
  assert.equal(await ops.ensureProject(session, cfg, f.g), 'https://flow.google.com/project/cafe0002-bbbb');
  assert.ok(!f.calls.some(c => c[0] === 'new-project'));
  f = fakeFlow();
  session = {page: f.page, profile: {name: 'acc1', project: 'Video Pilot', project_url: 'https://flow.google.com/project/dddd0003-cccc'}};
  assert.equal(await ops.ensureProject(session, cfg, f.g), 'https://flow.google.com/project/dddd0003-cccc');
  assert.deepEqual(f.calls, [['goto', 'https://flow.google.com/project/dddd0003-cccc']]);
  f = fakeFlow({canCreate: false});
  await assert.rejects(ops.ensureProject({page: f.page, profile: {name: 'acc1', project: 'X'}}, cfg, f.g), e => e.code === 'NEEDS_LOGIN');
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
  const s2 = {page: busy.page, profile: session.profile, pending: {kind: 'b2', frame: {}, ids: ['q0'], items: [item('f')]}};
  await assert.rejects(ops.imageCommit(s2, 10, fakeB2([], {pollError: 'FLOW_RECONCILIATION_REQUIRED'})), e => e.code === 'CAPTCHA' && e.submitted);
});

test('Flow refusals map to declined codes; timeouts stay unknown', async () => {
  class RateLimitedError extends Error { constructor(m) { super(m); this.name = 'RateLimitedError'; } }
  const run = async err => {
    const fp = {submit: async () => {}, waitForResults: async () => { throw err; }};
    const session = {page: fakePage('https://flow.google.com/project/1'), pending: {kind: 'flow', type: 'video', expected: 2, fp, before: new Set(), item: item('c', {variants: 2})}};
    return ops.flowCommit(session, 10, {}).catch(e => e);
  };
  assert.equal((await run(new RateLimitedError('slow down'))).code, 'RATE_LIMITED');
  const failed = new Error('Flow displayed a generation failed message.'); failed.name = 'GenerationFailedError';
  assert.equal((await run(failed)).code, 'GENERATION_FAILED');
  const timeout = new Error('Timed out waiting for 2 result(s).'); timeout.name = 'GenerationFailedError';
  const e = await run(timeout);
  assert.equal(e.code, 'TIMEOUT');
  assert.equal(e.submitted, true);
});

test('plain-Flow image: attaches refs, fills prompt, submits only on commit', async () => {
  const calls = [];
  const it = item('g', {kind: 'image', engine: 'flow', refs: ['/tmp/mascot.png']});
  const page = {url: () => 'https://flow.google.com/project/abcd0001-ef', goto: async () => {}, isClosed: () => false,
    evaluate: async () => ({text: '', frames: []}), context: () => ({}),
    getByText: () => ({count: async () => 0})};
  const g = {
    FlowPage: class { constructor() {} async assertReady() {} async applySettings(job) { calls.push(['settings', job]); }
      async resultSrcs() { return ['old']; } async fillPrompt(p) { calls.push(['prompt', p]); } async submit() { calls.push(['SUBMIT']); }
      async waitForResults(before, n, t, type) { calls.push(['wait', n, type]); return ['new-src?name=abcd-1234']; } },
    flowLocators: () => ({settingsButton: {first: () => ({innerText: async () => '🍌 Nano Banana 2 crop_16_9 x1'})}}),
    downloadResult: async ({basename, outDir}) => ({assetPath: path.join(outDir, basename + '.png')}),
    mediaIdFromSrc: () => 'abcd-1234',
  };
  const session = {page, profile: {name: 'acc1', project_url: 'https://flow.google.com/project/abcd0001-ef'}, projectUrl: null};
  // No ingredient button on this fake page: a reference that cannot be attached blocks before submit.
  page.locator = () => ({filter: () => ({first: () => ({isVisible: async () => false})})});
  await assert.rejects(ops.flowPrepare(session, [it], {}, g), e => e.code === 'REFERENCE_NOT_ATTACHED');
  assert.ok(!calls.some(c => c[0] === 'SUBMIT'));
  const noRef = {...it, refs: []};
  await ops.flowPrepare(session, [noRef], {flowpool_model_labels: {}}, g);
  assert.deepEqual(calls.find(c => c[0] === 'settings')[1], {type: 'image', ratio: '16:9', outputs: 1, model: 'Nano Banana 2'});
  assert.ok(!calls.some(c => c[0] === 'SUBMIT'));
  const [out] = await ops.flowCommit(session, 1000, g);
  assert.equal(calls.filter(c => c[0] === 'SUBMIT').length, 1);
  assert.deepEqual(calls.find(c => c[0] === 'wait').slice(1), [1, 'image']);
  assert.deepEqual([out.files.length, out.media_ids], [1, ['abcd-1234']]);
  await assert.rejects(ops.flowPrepare(session, [noRef, noRef], {}, g), e => e.code === 'INVALID_BATCH');
});

test('worker protocol: per-instance port, engine dispatch, commit semantics, disconnect only', async () => {
  const dir = fs.mkdtempSync(path.join(tmp, 'udd-'));
  let closed = 0;
  const seen = [];
  const operations = {
    ...ops,
    pickPage: async () => fakePage('https://flow.google.com/'),
    assertUsable: async () => ({state: 'ok'}), verifyAccount: async () => null,
    imagePrepare: async s => { seen.push('b2'); s.pending = {kind: 'b2'}; return ['q0']; },
    flowPrepare: async s => { seen.push('flow'); s.projectUrl = 'https://flow.google.com/project/aaaa0001-bb'; s.pending = {kind: 'flow'}; return [null]; },
    imageCommit: async s => { s.pending = null; throw Object.assign(new Error('boom'), {code: 'TIMEOUT'}); },
    flowCommit: async s => { s.pending = null; return [{id: 'x', files: ['/f.png'], media_ids: ['m']}]; },
  };
  const endpoints = [];
  const handle = createWorker({connect: async ep => { endpoints.push(ep); if (ep.includes('9399')) throw new Error('ECONNREFUSED'); return {close: async () => { closed++; }}; }, operations});
  assert.equal((await handle({op: 'open', profile: {name: 'P', user_data_dir: dir}})).code, 'NO_CDP');
  assert.equal((await handle({op: 'open', profile: {name: 'P', port: 9399}})).code, 'NO_CDP');
  assert.equal(endpointFor({name: 'P', port: 9301}), 'http://127.0.0.1:9301');
  fs.writeFileSync(path.join(dir, 'DevToolsActivePort'), '9222\n/devtools/browser/abc-123\n');
  assert.equal(endpointFor({name: 'P', user_data_dir: dir}), 'ws://127.0.0.1:9222/devtools/browser/abc-123');
  assert.equal((await handle({op: 'open', profile: {name: 'P', port: 9301}, cfg: {}})).ok, true);
  const early = await handle({op: 'commit', timeout_ms: 5});
  assert.deepEqual([early.ok, early.code, early.submitted], [false, 'INVALID_STATE', false]);
  const flowReply = await handle({op: 'prepare', kind: 'image', items: [{engine: 'flow'}]});
  assert.equal(flowReply.project_url, 'https://flow.google.com/project/aaaa0001-bb');
  assert.equal((await handle({op: 'commit', timeout_ms: 5})).items[0].id, 'x');
  assert.deepEqual((await handle({op: 'prepare', kind: 'image', items: [{engine: 'b2'}]})).prepared, ['q0']);
  const late = await handle({op: 'commit', timeout_ms: 5});
  assert.deepEqual([late.code, late.submitted], ['TIMEOUT', true]);
  await handle({op: 'prepare', kind: 'clip', items: [{engine: 'clip'}]});
  assert.deepEqual(seen, ['flow', 'b2', 'flow']);
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
