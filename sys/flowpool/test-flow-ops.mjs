import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import * as ops from './flow-ops.mjs';
import http from 'node:http';
import {createDaemon, createDashboard, debugEndpoint, endpointFromDir} from './daemon.mjs';
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
  assert.equal(ops.pickCredits(['1,050 Google Flow credits']).value, 1050);
  assert.equal(ops.pickCredits(['AI credits: 1,050']).value, 1050);
  assert.equal(ops.pickCredits(['Còn lại 980 tín dụng']).value, 980);
  assert.equal(ops.pickCredits(['Veo 3.1 - Fast uses 20 Google Flow credits', '20 credits per video']).value, null);
  assert.equal(ops.pickCredits(['1,050 credits', '900 credits']).value, null);
  assert.equal(ops.pickCredits(['no numbers here']).value, null);
});

test('credit probe opens the account panel and reads its balance link in both UI locales', async () => {
  for (const [label, creditLabel, creditSelector] of [
    ['Account details', '1,050 Google Flow credits', '[aria-label*="Google Flow credits" i]'],
    ['Thông tin về tài khoản', '1.050 tín dụng', '[aria-label*="tín dụng" i]'],
  ]) {
    let opened = false, escaped = false;
    const balance = {getBoundingClientRect: () => ({width: 180, height: 30}),
      getAttribute: name => name === 'aria-label' ? creditLabel : null, innerText: ''};
    const page = {
      locator: sel => ({evaluateAll: async fn => opened && sel === creditSelector ? fn([balance]) : [],
        first: () => ({isVisible: async () => sel.includes(`aria-label="${label}"`), click: async () => { opened = true; }})}),
      waitForTimeout: async () => {}, keyboard: {press: async key => { escaped = key === 'Escape'; }},
    };
    const got = await ops.readCredits(page, {selectors: [], open: []});
    assert.equal(got.value, 1050);
    assert.match(got.method, /^open:/);
    assert.ok(escaped);
  }
});

function tabs(list) {
  const pages = list.map(([url, id]) => ({...fakePage(url), id, closed: false, close: async function () { this.closed = true; }}));
  return {pages, browser: {contexts: () => [{pages: () => pages.filter(p => !p.closed)}]}, info: async p => p.id};
}

test('profiles are found by target id, then URL marker (duplicates closed), then account e-mail', async () => {
  const {pages, browser, info} = tabs([
    ['https://flow.google.com/project/aa11bb22', 'T10'],
    ['https://flow.google.com/#flowpool=profile-13', 'T13a'],
    ['https://flow.google.com/#flowpool=profile-13', 'T13b'],
    ['https://flow.google.com/', 'T14'],
    ['chrome://newtab/', 'TX'],
  ]);
  const emails = async p => (p.id === 'T14' ? ['c@example.com'] : []);
  const profiles = [
    {name: 'Profile 10', slug: 'profile-10', binding: {target_id: 'T10'}},
    {name: 'Profile 13', slug: 'profile-13'},
    {name: 'Profile 14', slug: 'profile-14', account_email: 'C@example.com'},
    {name: 'Profile 102', slug: 'profile-102'},
  ];
  let found = await ops.locateProfiles(browser, profiles, {info, emails});
  assert.deepEqual(Object.fromEntries(Object.entries(found).map(([n, f]) => [n, [f.target_id, f.via]])),
    {'Profile 10': ['T10', 'target'], 'Profile 13': ['T13a', 'marker'], 'Profile 14': ['T14', 'email']});
  assert.ok(!pages[2].closed);
  found = await ops.locateProfiles(browser, profiles, {info, emails, dedupe: true});
  assert.equal(found['Profile 13'].closed, 1);
  assert.ok(pages[2].closed && !pages[1].closed);
});

test('account check: a recorded e-mail must match what the tab shows', async () => {
  const page = {evaluate: async () => ['a@example.com']};
  assert.deepEqual(await ops.verifyAccount(page, {name: 'P'}), {email: 'a@example.com', verified: null});
  assert.deepEqual(await ops.verifyAccount(page, {name: 'P', account_email: 'A@example.com'}), {email: 'a@example.com', verified: true});
  await assert.rejects(ops.verifyAccount(page, {name: 'P', account_email: 'b@example.com'}), e => e.code === 'PROFILE_MISMATCH');
});

