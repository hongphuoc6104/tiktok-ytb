/** Resolve only browser-control Playwright from the per-user pinned runtime. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const manifest=JSON.parse(fs.readFileSync(new URL('./package.json',import.meta.url),'utf8'));
export async function resolve(specifier,context,nextResolve) {
  if(specifier!=='playwright')return nextResolve(specifier,context);
  const runtime=process.env.VP_CONTROL_RUNTIME;
  if(!runtime||!path.isAbsolute(runtime))throw Error('CONTROL_RUNTIME_MISSING: bootstrap apply --install');
  const folder=path.join(runtime,'node_modules/playwright');
  const pkg=JSON.parse(fs.readFileSync(path.join(folder,'package.json'),'utf8'));
  if(pkg.version!==manifest.dependencies.playwright)throw Error('CONTROL_PLAYWRIGHT_VERSION_MISMATCH');
  return {url:pathToFileURL(path.join(folder,'index.mjs')).href,shortCircuit:true};
}
