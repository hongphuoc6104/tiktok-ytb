import React, {useLayoutEffect} from 'react';
import {AbsoluteFill,Audio,Composition,Img,registerRoot,staticFile,useCurrentFrame,interpolate} from 'remotion';
const Video:React.FC<any>=(p)=>{
 const frame=useCurrentFrame(); const t=frame/30;
 useLayoutEffect(()=>{
  for(const element of document.querySelectorAll<HTMLElement>('[data-check]')){
   const rect=element.getBoundingClientRect();
   if(element.scrollWidth>element.clientWidth || (element.dataset.check==='subtitle' && element.offsetHeight>116)) throw new Error('Actual render text overflow: '+element.textContent);
  }
 },[frame]);
 const scene=p.scenes.find((s:any)=>t>=s.start&&t<s.end)||p.scenes[p.scenes.length-1];
 const sub=p.segments.find((s:any)=>t>=s.start&&t<s.end);
 const scale=interpolate(t,[scene.start,scene.end],[1,1.055],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <AbsoluteFill style={{background:'#142f32',fontFamily:'Arial, sans-serif',color:'white'}}>
 <Img src={staticFile(scene.image)} style={{width:'100%',height:'100%',objectFit:'cover',transform:`scale(${scale})`,opacity:interpolate(t,[scene.start,scene.start+.3,scene.end-.3,scene.end],[0,1,1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}/>
 <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(0,0,0,.4),transparent 40%,rgba(0,0,0,.85))'}}/>
 <div data-check="title" style={{position:'absolute',top:92,left:48,width:624,fontSize:42,fontWeight:700,lineHeight:1.2}}>{scene.title}</div>
 {sub&&<div data-check="subtitle" style={{position:'absolute',bottom:160,left:44,width:632,fontSize:34,fontWeight:600,lineHeight:'44px',textAlign:'center',padding:'14px 16px',boxSizing:'border-box',borderRadius:16,background:'rgba(10,25,28,.8)'}}>{sub.text}</div>}
 <Audio src={staticFile('narration.wav')}/>
 </AbsoluteFill>;
};
registerRoot(()=> <Composition id="Pilot" component={Video} width={720} height={1280} fps={30} durationInFrames={1800} defaultProps={{scenes:[],segments:[]}} calculateMetadata={({props})=>({durationInFrames:Math.ceil(props.duration*30)})}/>);
