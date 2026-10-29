(function(root){
 const REVIEW_ID='R3_FRESH_RESULT_HUMAN_REVIEW_R1';
 function validate(a){const errors=[];for(let i=1;i<=7;i++)if(!['YES','NO','REVIEW_REQUIRED'].includes(a['Q'+i]))errors.push('请回答 Q'+i);return errors;}
 function build(a,meta,timestamp,validationMode){
  if(validate(a).length)throw new Error('Incomplete review');
  const accepted=Array.from({length:7},(_,i)=>a['Q'+(i+1)]).every(v=>v==='YES')&&!validationMode;
  return {review_id:REVIEW_ID,phase:'HUMAN_R3_FRESH_RESULT_APPROVAL',canonical_contract_hash:meta.contract_hash,proximal_boundary_authority_hash:meta.proximal_hash,fresh_result_label_hash:meta.result_hash,technical_verdict:meta.status.technical_validation_verdict,revalidation_blockers:meta.status.review_reasons,Q1_overall_ownership:a.Q1,Q2_first_web:a.Q2,Q3_index_sheet:a.Q3,Q4_thumb_base_palm:a.Q4,Q5_hard_source_preservation:a.Q5,Q6_boundary_ambiguity:a.Q6,Q7_accept_ownership_authority_candidate:a.Q7,notes:a.notes||'',timestamp,validation_mode:!!validationMode,response_kind:validationMode?'AUTOMATED_UI_VALIDATION_NOT_HUMAN':'HUMAN_R3_FRESH_RESULT_REVIEW_RESPONSE',accepted_as_ownership_authority_candidate:accepted,authority_scope:'FRESH_R3_OWNERSHIP_CANDIDATE_ONLY',Human_approved_frozen:false,sheet_revalidation_pass:meta.sheet_valid,automatic_apply:false,automatic_solver_execution:false,skin_rebuild_approved:false,Stage6_approved:false,applies_production_changes:false,authorized_next_phase:null,after_separate_approval_and_revalidation:'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1'};
 }
 const api={REVIEW_ID,validate,build};if(typeof module!=='undefined')module.exports=api;root.FreshReview=api;
})(typeof globalThis!=='undefined'?globalThis:this);
