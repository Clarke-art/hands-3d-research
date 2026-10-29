from pathlib import Path
from collections import Counter,defaultdict
import re,json,sys,hashlib
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(r'<HANDS_ROOT>')
OUT=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_cap_dependency_blast_radius_audit_r1'
SNAP=json.loads((OUT/'PROTECTED_STATE_BEFORE.json').read_text(encoding='utf-8'))
OLD={151,158,1061,1074,1076,2189,2192,2569,2577}
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Qualified semantic references: never treat every numeric vertex ID or generic influence/forearm 'cap' as anatomical evidence.
SEM=re.compile(r'THUMB_DISTAL_CAP_AUDIT|thumb_cap_vertex|cap_vertices|cap_vertex_ids|cap_verts|distal_cap_vertex|approved_distal_cap|ref\s*\[\s*[\"\']cap[\"\']|(?:ctx|RG|LAB)\s*\[\s*[\"\'](?:cap|distal_cap|cap_vertices|CAP)[\"\']',re.I)
STRICT=re.compile(r'(?<![\d.])(?:13\.1646\d*|5\.964(?:3\d*|27\d*)|6\.5160\d*|6\.51595\d*)(?!\d)')
DIRECT=[];RECORDS=[];STRICTROWS=[];PARSE=[];EXCLUDED=[];SOURCES={}
TEXT_EXT={'.json','.md','.py','.js','.cjs','.html','.txt','.toml','.yaml','.yml','.csv','.obj'}
def evidence_text(p,text):
 hits=[]
 for m in SEM.finditer(text):
  line=text.count('\n',0,m.start())+1
  hits.append({'kind':'QUALIFIED_CAP_SEMANTIC_REFERENCE','locator':f'line {line}','excerpt':text[max(0,m.start()-65):min(len(text),m.end()+110)].replace('\n',' ')})
  if len(hits)>=12:break
 return hits
def json_membership(d):
 found=[];todo=[(d,'$','')]
 while todo:
  v,path,context=todo.pop()
  if isinstance(v,dict):
   for k,x in v.items():
    ctx=(context+'/'+k)[-350:]
    if isinstance(x,list) and re.search(r'(?:thumb.?cap|distal.?cap|cap.?vert|cap.?id|/CAP$)',ctx,re.I):
     numeric=[a for a in x if isinstance(a,int) and not isinstance(a,bool)]
     old=sorted(set(numeric)&OLD)
     if old:found.append({'kind':'OLD_CAP_ID_SET_IN_SEMANTIC_FIELD','locator':path+'.'+k,'old_ids':old,'field_length':len(x)})
    # Never descend into protected hash ledgers as though their strings are active selectors.
    todo.append((x,path+'.'+k,ctx))
  elif isinstance(v,list):
   for i,x in enumerate(v):
    if isinstance(x,(dict,list)):todo.append((x,path+f'[{i}]',context))
 return found[:20]
def stage(rel):
 parts=Path(rel).parts
 if 'stage5_production_rig' in parts:return parts[parts.index('stage5_production_rig')+1]
 if 'stage6_deformation' in parts:return parts[parts.index('stage6_deformation')+1]
 if 'stage4_blender' in parts:return 'stage4_blender'
 return parts[0]
