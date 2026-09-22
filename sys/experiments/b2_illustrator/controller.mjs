/** Isolated project-CDP controller. No browser launch or Codex extension. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {AttemptStore} from './attempt-store.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const localFile=path.join(here,'machine.local.json');
export const machineConfig=fs.existsSync(localFile)?JSON.parse(fs.readFileSync(localFile,'utf8')):{};
export const toolUrl=machineConfig.tool_url || 'https://flow.google.com/project/41d3d574-907c-4bb0-90a7-c98f85f5e22b/tool/2791e8ba-9ae0-4ca9-9368-b7efe600c53d';
export function browserConfig(config) {
  config={...config,...machineConfig};
  const dataDir=path.resolve(root,config.flow_user_data_dir || `.gflow/profiles/${config.flow_profile || 'video-pilot'}`);
  const profile=config.flow_profile_directory || 'Default';
  if(path.basename(profile)!==profile || profile==='.' || profile==='..') throw Error('Invalid profile directory');
  return {dataDir,profile,expectedProfilePath:path.join(dataDir,profile)};
}
export function debugEndpoint(contents) {
  const [rawPort, rawPath]=contents.trim().split(/\r?\n/);
  const port=Number(rawPort);
  if(!Number.isInteger(port)||port<1||port>65535) throw Error('Invalid project debugging port');
  if(!rawPath || !/^\/devtools\/browser\/[a-zA-Z0-9-]+$/.test(rawPath.trim())) throw Error('Invalid browser WebSocket path');
  return `ws://127.0.0.1:${port}${rawPath.trim()}`;
}
export async function findToolFrame(page,timeoutMs=20000) {
  const deadline=Date.now()+timeoutMs;
  while(Date.now()<deadline) {
    for(const frame of page.frames()) {
      if(frame===page.mainFrame()) continue;
      try {
        if(await frame.getByRole('heading',{name:'VP Stickman Lab',exact:true}).isVisible()
          && await frame.getByRole('button',{name:/Initialize Generation/}).isVisible()) return frame;
      } catch {}
    }
    await new Promise(resolve=>setTimeout(resolve,250));
  }
  throw Error('APP_FRAME_NOT_READY');
}
export function validateRequest(input) {
  if(!input || typeof input!=='object') throw Error('Request object required');
  if(!['9:16','16:9'].includes(input.ratio)) throw Error('Unsupported ratio');
  for(const k of ['topic','style','toolRevision']) if(typeof input[k]!=='string' || !input[k].trim()) throw Error(`${k} required`);
  if(!Array.isArray(input.visibleText) || input.visibleText.some(t=>typeof t!=='string')) throw Error('visibleText array required');
  const references=(input.references || []).map(ref=>{
    if(!['base','character'].includes(ref.role)) throw Error('Invalid reference role');
    const file=path.resolve(ref.path);
    return {role:ref.role,path:file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')};
  });
  if(new Set(references.map(r=>r.role)).size!==references.length) throw Error('Duplicate reference role');
  if(input.basedOn && !references.some(r=>r.role==='base')) throw Error('Dependent image requires real base reference');
  return {toolUrl,toolRevision:input.toolRevision,topic:input.topic,style:input.style,ratio:input.ratio,
    visibleText:input.visibleText,preserve:input.preserve || '',change:input.change || '',
    textStyle:input.textStyle || {},basedOn:input.basedOn || null,references};
}
export function identity(request) {
  const portable={...request,references:request.references.map(({role,sha256})=>({role,sha256}))};
  return crypto.createHash('sha256').update(JSON.stringify(portable)).digest('hex');
}
export function safeResults(base=path.join(here,'results','controller')) {
  const allowed=fs.realpathSync(path.join(here,'results'));
  const target=path.resolve(base);
  if(!target.startsWith(allowed+path.sep)) throw Error('Output outside experiment');
  let ancestor=target;
  while(!fs.existsSync(ancestor)) ancestor=path.dirname(ancestor);
  const real=fs.realpathSync(ancestor);
  if(real!==allowed && !real.startsWith(allowed+path.sep)) throw Error('Output symlink escapes experiment');
  fs.mkdirSync(target,{recursive:true});
  if(!fs.realpathSync(target).startsWith(allowed+path.sep)) throw Error('Output escapes experiment');
  return target;
}
export function prepare(input,base) {
  const request=validateRequest(input), key=identity(request), folder=safeResults(base);
  const destination=path.join(folder,key+'.json');
  const record={schema:'vp-tool-attempt-1',key,state:'prepared',createdAt:new Date().toISOString(),request,
    generationSubmitted:false,chargedCredits:null};
  try {fs.writeFileSync(destination,JSON.stringify(record,null,2)+'\n',{flag:'wx'});}
  catch(e) {if(e.code!=='EEXIST') throw e; return JSON.parse(fs.readFileSync(destination));}
  return record;
}
export function durablePrepare(input,base) {
  const request=validateRequest(input), folder=safeResults(base);
  // Do not let a new journal implementation bypass an older uncertain attempt.
  const legacy=path.join(folder,identity(request)+'.json');
  if(fs.existsSync(legacy)) {
    const record=JSON.parse(fs.readFileSync(legacy));
    if(record.state!=='prepared' || record.generationSubmitted)throw Error('LEGACY_ATTEMPT_REQUIRES_RECONCILIATION');
  }
  const portable={...request,references:request.references.map(({role,sha256})=>({role,sha256}))};
  return new AttemptStore(path.join(folder,'attempts-v2')).prepare(portable);
}
export function assertCanSubmit(record) {
  if(record.state!=='prepared' || record.generationSubmitted) throw Error('Reconcile existing request; never resubmit');
  // Disabled until real account/cost, iframe uploads and output capture are accepted.
  throw Error('LIVE_SUBMIT_NOT_ACCEPTED: inspect and verify tool input/output contract first');
}
export async function verifyBrowser(browser, config, keepPage=false) {
  const selected=browserConfig(config);
  const context=browser.contexts()[0];
  if(!context) throw Error('NO_CHROME_CONTEXT');
  const probe=await context.newPage();
  try {
    await probe.goto('chrome://version',{timeout:8000});
    const observedProfile=(await probe.locator('#profile_path').innerText()).trim();
    const executable=(await probe.locator('#executable_path').innerText()).trim();
    if(path.resolve(observedProfile)!==selected.expectedProfilePath) throw Error('PROFILE_PATH_MISMATCH');
    if(executable!==(config.executable_path || '/opt/google/chrome/google-chrome')) throw Error('EXECUTABLE_PATH_MISMATCH');
    const identity={observedProfile,executable,verifiedAt:new Date().toISOString()};
    if(keepPage) return {identity,page:probe};
    return identity;
  } catch(e) {await probe.close();throw e;} finally {if(!keepPage && !probe.isClosed())await probe.close();}
}
export async function inspect(config, sharedBrowser=null, bound=null) {
  const selected=browserConfig(config);
  const file=path.join(selected.dataDir,'DevToolsActivePort');
  if(!fs.existsSync(file)) return {status:'blocked',reason:'PROJECT_CHROME_CDP_UNAVAILABLE',...selected,generationSubmitted:false};
  const endpoint=debugEndpoint(fs.readFileSync(file,'utf8'));
  let browser, probe;
  try {
    browser=sharedBrowser || await chromium.connectOverCDP(endpoint,{timeout:20000});
    const context=browser.contexts()[0];
    if(!context) throw Error('No existing Chrome context');
    probe=bound?.page || await context.newPage();
    if(probe.isClosed())throw Error('BOUND_TAB_CLOSED');
    if(!bound) await probe.goto('chrome://version',{timeout:8000});
    const observedProfile=bound?.identity.observedProfile || (await probe.locator('#profile_path').innerText()).trim();
    const executable=bound?.identity.executable || (await probe.locator('#executable_path').innerText()).trim();
    if(path.resolve(observedProfile)!==selected.expectedProfilePath) return {status:'blocked',reason:'PROFILE_PATH_MISMATCH',...selected,observedProfile,executable,generationSubmitted:false};
    if(executable!==(config.executable_path || '/opt/google/chrome/google-chrome')) return {status:'blocked',reason:'GOOGLE_CHROME_REQUIRED',executable,generationSubmitted:false};
    if(['chrome://version','chrome://version/'].includes(probe.url())) await probe.goto(toolUrl,{waitUntil:'domcontentloaded',timeout:20000});
    else if(probe.url()!==toolUrl) {
      if (probe.url().startsWith('https://flow.google.com/project/')) {
        await probe.goto(toolUrl, { waitUntil: 'domcontentloaded', timeout: 20000 });
      } else {
        throw Error('BOUND_TAB_NAVIGATED: refusing to discard tool state');
      }
    }
    let readinessError=null;
    try {
      await probe.getByText('VP Stickman Lab',{exact:true}).first().waitFor({state:'visible',timeout:30000});
      await probe.waitForFunction(()=>document.querySelectorAll('iframe').length>0,{},{timeout:20000});
    } catch(e) {readinessError=e.message;}
    try {await findToolFrame(probe);} catch(e) {readinessError=e.message;}
    const snapshot=await probe.locator('body').ariaSnapshot({timeout:10000});
    const frames=[];
    for(const frame of probe.frames().filter(f=>f!==probe.mainFrame())) {
      try {frames.push({url:frame.url(),snapshot:await frame.locator('body').ariaSnapshot({timeout:3000})});} catch {}
    }
    const folder=safeResults();
    const screenshot=path.join(folder,`inspect-${Date.now()}.png`);
    await probe.screenshot({path:screenshot});
    return {status:!readinessError && probe.url().startsWith(toolUrl)?'inspected':'blocked',reason:readinessError || (probe.url().startsWith(toolUrl)?null:'TOOL_NOT_REACHED'),
      observedAt:new Date().toISOString(),...selected,observedProfile,executable,url:probe.url(),snapshot,frames,screenshot,
      accountVerified:false,costVerified:false,generationSubmitted:false};
  } finally {if(probe && !bound) await probe.close().catch(()=>{}); if(browser && !sharedBrowser) await browser.close();}
}
async function main() {
  const [command,arg]=process.argv.slice(2);
  if(command==='durable-prepare') console.log(JSON.stringify(durablePrepare(JSON.parse(fs.readFileSync(arg))),null,2));
  else if(command==='prepare') console.log(JSON.stringify(prepare(JSON.parse(fs.readFileSync(arg))),null,2));
  else if(command==='inspect') {
    let result;
    try {
      const config=JSON.parse(fs.readFileSync(path.join(root,'config.json')));
      const confirmed=JSON.parse(fs.readFileSync(path.join(here,'browser-profiles.json')));
      result=await inspect({...config,...confirmed});
    }
    catch(e) {result={status:'blocked',reason:e.message,generationSubmitted:false};}
    fs.writeFileSync(path.join(safeResults(),`inspect-${Date.now()}.json`),JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify(result,null,2)); if(result.status==='blocked') process.exitCode=2;
  } else if(command==='status') {
    const folder=safeResults();console.log(JSON.stringify(fs.readdirSync(folder).filter(x=>/^[a-f0-9]{64}\.json$/.test(x)).map(x=>{
      const r=JSON.parse(fs.readFileSync(path.join(folder,x)));return {key:r.key,state:r.state,generationSubmitted:r.generationSubmitted};
    }),null,2));
  } else if(command==='submit') throw Error('LIVE_SUBMIT_NOT_ACCEPTED: no image submitted');
  else throw Error('Usage: node controller.mjs inspect | prepare REQUEST.json | status');
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) main().catch(e=>{console.error(e.message);process.exitCode=2;});
