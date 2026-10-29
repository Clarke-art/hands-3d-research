const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),api=require('./review_logic.js');
const checks=[];function ck(name,fn){fn();checks.push({name,passed:true});}
let yes={notes:'AUTOMATED TEST ONLY — 中文备注\n非 Human response',Q8:'APPROVE_INPUT_CONTRACT'};for(let i=1;i<=7;i++)yes['Q'+i]='YES';
const h=JSON.parse(fs.readFileSync(path.join(__dirname,'R3_CONTRACT_HASH_R1.json'),'utf8')).canonical_contract_hash;
const p=JSON.parse(fs.readFileSync(path.join(__dirname,'REVIEW_VIEW_DATA.json'),'utf8')).proximal_hash,stamp='2026-10-03T00:00:00.000Z';
ck('Validation cannot grant authority or solver authorization',()=>{const r=api.buildResponse(yes,h,p,stamp,true);assert.equal(r.approved_for_input_contract,false);assert.equal(r.authorized_next_phase,null);assert.equal(r.response_kind,'AUTOMATED_UI_VALIDATION_NOT_HUMAN');assert.equal(r.automatic_solver_execution,false);assert.equal(r.automatic_apply,false);});
for(let i=1;i<=7;i++)for(const v of ['', 'NO','UNRESOLVED'])ck('Approval blocked when Q'+i+'='+v,()=>assert.throws(()=>api.buildResponse({...yes,['Q'+i]:v},h,p,stamp,true)));
ck('Q8 missing blocked',()=>assert.throws(()=>api.buildResponse({...yes,Q8:''},h,p,stamp,true)));
ck('Rejection can record unresolved design',()=>{const r=api.buildResponse({...yes,Q3:'UNRESOLVED',Q8:'REJECT'},h,p,stamp,true);assert.equal(r.approved_for_input_contract,false);});
ck('Keep unresolved supported',()=>assert.equal(api.buildResponse({...yes,Q8:'KEEP_UNRESOLVED'},h,p,stamp,true).authorized_next_phase,null));
ck('Invalid candidate hash rejected',()=>assert.throws(()=>api.buildResponse(yes,'bad',p,stamp,true)));
ck('Invalid timestamp rejected',()=>assert.throws(()=>api.buildResponse(yes,h,p,'bad',true)));
ck('Unicode and immutable binding round trip',()=>{const r=JSON.parse(JSON.stringify(api.buildResponse(yes,h,p,stamp,true)));assert.equal(r.notes,yes.notes);assert.equal(r.canonical_contract_hash,h);assert.equal(r.proximal_boundary_authority_hash,p);});
ck('Generated HTML JS parses',()=>{const s=fs.readFileSync(path.join(__dirname,'R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW.html'),'utf8');const scripts=[...s.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.ok(scripts.length);for(const x of scripts)new (require('node:vm').Script)(x[1]);});
fs.writeFileSync(path.join(__dirname,'RESPONSE_LOGIC_VERIFICATION_R1.json'),JSON.stringify({passed:true,qa_only:true,is_Human_response:false,check_count:checks.length,checks},null,2)+'\n');console.log(JSON.stringify({passed:true,checks:checks.length}));
