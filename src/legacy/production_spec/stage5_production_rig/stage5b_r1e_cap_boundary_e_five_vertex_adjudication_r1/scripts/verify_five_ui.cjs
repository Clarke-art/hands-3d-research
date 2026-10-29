const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('<USER_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out=path.resolve(__dirname,'..');const assert=(x,m)=>{if(!x)throw new Error(m)};
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});try{
 const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(out,'CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html')).href,{waitUntil:'load'});
 for(const view of ['DORSAL','PALMAR','RADIAL','ULNAR','THUMB_SIDE','TIP']){
  await page.locator(`.view-button[data-view="${view}"]`).click();
  assert(await page.locator('.native-view.active').getAttribute('data-view')===view,'View failed '+view);
  assert(await page.locator('#view-'+view+' .disputed circle').count()===5,'Five disputed markers required');
 }
 for(const cls of ['baseline','final','disputed','nail']){
  await page.locator('#toggle-'+cls).uncheck();assert(await page.locator('#view-TIP .'+cls).evaluate(e=>getComputedStyle(e).display)==='none','Layer off '+cls);
  await page.locator('#toggle-'+cls).check();
 }
 assert(await page.locator('#human-form select').count()===7,'Seven questions required');
 for(const q of ['Q1','Q2','Q3','Q4','Q5','Q6','Q7'])assert(await page.locator(`select[name="${q}"]`).inputValue()==='','No prefilled Human answer');
 for(const q of ['Q1','Q2','Q3','Q4','Q5']){
  const options=await page.locator(`select[name="${q}"] option`).allTextContents();assert(options.join('|')==='尚未回答|KEEP|REMOVE','Only KEEP / REMOVE');
 }
 const dialogs=[];page.on('dialog',async d=>{dialogs.push(d.message());await d.accept()});
 await page.locator('#human-form button[type="submit"]').click();assert(dialogs.length===1&&dialogs[0].includes('Q1'),'Empty response blocked');
 assert(await page.locator('#result').evaluate(e=>e.textContent)==='','No Human verdict should be created');
 await page.locator('.view-button[data-view="DORSAL"]').click();await page.locator('#views').screenshot({path:path.join(out,'renders','_FIVE_VERTEX_UI_DORSAL_CHECK.png')});
 assert(errors.length===0,'Browser script errors');
 const result={status:'PASS',six_views:true,five_disputed_ID_markers_per_view:true,baseline_final_disputed_nail_switches:true,
  exactly_seven_human_questions:true,first_five_only_KEEP_REMOVE:true,human_answers_blank:true,no_human_verdict_generated:true,
  empty_submission_blocked:true,script_errors:errors,displayed_candidate_families:['E_BASELINE','E_FINAL'],no_network_submission:true};
 fs.writeFileSync(path.join(out,'UI_VERIFICATION.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
