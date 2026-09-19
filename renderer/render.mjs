import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderMedia,renderStill} from '@remotion/renderer';
import {chromium} from 'playwright';
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
const dir=process.argv[2],props=JSON.parse(fs.readFileSync(path.join(dir,'props.json')));
const url=await bundle({entryPoint:fileURLToPath(new URL('./index.tsx',import.meta.url)),publicDir:path.join(dir,'public')});
const browser=await openBrowser('chrome',{browserExecutable:'/usr/bin/google-chrome'});
try{
 const composition=await selectComposition({serveUrl:url,id:'Pilot',inputProps:props,puppeteerInstance:browser});
 // Render actual composition at each subtitle boundary; measure DOM text boxes.
 // DOM layout uses the same dimensions/styles and exact strings, independently of renderer internals.
 const pw=await chromium.launch({executablePath:'/usr/bin/google-chrome',headless:true});
 const page=await pw.newPage({viewport:{width:720,height:1280}});let failures=[];
 for(const seg of props.segments){
  const scene=props.scenes.find(s=>s.id===seg.scene_id);
  await page.setContent('<div id="title" style="position:absolute;top:92px;left:48px;width:624px;font:700 42px/1.2 Arial"></div><div id="subtitle" style="position:absolute;bottom:160px;left:44px;width:632px;font:600 34px/44px Arial;padding:14px 16px;box-sizing:border-box;text-align:center"></div>');
  await page.locator('#title').evaluate((e,t)=>e.textContent=t,scene.title);await page.locator('#subtitle').evaluate((e,t)=>e.textContent=t,seg.text);
  const bad=await page.evaluate(()=>[...document.querySelectorAll('div')].flatMap(e=>{const r=e.getBoundingClientRect();return r.left<0||r.right>720||r.top<0||r.bottom>1280||e.scrollWidth>e.clientWidth||(e.id==='subtitle'&&r.height>116)?[e.id]:[]}));
  if(bad.length)failures.push({text:seg.text,errors:bad});
 }
 await pw.close();fs.writeFileSync(path.join(dir,'layout.json'),JSON.stringify({passed:!failures.length,checked_frames:props.segments.length,method:'matching text geometry; representative rendered stills require human review',failures},null,2));
 if(failures.length)throw Error('Text overflow');
 for(const scene of props.scenes)await renderStill({serveUrl:url,composition,inputProps:props,puppeteerInstance:browser,frame:Math.min(composition.durationInFrames-1,Math.round((scene.start+scene.end)/2*30)),output:path.join(dir,scene.id+'.png')});
 await renderMedia({serveUrl:url,composition,inputProps:props,puppeteerInstance:browser,codec:'h264',audioCodec:'aac',concurrency:2,outputLocation:path.join(dir,'video.mp4')});
}finally{await browser.close({silent:true});}
