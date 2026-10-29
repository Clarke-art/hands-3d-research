from common import *
import copy,subprocess,re,datetime
from html.parser import HTMLParser
from PIL import Image
from response_validator import validate
config=read(OUT/'RESPONSE_VALIDATION_CONFIG_R1.json');template=read(OUT/'CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_TEMPLATE_R1.json');checks={}
class PageParser(HTMLParser):
 def __init__(self):super().__init__();self.inputs=[];self.links=[];self.articles=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='input':self.inputs.append(a)
  if tag in ['img','a','link','script']:self.links.extend(a[k] for k in ['src','href'] if k in a)
  if tag=='article':self.articles.append(a.get('id'))
parser=PageParser();page=(OUT/'review.html').read_text(encoding='utf-8');parser.feed(page)
groups={a['name'] for a in parser.inputs if a.get('type')=='radio'}
checks['exact13_questions_no_defaults']=groups=={f'Q{i}' for i in range(1,14)} and not any('checked' in a for a in parser.inputs)
checks['three_case_only_homepage']=parser.articles==config['case_ids']
checks['case_pair_template_unanswered']=all(r['CASE_VISIBLE_PRODUCT_DEFECT'] is None for r in template['case_reviews']) and all(r['PAIR_ADJUDICATION'] is None for r in template['pair_reviews']) and template['exact_scope_confirmation'] is None and template['timestamp'] is None and template['all_questions_answered'] is False
checks['cross_pose_warning_present']='IDX_MCP_30 [1226,2742] = NOT_COVERED_BY_EXISTING_APPROVAL' in page
for p in parser.links:
 if not p.startswith('#'):assert (OUT/p.split('#')[0]).is_file(),p
checks['all_local_links_exist']=True
# Synthetic in-memory validator cases only. No Human answers/receipts are stored.
base=copy.deepcopy(template)
for r in base['case_reviews']:r['CASE_VISIBLE_PRODUCT_DEFECT']='NO_VISIBLE_PRODUCT_DEFECT'
for r in base['pair_reviews']:r['PAIR_ADJUDICATION']='ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT'
base.update(exact_scope_confirmation='YES',timestamp='2026-10-06T00:00:00Z',all_questions_answered=True)
samples=[('unanswered_template',template,True,False,False),('synthetic_complete_consistent',base,True,True,True)]
def sample(name,mutate,valid,complete=True,eligible=False):
 d=copy.deepcopy(base);mutate(d);samples.append((name,d,valid,complete,eligible))
sample('bound_hash_mismatch',lambda d:d.update(production_asset_hash='0'*64),False)
sample('duplicate_pair',lambda d:d['pair_reviews'].__setitem__(8,copy.deepcopy(d['pair_reviews'][0])),False,False)
sample('pair_pose_scope_wrong',lambda d:d['pair_reviews'][2].update(case_id='IDX_MCP_45'),False)
sample('case_no_pair_blocker_contradiction',lambda d:d['pair_reviews'][0].update(PAIR_ADJUDICATION='BLOCKING_VISIBLE_PRODUCT_DEFECT'),False)
sample('case_block_all_pairs_accept_no_note',lambda d:d['case_reviews'][0].update(CASE_VISIBLE_PRODUCT_DEFECT='VISIBLE_PRODUCT_DEFECT_BLOCKER'),False)
sample('case_block_unmapped_explicit_note',lambda d:d['case_reviews'][0].update(CASE_VISIBLE_PRODUCT_DEFECT='VISIBLE_PRODUCT_DEFECT_BLOCKER',visible_defect_not_attributable_to_named_pairs=True,notes='Synthetic validator test: defect explicitly outside named pair.'),True)
sample('unresolved_pair_never_closure',lambda d:d['pair_reviews'][0].update(PAIR_ADJUDICATION='UNRESOLVED_NEEDS_BETTER_EVIDENCE'),True)
sample('unresolved_case_never_closure',lambda d:d['case_reviews'][0].update(CASE_VISIBLE_PRODUCT_DEFECT='UNRESOLVED_NEEDS_BETTER_EVIDENCE'),True)
sample('scope_NO_never_closure',lambda d:d.update(exact_scope_confirmation='NO'),True)
sample('missing_one_pair',lambda d:(d['pair_reviews'][0].update(PAIR_ADJUDICATION=None),d.update(all_questions_answered=False)),True,False)
sample('question_identity_mismatch',lambda d:d['pair_reviews'][0].update(question_id='Q7'),False)
results=[]
js="const fs=require('fs'),vm=require('vm');const v=require(process.argv[1]);const x=JSON.parse(fs.readFileSync(0,'utf8'));for(const s of x.scripts)new vm.Script(s);process.stdout.write(JSON.stringify(x.samples.map(d=>v.validate(d,x.config))));"
scripts=re.findall(r'<script>([\s\S]*?)</script>',page)
node=subprocess.run(['node','-e',js,str(OUT/'response-validator.js')],input=json.dumps({'config':config,'samples':[s[1] for s in samples],'scripts':scripts}),text=True,capture_output=True,check=True)
jresults=json.loads(node.stdout)
for (name,d,valid,complete,eligible),jr in zip(samples,jresults):
 py=validate(d,config);ok=py['valid']==valid and py['complete']==complete and py['closure_eligible']==eligible and all(py[k]==jr[k] for k in ['valid','complete','closure_eligible','unresolved','errors','missing'])
 results.append({'synthetic_test':name,'passed':ok,'no_response_or_approval_saved':True})
