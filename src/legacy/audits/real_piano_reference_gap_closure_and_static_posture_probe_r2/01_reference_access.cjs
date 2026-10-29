const {chromium}=require('<USER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 let results=[];
 for(const [id,url] of [['piadoor','https://piadoor.com/en/piece/2/basic/'],['pianote','https://www.pianote.com/blog/play-piano-with-small-hands/'],['hoffman_d','https://app.hoffmanacademy.com/lessons/piano/d-major-pentascale/video/'],['hoffman_musette','https://app.hoffmanacademy.com/lessons/piano/musette-in-d-a-section/video/']]){
  const p=await b.newPage({viewport:{width:1360,height:900}});let error=null;
  try{await p.goto(url,{waitUntil:'domcontentloaded',timeout:30000});await p.waitForTimeout(1800)}catch(e){error=e.message}
  const data=await p.evaluate(()=>({title:document.title,text:document.body.innerText.slice(0,40000),iframes:[...document.querySelectorAll('iframe')].map(x=>x.src),images:[...document.images].map(x=>({alt:x.alt,src:x.currentSrc})),videos:[...document.querySelectorAll('video')].map(v=>({src:v.currentSrc,ready:v.readyState,duration:Number.isFinite(v.duration)?v.duration:null}))}));
  results.push({id,url,error,...data});console.log(JSON.stringify({id,error,title:data.title,iframes:data.iframes,images:data.images.filter(x=>/octave|left_hand|Small|small|hands/i.test(x.src+' '+x.alt))}));await p.close();
 }
 fs.writeFileSync(path.join(__dirname,'REFERENCE_ACCESS_R2.json'),JSON.stringify(results,null,2));await b.close();
})().catch(e=>{console.error(e);process.exitCode=1});