CORRECTION_MARKERS=['human_cap_authority_correction','human_cap_authority_freeze','cap_boundary_e_five','thumb_distal_cap_boundary_review','native_branch_identity','manual_anatomical_reference','human_authority_and_v2192','narrow_anatomical_review']
RECEIPT=re.compile(r'FROZEN_HASH|FROZEN_INPUT|HASHES_BEFORE|HASH_VERIFICATION|OUTPUT_VERIFICATION|PROTECTED_STATE|extract_hash_check|reproducibility_check',re.I)
STATIC=re.compile(r'TOPOLOGY_DRIFT|ZERO_POSE_BIND|PARENT_BIND|VERTEX_INFLUENCE|PRUNE|POSTSAVE|REPRODUCIBILITY|ZERO_RESTORE',re.I)
for rel,digest in sorted(SNAP['workspace'].items()):
 p=ROOT/rel
 if '__pycache__' in p.parts or '.workbuddy' in p.parts or p.suffix in ['.pyc','.pyo']:
  EXCLUDED.append({'path':rel,'reason':'Execution cache/assistant metadata; protected, excluded from semantic artifact counts'});continue
 st=stage(rel);text='';jdata=None;ev=[]
 if p.suffix.lower() in TEXT_EXT:
  try:text=p.read_text(encoding='utf-8-sig')
  except UnicodeError:
   try:text=p.read_text(encoding='gb18030')
   except UnicodeError:PARSE.append({'path':rel,'error':'Text encoding unresolved'})
  if text:ev=evidence_text(p,text)
  if p.suffix=='.json':
   try:jdata=json.loads(text);ev=json_membership(jdata)+ev
   except Exception as e:PARSE.append({'path':rel,'error':str(e)[:250],'historical_file_untouched':True})
 corrected=any(m in st for m in CORRECTION_MARKERS)
 downstream=st.startswith(('stage5a_r2a','stage5a_r2b','stage5a_freeze','stage5b','stage6'))
 report_only=p.suffix in ['.md','.html','.png','.jpg','.jpeg','.svg']
 receipt=bool(RECEIPT.search(p.name))
 static=bool(STATIC.search(p.name))
 formalreview='endpoint_authority_review' in st or 'feasibility_audit' in st
 kind='';tier='';basis='';cont=[]
 if ev:
  kind='DIRECT_DEPENDENCY';basis='Qualified direct reference to historical cap authority or cap-ID set; reporting usage distinguished from active implementation below'
  if corrected or receipt:cont=['REPORTING_ONLY_CONTAMINATION'];tier='TIER_0'
  elif st.startswith('stage6'):
   cont=['VALIDATOR_CONTAMINATION']+(['AUTHORITY_CONTAMINATION'] if 'ownership' in p.name.lower() else [])
   tier='TIER_2' if 'r3_thumb' in st or st=='stage6b_r1a_seam_provenance' or ('ownership' in p.name.lower()) else ('TIER_1' if report_only or static else 'TIER_4')
  elif st.startswith('stage5b'):
   cont=['IMPLEMENTATION_CONTAMINATION'] if p.suffix=='.py' and any(x in p.name for x in ['build','common','bind']) else ['VALIDATOR_CONTAMINATION']
   tier='TIER_2' if p.suffix=='.py' or formalreview else ('TIER_1' if report_only or static else 'TIER_3')
  else:cont=['AUTHORITY_CONTAMINATION'];tier='TIER_2' if not report_only else 'TIER_1'
 elif corrected or receipt:
  kind='NO_CAP_DEPENDENCY';tier='TIER_0';basis='Corrected native independent evidence or a byte/hash receipt; references are provenance targets, never a selector input'
 elif not downstream:
  kind='NO_CAP_DEPENDENCY';tier='TIER_0';basis='Stage0–4/source-reference or pre-R2A Stage5A asset: temporal/constructor upstream of old cap9, no qualified cap-authority reference detected'
 elif st=='stage5a_r2a':
  if any(x in p.name.upper() for x in ['INDEX_MCP','OBJECT_FRAME','ORIGIN','V_S4A','V_S5A','DUMPVERTS']):
   kind='NO_CAP_DEPENDENCY';tier='TIER_0';basis='Independent origin/index MCP or stored geometry coordinate payload; no cap-derived bone/selector result used'
  elif p.suffix=='.blend':kind='DERIVED_DEPENDENCY';tier='TIER_3';cont=['IMPLEMENTATION_CONTAMINATION'];basis='s5a_r2a_build.py L163–190,L245–260 writes old-cap REP into TIP head/tail, IP tail and roll'
  else:kind='DERIVED_DEPENDENCY';tier='TIER_2' if not report_only else 'TIER_1';cont=['AUTHORITY_CONTAMINATION'];basis='R2A cap/TIP branch diagnostic or output; joint hierarchy and unrelated heads remain independent components'
 elif st=='stage5a_r2b':
  kind='DERIVED_DEPENDENCY';tier='TIER_2' if not report_only else 'TIER_1';cont=['AUTHORITY_CONTAMINATION'];basis='IP-to-cap feasibility uses frozen R2A cap endpoint; cannot establish true-cap feasibility'
 elif st.startswith('stage5a_freeze'):
  kind='TRANSITIVE_DEPENDENCY';tier='TIER_1';cont=['REPORTING_ONLY_CONTAMINATION'];basis='Mixed Human approval contains cap-derived THUMB_TIP/IP-tail claim; unrelated hierarchy/heads approval is retained'
 elif st.startswith('stage5b_freeze'):
  kind='TRANSITIVE_DEPENDENCY';tier='TIER_1' if not static else 'TIER_0';cont=['REPORTING_ONLY_CONTAMINATION'];basis='Historical skin approval/receipt for cap-dependent skin; remains a historical fact, cap-dependent qualification cannot be inherited'
 elif st=='stage5b_r1':
  if static:
   kind='VALIDATION_ONLY_DEPENDENCY';tier='TIER_1';cont=['VALIDATOR_CONTAMINATION'];basis='Structural arithmetic remains factual; current qualification must test reconciled data'
  else:
   kind='DERIVED_DEPENDENCY';tier='TIER_3' if p.suffix=='.blend' else ('TIER_2' if p.suffix=='.py' else 'TIER_1');cont=['IMPLEMENTATION_CONTAMINATION'];basis='R1 copies cap-derived R2A rig and uses live BH/BT for segment distances/radii/raw mu; no explicit old-cap ID selector'
 elif st.startswith(('stage5b_r1a','stage5b_r1b','stage5b_r1c','stage5b_r1d','stage5b_r1e')):
  if static:
   kind='VALIDATION_ONLY_DEPENDENCY';tier='TIER_1';cont=['VALIDATOR_CONTAMINATION'];basis='Topology/weight arithmetic itself independent; tests run on cap-derived skin and only preserve old-object numerical facts'
  elif p.suffix=='.blend' or (p.suffix=='.json' and any(x in p.name for x in ['WEIGHT_DELTA','REGION','BUILD'])):
   kind='DERIVED_DEPENDENCY';tier='TIER_3';cont=['IMPLEMENTATION_CONTAMINATION'];basis='Stage builder/history links old cap-derived ownership/masks/weights into this data artifact'
  elif p.suffix=='.py':
   kind='DERIVED_DEPENDENCY';tier='TIER_2';cont=['IMPLEMENTATION_CONTAMINATION'];basis='Helper imports cap-derived r1a/r1b or R2/R3 context; script inspected as source, never executed'
  elif p.suffix in ['.png','.jpg','.svg']:
   kind='TRANSITIVE_DEPENDENCY';tier='TIER_0';cont=['REPORTING_ONLY_CONTAMINATION'];basis='Frozen historical render of contaminated input; retain, do not advertise as current qualification'
  else:
   kind='TRANSITIVE_DEPENDENCY';tier='TIER_2' if formalreview else 'TIER_1';cont=['REPORTING_ONLY_CONTAMINATION'];basis='Downstream saved metric/status/report inherits cap-derived skin or endpoint result'
 elif st.startswith('stage6'):
  r3='r3_thumb_tip' in st;r2=st=='stage6b_r1a_seam_provenance' or 'OWNERSHIP' in p.name.upper()
  if static:
   kind='VALIDATION_ONLY_DEPENDENCY';tier='TIER_1';cont=['VALIDATOR_CONTAMINATION'];basis='Structural validator can remain algorithmically valid, but its harness/current-data qualification needs static revalidation'
  elif p.suffix=='.py':
   kind='DERIVED_DEPENDENCY';tier='TIER_2';cont=['VALIDATOR_CONTAMINATION'];basis='Executable helper inherits cap-derived rig/skin/ownership context, independent angle/math code separated at component level'
  elif r3 or r2:
   kind='DERIVED_DEPENDENCY';tier='TIER_2' if p.suffix not in ['.md','.png'] else 'TIER_1';cont=['AUTHORITY_CONTAMINATION'];basis='R2 seed/R3 strong anchors and inherited geometry determine label, boundary and ownership classifier evidence'
  elif p.suffix=='.png':
   kind='TRANSITIVE_DEPENDENCY';tier='TIER_0';cont=['REPORTING_ONLY_CONTAMINATION'];basis='Historical posed render is retained as actual old-harness observation'
  else:
   kind='TRANSITIVE_DEPENDENCY';tier='TIER_4' if p.suffix in ['.json','.blend'] else 'TIER_1';cont=['IMPLEMENTATION_CONTAMINATION' if p.suffix=='.blend' else 'VALIDATOR_CONTAMINATION'];basis='Historical deformed mesh/pose results inherit cap-driven rig/skin; requalify corrected production, preserve measured numbers'
 else:
  kind='UNRESOLVED';tier='TIER_1';basis='No reliable generator or component lineage established; absence of literal cap IDs is not proof of independence'
 if any(x['path']==rel for x in PARSE) and downstream and not ev:
  kind='UNRESOLVED';tier='TIER_1';basis+='; invalid/unreadable legacy data limits machine-verifiable provenance'
 # Qualified-cap audit can itself be an independent observation. Never invalidate its raw mesh value by classification alone.
 currentrole='CORRECTION_OR_HISTORICAL_PROVENANCE_ONLY' if corrected or receipt or p.suffix=='.png' else 'FUTURE_REUSE_REQUIRES_RECONCILIATION' if downstream else 'UPSTREAM_INDEPENDENT'
 record={'artifact_id':rel,'path':rel,'sha256':digest,'stage':st,'dependency_class':kind,'evidence':ev,'basis':basis,
  'classification_confidence':'DIRECT_SOURCE_OR_SET' if ev else 'DOCUMENTED_STAGE_LINEAGE' if kind not in ['NO_CAP_DEPENDENCY','UNRESOLVED'] else 'UPSTREAM_OR_CORRECTION_PROVENANCE' if kind=='NO_CAP_DEPENDENCY' else 'INSUFFICIENT_EVIDENCE',
  'contamination_dimensions':cont,'remediation_tier':tier,'current_role':currentrole,'historical_file_action':'PRESERVE_BYTE_IDENTICAL',
  'numeric_observation':'NUMERIC_OBSERVATION_STILL_FACTUAL_IF_MEASURED_ON_RECORDED_INPUT','qualification_scope':'Component-level exceptions in detailed audits override mixed-file severity; counts assign exactly one primary dependency class per file'}
 RECORDS.append(record)
 if ev:DIRECT.append({'artifact':rel,'sha256':digest,'references':ev,'dependency_class':kind,'role':currentrole,'contamination_dimensions':cont})
 if STRICT.search(text):
  hitrows=[]
  for m in STRICT.finditer(text):
   excerpt=text[max(0,m.start()-110):min(len(text),m.end()+180)].replace('\n',' ')
   hitrows.append({'line':text.count('\n',0,m.start())+1,'value_text':m.group(),'excerpt':excerpt})
   if len(hitrows)>=12:break
  strictcontext=any(x in (text[:3000]+p.name).lower() for x in ['cap','strict','feasib','endpoint','bound','report','status'])
  if strictcontext:
   interpretation=any(x in st for x in ['feasibility_audit','endpoint_authority_review']) or st=='stage5b_r1e'
   classes=['HISTORICAL_VALUE_ONLY'] if corrected or receipt else (['HISTORICAL_VALUE_ONLY','INVALIDATED_INTERPRETATION','RECOMPUTE_REQUIRED'] if interpretation else ['HISTORICAL_VALUE_ONLY','INVALIDATED_INTERPRETATION'])
   STRICTROWS.append({'path':rel,'sha256':digest,'dependency_class':kind,'reference_examples':hitrows,'reference_example_limit':12,'complete_hit_count':len(STRICT.findall(text)),
    'scope_classifications':classes,'new_true_cap_bound_recompute':'PENDING UNTIL DEPENDENCY RECONCILIATION COMPLETE','historical_arithmetic_preserved':True,'current_anatomical_endpoint_authority':'INVALIDATED' if not (corrected or receipt) else 'EXPLICITLY_SUPERSEDED_HISTORICAL_REFERENCE'})