checks['response_validator13_synthetic_cases_python_JS_agree']=all(r['passed'] for r in results)
dump('RESPONSE_VALIDATOR_VERIFICATION_R1.json',{'status':'PASS' if checks['response_validator13_synthetic_cases_python_JS_agree'] else 'FAIL_CLOSED','tests':results,'synthetic_only':True,'Human_response_files_written':0,'Human_approvals_written':0,'inline_browser_script_syntax_checked':True})
visual=read(OUT/'RENDER_ONLY_VISUAL_MANIFEST_R1.json');pairs=read(OUT/'CURRENT_FULL_STAGE6A_PAIR_FORENSIC_EVIDENCE_R1.json')['pairs'];casee=read(OUT/'CURRENT_FULL_STAGE6A_CASE_VISUAL_EVIDENCE_R1.json')['cases'];coords=read(FRESH/'POSED_COORDINATES_R1.json')['positions_world_m']
checks['render_only_no_pose_measurement']=visual['production_blend_opens']==visual['pose_applications']==visual['qualified_asset_depsgraph_evaluations']==visual['crossing_classifier_calls']==visual['edge_strain_calls']==0
checks['display_coordinates_exact']=all(p['all3416_positions_exact'] and p['all3414_face_cycles_exact'] and p['armature_objects']==p['mesh_modifiers']==0 and p['source_case_coordinate_digest']==digest(coords[p['case_id']]) for p in visual['display_coordinate_proofs'])
for r in visual['renders']:
 im=Image.open(OUT/r['file']);im.verify();assert Image.open(OUT/r['file']).size==(1600,1100)
 assert r['source_case_coordinate_digest']==digest(coords[r['source_case']]) and r['all_native_coordinates_exact_after_render']
