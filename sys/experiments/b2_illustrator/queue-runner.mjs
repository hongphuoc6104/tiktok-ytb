/** Queue UI adapter. Local journal is authoritative; never resubmit an unknown attempt. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {AttemptStore} from './attempt-store.mjs';
import {findToolFrame, toolUrl, safeResults} from './controller.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function reference(file,mediaId) {
 if(!file)return null;
 if(!mediaId)throw Error('REFERENCE_MEDIA_ID_REQUIRED');
 const bytes=fs.readFileSync(file), ext=path.extname(file).toLowerCase();
 const mimeType={'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}[ext];
 if(!mimeType)throw Error('REFERENCE_FORMAT_UNSUPPORTED');
 return {mediaId,base64:bytes.toString('base64'),mimeType,name:path.basename(file),sha256:hash(bytes)};
}
export function prepareRequests(specs) {
 if(!Array.isArray(specs)||!specs.length||specs.length>4)throw Error('QUEUE_SIZE_1_TO_4_REQUIRED');
 if(new Set(specs.map(s=>s.testCase)).size!==specs.length)throw Error('DUPLICATE_REQUEST_ID');
 return specs.map(s=>{
  if(!/^[\w-]+$/.test(s.testCase)||!s.prompt||!['9:16','16:9'].includes(s.ratio))throw Error('INVALID_QUEUE_REQUEST');
  const character=reference(s.characterRefPath,s.charMediaId),base=reference(s.baseRefPath,s.baseMediaId);
  if(!character)throw Error('CHARACTER_REFERENCE_REQUIRED');
  return {spec:s,character,base,identity:{toolUrl,id:s.testCase,prompt:s.prompt,ratio:s.ratio,preserve:s.preserve||'',change:s.change||'',literalText:s.literalText||'',model:'Nano Banana Pro',references:[character,base].filter(Boolean).map(({mediaId,sha256})=>({mediaId,sha256})),outDir:path.resolve(s.outDir)}};
 });
}
export async function runQueue(specs,bound) {
 const requests=prepareRequests(specs),store=new AttemptStore(path.join(safeResults(),'production-attempts'));
 const attempts=requests.map(r=>store.prepare(r.identity));
 // Reuse fully downloaded results without interacting with Flow.
 if(attempts.every(a=>a.state==='collected'))return {items:attempts.map(a=>a.events.at(-1).collection)};
 if(attempts.every(a=>['generated','collected'].includes(a.state)))return collectResults(store,attempts,requests);
 if(attempts.some(a=>a.state!=='prepared'))throw Error('FLOW_RECONCILIATION_REQUIRED: existing attempt; no resubmission');
 const page=bound.page;
 if(!page.url().startsWith(toolUrl))throw Error('WRONG_TOOL_URL');
 const frame=await findToolFrame(page);
 const state=()=>frame.evaluate(()=>JSON.parse(localStorage.getItem('VP_LAB_STATE_V2')||'{}'));
 const initial=await state();
 if(initial.status==='UNKNOWN'||initial.queue?.some(i=>!['COMPLETED','ACCEPTED'].includes(i.status)))throw Error('UNRESOLVED_FLOW_QUEUE');
 const ids=[];
 for(const r of requests) {
  await frame.evaluate(({character,base})=>{
   const el=document.getElementById('character-selector');
   let f=el?.[Object.keys(el).find(k=>k.startsWith('__reactFiber$'))];
   while(f&&!(typeof f.type==='function'&&f.type.name==='App'))f=f.return;
   let h=f?.memoizedState;
   while(h&&!(h.memoizedState?.topic&&h.queue?.dispatch))h=h.next;
   if(!h?.next?.next?.queue?.dispatch)throw Error('REFERENCE_HOOK_NOT_FOUND');
   h.next.queue.dispatch(base);h.next.next.queue.dispatch(character);
  },r);
  await frame.getByRole('button',{name:'Clear Character',exact:true}).waitFor();
  const boxes=frame.getByRole('textbox');
  await boxes.nth(0).fill(r.spec.prompt);await boxes.nth(1).fill('Match the attached canonical character and scene references.');
  await boxes.nth(2).fill(r.spec.preserve||'');await boxes.nth(3).fill(r.spec.change||'');await boxes.nth(4).fill(r.spec.literalText||'');
  await frame.getByRole('button',{name:r.spec.ratio,exact:true}).click();
  await frame.getByRole('combobox').nth(2).selectOption({label:'🍌 Nano Banana Pro'});
  const before=await state();
  await frame.getByRole('button',{name:'Initialize Generation',exact:true}).click();
  const after=await state(),added=after.queue.filter(i=>!before.queue?.some(p=>p.id===i.id));
  if(added.length!==1||added[0].config.topic!==r.spec.prompt||added[0].characterRefMediaId!==r.character.mediaId||added[0].baseImageMediaId!==(r.base?.mediaId||null)||added[0].config.aspectRatio!==r.spec.ratio)throw Error('QUEUE_REFERENCE_MAPPING_FAILED');
  ids.push(added[0].id);
 }
 await frame.getByRole('combobox').nth(3).selectOption({label:`${requests.length===3?2:requests.length} Workers`});
 const queued=await state();
 if(queued.queue.filter(i=>i.status==='QUEUED').length!==ids.length)throw Error('UNEXPECTED_QUEUED_REQUEST');
 const shot=path.join(safeResults(),`queue-before-${Date.now()}.png`);
 await page.screenshot({path:shot});
 // Mark the entire group before Start. A crash anywhere makes retry conservative.
 for(let i=0;i<attempts.length;i++)store.beginSubmission(attempts[i],{queueId:ids[i],screenshot:shot});
 await frame.getByRole('button',{name:'Start Queue',exact:true}).click();
 const started=Date.now(),captured=new Set();
 while(Date.now()-started<180000) {
  const current=await state();
  for(let i=0;i<ids.length;i++) {
   const item=current.queue?.find(x=>x.id===ids[i]);
   if(!item)throw Error('QUEUE_DISAPPEARED_RECONCILE_NO_RESUBMIT');
   if(item.mediaId&&item.result?.base64&&!captured.has(i)) {
    store.recordGenerated(attempts[i],{mediaId:item.mediaId,result:item.result,queueId:item.id,timestamps:item.timestamps});captured.add(i);
   }
  }
  if(captured.size===ids.length)break;
  if(current.status==='UNKNOWN'||current.queue.some(i=>ids.includes(i.id)&&['UNKNOWN','FAILED'].includes(i.status)))throw Error('FLOW_RECONCILIATION_REQUIRED');
  await new Promise(resolve=>setTimeout(resolve,500));
 }
 if(captured.size!==ids.length)throw Error('FLOW_TIMEOUT_RECONCILE_NO_RESUBMIT');
 const afterShot=path.join(safeResults(),`queue-after-${Date.now()}.png`);await page.screenshot({path:afterShot});
 return collectResults(store,attempts,requests,afterShot,started);
}
function collectResults(store,attempts,requests,afterShot=null,started=null) {
 const items=[];
 for(let i=0;i<attempts.length;i++) {
  const a=store.read(attempts[i]);
  if(a.state==='collected'){items.push(a.events.at(-1).collection);continue;}
  const event=a.events.find(e=>e.event==='generated'),r=event.result;
  const submission=a.events.find(e=>e.event==='submitting');
  const shot=submission.screenshot;
  const ext={'image/png':'.png','image/jpeg':'.jpg','image/webp':'.webp'}[r.mimeType];
  if(!ext)throw Error('OUTPUT_FORMAT_UNSUPPORTED');
  const folder=path.resolve(requests[i].spec.outDir);fs.mkdirSync(folder,{recursive:true});
  const file=path.join(folder,`${a.identity}${ext}`);fs.writeFileSync(file,Buffer.from(r.base64,'base64'));
  const validation=JSON.parse(execFileSync('python3',[path.join(here,'validate_asset.py'),file,'--ratio',requests[i].spec.ratio],{encoding:'utf8'}));
  const result={path:file,forge_id:a.mediaId,media_id:a.mediaId,before_submit:shot,screenshot:afterShot||shot,technical_validation:validation,latency:started?(Date.now()-started)/1000:null,request_id:requests[i].spec.testCase};
  store.recordCollected(a,result);items.push(result);
 }
 return {items};
}
