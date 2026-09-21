import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {browserConfig,debugEndpoint,findToolFrame,validateRequest,identity,prepare,safeResults,assertCanSubmit} from './controller.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const input={topic:'A person',style:'Black lines',ratio:'16:9',visibleText:[],toolRevision:'test-only'};
test('Chrome consent connection uses local browser websocket',()=>assert.equal(debugEndpoint('9222\n/devtools/browser/abc-123\n'),'ws://127.0.0.1:9222/devtools/browser/abc-123'));
test('tool discovery ignores empty frame before actual app',async()=>{
 const blank={getByRole:()=>({isVisible:async()=>false})};
 const app={getByRole:()=>({isVisible:async()=>true})};
 const main={}; const page={mainFrame:()=>main,frames:()=>[main,blank,app]};
 assert.equal(await findToolFrame(page,100),app);
});
test('invalid endpoint cannot redirect connection',()=>{
 for(const value of ['0\n/devtools/browser/a','9222\nhttps://example.com','9222']) assert.throws(()=>debugEndpoint(value));
});
test('project profile default is Default, not flow_profile',()=>assert.equal(browserConfig({flow_profile:'video-pilot'}).profile,'Default'));
test('reject profile traversal',()=>assert.throws(()=>browserConfig({flow_profile_directory:'../x'})));
test('dependent image requires base file',()=>assert.throws(()=>validateRequest({...input,basedOn:'A1'})));
test('tool revision and ratio affect identity',()=>{
 const a=identity(validateRequest(input));
 assert.notEqual(a,identity(validateRequest({...input,toolRevision:'v2'})));
 assert.notEqual(a,identity(validateRequest({...input,ratio:'9:16'})));
});
test('outside output rejected',()=>assert.throws(()=>safeResults('/tmp/vp-controller-test')));
test('symlink output escape rejected',()=>{
 const p=path.join(here,'results','test-escape-'+process.pid);
 fs.symlinkSync('/tmp',p);
 try {assert.throws(()=>safeResults(path.join(p,'child')));} finally {fs.unlinkSync(p);}
});
test('prepare never overwrites unknown submission',()=>{
 const folder=path.join(here,'results','controller-test-'+process.pid);
 try {
  const r=prepare(input,folder);r.state='unknown';r.generationSubmitted=true;
  fs.writeFileSync(path.join(folder,r.key+'.json'),JSON.stringify(r));
  assert.equal(prepare(input,folder).state,'unknown');
  assert.throws(()=>assertCanSubmit(r),/never resubmit/);
 } finally {fs.rmSync(folder,{recursive:true,force:true});}
});
test('unaccepted submit stays locked',()=>assert.throws(()=>assertCanSubmit({state:'prepared',generationSubmitted:false}),/NOT_ACCEPTED/));

test('verified browser keeps the exact probe tab for later tool work',async()=>{
 const {verifyBrowser}=await import('./controller.mjs');
 let closed=false,created=0;
 const page={goto:async()=>{},locator:s=>({innerText:async()=>s==='#profile_path'?'/tmp/confirmed/Profile 10':'/opt/google/chrome/google-chrome'}),close:async()=>{closed=true;},isClosed:()=>closed};
 const browser={contexts:()=>[{newPage:async()=>{created++;return page;}}]};
 const binding=await verifyBrowser(browser,{flow_user_data_dir:'/tmp/confirmed',flow_profile_directory:'Profile 10'},true);
 assert.equal(binding.page,page);assert.equal(closed,false);assert.equal(created,1);
});
test('wrong profile closes untrusted probe even when retention requested',async()=>{
 const {verifyBrowser}=await import('./controller.mjs');let closed=false;
 const page={goto:async()=>{},locator:s=>({innerText:async()=>s==='#profile_path'?'/tmp/confirmed/Profile 102':'/opt/google/chrome/google-chrome'}),close:async()=>{closed=true;},isClosed:()=>closed};
 await assert.rejects(verifyBrowser({contexts:()=>[{newPage:async()=>page}]},{flow_user_data_dir:'/tmp/confirmed',flow_profile_directory:'Profile 10'},true),/PROFILE_PATH_MISMATCH/);
 assert.equal(closed,true);
});
test('new durable preparation cannot bypass an old unknown attempt',async()=>{
 const {durablePrepare}=await import('./controller.mjs');
 const folder=fs.mkdtempSync(path.join(here,'results','migration-test-'));
 try {
  const old=prepare(input,folder);old.state='unknown';old.generationSubmitted=true;
  fs.writeFileSync(path.join(folder,old.key+'.json'),JSON.stringify(old));
  assert.throws(()=>durablePrepare(input,folder),/LEGACY_ATTEMPT_REQUIRES_RECONCILIATION/);
 }finally{fs.rmSync(folder,{recursive:true,force:true});}
});
