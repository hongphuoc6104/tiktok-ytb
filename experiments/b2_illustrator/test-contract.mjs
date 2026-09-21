import test from 'node:test';
import assert from 'node:assert/strict';
import {checkContract} from './check_contract.mjs';
test('absent UI cannot become an accepted tool',()=>{
 const report=checkContract({status:'blocked',frames:[]});
 assert.equal(report.uiContract,'fail');assert.equal(report.productionReady,false);
 assert.ok(report.missing.includes('style'));
});
test('visible controls never prove conditioning or production readiness',()=>{
 const snapshot='heading "VP Stickman Lab" '+['Topic / Prompt','Style','Preserve','Change','Literal Text Overlay'].map(n=>`textbox "${n}"`).join(' ')+['Select Base Scene','Select Character','16:9','9:16','Initialize Generation'].map(n=>`button "${n}"`).join(' ');
 const report=checkContract({status:'inspected',frames:[{snapshot}]});
 assert.equal(report.uiContract,'pass');assert.equal(report.sdkReferenceConditioning,'unverified');assert.equal(report.productionReady,false);
});
