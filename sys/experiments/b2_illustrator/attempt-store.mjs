/**
 * Durable, local attempt journal for the isolated B-2 experiment.
 *
 * The caller must append `submitting` and wait for this method to return
 * before making the external generation call.  A durable `submitting` event
 * means that the outcome may have reached the service; on reload it is
 * therefore recovered as `unknown` and can never be submitted again.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export const STATES = Object.freeze([
  'prepared',
  'submitting',
  'unknown',
  'generated',
  'collected',
  'accepted',
]);

const TERMINAL_STATES = new Set(['accepted']);
const STATE_EVENTS = new Set(STATES);

function fail(message, code = 'ATTEMPT_STORE_ERROR') {
  const error = new Error(message);
  error.code = code;
  return error;
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/** Return a stable JSON-safe value with object keys sorted recursively. */
export function canonicalize(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') {
    return typeof value === 'string' ? value.normalize('NFC') : value;
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) throw fail('Identity input contains a non-finite number', 'INVALID_IDENTITY_INPUT');
    return value;
  }
  if (Array.isArray(value)) return value.map(canonicalize);
  if (isPlainObject(value)) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [
      key.normalize('NFC'),
      canonicalize(value[key]),
    ]));
  }
  throw fail(`Identity input contains unsupported value: ${typeof value}`, 'INVALID_IDENTITY_INPUT');
}

export function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

/** The identity covers the complete request, including reference identities. */
export function attemptIdentity(request) {
  return crypto.createHash('sha256').update(canonicalJson(request), 'utf8').digest('hex');
}

export const identity = attemptIdentity;

