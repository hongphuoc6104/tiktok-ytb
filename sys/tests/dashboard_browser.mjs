// Browser fixture verification only; no provider/profile or production artifact.
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.VP_PLAYWRIGHT_MODULE||'playwright');
const browser=await chromium.launch({headless:true,executablePath:process.env.VP_CHROME_PATH||'/usr/bin/google-chrome',args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.argv[2]);
 await page.getByText(/Đã đọc dữ liệu/).waitFor();
 const tabs=page.locator('nav button');
 if(await tabs.count()!==8)throw Error('Expected eight actual tabs');
 const checks=[];
 for(let i=0;i<8;i++){
  await tabs.nth(i).click();
  const title=await page.locator('#title').textContent();
  if(!title||await page.locator('#content').textContent()==='')throw Error('Empty tab '+i);
  checks.push(title);
 }
 await tabs.nth(4).click();
 if(await page.locator('audio').count()<1||await page.locator('img').count()<1)throw Error('Actual manifest media missing');
 await page.locator('audio').first().evaluate(async a=>{if(a.readyState<1)await new Promise((resolve,reject)=>{a.addEventListener('loadedmetadata',resolve,{once:true});a.addEventListener('error',()=>reject(Error('WAV not readable')),{once:true});});if(!Number.isFinite(a.duration)||a.duration<=0)throw Error('No actual WAV duration');});
 await page.locator('img').first().evaluate(async a=>{await a.decode();if(!a.naturalWidth)throw Error('PNG not readable');});
 await page.locator('button', {hasText:'Duyệt đúng revision'}).first().waitFor();
 page.once('dialog',dialog=>dialog.accept('TEST browser exact audio decision'));
 await page.locator('button', {hasText:'Duyệt đúng revision'}).first().click();
 await page.getByText('Đã ghi thao tác qua công cụ chính thức.').waitFor();
 await tabs.nth(5).click();
 if(await page.locator('video').count()<1)throw Error('Manifest video missing');
 if(errors.length)throw Error(errors.join('; '));
 console.log(JSON.stringify({tabs:checks,fixture_wav_metadata:true,fixture_png_decode:true,exact_audio_review:true,video_element:true,page_errors:errors}));
}finally{await browser.close();}
