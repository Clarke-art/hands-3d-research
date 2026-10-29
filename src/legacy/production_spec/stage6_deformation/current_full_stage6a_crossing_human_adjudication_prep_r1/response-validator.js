(function(root){
function validate(data,config){
 const errors=[],missing=[],cases=data.case_reviews||[],pairs=data.pair_reviews||[];
 for(const [k,v] of Object.entries(config.fixed_fields))if(data[k]!==v)errors.push('BOUND_FIELD_MISMATCH:'+k);
 if(!Array.isArray(cases)||!Array.isArray(pairs))return {valid:false,complete:false,closure_eligible:false,errors:['REVIEW_LIST_TYPE'],missing:[]};
 const cmap=Object.fromEntries(cases.map(r=>[r.case_id,r])),pmap=Object.fromEntries(pairs.map(r=>[r.pair_id,r]));
 const eqset=(a,b)=>a.length===b.length&&a.every(x=>b.includes(x));
 if(cases.length!==3||!eqset(Object.keys(cmap),config.case_ids))errors.push('CASE_SCOPE_OR_DUPLICATE');
 if(pairs.length!==9||!eqset(Object.keys(pmap),config.pairs.map(p=>p.pair_id)))errors.push('PAIR_SCOPE_OR_DUPLICATE');
 const cc=['NO_VISIBLE_PRODUCT_DEFECT','VISIBLE_PRODUCT_DEFECT_BLOCKER','UNRESOLVED_NEEDS_BETTER_EVIDENCE'],pc=['ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT','BLOCKING_VISIBLE_PRODUCT_DEFECT','UNRESOLVED_NEEDS_BETTER_EVIDENCE'];
 for(const cid of config.case_ids){if(cmap[cid]?.question_id!==config.case_question_ids[cid])errors.push('CASE_QUESTION_MISMATCH:'+cid);const answer=cmap[cid]?.CASE_VISIBLE_PRODUCT_DEFECT;if(answer==null)missing.push(cid);else if(!cc.includes(answer))errors.push('INVALID_CASE_CHOICE:'+cid);}
 for(const p of config.pairs){const r=pmap[p.pair_id]||{};if(r.case_id!==p.case_id||JSON.stringify(r.face_ids)!==JSON.stringify(p.face_ids)||r.question_id!==p.question_id)errors.push('PAIR_IDENTITY_MISMATCH:'+p.pair_id);if(r.PAIR_ADJUDICATION==null)missing.push(p.pair_id);else if(!pc.includes(r.PAIR_ADJUDICATION))errors.push('INVALID_PAIR_CHOICE:'+p.pair_id);}
 const scope=data.exact_scope_confirmation;if(scope==null)missing.push('Q13');else if(!['YES','NO'].includes(scope))errors.push('INVALID_SCOPE_CHOICE');
 for(const cid of config.case_ids){const c=cmap[cid]||{},rr=config.pairs.filter(p=>p.case_id===cid).map(p=>pmap[p.pair_id]?.PAIR_ADJUDICATION);
  if(c.CASE_VISIBLE_PRODUCT_DEFECT==='NO_VISIBLE_PRODUCT_DEFECT'&&rr.includes('BLOCKING_VISIBLE_PRODUCT_DEFECT'))errors.push('CASE_NO_PAIR_BLOCKING_CONTRADICTION:'+cid);
  if(c.CASE_VISIBLE_PRODUCT_DEFECT==='VISIBLE_PRODUCT_DEFECT_BLOCKER'&&rr.every(a=>a==='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT')&&(c.visible_defect_not_attributable_to_named_pairs!==true||typeof c.notes!=='string'||!c.notes.trim()))errors.push('CASE_BLOCK_ALL_PAIRS_ACCEPTED_NEEDS_EXPLICIT_NOTE:'+cid);
 }
 const complete=missing.length===0;if(data.all_questions_answered!==complete)errors.push('ANSWERED_FLAG_MISMATCH');
 if(complete&&(typeof data.timestamp!=='string'||!/(Z|[+-]\d\d:\d\d)$/.test(data.timestamp)||Number.isNaN(Date.parse(data.timestamp))))errors.push('TIMESTAMP_REQUIRED_ISO_WITH_TIMEZONE');
 const unresolved=cases.some(r=>r.CASE_VISIBLE_PRODUCT_DEFECT==='UNRESOLVED_NEEDS_BETTER_EVIDENCE')||pairs.some(r=>r.PAIR_ADJUDICATION==='UNRESOLVED_NEEDS_BETTER_EVIDENCE');
 const eligible=!errors.length&&complete&&!unresolved&&scope==='YES'&&config.case_ids.every(cid=>cmap[cid]?.CASE_VISIBLE_PRODUCT_DEFECT==='NO_VISIBLE_PRODUCT_DEFECT')&&config.pairs.every(p=>pmap[p.pair_id]?.PAIR_ADJUDICATION==='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT');
 return {valid:errors.length===0,complete,closure_eligible:eligible,unresolved,errors,missing,approval_or_closure_written:false};
}
if(typeof module!=='undefined')module.exports={validate};root.reviewResponseValidator={validate};
})(globalThis);
