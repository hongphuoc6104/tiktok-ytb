import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {AttemptStore, attemptIdentity, canonicalJson} from './attempt-store.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const input = {
  topic: 'Một người cầm đèn',
  style: 'clean stick figure',
  ratio: '16:9',
  visibleText: ['Xin chào'],
  references: [{role: 'base', sha256: 'a'.repeat(64)}],
  toolRevision: 'experiment-1',
};

function tempStore() {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'vp-attempt-store-'));
  return {directory, store: new AttemptStore(directory)};
}

function cleanup(directory) {
  fs.rmSync(directory, {recursive: true, force: true});
}

function childCode(directory, request) {
  return `import {AttemptStore} from ${JSON.stringify(path.join(here, 'attempt-store.mjs'))};\n` +
    `const s=new AttemptStore(${JSON.stringify(directory)});\n` +
    `const r=s.prepare(${JSON.stringify(request)}); s.beginSubmission(r.identity);\n`;
}

function runChild(code) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['--input-type=module', '-e', code], {stdio: ['ignore', 'pipe', 'pipe']});
    let stderr = '';
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('exit', (codeValue, signal) => resolve({code: codeValue, signal, stderr}));
  });
}

test('canonical identity is key-order independent and Unicode stable', () => {
  assert.equal(canonicalJson({b: 1, a: 'e\u0301'}), canonicalJson({a: 'é', b: 1}));
  assert.equal(attemptIdentity({b: 1, a: 'e\u0301'}), attemptIdentity({a: 'é', b: 1}));
});

test('durable lifecycle persists mediaId through collection and acceptance', () => {
  const {directory, store} = tempStore();
  try {
    const prepared = store.prepare(input);
    assert.equal(prepared.state, 'prepared');
    const submitting = store.beginSubmission(prepared.identity, {requestId: 'req-1'});
    assert.equal(submitting.state, 'submitting');
    const generated = store.recordGenerated(prepared.identity, {mediaId: 'media-42', mimeType: 'image/png'});
    assert.equal(generated.state, 'generated');
    assert.equal(generated.mediaId, 'media-42');
    const collected = store.recordCollected(prepared.identity, {sha256: 'b'.repeat(64), width: 1920, height: 1080});
    assert.equal(collected.state, 'collected');
    const accepted = store.recordAccepted(prepared.identity, {review: 'pass'});
    assert.equal(accepted.state, 'accepted');
    assert.equal(accepted.mediaId, 'media-42');
    const lines = fs.readFileSync(path.join(directory, `${prepared.identity}.ndjson`), 'utf8').trim().split('\n').map(JSON.parse);
    assert.deepEqual(lines.map((line) => line.state), ['prepared', 'submitting', 'generated', 'collected', 'accepted']);
    assert.equal(lines[2].mediaId, 'media-42');
  } finally { cleanup(directory); }
});

test('prepare is idempotent and duplicate submit is rejected', () => {
  const {directory, store} = tempStore();
  try {
    const first = store.prepare(input);
    const second = store.prepare({...input});
    assert.equal(second.identity, first.identity);
    store.beginSubmission(first.identity);
    assert.throws(() => store.beginSubmission(first.identity), /Cannot transition submitting -> submitting/);
    assert.equal(store.read(first.identity).state, 'submitting');
  } finally { cleanup(directory); }
});

test('reload after interrupted submitting becomes unknown and cannot retry', async () => {
  const {directory} = tempStore();
  try {
    const result = await runChild(childCode(directory, input));
    assert.equal(result.code, 0, result.stderr);
    const reloaded = new AttemptStore(directory).load(input);
    assert.equal(reloaded.state, 'unknown');
    assert.throws(() => new AttemptStore(directory).beginSubmission(reloaded.identity), /UNKNOWN_SUBMISSION|Cannot transition unknown/);
    const events = fs.readFileSync(path.join(directory, `${reloaded.identity}.ndjson`), 'utf8').trim().split('\n').map(JSON.parse);
    assert.deepEqual(events.map((event) => event.state), ['prepared', 'submitting', 'unknown']);
  } finally { cleanup(directory); }
});

test('unknown outcome can be reconciled with mediaId without resubmission', () => {
  const {directory, store} = tempStore();
  try {
    const prepared = store.prepare(input);
    store.beginSubmission(prepared.identity);
    const unknown = store.load(prepared.identity);
    assert.equal(unknown.state, 'unknown');
    const generated = store.recordGenerated(prepared.identity, {mediaId: 'media-after-reload', reconciliationEvidence:'test fixture only'});
    assert.equal(generated.state, 'generated');
    assert.equal(generated.mediaId, 'media-after-reload');
    assert.throws(() => store.beginSubmission(prepared.identity), /Cannot transition generated/);
  } finally { cleanup(directory); }
});

