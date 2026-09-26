/** Persistent local session; fixed commands only, no arbitrary browser execution. */
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {browserConfig,debugEndpoint,inspect,safeResults,toolUrl,verifyBrowser} from './controller.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const socketPath=path.join(here,'results','controller','session.sock');

export class Session {
  constructor(connect,verify=async()=>null){this.connect=connect;this.verify=verify;this.identity=null;this.browser=null;this.attempted=false;}
  async start(){
    if(this.browser?.isConnected()) {this.identity=await this.verify(this.browser);return {status:'connected',reused:true,identity:this.identity};}
    if(this.attempted) throw Error('Session ended: no automatic reconnect; restart the service explicitly');
    this.attempted=true;
    this.browser=await this.connect();
    try {this.identity=await this.verify(this.browser);} catch(e) {await this.stop();throw e;}
    return {status:'connected',reused:false,identity:this.identity};
  }
  status(){return {status:this.browser?.isConnected()?'connected':this.attempted?'disconnected':'not_connected'};}
  // Never browser.close(): on a CDP-attached user Chrome it quits Chrome itself (FLOW-007/B2-001). Drop the
  // reference; the connection ends when this process exits.
  async stop(){this.browser=null;this.identity=null;}
}
async function serve(){
  safeResults();
  if(fs.existsSync(socketPath)) throw Error('Session socket exists: use status; do not start a second session');
  const config={...JSON.parse(fs.readFileSync(path.join(here,'../../config.json'))),...JSON.parse(fs.readFileSync(path.join(here,'browser-profiles.json')))};
  const selected=browserConfig(config);
  let bound=null;
  const session=new Session(async()=>{
    const endpoint=debugEndpoint(fs.readFileSync(path.join(selected.dataDir,'DevToolsActivePort'),'utf8'));
    return chromium.connectOverCDP(endpoint,{timeout:60000});
  }, async browser=>{
    const context=browser.contexts()[0];
    if(!context) throw Error('NO_CHROME_CONTEXT');
    if(bound) {
      if(bound.page.isClosed()) throw Error('BOUND_TAB_CLOSED');
      return bound.identity;
    }
    bound=await verifyBrowser(browser,config,true);
    if(bound.page.isClosed())throw Error('BOUND_TAB_CLOSED');
    return bound.identity;
  });
  const ensureBoundPage=async()=>{
    if(bound?.page && !bound.page.isClosed()) return bound;
    throw Error('BOUND_TAB_CLOSED: reconnect and verify the configured profile; do not replace the tab silently');
  };
  let queue=Promise.resolve();
  const server=net.createServer(client=>{
    let data='';
    client.on('error',()=>{});
    client.on('data',chunk=>{
      data+=chunk;
      if(data.length>8192){client.destroy();return;}
      if(!data.includes('\n'))return;
      client.removeAllListeners('data');
      const command=data.trim();
      if(command==='status') {
        // Read-only and synchronous: answer immediately instead of waiting
        // behind whatever long tool-snapshot/connect call is already queued.
        // A status probe queued behind a multi-minute batch submission was
        // the main reason a 5s (now configurable, retried) client-side
        // timeout looked like a dead daemon when it was really just busy.
        client.end(JSON.stringify(session.status())+'\n');
        return;
      }
      queue=queue.then(async()=>{
        try {
          let result;
          if(command==='connect') {
            result=await session.start();
            await ensureBoundPage();
            if(bound?.page && !bound.page.url().startsWith(toolUrl)) {
              await bound.page.goto(toolUrl,{waitUntil:'domcontentloaded',timeout:30000});
            }
          }
          else if(command==='inspect') {
            if(session.status().status!=='connected') throw Error('CONNECT_FIRST: session unavailable');
            await ensureBoundPage();
            result=await inspect(config,session.browser,bound);
            fs.writeFileSync(path.join(safeResults(),`session-inspect-${Date.now()}.json`),JSON.stringify(result,null,2));
          } else if(['editor-inspect','reference-inspect'].includes(command) || command.startsWith('tool-snapshot')) {
            if(session.status().status!=='connected')throw Error('CONNECT_FIRST');
            await ensureBoundPage();
            const operations=await import('./browser-operations.mjs?revision='+Date.now());
            result=await operations.runOperation(command,bound);
          } else if(command==='stop') {
            if(bound && !bound.page.isClosed())await bound.page.close();
            await session.stop();result={status:'stopped'};
          } else throw Error('Unsupported session command');
          client.end(JSON.stringify(result)+'\n');
          if(command==='stop'){server.close();setTimeout(()=>process.exit(0),300);}
        }catch(e){client.end(JSON.stringify({status:'blocked',reason:e.message})+'\n');}
      });
    });
  });
  server.on('close',()=>{if(fs.existsSync(socketPath))fs.unlinkSync(socketPath);});
  server.on('error',e=>{console.error(e.message);process.exitCode=2;});
  server.listen(socketPath,()=>{fs.chmodSync(socketPath,0o600);console.log('Persistent session ready; run session.mjs connect once.');});
  for(const sig of ['SIGTERM','SIGINT'])process.on(sig,async()=>{await session.stop().catch(()=>{});server.close();setTimeout(()=>process.exit(0),300);});
}
async function client(command){
  await new Promise((resolve,reject)=>{
    const socket=net.createConnection(socketPath,()=>socket.write(command+'\n'));
    let response='';
    socket.setTimeout(180000,()=>socket.destroy(Error('SESSION_COMMAND_TIMEOUT: inspect status before retrying')));
    socket.on('data',d=>{response+=d;process.stdout.write(d);});
    socket.on('end',()=>{try {if(JSON.parse(response).status==='blocked')process.exitCode=2;}catch{process.exitCode=2;}resolve();});socket.on('error',reject);
  });
}
if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
 const cmd=process.argv[2];
 (cmd==='serve'?serve():client(cmd||'status')).catch(e=>{console.error(e.message);process.exitCode=2;});
}
