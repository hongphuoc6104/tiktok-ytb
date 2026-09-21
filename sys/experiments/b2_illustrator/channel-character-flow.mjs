/** Asset registration only; never generates or clears any unresolved state. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const project='https://flow.google.com/project/7c815425-4625-4afb-ba84-4290d3fa9ea4';
const folder=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../assets/characters/channel-mascot');
export async function runCharacterOperation(command,bound) {
 const page=bound?.page;if(!page || page.isClosed())throw Error('No existing bound page');
 if(command==='tool-snapshot:mascot-verify') {
  const previous=page.url();
  await page.screenshot({path:path.join(folder,'before-navigation.png')});
  await page.goto('chrome://version');
  const profile=(await page.locator('#profile_path').innerText()).trim();
  const executable=(await page.locator('#executable_path').innerText()).trim();
  fs.writeFileSync(path.join(folder,'browser-verification.json'),JSON.stringify({profile,executable,observedAt:new Date().toISOString(),previous},null,2));
  if(profile!=='/home/hongphuoc/.config/google-chrome/Profile 10' || executable!=='/opt/google/chrome/google-chrome')throw Error('Exact browser/profile mismatch');
  bound.identity={observedProfile:profile,executable,verifiedAt:new Date().toISOString()};
  await page.goto(project,{waitUntil:'domcontentloaded'});
 }
 if(command==='tool-snapshot:mascot-add-menu')await page.getByRole('button',{name:'Add media menu',exact:true}).click();
 if(command==='tool-snapshot:mascot-upload') {
 const chooser=page.waitForEvent('filechooser');
 await page.getByRole('menuitem',{name:'Upload',exact:true}).click();
 await (await chooser).setFiles(path.join(folder,'reference-v1.png'));
 }
 if(command==='tool-snapshot:mascot-create-character')await page.getByRole('menuitem',{name:'Create character',exact:true}).click({timeout:5000});
 if(command==='tool-snapshot:mascot-tiles')return await page.getByRole('img',{name:"Tile displaying a user's image"}).evaluateAll(xs=>xs.slice(0,3).map(x=>x.parentElement.outerHTML));
 const snapshot=await page.locator('body').ariaSnapshot();
 const inputs=await page.locator('input').evaluateAll(xs=>xs.map(x=>({type:x.type,accept:x.accept,outerHTML:x.outerHTML})));
 const result={url:page.url(),snapshot,inputs,observedAt:new Date().toISOString(),generationSubmitted:false};
 fs.writeFileSync(path.join(folder,'flow-current.json'),JSON.stringify(result,null,2));return result;
}
