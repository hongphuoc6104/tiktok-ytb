// Independent browser QA: tiny generated fixture media, no provider/login/GPU.
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.VP_PLAYWRIGHT_MODULE);
const [url,expectedMode,expectedRevision]=process.argv.slice(2);
const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
try {
 const page=await browser.newPage({viewport:{width:1240,height:960}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url);await page.getByText(/Đã đọc dữ liệu/).waitFor();
 const state=await page.evaluate(async()=>await (await fetch('/api/state')).json());
 const job=state.jobs[0];
 if(job.state.mode!==expectedMode)throw Error('Wrong mode '+job.state.mode);
 const audio=job.checkpoints.find(c=>c.phase==='audio');
 if(audio.revision!==Number(expectedRevision))throw Error('Wrong artifact revision');
 const tabs=page.locator('nav button');if(await tabs.count()!==8)throw Error('Wrong tabs');
 const checks=[];
 for(let i=0;i<8;i++) {
  await tabs.nth(i).click();const title=await page.locator('#title').textContent();
  const body=await page.locator('#content').textContent();if(!title||!body.trim())throw Error('Empty tab '+i);
  checks.push({title,characters:body.length});
 }
 await tabs.nth(4).click();
 if(!(await page.locator('#content').textContent()).includes('bản '+expectedRevision))throw Error('Revision missing on Media');
 await page.locator('audio').first().evaluate(async a=>{if(a.readyState<1)await new Promise((ok,no)=>{a.addEventListener('loadedmetadata',ok,{once:true});a.addEventListener('error',()=>no(Error('WAV failed')),{once:true});});if(a.duration!==1)throw Error('Actual WAV duration wrong');});
 await page.locator('img').first().evaluate(async image=>{await image.decode();if(image.naturalWidth!==1)throw Error('Fixture PNG wrong');});
 await tabs.nth(5).click();
 await page.locator('video').first().evaluate(async v=>{if(v.readyState<1)await new Promise((ok,no)=>{v.addEventListener('loadedmetadata',ok,{once:true});v.addEventListener('error',()=>no(Error('Fixture MP4 failed')),{once:true});});if(!Number.isFinite(v.duration)||v.duration<.9||v.duration>1.1)throw Error('MP4 metadata wrong');});
 await page.locator('video').first().evaluate(async v=>{v.muted=true;await v.play();await new Promise(ok=>v.requestVideoFrameCallback(ok));v.pause();if(v.videoWidth!==64||v.videoHeight!==96)throw Error('Fixture MP4 did not decode');});
 if(await page.locator('button',{hasText:'Duyệt đúng revision'}).count()!== (expectedMode==='review'?1:0))throw Error('Wrong mode controls');
 const stale=await page.evaluate(async csrf=> {const r=await fetch('/api/actions/approve',{method:'POST',headers:{'Content-Type':'application/json','X-VP-CSRF':csrf},body:JSON.stringify({job:'qa-browser-job',phase:'video',revision:999,note:'QA synthetic stale feedback'})});return {status:r.status,body:await r.json()};},state.csrf);
 if(stale.status===200&&!stale.body.blocked)throw Error('Stale decision succeeded');
 if(errors.length)throw Error(errors.join(';'));
 if(process.env.VP_QA_SCREENSHOT_DIR)await page.screenshot({path:process.env.VP_QA_SCREENSHOT_DIR+'/qa-remote-web-'+expectedMode+'-'+expectedRevision+'.png',fullPage:true});
 console.log(JSON.stringify({fixture:true,mode:expectedMode,revision:Number(expectedRevision),tabs:checks,wav_duration:1,png_decode:true,mp4_metadata:true,mp4_decode:true,stale_feedback_blocked:true,page_errors:errors}));
} finally {await browser.close();}
