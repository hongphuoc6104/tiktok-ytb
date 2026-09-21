/** Read-only audit: visible controls are necessary, not proof of SDK behavior. */
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
export function checkContract(inspection) {
 const app=inspection.frames?.find(f=>f.snapshot.includes('heading "VP Stickman Lab"'))?.snapshot || '';
 const required={topic:'textbox "Topic / Prompt"',style:'textbox "Style"',preserve:'textbox "Preserve"',change:'textbox "Change"',text:'textbox "Literal Text Overlay"',base:'button "Select Base Scene"',character:'button "Select Character"',wide:'button "16:9"',vertical:'button "9:16"',generate:'button "Initialize Generation"'};
 const missing=Object.entries(required).filter(([,text])=>!app.includes(text)).map(([name])=>name);
 return {observedAt:inspection.observedAt || null,profile:inspection.observedProfile || null,
   missing,uiContract:inspection.status==='inspected' && !missing.length?'pass':'fail',
   sdkReferenceConditioning:'unverified',resultRecovery:'unverified',modelAvailability:'unverified',creditCost:'unverified',productionReady:false};
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(checkContract(JSON.parse(fs.readFileSync(process.argv[2]))),null,2));
