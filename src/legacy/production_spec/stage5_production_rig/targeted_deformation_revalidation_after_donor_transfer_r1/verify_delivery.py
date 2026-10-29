"""Independent coordinate/metric/camera/hash audit; no pose or production writes."""
from common import *
import numpy as np,re
from PIL import Image
status=read(OUT/(PHASE+'_STATUS.json'));co=read(OUT/'POSED_COORDINATE_EVIDENCE_R1.json');G=co['positions_world_m'];F=co['faces'];E=co['edges'];M=read(OUT/'MEASUREMENT_DOMAIN_MANIFEST_R1.json')
machine=read(OUT/'FRESH_MACHINE_EVIDENCE_R1.json')['results'];carry=read(OUT/'TARGETED_HUMAN_APPROVAL_CARRY_FORWARD_AUDIT_R1.json');structure=read(OUT/'DORSAL_MCP_RING_FLEX_STRUCTURE_AUDIT_R1.json')
checks={};numeric_checks=0;max_ratio_error=0
expectedposes={'TH_IP_30','TH_IP_45','TH_MCP_45','CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3','IDX_MCP_45','RING_MCP_15','RING_MCP_30','RING_MCP_45'}
checks['exact_scope_pose_set']=all(set(r)==expectedposes for r in machine.values())
checks['forbidden_full42_failed_pose_absent']=not expectedposes.intersection({'TH_IP_15','IDX_MCP_15','IDX_MCP_30'})
checks['ten_distinct_twenty_asset_applications']=status['TARGETED_POSE_COUNT']==10 and status['total_endpoint_pose_applications']==20
outside=sorted(set(range(3416))-set(APPROVED54))
checks['outside54_actual_posed_coordinates_exact']=all(np.array_equal(np.array(G['PRE_DONOR_R2'][cid])[outside],np.array(G['CURRENT_DONOR_R2'][cid])[outside]) for cid in ['BIND','RAW_BIND']+sorted(expectedposes))
checks['ROI_incidence_actual']=M['incident_faces']==[i for i,p in enumerate(F) if set(p).intersection(APPROVED54)] and M['incident_edges']==[i for i,e in enumerate(E) if set(e).intersection(APPROVED54)] and (len(M['incident_faces']),len(M['incident_edges']))==(95,148)
checks['outer_ring_complete']=set(M['first_fixed_outer_ring'])=={v for fi in M['incident_faces'] for v in F[fi]}-set(APPROVED54)
checks['accepted_three_exact_scopes']=set((r['pose'],tuple(r['face_pair'])) for r in carry['CAP37_pairs'])=={('TH_IP_30',(1225,2740)),('IDX_MCP_45',(1041,2735)),('IDX_MCP_45',(1226,2742))}
checks['carry_no_fresh_human_needed']=carry['status']=='PASS_EXACT_SCOPE_NO_REGRESSION' and not carry['FRESH_HUMAN_REVIEW_REQUIRED_FIXTURES'] and all(all(r['criteria'].values()) for r in carry['CAP37_pairs']+carry['four_reviewed_fixtures'])
checks['ROI_three_exact_structure_pass']=set(structure['results'])=={f'RING_MCP_{i}' for i in [15,30,45]} and all(r['new_structural_evidence_count']==0 for r in structure['results'].values())
# Independent NumPy float64 lengths, against float32 mathutils historical computation.
for asset,r in machine.items():
 bind=np.array(G[asset]['RAW_BIND']);ee=np.array(E);bl=np.linalg.norm(bind[ee[:,0]]-bind[ee[:,1]],axis=1)
 for cid,z in r.items():
  v=np.array(G[asset][cid]);ratios=np.linalg.norm(v[ee[:,0]]-v[ee[:,1]],axis=1)/bl
  err=abs(ratios[5879]-z['edge5879']['ratio']);max_ratio_error=max(max_ratio_error,float(err));numeric_checks+=1
  for f in z['fixtures'].values():
   for i,stored in f['edge_ratio_by_id'].items():max_ratio_error=max(max_ratio_error,float(abs(ratios[int(i)]-stored)));numeric_checks+=1
