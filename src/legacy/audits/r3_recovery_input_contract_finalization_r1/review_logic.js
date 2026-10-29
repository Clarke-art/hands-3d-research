/* Response schema only. No authority application or solver call. */
(function(root){
 const REVIEW_ID='R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW_R1';
 function validateAnswers(a){
  const errors=[];
  for(let i=1;i<=7;i++)if(!['YES','NO','UNRESOLVED'].includes(a['Q'+i]))errors.push('Q'+i+' 尚未填写。');
  if(!['APPROVE_INPUT_CONTRACT','REJECT','KEEP_UNRESOLVED'].includes(a.Q8))errors.push('Q8 尚未填写。');
  if(a.Q8==='APPROVE_INPUT_CONTRACT'&&Array.from({length:7},(_,i)=>a['Q'+(i+1)]).some(x=>x!=='YES'))errors.push('批准进入 fresh R3 需要 Q1–Q7 全为 YES；否则请拒绝或保留未决。');
  if(typeof a.notes!=='string')errors.push('Notes 必须是文本。');
  return errors;
 }
 function buildResponse(a,hash,proxHash,timestamp,validation=false){
  const e=validateAnswers(a);if(e.length)throw Error(e.join('\n'));
  if(!/^[a-f0-9]{64}$/.test(hash)||!/^[a-f0-9]{64}$/.test(proxHash))throw Error('Candidate hash invalid.');
  if(!Number.isFinite(Date.parse(timestamp)))throw Error('Invalid timestamp.');
  const approved=!validation&&a.Q8==='APPROVE_INPUT_CONTRACT';
  return {review_id:REVIEW_ID,contract_id:'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1',canonical_contract_hash:hash,proximal_boundary_authority_hash:proxHash,Q1_thumb_high_confidence_sources:a.Q1,Q2_index_resolved_sources:a.Q2,Q3_neutral_interface_no_hard_pins:a.Q3,Q4_graph_is_solver_workspace:a.Q4,Q5_P04_P05_boundary_respected:a.Q5,Q6_corrected_common_mm_cost_semantics:a.Q6,Q7_fresh_R3_no_historical_label_target:a.Q7,Q8_approve_next_R3_recompute:a.Q8,notes:a.notes,timestamp,approved_for_input_contract:approved,cost_semantics_approved_with_contract:approved,authorized_next_phase:approved?'R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1':null,authority_scope:'R3_RECOVERY_INPUT_CONTRACT_ONLY',response_kind:validation?'AUTOMATED_UI_VALIDATION_NOT_HUMAN':'HUMAN_R3_RECOVERY_INPUT_CONTRACT_APPROVAL_RESPONSE',validation_mode:validation,applies_production_changes:false,automatic_apply:false,automatic_solver_execution:false,frozen_membership_changes:false,anatomical_ownership_map_approved:false,skin_weights_approved:false,Stage6_approved:false};
 }
 const api={REVIEW_ID,validateAnswers,buildResponse};root.R3Review=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(globalThis);
