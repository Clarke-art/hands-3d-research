/* Pure response construction; no persistence and no production mutation. */
(function(root) {
  const REVIEW_ID = 'PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW_R1';
  const boundaries = {
    A: {stop:'STOP_AFTER_P03', rows:['P03','P04'], edges:[1375,1374], vertices:[[1518,293],[386,1518]], face_transitions:[[1373,1368],[1374,1371]]},
    B: {stop:'STOP_AFTER_P04', rows:['P04','P05'], edges:[4666,4668], vertices:[[1444,2822],[1520,2822]], face_transitions:[[1368,1369],[1371,1370]]},
    C: {stop:'STOP_AFTER_P05', rows:['P05','P06'], edges:[1376,1377], vertices:[[294,1519],[1519,385]], face_transitions:[[1369,1378],[1370,1377]]}
  };
  function validateAnswers(a) {
    const errors=[];
    if (!['A','B','C','D'].includes(a.selected_option)) errors.push('请选择 A、B、C 或 D；页面没有预选答案。');
    for (const [key,title] of [['Q1_P02_digit_web_acceptable','Q1'],['Q2_P06_broader_interface_acceptable','Q2'],['Q4_native_RSSF_context_acceptable','Q4']]) {
      if (!['YES','NO','UNRESOLVED'].includes(a[key])) errors.push(title+' 尚未填写。');
    }
    if (!['APPROVE_BOUNDARY_ONLY','REJECT','KEEP_UNRESOLVED'].includes(a.Q5_approve_for_boundary_authority)) errors.push('Q5 尚未填写。');
    if (a.Q5_approve_for_boundary_authority==='APPROVE_BOUNDARY_ONLY') {
      if (!['A','B','C'].includes(a.selected_option)) errors.push('D 保持未决，不能同时批准 boundary authority。');
      if ([a.Q1_P02_digit_web_acceptable,a.Q2_P06_broader_interface_acceptable,a.Q4_native_RSSF_context_acceptable].some(v=>v!=='YES')) errors.push('批准边界需 Q1、Q2、Q4 全部为 YES；否则请拒绝或保留未决。');
    }
    if (typeof a.notes!=='string') errors.push('备注必须是文本。');
    return errors;
  }
  function buildResponse(a, timestamp, validationMode=false) {
    const errors=validateAnswers(a);
    if(errors.length) throw new Error(errors.join('\n'));
    if(!Number.isFinite(Date.parse(timestamp))) throw new Error('timestamp 无效。');
    const q=boundaries[a.selected_option];
    return {
      review_id:REVIEW_ID,
      authority_id:'PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1',
      selected_option:a.selected_option,
      Q1_P02_digit_web_acceptable:a.Q1_P02_digit_web_acceptable,
      Q2_P06_broader_interface_acceptable:a.Q2_P06_broader_interface_acceptable,
      Q3_selected_boundary:q ? {option:a.selected_option,stop:q.stop,distal_row:q.rows[0],proximal_row:q.rows[1],left_boundary_edge_id:q.edges[0],right_boundary_edge_id:q.edges[1],boundary_vertex_ids:q.vertices,incident_face_transitions:q.face_transitions} : {option:'D',stop:'KEEP_UNRESOLVED',distal_row:null,proximal_row:null,left_boundary_edge_id:null,right_boundary_edge_id:null,boundary_vertex_ids:null,incident_face_transitions:null},
      Q4_native_RSSF_context_acceptable:a.Q4_native_RSSF_context_acceptable,
      Q5_approve_for_boundary_authority:a.Q5_approve_for_boundary_authority,
      approved_for_boundary_authority:!validationMode && a.Q5_approve_for_boundary_authority==='APPROVE_BOUNDARY_ONLY',
      authority_scope:'THUMB_SHARED_STRIP_PROXIMAL_SEMANTIC_STOP_ONLY',
      notes:a.notes,
      timestamp,
      response_kind:validationMode?'AUTOMATED_UI_VALIDATION_NOT_HUMAN':'HUMAN_ANATOMICAL_ADJUDICATION_RESPONSE',
      validation_mode:validationMode,
      applies_production_changes:false,
      frozen_membership_changes:false,
      first_web_hard_pin_count:0,
      automatic_role_extension:false,
      automatic_solver_execution:false
    };
  }
  const api={REVIEW_ID,boundaries,validateAnswers,buildResponse};
  root.BoundaryReview=api;
  if(typeof module!=='undefined' && module.exports) module.exports=api;
})(globalThis);
