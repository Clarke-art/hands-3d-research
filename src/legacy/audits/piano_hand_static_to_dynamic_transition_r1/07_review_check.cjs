const {chromium}=require('<USER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await browser.newPage({viewport:{width:1560,height:1100}}),errors=[],states=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith('http://127.0.0.1:8847/')&&r.status()>=400)errors.push(r.status()+' '+r.url())});
 const url='http://127.0.0.1:8847/review.html';await page.goto(url,{waitUntil:'networkidle'});
 for(const hand of ['L','R']){
  await page.locator(`[data-hand=${hand}]`).click();await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=3&&Number.isFinite(v.duration)});
  await page.locator('#speed').selectOption('0.25');await page.locator('#next').click();await page.waitForFunction(()=>document.querySelector('video').currentTime>=.016);const step=await page.locator('video').evaluate(v=>v.currentTime);
  await page.locator('#play').click();await page.waitForFunction(()=>document.querySelector('video').currentTime>.08);await page.locator('#play').click();await page.locator('#speed').selectOption('1');
  await page.locator('video').evaluate(v=>{v.currentTime=0;v.play()});await page.waitForFunction(()=>document.querySelector('video').ended,{},{timeout:10000});
  states.push(await page.locator('video').evaluate((v,{hand,step})=>({hand,step,duration:v.duration,ended:v.ended,error:v.error?.message||null,width:v.videoWidth,height:v.videoHeight}),{hand,step}));
 }
 await page.locator('[data-hand=L]').click();await page.waitForFunction(()=>document.querySelector('video').readyState>=3);await page.screenshot({path:path.join(__dirname,'_qa/review_desktop.png'),fullPage:false});
 const desktop=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(__dirname,'_qa/review_mobile.png'),fullPage:false});const mobile=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
 const images=await page.locator('img').evaluateAll(xs=>xs.map(x=>({src:x.getAttribute('src'),loaded:x.complete&&x.naturalWidth>0})));const links=[];
 for(const a of await page.locator('a[href]').all()){const href=await a.getAttribute('href');const r=await page.request.get(new URL(href,url).href);links.push({href,status:r.status()});if(!r.ok())errors.push(href+' '+r.status());}
 const pass=!errors.length&&states.every(x=>x.ended&&!x.error&&x.width===2304&&x.height===756&&Math.abs(x.step-1/60)<.002)&&images.every(x=>x.loaded)&&desktop.scroll<=desktop.width&&mobile.scroll<=mobile.width;
 const result={status:pass?'PASS_REVIEW_UI_AND_COMPLETE_PLAYBACK':'FAIL',url,states,images,links,desktop,mobile,errors,not_human_approval:true};fs.writeFileSync(path.join(__dirname,'REVIEW_UI_VALIDATION_R1.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();if(!pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
