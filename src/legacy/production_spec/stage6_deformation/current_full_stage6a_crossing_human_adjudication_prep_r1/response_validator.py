"""Validate a supplied Human response; never create approval or closure artifacts."""
import json,datetime,sys
from pathlib import Path
CASE_CHOICES={'NO_VISIBLE_PRODUCT_DEFECT','VISIBLE_PRODUCT_DEFECT_BLOCKER','UNRESOLVED_NEEDS_BETTER_EVIDENCE'}
PAIR_CHOICES={'ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT','BLOCKING_VISIBLE_PRODUCT_DEFECT','UNRESOLVED_NEEDS_BETTER_EVIDENCE'}
def validate(data,config):
 errors=[];missing=[]
 for k,v in config['fixed_fields'].items():
  if data.get(k)!=v:errors.append('BOUND_FIELD_MISMATCH:'+k)
 cases=data.get('case_reviews',[]);pairs=data.get('pair_reviews',[])
 if not isinstance(cases,list) or not isinstance(pairs,list):return {'valid':False,'complete':False,'closure_eligible':False,'errors':['REVIEW_LIST_TYPE'],'missing':[]}
 cmap={r.get('case_id'):r for r in cases};pmap={r.get('pair_id'):r for r in pairs}
 if len(cases)!=3 or set(cmap)!=set(config['case_ids']):errors.append('CASE_SCOPE_OR_DUPLICATE')
 if len(pairs)!=9 or set(pmap)!={p['pair_id'] for p in config['pairs']}:errors.append('PAIR_SCOPE_OR_DUPLICATE')
 for cid in config['case_ids']:
  if cmap.get(cid,{}).get('question_id')!=config['case_question_ids'][cid]:errors.append('CASE_QUESTION_MISMATCH:'+cid)
  answer=cmap.get(cid,{}).get('CASE_VISIBLE_PRODUCT_DEFECT')
  if answer is None:missing.append(cid)
  elif answer not in CASE_CHOICES:errors.append('INVALID_CASE_CHOICE:'+cid)
 for p in config['pairs']:
  r=pmap.get(p['pair_id'],{})
  if r.get('case_id')!=p['case_id'] or r.get('face_ids')!=p['face_ids'] or r.get('question_id')!=p['question_id']:errors.append('PAIR_IDENTITY_MISMATCH:'+p['pair_id'])
  answer=r.get('PAIR_ADJUDICATION')
  if answer is None:missing.append(p['pair_id'])
  elif answer not in PAIR_CHOICES:errors.append('INVALID_PAIR_CHOICE:'+p['pair_id'])
 scope=data.get('exact_scope_confirmation')
 if scope is None:missing.append('Q13')
 elif scope not in {'YES','NO'}:errors.append('INVALID_SCOPE_CHOICE')
 for cid in config['case_ids']:
  c=cmap.get(cid,{});ans=c.get('CASE_VISIBLE_PRODUCT_DEFECT');rr=[pmap.get(p['pair_id'],{}).get('PAIR_ADJUDICATION') for p in config['pairs'] if p['case_id']==cid]
  if ans=='NO_VISIBLE_PRODUCT_DEFECT' and 'BLOCKING_VISIBLE_PRODUCT_DEFECT' in rr:errors.append('CASE_NO_PAIR_BLOCKING_CONTRADICTION:'+cid)
  if ans=='VISIBLE_PRODUCT_DEFECT_BLOCKER' and rr and all(a=='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT' for a in rr):
   if c.get('visible_defect_not_attributable_to_named_pairs') is not True or not isinstance(c.get('notes'),str) or not c['notes'].strip():errors.append('CASE_BLOCK_ALL_PAIRS_ACCEPTED_NEEDS_EXPLICIT_NOTE:'+cid)
 complete=not missing
 if data.get('all_questions_answered')!=complete:errors.append('ANSWERED_FLAG_MISMATCH')
 if complete:
  try:
   t=datetime.datetime.fromisoformat(str(data.get('timestamp')).replace('Z','+00:00'))
   if t.tzinfo is None:raise ValueError()
  except (ValueError,TypeError):errors.append('TIMESTAMP_REQUIRED_ISO_WITH_TIMEZONE')
 unresolved=any(cmap.get(cid,{}).get('CASE_VISIBLE_PRODUCT_DEFECT')=='UNRESOLVED_NEEDS_BETTER_EVIDENCE' for cid in config['case_ids']) or any(pmap.get(p['pair_id'],{}).get('PAIR_ADJUDICATION')=='UNRESOLVED_NEEDS_BETTER_EVIDENCE' for p in config['pairs'])
 eligible=not errors and complete and not unresolved and scope=='YES' and all(cmap.get(cid,{}).get('CASE_VISIBLE_PRODUCT_DEFECT')=='NO_VISIBLE_PRODUCT_DEFECT' for cid in config['case_ids']) and all(pmap.get(p['pair_id'],{}).get('PAIR_ADJUDICATION')=='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT' for p in config['pairs'])
 return {'valid':not errors,'complete':complete,'closure_eligible':eligible,'unresolved':unresolved,'errors':errors,'missing':missing,'approval_or_closure_written':False}
if __name__=='__main__':
 config=json.loads((Path(__file__).parent/'RESPONSE_VALIDATION_CONFIG_R1.json').read_text(encoding='utf-8-sig'))
 data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
 print(json.dumps(validate(data,config),ensure_ascii=False,indent=2))