test('download failure keeps generated state retryable and preserves mediaId', () => {
  const {directory, store} = tempStore();
  try {
    const prepared = store.prepare(input);
    store.beginSubmission(prepared.identity);
    store.recordGenerated(prepared.identity, 'media-download');
    store.recordCollectionFailure(prepared.identity, new Error('timeout'));
    assert.equal(store.load(prepared.identity).state, 'generated');
    assert.equal(store.load(prepared.identity).mediaId, 'media-download');
    assert.equal(store.recordCollected(prepared.identity, {path: 'asset.png'}).state, 'collected');
  } finally { cleanup(directory); }
});

test('concurrent writer is rejected while lock is held', async () => {
  const {directory, store} = tempStore();
  try {
    const prepared = store.prepare(input);
    const held = store.acquireWriterLock(prepared.identity);
    try {
      assert.throws(() => store.beginSubmission(prepared.identity), /ATTEMPT_LOCKED|already locked/);
    } finally { held.release(); }
    assert.equal(store.beginSubmission(prepared.identity).state, 'submitting');
  } finally { cleanup(directory); }
});

test('separate process cannot write through another process lock', async () => {
  const {directory, store} = tempStore();
  const ready = path.join(directory, 'lock-ready');
  try {
    const prepared = store.prepare(input);
    const code = `import fs from 'node:fs'; import {AttemptStore} from ${JSON.stringify(path.join(here, 'attempt-store.mjs'))};\n` +
      `const s=new AttemptStore(${JSON.stringify(directory)}); s.acquireWriterLock(${JSON.stringify(prepared.identity)}); fs.writeFileSync(${JSON.stringify(ready)}, 'ready'); setTimeout(()=>{}, 120);`;
    const child = spawn(process.execPath, ['--input-type=module', '-e', code], {stdio: 'ignore'});
    const deadline = Date.now() + 2000;
    while (!fs.existsSync(ready) && Date.now() < deadline) await new Promise((resolve) => setTimeout(resolve, 5));
    assert.equal(fs.existsSync(ready), true, 'child did not acquire lock');
    assert.throws(() => store.beginSubmission(prepared.identity), /ATTEMPT_LOCKED|already locked/);
    await new Promise((resolve) => child.once('exit', resolve));
    assert.throws(()=>store.beginSubmission(prepared.identity), /already locked/); // stale lock is never stolen
  } finally { cleanup(directory); }
});

test('withWriterLock serializes async writers', async () => {
  const {directory, store} = tempStore();
  try {
    const prepared = store.prepare(input);
    const order = [];
    const first = store.withWriterLock(prepared.identity, async () => {
      order.push('first-start');
      await new Promise((resolve) => setTimeout(resolve, 20));
      order.push('first-end');
    });
    await assert.rejects(store.withWriterLock(prepared.identity, async () => {}), /ATTEMPT_LOCKED|already locked/);
    await first;
    assert.deepEqual(order, ['first-start', 'first-end']);
  } finally { cleanup(directory); }
});

test('reserved metadata cannot reset submission state or overwrite sequence',()=>{
 const {directory,store}=tempStore();try {
  const r=store.prepare(input);
  const next=store.beginSubmission(r.identity,{state:'prepared',seq:99,event:'prepared'});
  assert.equal(next.state,'submitting');assert.equal(next.events.at(-1).seq,2);
  assert.equal(next.events.at(-1).event,'submitting');
  assert.throws(()=>store.beginSubmission(r.identity));
 }finally{cleanup(directory);}
});
test('scoped writer persists mediaId without reacquiring its own lock',async()=>{
 const {directory,store}=tempStore();try {
  const r=store.prepare(input);
  await store.withWriterLock(r.identity,async writer=>{
   writer.beginSubmission();
   assert.throws(()=>store.beginSubmission(r.identity),/already locked/);
   writer.recordGenerated({mediaId:'fixture-media'});
  });
  assert.equal(store.load(r.identity).mediaId,'fixture-media');
 }finally{cleanup(directory);}
});
test('unknown reconciliation requires evidence',()=>{
 const {directory,store}=tempStore();try {
  const r=store.prepare(input);store.beginSubmission(r.identity);store.load(r.identity);
  assert.throws(()=>store.recordGenerated(r.identity,'no-evidence'),/evidence required/);
 }finally{cleanup(directory);}
});
