const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('<USER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],results=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8789/review.html');
 for(const [button,id] of [['#show-new','#new-video'],['#show-compare','#compare-video']]){
  await page.locator(button).click();await page.waitForFunction(id=>document.querySelector(id).readyState>=2,id);
  const metadata=await page.locator(id).evaluate(v=>({duration:v.duration,muted:v.muted,volume:v.volume,width:v.videoWidth,height:v.videoHeight}));assert.equal(metadata.duration,3.4);assert.equal(metadata.muted,false);
  for(const t of [.85,1.15,1.85,2.5]){await page.locator(`[data-time="${t===2.5?'2.50':t}"]`).click();await page.waitForFunction(({id,t})=>{const v=document.querySelector(id);return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-t)<.02},{id,t});}
  await page.locator('#next').click();let step=await page.locator(id).evaluate(v=>v.currentTime);assert(Math.abs(step-(2.5+1/60))<.001);
  await page.locator('#replay').click();await page.waitForFunction(id=>document.querySelector(id).currentTime>.15,id);await page.locator('#pause').click();const t=await page.locator(id).evaluate(v=>v.currentTime);await page.waitForTimeout(180);assert(Math.abs(await page.locator(id).evaluate(v=>v.currentTime)-t)<.01);
  await page.locator('#speed').selectOption('0.5');await page.locator('#play').click();await page.waitForTimeout(600);await page.locator('#pause').click();const slow=await page.locator(id).evaluate(v=>({t:v.currentTime,rate:v.playbackRate}));assert.equal(slow.rate,.5);assert(slow.t>t+.2&&slow.t<t+.5);
  await page.locator('#speed').selectOption('1');await page.locator('#replay').click();await page.waitForFunction(id=>document.querySelector(id).ended,id,{timeout:10000});
  results.push({id,...metadata,play_pause_seek_step_replay:'PASS',half_speed:'PASS',full_3_4sec_playback_to_end:'PASS'});
 }
 await page.locator('#show-new').click();await page.locator('[data-time="1.15"]').click();await page.waitForFunction(()=>!document.querySelector('#new-video').seeking&&document.querySelector('#clock').textContent.startsWith('1.150'));await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(__dirname,'_review_ui.png'),fullPage:false});
 await page.setViewportSize({width:390,height:844});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert(!overflow,'Mobile horizontal overflow');assert.equal(errors.length,0);
 const result={status:'PASS',videos:results,mobile_horizontal_overflow:false,errors,browser:'Isolated headless Chrome; existing CUA unavailable',scope:'Playback, seeking, audio-unmuted and media decoding; not physical-speaker listening or Human approval'};
 fs.writeFileSync(path.join(__dirname,'REVIEW_UI_VALIDATION_R1.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