test('project URLs are canonical and resolved on the current (flow.google.com) host', async () => {
  assert.equal(ops.projectUrlOf('https://flow.google.com/project/7c815425-4625-4afb?x=1#flowpool=a'), 'https://flow.google.com/project/7c815425-4625-4afb');
  assert.equal(ops.projectUrlOf('https://labs.google/fx/tools/flow/project/41d3d574-907c/tool/2791'), 'https://labs.google/fx/tools/flow/project/41d3d574-907c');
  assert.equal(ops.projectUrlOf('https://flow.google.com/'), null);
  const page = {url: () => 'https://flow.google.com/', evaluate: async () => '/project/0123abcd-ef'};
  assert.equal(await ops.findProjectUrl(page, 'Video Pilot'), 'https://flow.google.com/project/0123abcd-ef');
});

test('current project is reused and missing editor is distinct from sign-out or CAPTCHA', async () => {
  const calls = [];
  const editor = {waitFor: async () => {}, isVisible: async () => true,
    click: async () => calls.push('click'), press: async k => calls.push(k),
    pressSequentially: async s => calls.push(s)};
  const page = {...fakePage('https://flow.google.com/project/abcd1234-ef'),
    locator: sel => { assert.equal(sel, ops.PROMPT_EDITOR); return {first: () => editor}; }};
  const s = {page, profile: {name: 'P', project: 'Video Pilot'}};
  assert.equal(await ops.ensureProject(s, {}, {}), 'https://flow.google.com/project/abcd1234-ef');
  assert.equal(s.projectUrl, 'https://flow.google.com/project/abcd1234-ef');
  await ops.fillFlowPrompt(page, 'A hunter waits.', {dismissOpenLayers: async () => {}});
  assert.deepEqual(calls, ['click', 'ControlOrMeta+a', 'Backspace', 'A hunter waits.']);
  editor.isVisible = async () => false;
  await assert.rejects(ops.readyProjectEditor(page), e => e.code === 'EDITOR_NOT_FOUND');
  page.evaluate = async () => ({text: 'Choose an account to continue', frames: []});
  await assert.rejects(ops.readyProjectEditor(page), e => e.code === 'NEEDS_LOGIN');
  page.evaluate = async () => ({text: "Verify you're not a robot", frames: []});
  await assert.rejects(ops.readyProjectEditor(page), e => e.code === 'CAPTCHA');
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
  await assert.rejects(ops.ensureProject({page: f.page, profile: {name: 'acc1', project: 'X'}}, cfg, f.g), e => e.code === 'PROJECT_NOT_FOUND');
  f = fakeFlow();
  await assert.rejects(ops.ensureProject({page: f.page, profile: {name: 'acc1', project: 'X'}}, cfg, f.g, {create: false}),
    e => e.code === 'PROJECT_NOT_FOUND');
  assert.ok(!f.calls.some(c => c[0] === 'new-project'));
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
  const editor = {waitFor: async () => {}, isVisible: async () => true, click: async () => {},
    press: async () => {}, pressSequentially: async p => calls.push(['prompt', p])};
  const g = {
    FlowPage: class { constructor() {} async assertReady() { throw new Error('old role=textbox locator failed'); }
      async applySettings(job) { calls.push(['settings', job]); }
      async resultSrcs() { return ['old']; } async fillPrompt(p) { calls.push(['prompt', p]); } async submit() { calls.push(['SUBMIT']); }
      async waitForResults(before, n, t, type) { calls.push(['wait', n, type]); return ['new-src?name=abcd-1234']; } },
    flowLocators: () => ({settingsButton: {first: () => ({innerText: async () => '🍌 Nano Banana 2 crop_16_9 x1'})}}),
    downloadResult: async ({basename, outDir}) => ({assetPath: path.join(outDir, basename + '.png')}),
    mediaIdFromSrc: () => 'abcd-1234',
    dismissOpenLayers: async () => {},
  };
  const session = {page, profile: {name: 'acc1', project_url: 'https://flow.google.com/project/abcd0001-ef'}, projectUrl: null};
  // No ingredient button on this fake page: a reference that cannot be attached blocks before submit.
  page.locator = sel => sel === ops.PROMPT_EDITOR ? {first: () => editor}
    : {filter: () => ({first: () => ({isVisible: async () => false})})};
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

function fakeBrowser() {
  const handlers = {};
  return {connected: true, closes: 0, isConnected() { return this.connected; }, on(ev, fn) { handlers[ev] = fn; },
    drop() { this.connected = false; handlers.disconnected?.(); }, async close() { this.closes += 1; this.connected = false; }};
}

function daemonWith({connectResults, operations = {}}) {
  const connects = [];
  const results = [...connectResults];
  const handle = createDaemon({
    endpoint: () => 'ws://127.0.0.1:9222/devtools/browser/x',
    connect: async ep => { connects.push(ep); const r = results.shift(); if (r instanceof Error) throw r; return r; },
    operations: {...ops, assertUsable: async () => ({state: 'ok'}), verifyAccount: async () => ({email: 'a@x.com', verified: null}),
      locateProfiles: async (b, ps) => Object.fromEntries(ps.map(p => [p.name, {page: fakePage('https://flow.google.com/'), target_id: 'T-' + p.name, url: 'u', via: 'target', closed: 0}])),
      ...operations},
    onShutdown: () => {},
  });
  return {handle, connects};
}

test('daemon: one connection, one automatic reconnect, then NEEDS_ALLOW until the user reconnects', async () => {
  const b1 = fakeBrowser(), b2 = fakeBrowser(), b3 = fakeBrowser();
  const {handle, connects} = daemonWith({connectResults: [b1, b2, new Error('not allowed'), b3]});
  const P = {name: 'Profile 10', slug: 'profile-10'};
  assert.equal((await handle({op: 'open', profile: P})).code, 'NOT_CONNECTED');
  assert.equal((await handle({op: 'reconnect'})).connected, true);
  assert.equal((await handle({op: 'reconnect'})).reused, true);
  const opened = await handle({op: 'open', profile: P});
  assert.deepEqual([opened.ok, opened.email, opened.binding.target_id], [true, 'a@x.com', 'T-Profile 10']);
  assert.equal(connects.length, 1);
  b1.drop();
  assert.equal((await handle({op: 'open', profile: P})).ok, true);       // the one automatic reconnect
  assert.equal(connects.length, 2);
  b2.drop();
  const lost = await handle({op: 'open', profile: P});
  assert.equal(lost.code, 'NEEDS_ALLOW');
  assert.equal((await handle({op: 'credits', profile: P})).code, 'NEEDS_ALLOW');
  assert.equal(connects.length, 2);                                       // no reconnect loop
  assert.equal((await handle({op: 'reconnect'})).code, 'NEEDS_ALLOW');     // user has not clicked Allow yet
  assert.equal((await handle({op: 'reconnect'})).connected, true);
  const st = await handle({op: 'status'});
  assert.deepEqual([st.connected, st.needs_allow, st.activity['Profile 10'].last_error.code], [true, false, 'NEEDS_ALLOW']);
  assert.equal((await handle({op: 'shutdown'})).stopped, true);
  assert.equal(b3.closes, 1);
});

test('daemon: prepare/commit per profile, serialized per tab, parallel across profiles', async () => {
  const order = [];
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const operations = {
    flowPrepare: async (s, items) => { order.push(`prep ${s.profile.name}`); await sleep(20); s.projectUrl = 'https://flow.google.com/project/p1'; s.pending = {kind: 'flow'}; return [null]; },
    imagePrepare: async s => { s.pending = {kind: 'b2'}; return ['q0']; },
    flowCommit: async s => { order.push(`commit ${s.profile.name}`); s.pending = null; return [{id: 'x', files: ['/f.png'], media_ids: ['m']}]; },
    imageCommit: async s => { s.pending = null; throw Object.assign(new Error('boom'), {code: 'TIMEOUT'}); },
  };
  const {handle} = daemonWith({connectResults: [fakeBrowser()], operations});
  await handle({op: 'reconnect'});
  const A = {name: 'A', slug: 'a'}, B = {name: 'B', slug: 'b'};
  assert.deepEqual([(await handle({op: 'commit', profile: A})).code, (await handle({op: 'commit', profile: A})).submitted], ['INVALID_STATE', false]);
  const [pa, ca, pb] = await Promise.all([handle({op: 'prepare', profile: A, kind: 'image', items: [{engine: 'flow'}]}),
    handle({op: 'commit', profile: A, timeout_ms: 5}), handle({op: 'prepare', profile: B, kind: 'clip', items: [{}]})]);
  assert.equal(pa.project_url, 'https://flow.google.com/project/p1');
  assert.equal(ca.items[0].id, 'x');
  assert.ok(pb.ok);
  assert.ok(order.indexOf('commit A') > order.indexOf('prep A'));          // same tab: in order
  assert.ok(order.indexOf('prep B') < order.indexOf('commit A'));          // other profile: in parallel
  await handle({op: 'prepare', profile: A, kind: 'image', items: [{engine: 'b2'}]});
  const late = await handle({op: 'commit', profile: A, timeout_ms: 5});
  assert.deepEqual([late.code, late.submitted], ['TIMEOUT', true]);
  assert.equal((await handle({op: 'prepare'})).code, 'PROTOCOL');
  assert.equal((await handle({op: 'launch'})).code, 'PROTOCOL');
});

test('daemon: missing tab is reported with the open-profile command', async () => {
  const {handle} = daemonWith({connectResults: [fakeBrowser()], operations: {locateProfiles: async () => ({})}});
  await handle({op: 'reconnect'});
  const r = await handle({op: 'open', profile: {name: 'Profile 13', slug: 'profile-13'}});
  assert.equal(r.code, 'PROFILE_TAB_NOT_FOUND');
  assert.match(r.error, /open-profile "Profile 13"/);
});

test('endpoint comes from DevToolsActivePort in the user-data-dir (port + ws path)', () => {
  const dir = fs.mkdtempSync(path.join(tmp, 'udd-'));
  assert.throws(() => endpointFromDir(dir), e => e.code === 'NEEDS_ALLOW');
  fs.writeFileSync(path.join(dir, 'DevToolsActivePort'), '9222\n/devtools/browser/abc-123\n');
  assert.equal(endpointFromDir(dir), 'ws://127.0.0.1:9222/devtools/browser/abc-123');
  assert.throws(() => debugEndpoint('abc'), e => e.code === 'NO_CDP');
});

async function serveDashboard(runPython) {
  const handler = createDashboard({handle: async () => ({ok: true, connected: true}), runPython, html: () => '<h1>FlowPool</h1>'});
  const server = http.createServer(handler);
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  return {base, close: () => new Promise(r => server.close(r))};
}

test('dashboard API: state, media allow-list, pick and regenerate', async () => {
  const img = path.join(tmp, 'v1.png');
  fs.writeFileSync(img, Buffer.from('iVBORw0KGgo=', 'base64'));
  const calls = [];
  const key = 'ab'.repeat(32);
  const runPython = async args => {
    calls.push(args);
    if (args[0] === 'ui-state') return {status: {profiles: []}, queue: [], gallery: [{key, variants: [{index: 0, path: img}]}]};
    return {ok: true, next: 'python3 pilot.py reject j media --image SC01'};
  };
  const {base, close} = await serveDashboard(runPython);
  try {
    assert.match(await (await fetch(base + '/')).text(), /FlowPool/);
    const state = await (await fetch(base + '/api/state')).json();
    assert.equal(state.daemon.connected, true);
    assert.equal((await fetch(`${base}/media?key=${key}&i=0`)).status, 200);
    assert.equal((await fetch(`${base}/media?key=${key}&i=1`)).status, 404);
    assert.equal((await fetch(`${base}/media?key=../../etc&i=0`)).status, 404);
    const post = (url, body, type = 'application/json') => fetch(base + url, {method: 'POST', headers: {'content-type': type}, body: JSON.stringify(body)});
    assert.equal((await post('/api/pick', {key, index: 1})).status, 200);
    assert.deepEqual(calls.at(-1), ['decide', 'pick', key, '--index', '1']);
    await post('/api/regenerate', {key, note: 'rõ mặt hơn'});
    assert.deepEqual(calls.at(-1), ['decide', 'regenerate', key, '--note', 'rõ mặt hơn']);
    assert.equal((await post('/api/pick', {key: 'x; rm -rf /', index: 0})).status, 400);
    assert.equal((await post('/api/pick', {key, index: 0}, 'text/plain')).status, 415);
    assert.equal((await fetch(base + '/api/nope')).status, 404);
  } finally { await close(); }
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