function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class AttemptStore {
  constructor(directory, {lockTimeoutMs = 0} = {}) {
    if (typeof directory !== 'string' || !directory) throw fail('Attempt store directory required');
    this.directory = path.resolve(directory);
    this.lockTimeoutMs = lockTimeoutMs;
    fs.mkdirSync(this.directory, {recursive: true});
    this._fsyncDirectory();
  }

  _fsyncDirectory() {
    let fd;
    try {
      fd = fs.openSync(this.directory, 'r');
      fs.fsyncSync(fd);
    } catch (error) {
      // Some filesystems do not allow fsync on a directory. File data remains
      // fsynced; the limitation is surfaced only when even opening fails.
      if (!['EINVAL', 'ENOTSUP', 'EBADF'].includes(error.code)) throw error;
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }
  }

  _paths(identityValue) {
    if (!/^[a-f0-9]{64}$/.test(identityValue)) throw fail('Invalid attempt identity', 'INVALID_IDENTITY');
    return {
      log: path.join(this.directory, `${identityValue}.ndjson`),
      lock: path.join(this.directory, `${identityValue}.lock`),
    };
  }

  _identity(input) {
    if (typeof input === 'string') return input;
    if (input && typeof input.identity === 'string') return input.identity;
    if (input && typeof input.key === 'string') return input.key;
    if (!input || typeof input !== 'object') throw fail('Attempt identity or request required');
    return attemptIdentity(input);
  }

  _acquire(identityValue) {
    const {lock} = this._paths(identityValue);
    const started = Date.now();
    let fd;
    while (true) {
      try {
        fd = fs.openSync(lock, 'wx', 0o600);
        fs.writeSync(fd, `${process.pid}\n`);
        fs.fsyncSync(fd);
        this._fsyncDirectory();
        return {fd, lock, release: () => this._release({fd, lock})};
      } catch (error) {
        if (fd !== undefined) {
          try { fs.closeSync(fd); } catch {}
          fd = undefined;
        }
        if (error.code !== 'EEXIST') throw error;
        if (this.lockTimeoutMs <= 0 || Date.now() - started >= this.lockTimeoutMs) {
          throw fail(`Attempt ${identityValue} is already locked`, 'ATTEMPT_LOCKED');
        }
        // This path is intentionally synchronous: state transitions are
        // short and keeping one writer makes append ordering deterministic.
        const until = Math.min(10, this.lockTimeoutMs - (Date.now() - started));
        if (until > 0) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, until);
      }
    }
  }

  _release(handle) {
    if (!handle) return;
    try { fs.closeSync(handle.fd); } catch {}
    try { fs.unlinkSync(handle.lock); } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
    this._fsyncDirectory();
  }

  /** Run a callback while holding this attempt's exclusive writer lock. */
  async withWriterLock(input, callback) {
    const identityValue = this._identity(input);
    const handle = this._acquire(identityValue);
    try {
      return await callback({
        beginSubmission: (metadata={})=>this._transition(identityValue,'submitting',metadata,true),
        recordGenerated: (result)=>this._transition(identityValue,'generated',typeof result==='string'?{mediaId:result}:result,true),
        read: ()=>this._loadRaw(identityValue),
      });
    } finally {
      this._release(handle);
    }
  }

  acquireWriterLock(input) {
    return this._acquire(this._identity(input));
  }

  _append(identityValue, event, payload = {}) {
    const {log} = this._paths(identityValue);
    const events = this._readEvents(identityValue, {allowMissing: true});
    const clean=clone(payload);
    for(const key of ['schema','identity','seq','at','event'])delete clean[key];
    const entry = {
      ...clean,
      schema: 'vp-attempt-event-1',
      identity: identityValue,
      seq: events.length + 1,
      at: new Date().toISOString(),
      event,
      state: payload.state || event,
    };
    delete entry.identity;
    // Reinsert identity after spread so payload cannot spoof it.
    entry.identity = identityValue;
    const line = JSON.stringify(entry) + '\n';
    const fd = fs.openSync(log, 'a', 0o600);
    try {
      fs.writeFileSync(fd, line, 'utf8');
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    this._fsyncDirectory();
    return entry;
  }

  _readEvents(identityValue, {allowMissing = false} = {}) {
    const {log} = this._paths(identityValue);
    if (!fs.existsSync(log)) {
      if (allowMissing) return [];
      throw fail(`Attempt ${identityValue} does not exist`, 'ATTEMPT_NOT_FOUND');
    }
    const text = fs.readFileSync(log, 'utf8');
    if(text && !text.endsWith('\n'))throw fail('Truncated attempt log', 'CORRUPT_ATTEMPT_LOG');
    const lines = text.split('\n');
    if (lines.at(-1) === '') lines.pop();
    const events = [];
    for (let index = 0; index < lines.length; index += 1) {
      let event;
      try { event = JSON.parse(lines[index]); } catch {
        throw fail(`Corrupt attempt log at line ${index + 1}`, 'CORRUPT_ATTEMPT_LOG');
      }
      if (!event || event.identity !== identityValue || event.seq !== index + 1 || !STATE_EVENTS.has(event.state)) {
        throw fail(`Invalid attempt log at line ${index + 1}`, 'CORRUPT_ATTEMPT_LOG');
      }
      events.push(event);
    }
    return events;
  }

  _snapshot(identityValue, events) {
    if (!events.length) throw fail(`Attempt ${identityValue} does not exist`, 'ATTEMPT_NOT_FOUND');
    const last = events.at(-1);
    const prepared = events.find((event) => event.event === 'prepared');
    const generated = [...events].reverse().find((event) => event.event === 'generated');
    return {
      schema: 'vp-attempt-1',
      identity: identityValue,
      key: identityValue,
      state: last.state,
      request: clone(prepared?.request),
      mediaId: generated?.mediaId ?? null,
      generationSubmitted: events.some((event) => ['submitting', 'unknown', 'generated', 'collected', 'accepted'].includes(event.state)),
      createdAt: events[0].at,
      updatedAt: last.at,
      events: clone(events),
    };
  }

  _loadRaw(input) {
    const identityValue = this._identity(input);
    return this._snapshot(identityValue, this._readEvents(identityValue));
  }

  /** Read and recover an attempt. A durable submitting event becomes unknown. */
  load(input, {recover = true} = {}) {
    const identityValue = this._identity(input);
    let snapshot = this._loadRaw(identityValue);
    if (recover && snapshot.state === 'submitting') {
      const handle = this._acquire(identityValue);
      try {
        snapshot = this._loadRaw(identityValue);
        if (snapshot.state === 'submitting') {
          this._append(identityValue, 'unknown', {
            state: 'unknown',
            reason: 'interrupted-submission',
          });
          snapshot = this._loadRaw(identityValue);
        }
      } finally {
        this._release(handle);
      }
    }
    return snapshot;
  }

  read(input) {
    return this._loadRaw(input);
  }

  status(input) {
    return this.load(input);
  }

  prepare(request) {
    const identityValue = attemptIdentity(request);
    const {log} = this._paths(identityValue);
    if (fs.existsSync(log)) return this.load(identityValue);
    const handle = this._acquire(identityValue);
    try {
      if (!fs.existsSync(log)) {
        this._append(identityValue, 'prepared', {state: 'prepared', request: clone(canonicalize(request))});
      }
      return this._loadRaw(identityValue);
    } finally {
      this._release(handle);
    }
  }

  _transition(input, target, payload = {}, owned = false) {
    const identityValue = this._identity(input);
    if (!STATE_EVENTS.has(target)) throw fail(`Invalid target state: ${target}`);
    const handle = owned ? null : this._acquire(identityValue);
    try {
      const current = this._loadRaw(identityValue);
      const from = current.state;
      const allowed = {
        submitting: new Set(['prepared']),
        unknown: new Set(['submitting']),
        generated: new Set(['submitting', 'unknown']),
        collected: new Set(['generated']),
        accepted: new Set(['collected']),
      };
      if (!allowed[target]?.has(from)) {
        if (target === 'generated' && from === 'generated' && payload.mediaId === current.mediaId) return current;
        if (target === 'collected' && from === 'collected') return current;
        if (target === 'accepted' && from === 'accepted') return current;
        throw fail(`Cannot transition ${from} -> ${target}`, from === 'unknown' ? 'UNKNOWN_SUBMISSION' : 'INVALID_TRANSITION');
      }
      if(target==='generated' && from==='unknown' && !payload.reconciliationEvidence)throw fail('Reconciliation evidence required','EVIDENCE_REQUIRED');
      if (target === 'generated') {
        if (typeof payload.mediaId !== 'string' || !payload.mediaId.trim()) throw fail('mediaId required for generated state', 'MEDIA_ID_REQUIRED');
        if (current.mediaId && current.mediaId !== payload.mediaId) throw fail('mediaId cannot change', 'MEDIA_ID_MISMATCH');
      }
      this._append(identityValue, target, {...clone(payload), state: target});
      return this._loadRaw(identityValue);
    } finally {
      this._release(handle);
    }
  }

  beginSubmission(input, metadata = {}) { return this._transition(input, 'submitting', metadata); }
  markSubmitting(input, metadata = {}) { return this.beginSubmission(input, metadata); }
  recordGenerated(input, result) {
    const mediaId = typeof result === 'string' ? result : result?.mediaId;
    return this._transition(input, 'generated', {mediaId, ...(isPlainObject(result) ? result : {})});
  }
  markGenerated(input, result) { return this.recordGenerated(input, result); }
  recordCollected(input, metadata = {}) { return this._transition(input, 'collected', {collection: clone(metadata)}); }
  markCollected(input, metadata = {}) { return this.recordCollected(input, metadata); }
  recordAccepted(input, metadata = {}) { return this._transition(input, 'accepted', {acceptance: clone(metadata)}); }
  markAccepted(input, metadata = {}) { return this.recordAccepted(input, metadata); }

  /** A failed download leaves the generated attempt retryable. */
  recordCollectionFailure(input, error) {
    const identityValue = this._identity(input);
    const handle = this._acquire(identityValue);
    try {
      const current = this._loadRaw(identityValue);
      if (current.state !== 'generated') throw fail(`Cannot retry collection from ${current.state}`, 'INVALID_COLLECTION_RETRY');
      this._append(identityValue, 'collection_failed', {
        state: 'generated',
        mediaId: current.mediaId,
        error: String(error?.message || error || 'collection failed'),
      });
      return this._loadRaw(identityValue);
    } finally {
      this._release(handle);
    }
  }
}

export function createAttemptStore(directory, options) {
  return new AttemptStore(directory, options);
}