checks['three_cases_four_plain_views']=len(casee)==3 and all(len(c['plain_surface_evidence'])==4 and all(r['kind']=='PLAIN_PRODUCT' and r['plain_all3414_faces_present'] and not r['plain_colored_overlay'] and not r['plain_crossing_markers'] for r in c['plain_surface_evidence']) for c in casee)
checks['nine_complete_forensic']=len(pairs)==9 and all(len(p['ordinary_surface_context'])==3 and len(p['colored_context'])==2 and p['isolated_pair'] and p['exact_stored_points_segment'] and p['vertex_ids'] for p in pairs)
checks['THIP15_six_large_readable']=len([p for p in pairs if p['case_id']=='TH_IP_15'])==6 and all(p['ordinary_surface_context'][0]['resolution']==p['exact_stored_points_segment']['resolution']==[1600,1100] for p in pairs if p['case_id']=='TH_IP_15')
inputs=read(OUT/'CURRENT_FULL_STAGE6A_HUMAN_REVIEW_INPUT_HASHES_R1.json');checks['all_inputs_bound_unchanged']=all(inputs['checks'].values()) and all(sha(ROOT/r['path'])==r['sha256'] for r in inputs['sources'].values())
checks['current_machine9_untouched']=read(FRESH/'FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1_STATUS.json')['MACHINE_HARD_BLOCKER_COUNT']==9
checks['prior_three_contacts_not_questions']=not any(p['case_id'] in ['TH_IP_30','IDX_MCP_45'] for p in template['pair_reviews'])
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();changed=[n for n,h in before.items() if n in after and after[n]!=h];deleted=sorted(set(before)-set(after));new=sorted(set(after)-set(before));drift=len(changed)+len(deleted)+len(new);checks['production_all_history_no_drift']=drift==0
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS' if drift==0 else 'FAIL_CLOSED','PRODUCTION_DRIFT':drift,'protected_preexisting_file_count':len(before),'changed_files':changed,'deleted_files':deleted,'new_files_outside_current_phase':new,'all_preexisting_bytes_exact':before==after,'current_asset':ref(CAND),'current_Full42_artifacts_unchanged':True,'production_saves':0,'qualification_pose_or_metric_runs':0})
passed=all(checks.values());verdict='READY_FOR_HUMAN_CURRENT_FULL_STAGE6A_CROSSING_ADJUDICATION' if passed else 'FAIL_CLOSED_HUMAN_ADJUDICATION_PREP'
status={'phase':PHASE,'CURRENT_MACHINE_BLOCKER_COUNT':9,'CURRENT_MACHINE_BLOCKER_CASE_COUNT':3,'CASE_REVIEW_COUNT':3,'PAIR_REVIEW_COUNT':9,'QUESTION_COUNT':13,'IDX_MCP_15_PAIR_COUNT':1,'IDX_MCP_30_PAIR_COUNT':2,'TH_IP_15_PAIR_COUNT':6,'ALL_9_CURRENT_METRICS_BOUND_TO_ACTIVE_AUTHORITY':checks['all_inputs_bound_unchanged'],'ALL_9_EVIDENCE_COMPLETE':checks['nine_complete_forensic'],'TH_IP_15_ALL_6_PAIRS_HAVE_LARGE_EVIDENCE':checks['THIP15_six_large_readable'],'IDX_MCP_30_PAIR_1226_2742_CROSS_POSE_WARNING_PRESENT':checks['cross_pose_warning_present'],'PREVIOUS_ACCEPTED_CONTACTS_REVIEWED_AGAIN':'NO','FULL42_RERUN':0,'FULL42_FORMAL_POSE_APPLICATIONS':0,'POSE_APPLICATIONS':0,'CROSSING_REMEASUREMENTS':0,'CROSSING_CLASSIFIER_RUNS':0,'GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'RIG_WRITES':0,'STAGE6B_RUNS':0,'HUMAN_APPROVAL_RECORDED':'NO','DORSAL_MCP_FULL_STAGE6A_MACHINE':'PASS','DORSAL_MCP_HUMAN_VISUAL_STATUS':'PENDING_HUMAN_REVIEW','PRODUCTION_PROMOTION':'NO','PRODUCTION_DRIFT':drift,'DEDICATED_PNG_COUNT':len(visual['renders']),'VERDICT':verdict,PHASE:verdict,'checks':checks,'minimal_gaps':[k for k,v in checks.items() if not v],'NEXT':'HUMAN_REVIEW_CURRENT_9_STAGE6A_CROSSINGS' if passed else 'STOP_MINIMAL_EVIDENCE_GAP','NEXT_EXECUTED':False,'STOP':'HUMAN REVIEW','CURRENT_ACTIVE_MACHINE_QUALIFICATION_UNCHANGED':'FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION','input_hashes':inputs['input_hashes'],'Human_answers_all_null':True,'cause_diagnosis_performed':False}
dump(PHASE+'_STATUS.json',status)
md=['# '+PHASE,'','**'+verdict+'**','', '仅准备Human product-visible acceptability证据，没有重跑Full42/pose/depsgraph坐标评估/crossing/edge-strain，没有classification改写或causal研究。当前active machine9/3保持FAIL_CLOSED。','', '| Required field | Result |','|---|---|']
md += ['| `'+k+'` | `'+str(v)+'` |' for k,v in status.items() if k.isupper() and not isinstance(v,dict)]
md+=['','## Current authority binding','','current status、current crossing audit、old9 fresh remeasurement、production asset以及saved current coordinate payload的SHA256见CURRENT_FULL_STAGE6A_HUMAN_REVIEW_INPUT_HASHES_R1.json。9个pose/pair、poke、bind facet、segment、classification按active current authority精确绑定；与用户12位小数显示完全匹配。pre-donor只作comparator，UNCHANGED_EXACT不是Human答案。','', '## Ordinary product evidence before forensic','','仅首页3个case。每case全手、主要/相反/oblique普通实体优先，无overlay/marker/透明/隐藏表面。每pair分别有1600×1100普通one-ring位置图、近距/alternate、彩色context、isolated及stored exact points/segment。THIP15六对全部独立放大，IDX30两对分开。sourcecurrent3416coordinates/native3414cycles逐项相同；camera/lighting/scale/source payload hash逐图记录。平滑仅为display normals，没有修改生产geometry。','', '有些machine pair被其它产品表面遮挡；普通视图忠实保留遮挡。forensic黄色投影定位框帮助定位，不声称被遮挡faces在成品上可见；绿色来自已保存intersection witness，未重新求交。Human可以选择UNRESOLVED_NEEDS_BETTER_EVIDENCE。Codex没有代替Human判断。','', '## Response safeguards','','13个radio问题全部无默认答案；3case与9pair不能互相代填。响应绑定所有source哈希，9个pair各自独立answer。NO-case与blocking-pair矛盾被拒绝；blocking-case但all-pairs accepted需要Human明确checkbox及说明，指出缺陷不对应命名pair。任何UNRESOLVED、scope NO或未完成答案均无closure eligibility。Python/浏览器JS校验器13个synthetic in-memory测试一致；没有保存synthetic Human responses或approval receipts。','', 'B2 IDX_MCP30[1226,2742]明确NOT_COVERED_BY_EXISTING_APPROVAL；旧45°收据不扩展。旧三条accepted scope仅reference，没有控件。donor ROI Human visual、14joint整体appearance、nail和Full Stage6A overall closure本轮不处理。','', '未来9/9accepted＋3caseNO＋scopeYES才eligible for独立CURRENT_FULL_STAGE6A_CROSSING_HUMAN_CLOSURE_R1；任一blocking→未来最小causal诊断；任一unresolved→需要更清楚的证据。本轮没有实际Human outcome，没有自动closure/repair。','', '## Read-only and stop','', str(len(before))+'个预存workspace文件before/after SHA256逐项相同；PRODUCTION_DRIFT='+str(drift)+'。生产asset未打开/保存，模型pose/骨骼/weights未操作。Blender只构建fixed-coordinate display copies并render；4次render-only执行（相机receipt纠正与位置视野补图），含12个display mesh构建，不是生产geometry写入。','', '[Focused Human review](CURRENT_FULL_STAGE6A_CROSSING_HUMAN_REVIEW_R1.html) · [Unanswered response template](CURRENT_FULL_STAGE6A_CROSSING_HUMAN_RESPONSE_TEMPLATE_R1.json)','', '**NEXT=HUMAN_REVIEW_CURRENT_9_STAGE6A_CROSSINGS。STOP — HUMAN REVIEW。**']
(OUT/(PHASE+'_REPORT.md')).write_text('\n'.join(md)+'\n',encoding='utf-8')
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',{'status':'PASS' if passed else 'FAIL_CLOSED','checks':checks,'failed_checks':status['minimal_gaps'],'synthetic_validator_tests':13,'protected_files':len(before),'production_drift':drift,'human_decisions_inferred_from_visual_inspection':0})
dump('OUTPUT_ARTIFACT_HASH_MANIFEST.json',{p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST.json'})
print(json.dumps({'verdict':verdict,'questions':13,'pairs':9,'images':len(visual['renders']),'protected_files':len(before),'drift':drift,'failed_checks':status['minimal_gaps']},ensure_ascii=False),flush=True)
assert passed,'FAIL CLOSED: evidence prep gap only; do not run poses or repair production'
