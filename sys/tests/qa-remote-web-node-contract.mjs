// Independent real Node contract execution against a fake UI; no browser/Flow.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=process.argv[2],dir=path.join(root,'sys/experiments/b2_illustrator');
const {prepareRequests,runQueue}=await import(pathToFileURL(path.join(dir,'queue-runner.mjs')));
const cfg=JSON.parse(fs.readFileSync(path.join(root,'sys/config.json')));
const ref=path.join(root,'reference.png');fs.writeFileSync(ref,'QA SYNTHETIC reference bytes');
const spec={testCase:'QA_FROZEN_NODE',prompt:'QA synthetic prompt',ratio:'9:16',outDir:path.join(root,'outputs'),characterRefPath:ref,charMediaId:'QA_REFERENCE_ID',managementContract:1,model:'Nano Banana Pro',project:'QA-FROZEN-PROJECT',toolUrl:cfg.flow_tool_url};
assert.equal(prepareRequests([spec])[0].identity.model,'Nano Banana Pro');
assert.equal(prepareRequests([spec])[0].identity.project,'QA-FROZEN-PROJECT');
assert.throws(()=>prepareRequests([{...spec,toolUrl:'https://flow.google.com/project/WRONG'}]),/CONTRACT/);
assert.throws(()=>prepareRequests([{...spec,model:null}]),/CONTRACT/);
const fakeUI=({ignoreModel=false}={})=>{
 const trace={starts:0,initialize:0,models:[]},state={status:'IDLE',queue:[]};
 let topic='',ratio='',refs={},selected='QA WRONG GLOBAL MODEL';
 const frame={
  evaluate:async(fn,arg)=>{if(arg){refs=arg;return;}return structuredClone(state);},
  getByRole:(role,options={})=>({
   isVisible:async()=>true,waitFor:async()=>{},
   click:async()=>{if(options.name==='Initialize Generation'){trace.initialize++;state.queue.push({id:'qa-queue-'+trace.initialize,status:'QUEUED',config:{topic,aspectRatio:ratio},characterRefMediaId:refs.character.mediaId,baseImageMediaId:refs.base?.mediaId||null});}else if(options.name==='Start Queue'){trace.starts++;throw Error('QA_STOP_AT_PROVIDER_SEND_BOUNDARY');}else if(['9:16','16:9'].includes(options.name))ratio=options.name;},
   nth:n=>({fill:async value=>{if(role==='textbox'&&n===0)topic=value;},selectOption:async option=>{if(n===2){trace.models.push(option.label);if(!ignoreModel)selected=option.label;}},locator:()=>({innerText:async()=>selected})})
  })
 };
 return {trace,bound:{page:{url:()=>cfg.flow_tool_url,frames:()=>[frame],mainFrame:()=>null}}};
};
const normal=fakeUI();
const first=await runQueue([spec],normal.bound);
assert.equal(first.status,'blocked');assert.equal(first.reason,'QA_STOP_AT_PROVIDER_SEND_BOUNDARY');
assert.equal(normal.trace.starts,1);assert.deepEqual(normal.trace.models,['🍌 Nano Banana Pro']);
assert.equal(first.generationSubmitted,true);
const replay=await runQueue([spec],normal.bound);
assert.equal(replay.status,'blocked');assert.match(replay.reason,/RECONCILIATION/);assert.equal(normal.trace.starts,1);
const ignored=fakeUI({ignoreModel:true});
const mismatch=await runQueue([{...spec,testCase:'QA_MODEL_IGNORED'}],ignored.bound);
assert.equal(mismatch.status,'blocked');assert.equal(mismatch.reason,'FROZEN_FLOW_MODEL_MISMATCH');
assert.equal(mismatch.generationSubmitted,false);assert.equal(ignored.trace.starts,0);
console.log(JSON.stringify({fixture:true,live_provider:false,actual_node:true,frozen_model_selected:true,frozen_project_identity:true,wrong_url_rejected:true,ignored_model_blocks_before_start:true,unknown_no_duplicate_start:true,provider_start_simulated:true}));