COUNTS=Counter(x['dependency_class'] for x in RECORDS);TIERS=Counter(x['remediation_tier'] for x in RECORDS)
assert sum(COUNTS.values())==len(RECORDS)==sum(TIERS.values())
dump('CAP_DIRECT_REFERENCE_AUDIT.json',{'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','artifact_counting_unit':'Unique preexisting workspace file, one primary class; content match is reference presence, not proof of causal label changes','audit_universe_count':len(RECORDS),'classification_counts':dict(COUNTS),'remediation_tier_counts':dict(TIERS),
 'direct_reference_artifacts':DIRECT,'artifact_classification':RECORDS,'excluded_protected_infrastructure':EXCLUDED,'legacy_parse_errors':PARSE,
 'method':'Qualified cap-ID fields and semantic authority text, plus reviewed constructors/source lineage; generic IDs, CAP_MAX flow capacities and forearm cap mentions excluded. Missing exact counterfactual effects are recorded UNRESOLVED in component audits.',
 'all_requested_stage_and_audit_families_scanned':True,'absence_of_literal_ids_used_as_independence_proof':False})
dump('STRICT_BOUND_DEPENDENCY_INVALIDATION_AUDIT.json',{'execution':'CAP_DEPENDENCY_BLAST_RADIUS_AUDIT_R1','settled_invalidations':{'13.1646_mm_path':'INVALIDATED AS TRUE_THUMB_CAP→COLLAR ANATOMICAL ENDPOINT EVIDENCE','CMC_MCP_L3_5.9643':'INVALIDATED AS TRUE_THUMB_CAP ENDPOINT BOUND','FULL_OPP_L3_6.5160':'INVALIDATED AS TRUE_THUMB_CAP ENDPOINT BOUND'},
 'reference_artifact_count':len(STRICTROWS),'references':STRICTROWS,'historical_numeric_observations':'PRESERVED; fixed-ID path arithmetic and actual old-blend motion remain factual',
 'reporting_decision_invalidation':'Any mesh-limit/retopo/no-legal-weight recommendation that rests on a TRUE_THUMB_CAP endpoint interpretation must not be inherited; historical failed deformation measurements are not erased',
 'new_true_cap_bounds':'PENDING UNTIL DEPENDENCY RECONCILIATION COMPLETE','prerequisites':['kinematic tip/IP-tail dependency resolved','R2/R3 anchors/ownership reconciled','cap skin driver authority reconciled','reconciled skin/endpoint field fixed'],
 'strict_bound_recompute_runs':0,'cap_to_collar_path_runs':0,'all_matched_references_inventoried':True})
dump('_INVENTORY_SUMMARY.json',{'classes':dict(COUNTS),'tiers':dict(TIERS),'artifact_count':len(RECORDS),'direct_reference_count':len(DIRECT),'strict_reference_artifacts':len(STRICTROWS),'excluded_count':len(EXCLUDED),'parse_errors':PARSE})
print(json.dumps({'artifact_count':len(RECORDS),'classes':dict(COUNTS),'tiers':dict(TIERS),'strict_reference_artifacts':len(STRICTROWS),'legacy_parse_errors':len(PARSE),'excluded_cache_metadata':len(EXCLUDED)}))
