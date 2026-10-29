const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'review.html'),'utf8'),json=JSON.parse(html.match(/<script type="application\/json" id="evidence">([\s\S]*?)<\/script>/)[1]);
const code=html.match(/<script>([\s\S]*?)<\/script>/)[1];new vm.Script(code);
const elements={};function elem(id){return elements[id]??=(function(){let obj={value:'',events:{},addEventListener(n,f){this.events[n]=f;}};Object.defineProperty(obj,'innerHTML',{set(v){obj._html=v;const m=v.match(/value="([^"]*)"/);if(m)obj.value=m[1]},get(){return obj._html}});return obj})();}
elem('evidence').textContent=JSON.stringify(json);elem('baseline').value='R1B_DONOR';elem('style').value='solid';
const context=vm.createContext({document:{getElementById:elem},console});vm.runInContext(code,context);
let combinations=0;
for(const fixture of Object.keys(json.fixtures)){
 elem('fixture').value=fixture;elem('fixture').events.change();
 const poses=[...new Set(json.outputs.filter(o=>o.fixture===fixture&&o.style==='solid').map(o=>o.pose))];
 for(const pose of poses)for(const asset of ['R1B_DONOR','R1E','R1_CORRECTED_RIG'])for(const style of ['solid','strain']){
   elem('pose').value=pose;elem('baseline').value=asset;elem('style').value=style;elem('baseline').events.change();
   for(const id of ['left','right','pairLeft','pairRight'])assert(fs.existsSync(path.join(__dirname,elem(id).src)),elem(id).src);
   combinations++;
 }
}
for(let i=0;i<3;i++){elem('failureSelect').value=String(i);elem('failureSelect').events.change();assert(fs.existsSync(path.join(__dirname,elem('pairRight').src)));}
assert.equal(json.status.TARGETED_DEFORMATION_VERDICT,'FAIL_CLOSED_TARGETED_DEFORMATION');assert.equal(json.status.R2_INCREMENTAL_INTRODUCED_FAILURE_COUNT,0);assert(!html.includes('__DATA__'));
fs.writeFileSync(path.join(__dirname,'REVIEW_UI_LOGIC_VERIFICATION.json'),JSON.stringify({status:'PASS',method:'Independent Node VM mocked DOM exercises every available fixture/pose/baseline/style selection and three crossing-pair selections; referenced files exist',comparison_combinations:combinations,inline_script_syntax:'PASS',browser_layout_verified:false,no_approval_or_modification_actions:true},null,2));
console.log('Review UI logic PASS: '+combinations+' comparisons, all evidence links exist');
