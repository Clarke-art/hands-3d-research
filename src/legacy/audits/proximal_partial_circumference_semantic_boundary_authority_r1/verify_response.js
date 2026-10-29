/* QA only. Outputs test results, never Human answers. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const api=require('./review_logic.js'),checks=[];
function check(name,fn){fn();checks.push({name,passed:true});}
const base={selected_option:'A',Q1_P02_digit_web_acceptable:'YES',Q2_P06_broader_interface_acceptable:'YES',Q4_native_RSSF_context_acceptable:'YES',Q5_approve_for_boundary_authority:'APPROVE_BOUNDARY_ONLY',notes:'QA only — 中文备注\n非 Human response'};
const stamp='2026-10-03T00:00:00.000Z';
const expected={A:[1375,1374,[[1518,293],[386,1518]],[[1373,1368],[1374,1371]]],B:[4666,4668,[[1444,2822],[1520,2822]],[[1368,1369],[1371,1370]]],C:[1376,1377,[[294,1519],[1519,385]],[[1369,1378],[1370,1377]]]};
for(const option of Object.keys(expected)){
 check(option+' exports exact original boundary',()=>{
  const r=api.buildResponse({...base,selected_option:option},stamp,true),q=r.Q3_selected_boundary,e=expected[option];
  assert.deepEqual([q.left_boundary_edge_id,q.right_boundary_edge_id,q.boundary_vertex_ids,q.incident_face_transitions],e);
  assert.equal(r.approved_for_boundary_authority,false);assert.equal(r.response_kind,'AUTOMATED_UI_VALIDATION_NOT_HUMAN');
  assert.equal(r.applies_production_changes,false);assert.equal(r.frozen_membership_changes,false);
 });
}
check('D keeps boundary IDs null',()=>{const r=api.buildResponse({...base,selected_option:'D',Q5_approve_for_boundary_authority:'KEEP_UNRESOLVED'},stamp,true);assert.equal(r.Q3_selected_boundary.stop,'KEEP_UNRESOLVED');assert.equal(r.Q3_selected_boundary.left_boundary_edge_id,null);assert.equal(r.approved_for_boundary_authority,false);});
check('No answer is rejected',()=>assert.throws(()=>api.buildResponse({...base,selected_option:''},stamp,true)));
check('Fourth boundary is rejected',()=>assert.throws(()=>api.buildResponse({...base,selected_option:'E'},stamp,true)));
check('D cannot approve authority',()=>assert.throws(()=>api.buildResponse({...base,selected_option:'D'},stamp,true)));
for(const k of ['Q1_P02_digit_web_acceptable','Q2_P06_broader_interface_acceptable','Q4_native_RSSF_context_acceptable'])for(const value of ['','NO','UNRESOLVED'])check(k+'='+value+' cannot approve',()=>assert.throws(()=>api.buildResponse({...base,[k]:value},stamp,true)));
check('Unresolved controls can export rejection',()=>{assert.equal(api.buildResponse({...base,Q1_P02_digit_web_acceptable:'UNRESOLVED',Q5_approve_for_boundary_authority:'REJECT'},stamp,true).approved_for_boundary_authority,false);});
check('Invalid Q5 rejected',()=>assert.throws(()=>api.buildResponse({...base,Q5_approve_for_boundary_authority:''},stamp,true)));
check('Timestamp required',()=>assert.throws(()=>api.buildResponse(base,'invalid',true)));
check('Unicode notes and required schema survive round trip',()=>{const r=JSON.parse(JSON.stringify(api.buildResponse(base,stamp,true)));for(const k of ['review_id','selected_option','Q1_P02_digit_web_acceptable','Q2_P06_broader_interface_acceptable','Q3_selected_boundary','Q4_native_RSSF_context_acceptable','Q5_approve_for_boundary_authority','notes','timestamp'])assert.ok(Object.hasOwn(r,k));assert.equal(r.notes,base.notes);});
check('Generated HTML inline JavaScript parses',()=>{const html=fs.readFileSync(path.join(__dirname,'PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW.html'),'utf8');const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.ok(scripts.length);for(const s of scripts)new (require('node:vm').Script)(s[1]);});
fs.writeFileSync(path.join(__dirname,'RESPONSE_LOGIC_VERIFICATION_R1.json'),JSON.stringify({qa_only:true,is_human_response:false,passed:true,check_count:checks.length,checks},null,2)+'\n');
console.log(JSON.stringify({passed:true,check_count:checks.length}));
