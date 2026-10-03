/** Imports control API without launching a browser, connecting or generating. */
import fs from 'node:fs';
import path from 'node:path';
import {chromium} from 'playwright';
const pkg=JSON.parse(fs.readFileSync(path.join(process.env.VP_CONTROL_RUNTIME,'node_modules/playwright/package.json'),'utf8'));
console.log(JSON.stringify({playwright:pkg.version,connect_api:typeof chromium.connectOverCDP==='function',browser_started:false,provider_called:false}));
