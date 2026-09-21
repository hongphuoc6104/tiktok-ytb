import test from 'node:test';
import assert from 'node:assert/strict';
import {Session} from './session.mjs';
test('multiple commands reuse one connection',async()=>{
 let count=0,alive=true;const s=new Session(async()=>{count++;return {isConnected:()=>alive,close:async()=>{alive=false;}};});
 await s.start();assert.equal((await s.start()).reused,true);assert.equal(count,1);
 assert.equal(s.status().status,'connected');await s.stop();assert.equal(alive,false);
});
test('disconnect does not trigger another permission prompt',async()=>{
 let alive=true,count=0;const s=new Session(async()=>{count++;return{isConnected:()=>alive};});
 await s.start();alive=false;await assert.rejects(s.start(),/no automatic reconnect/);assert.equal(count,1);
});
test('denied connection is not retried silently',async()=>{
 let count=0;const s=new Session(async()=>{count++;throw Error('denied');});
 await assert.rejects(s.start(),/denied/);await assert.rejects(s.start(),/no automatic reconnect/);assert.equal(count,1);
});
test('wrong profile fails connection and disconnects transport',async()=>{
 let closed=false;const s=new Session(async()=>({isConnected:()=>!closed,close:async()=>{closed=true;}}),async()=>{throw Error('PROFILE_PATH_MISMATCH');});
 await assert.rejects(s.start(),/PROFILE_PATH_MISMATCH/);assert.equal(closed,true);
 await assert.rejects(s.start(),/no automatic reconnect/);
});
test('reuse rechecks profile rather than trusting old verification',async()=>{
 let profile='10',checks=0;const s=new Session(async()=>({isConnected:()=>true,close:async()=>{}}),async()=>{checks++;if(profile!=='10')throw Error('PROFILE_PATH_MISMATCH');return {profile};});
 await s.start();profile='102';await assert.rejects(s.start(),/PROFILE_PATH_MISMATCH/);assert.equal(checks,2);
});