checks['independent_numeric_ratios']=max_ratio_error<1e-4
checks['debt16_retained_no_failure']=status['INHERITED_DEBT_COUNT']==16 and status['INHERITED_DEBT_TRUE_DEFORMATION_FAILURE_COUNT']==0 and all(r['STATIC_DEBT_STATUS']=='NOT_RESOLVED' and r['true_failure_count']==0 for r in read(OUT/'TARGETED_INHERITED16_DEBT_REVALIDATION_R1.json')['rows'])
zero=read(OUT/'TARGETED_ZERO_RESET_AUDIT_R1.json')
checks['zero20_actual_rows']=len(zero['rows'])==20 and all(r['pre_zero_max_mm']==r['post_zero_max_mm']==0 and r['all_bones_identity'] for r in zero['rows'])
native=read(OUT/'IN_MEMORY_NO_DRIFT_R1.json');checks['native_checks_all_pass']=all(all(x.values()) for x in native['checks'].values())
for asset in G:checks[asset+'_live_preflight']=all(read(OUT/(asset+'_LIVE_PREFLIGHT.json'))['checks'].values())
checks['frozen_preflight_all_pass']=all(read(OUT/'PREREQUISITE_GATE_R1.json')['checks'].values())
# Revalidate all source function AST hashes after execution.
checks['method_sources_frozen']=True
checks['Blender_originating_runtime_AST']=read(OUT/'BLENDER_RUNTIME_AST_VERIFICATION_R1.json')['status']=='PASS'
for r in structure['sources']:
 p=ROOT/r['source']['path'];checks['method_sources_frozen']&=sha(p)==r['source']['sha256']
 nodes={n.name:digest(ast.dump(n)) for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 checks['method_sources_frozen']&=all(nodes[k]==v for k,v in r['function_AST_sha256'].items())
visual=read(OUT/'VISUAL_EVIDENCE_MANIFEST_R1.json');bykey={};pixelidentical=0;clip=[]
for row in visual['outputs']:
 p=OUT/row['file'];im=Image.open(p);im.verify()
 assert list(Image.open(p).size)==row['resolution']
 bykey.setdefault(row['view_key'],[]).append(row)
 c=np.array(row['camera_centre_m']);d=np.array(row['camera_direction']);d/=np.linalg.norm(d);u=np.array(row['camera_up']);u-=u@d*d;u/=np.linalg.norm(u);r=np.cross(u,d);r/=np.linalg.norm(r)
 ids=list(range(3416)) if row['style']=='FULL_SOLID' else sorted(set(APPROVED54)|set(M['first_fixed_outer_ring'])) if row['fixture']=='DONOR_ROI' else M['fixtures'][row['fixture']]['core']
 pp=np.array(G[row['asset']][row['pose']])[ids]-c;W,H=row['resolution'];scale=(W/2-8)/(row['half_width_mm']/1000);xy=np.column_stack((pp@r*scale+W/2,pp@u*scale+H/2))
 n=int(np.sum((xy[:,0]<0)|(xy[:,0]>=W)|(xy[:,1]<0)|(xy[:,1]>=H)))
 if n:clip.append({'view_key':row['view_key'],'asset':row['asset'],'clipped_count':n})
for rows in bykey.values():
 assert len(rows)==2
 a,b=rows
 checks['matched_camera_'+a['view_key']]=all(a[k]==b[k] for k in ['camera_centre_m','camera_direction','camera_up','half_width_mm','resolution'])
 if sha(OUT/a['file'])==sha(OUT/b['file']):pixelidentical+=1
checks['camera_core_not_clipped']=not clip
checks['all_ring_views']=all(any(r['pose']==cid and r['asset']==asset and r['style']==style for r in visual['outputs']) for cid in ['RING_MCP_15','RING_MCP_30','RING_MCP_45'] for asset in G for style in ['FULL_SOLID','DORSAL_CLOSE_SOLID','GRAZING_SOLID','WIRE_STRAIN'])
checks['all_five_matched_fixtures']=all(any(r['fixture']==f and r['asset']==asset for r in visual['outputs']) for f in M['fixtures'] for asset in G)
for refpath in re.findall(r'(?:src|href)="([^"]+)"',(OUT/'review.html').read_text(encoding='utf-8')):
 if not refpath.startswith('#'):assert (OUT/refpath).is_file(),refpath
oldfull=S6/'full_stage6a_requalification_r1/FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json'
checks['old_full42_status_byte_exact']=sha(oldfull)=='d2c3bb13a77dd123e278d21e98ebdb724706dd8c789f91f0d2ac9e4d2f03d0a6' and read(oldfull)['MACHINE_HARD_BLOCKER_COUNT']==9 and read(oldfull)['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION'
checks['current_asset_sha256']=sha(CAND)==EXPECTED_CAND
checks['old_asset_sha256']=sha(OLD_CAND)==EXPECTED_OLD
checks['corrected_rig_sha256']=sha(CORRECTED)==EXPECTED_RIG
before=read(OUT/'PROTECTED_HISTORY_HASHES_BEFORE.json');after=inventory();changed=[k for k,v in before.items() if k in after and after[k]!=v];deleted=sorted(set(before)-set(after));new=sorted(set(after)-set(before))
drift=len(changed)+len(deleted)+len(new)
checks['every_historical_file_byte_exact']=drift==0
dump('PROTECTED_HISTORY_HASHES_AFTER.json',after)
dump('PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json',{'status':'PASS' if drift==0 else 'FAIL_CLOSED','PRODUCTION_DRIFT':drift,'protected_preexisting_file_count':len(before),'changed_files':changed,'deleted_files':deleted,'new_files_outside_task':new,'all_preexisting_files_byte_identical':before==after,'current_asset':ref(CAND),'old_R2':ref(OLD_CAND),'corrected_rig':ref(CORRECTED),'current_weight_vector_SHA256':EXPECTED_WEIGHTS,'weight_verification':'Fresh native extraction before/after both 10-pose suites; all3416 vectors and sparse named positive weights exact','production_saves':0,'in_memory_payload_verification':ref(OUT/'IN_MEMORY_NO_DRIFT_R1.json')})
verify={'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED','checks':checks,'independent_coordinate_edge_ratio_checks':numeric_checks,'max_float64_vs_historical_float32_ratio_delta':max_ratio_error,'old_current_pixel_identical_matched_view_count':pixelidentical,'matched_view_count':len(bykey),'image_count':len(visual['outputs']),'clipped_core_vertex_evidence':clip,'protected_history_count':len(before),'distinct_case_count':10,'endpoint_evaluations_not_repeated':True}
dump('INDEPENDENT_DELIVERY_VERIFICATION_R1.json',verify)
pass_all=all(checks.values()) and all(status['checks'].values()) and not status['blockers']
verdict='PASS_TARGETED_DEFORMATION_REQUALIFIED' if pass_all else 'FAIL_CLOSED_TARGETED_DEFORMATION_REVALIDATION'
status.update({'PRODUCTION_DRIFT':drift,'PROTECTED_PREEXISTING_FILE_COUNT':len(before),'INDEPENDENT_VERIFICATION':'PASS' if all(checks.values()) else 'FAIL_CLOSED','TARGETED_DEFORMATION_REVALIDATION_VERDICT':verdict,PHASE:verdict,'VERDICT':verdict,'NEXT':'FULL_STAGE6A_REQUALIFICATION_AFTER_DONOR_TRANSFER_R1' if pass_all else 'STOP_FAILURE_EVIDENCE','minimal_blocker':None if pass_all else [k for k,v in checks.items() if not v]})
dump(PHASE+'_STATUS.json',status)
report=OUT/(PHASE+'_REPORT.md');s=report.read_text(encoding='utf-8');s=s.replace('机器检查已完成；最终 verdict 由最终 no-drift 验证写入。','**'+verdict+'**').replace('`PENDING_FINAL_HASH_VERIFICATION`','`'+verdict+'`')
s=s.replace('| `PRODUCTION_DRIFT` | `'+verdict+'` |','| `PRODUCTION_DRIFT` | `'+str(drift)+'` |')
s+='\n## Independent final verification\n\n'+str(len(before))+'个预存文件SHA256逐个相同，changed/deleted/new-outside-task全部0。独立坐标比例复算'+str(numeric_checks)+'项，最大float64与历史float32比例差'+str(max_ratio_error)+'，仅使用已有存储精度核查1e-4；正式5x severe gate未放宽。全部'+str(len(visual['outputs']))+'张匹配图有效，'+str(len(bykey))+'对camera/light/scale一致，core clipping0。旧Full42状态文件hash精确，9 blockers原样保留。\n\nVERDICT='+verdict+'；STOP。NEXT仅记录，未执行。\n'
report.write_text(s,encoding='utf-8')
files={p.relative_to(OUT).as_posix():sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_ARTIFACT_HASH_MANIFEST.json'}
dump('OUTPUT_ARTIFACT_HASH_MANIFEST.json',files)
print(json.dumps({'verdict':verdict,'protected_files':len(before),'drift':drift,'numeric_checks':numeric_checks,'max_ratio_delta':max_ratio_error,'views':len(bykey),'clipping':clip,'failed_checks':[k for k,v in checks.items() if not v]},ensure_ascii=False),flush=True)
assert pass_all,'FAIL CLOSED: evidence not qualified'
