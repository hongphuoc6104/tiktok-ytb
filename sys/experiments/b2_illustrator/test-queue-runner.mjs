import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {prepareRequests} from './queue-runner.mjs';
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'vp-queue-'));
const file=path.join(dir,'ref.png');fs.writeFileSync(file,'reference');
const request={testCase:'scene-1',prompt:'Borrow a book',ratio:'9:16',outDir:dir,characterRefPath:file,charMediaId:'mascot-id'};
test('reference content and media identity are captured',()=>{
 const [r]=prepareRequests([request]);assert.equal(r.character.mediaId,'mascot-id');assert.equal(r.identity.references.length,1);assert.equal(r.identity.references[0].sha256.length,64);
});
test('missing base media ID blocks before browser operations',()=>assert.throws(()=>prepareRequests([{...request,baseRefPath:file}]),/MEDIA_ID/));
test('duplicate scene IDs and oversized batches are rejected',()=>{
 assert.throws(()=>prepareRequests([request,request]),/DUPLICATE/);
 assert.throws(()=>prepareRequests(Array(5).fill(request)),/SIZE/);
});
test('ratio and character reference are required',()=>{
 assert.throws(()=>prepareRequests([{...request,ratio:'1:1'}]),/INVALID/);
 assert.throws(()=>prepareRequests([{...request,characterRefPath:null}]),/CHARACTER/);
});
test.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
