const fs=require('fs');const path=require('path');
const {chromium}=require('<USER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8788/review.html');await page.waitForFunction(()=>Number.isFinite(document.querySelector('video').duration));
 const before=await page.locator('video').evaluate(v=>({duration:v.duration,muted:v.muted,volume:v.volume,paused:v.paused}));
 await page.getByRole('button',{name:'播放并开启声音',exact:true}).click();await page.waitForFunction(()=>document.querySelector('video').currentTime>.12);
 await page.getByRole('button',{name:'暂停',exact:true}).click();const paused=await page.locator('video').evaluate(v=>({time:v.currentTime,paused:v.paused,muted:v.muted}));await page.waitForTimeout(180);const held=await page.locator('video').evaluate(v=>v.currentTime);
 await page.locator('video').evaluate(v=>{v.currentTime=2.6});await page.waitForFunction(()=>Math.abs(document.querySelector('video').currentTime-2.6)<.02);
 await page.getByRole('button',{name:'重播',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('video').paused&&document.querySelector('video').currentTime>.12&&document.querySelector('video').currentTime<1);
 const replay=await page.locator('video').evaluate(v=>({time:v.currentTime,paused:v.paused,muted:v.muted,videoWidth:v.videoWidth,videoHeight:v.videoHeight,readyState:v.readyState,error:v.error?.message||null}));
 await page.getByRole('button',{name:'暂停',exact:true}).click();await page.screenshot({path:path.join(__dirname,'_review_ui.png'),fullPage:false});
 const result={status:before.duration===3.4&&paused.paused&&Math.abs(held-paused.time)<.02&&!replay.paused&&!replay.muted&&replay.videoWidth===1600&&errors.length===0?'PASS':'FAIL',before,paused,heldTime:held,replay,errors,browser:'Isolated headless Chrome fallback; native CUA kernel unavailable',audibility_scope:'DOM unmuted and media decoded; non-silence and pitch checked from decoded AAC separately, not physical-speaker listening'};
 fs.writeFileSync(path.join(__dirname,'REVIEW_UI_VALIDATION_R1.json'),JSON.stringify(result,null,2));await browser.close();console.log(JSON.stringify(result));if(result.status!=='PASS')process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
