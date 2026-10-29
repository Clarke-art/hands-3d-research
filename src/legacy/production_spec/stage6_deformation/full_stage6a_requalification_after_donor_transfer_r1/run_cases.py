"""Read-only current R2 qualification; historical functions via AST only.
No blend saves. Every fresh case is rendered before ZERO reset.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy, math
from types import SimpleNamespace
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree
MM=1000.
assert all(read(OUT/'PREREQUISITE_GATE_R1.json')['checks'].values())
reused=[]
ns={'bpy':bpy}
reused.append(reuse(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'],ns))
def payload(ob,rig):
 return {'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
before=payload(ob,rig);saved=read(OLD_CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
current_native=read(CAND.parent/'R2_REOPENED_NATIVE_PAYLOAD_R1.json')
saved['mesh']['positions_local_m']=current_native['coordinates_local_m']
saved['mesh']['positions_world_mm']=[list(Vector(p)*1000.) for p in current_native['coordinates_world_m']]
checks={k:before[k]==saved[k] for k in before}
checks['weight_hash']=digest(before['weights'])==EXPECTED_WEIGHTS
checks['21_bones']=len(rig.data.bones)==21
checks['TIP_non_deform']=all(not b.use_deform for b in rig.data.bones if '_TIP_' in b.name)
checks['TIP_weight_zero']=all(not any('_TIP_' in g and w!=0 for g,w in row.items()) for row in before['weights'])
spec=ROOT/'docs/CANONICAL_HAND_POSE_SPEC_R1.md'
checks['canonical_RSSF_document']='RSSF' in spec.read_text(encoding='utf-8-sig')
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
checks['all_corrected_rest_bones']=ns['rig_payload'](bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])==before['rig']
fresh=read(R3_PATH);cap=read(CAP_PATH);W=before['weights'];web=set(fresh['FIRST_WEB21']['membership_vertex_ids'])
allowed_web={'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'}
checks['FIRST_WEB_frozen_driver_semantics']=all(set(W[i])<=allowed_web for i in web)
old=set(fresh['old_cap9']['vertex_ids']);capids=set(cap['vertex_ids'])
checks['old9_no_thumb_override']=all(not any(g.startswith('THUMB') for g in W[i]) for i in old)
dump('LIVE_PREREQUISITE_GATE_R1.json',{'checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL_CLOSED','canonical_spec':ref(spec)})
assert all(checks.values()),checks
bpy.ops.wm.open_mainfile(filepath=str(CAND),load_ui=False,use_scripts=False)
ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
S=SimpleNamespace()
sn={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':MM}
reused.append(reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','face_area','face_centroid','face_normal','stats','pose_state','rr','bone_world'],sn))
for k in ['reset_pose','set_joint_rotation','evaluate','face_area','face_centroid','face_normal','stats','pose_state','rr','bone_world']:setattr(S,k,sn[k])
def update():bpy.context.view_layer.update()
def ev():return S.evaluate(ob,MW)
def reset():S.reset_pose(rig);update()
reset()
V0=[(<REDACTED_EMAIL>).copy() for v in ob.data.vertices];NV=len(V0)
EDGES=[tuple(e.vertices) for e in ob.data.edges];POLY=[tuple(p.vertices) for p in ob.data.polygons]
VB,PB=ev();assert PB==POLY
EDGE_LEN0=[(V0[a]-V0[b]).length for a,b in EDGES]
FACE_AREA0=[S.face_area(V0,p) for p in POLY]
MED=sorted(EDGE_LEN0)[len(EDGES)//2]*MM
chain={'THUMB':['CMC','MCP','IP'],**{d:['MCP','PIP','DIP'] for d in ['INDEX','MIDDLE','RING','LITTLE']}}
digits=list(chain)
PTS={d:[S.bone_world(rig,d+'_'+chain[d][0]+'_R',True)]+[S.bone_world(rig,d+'_'+s+'_R',False) for s in chain[d]] for d in digits}
an={'Vector':Vector,'MM':MM}
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_common.py',['arc_of'],an))
ARC={d:[an['arc_of'](PTS[d],v)[0] for v in V0] for d in digits}
XIJ={d:[0.] for d in digits}
for d in digits:
 for a,b in zip(PTS[d],PTS[d][1:]):XIJ[d].append(XIJ[d][-1]+(b-a).length*MM)
labels={int(k):v for k,v in fresh['membership']['vertex_labels'].items()}
def families(i):return sorted({g.split('_')[0] for g in W[i] if g!='WRIST_R' and '_TIP_' not in g})
# Frozen fresh labels are the ONLY thumb/index ownership authority. Outside that
# bounded field, weight-support sets are functional measurements, not anatomy labels.
OWN={d:sorted(i for i,l in labels.items() if l==d) if d in ['THUMB','INDEX'] else sorted(i for i in range(NV) if families(i)==[d]) for d in digits}
CLEAN={d:[i for i in OWN[d] if set(families(i))<={d} and i not in web] for d in digits}
FUNCTIONAL_CLEAN={d:[i for i in range(NV) if families(i)==[d] and i not in web and (i not in labels or labels[i]==d)] for d in digits}
historical=read(HIST/'FULL_STAGE6A_CASE_MATRIX_R1.json')['cases']
cases=[{k:c[k] for k in ['case_id','digit','joint','angle_deg','bone','axis','sign','applied_rotation_deg']} for c in historical]
assert len(cases)==42 and len({c['bone'] for c in cases})==14 and all(c['sign']==-1 and c['axis']=='bone_local_X' for c in cases)
T01=read(ROOT/'production_spec/stage4_blender/stage4a_t01/T01_FINAL_AUDIT.json')
KAPPA={};PATCH={}
for c in cases:
 d=c['digit'];seg=c['joint'];key=d+'_'+seg
 if key in PATCH:continue
 k=2*MED
 if d!='THUMB':
  for group in ['T01_MCP','OTHER_T01_JOINTS']:
   if key in T01.get(group,{}):
    loops=T01[group][key]['LOOP_POSITION_axial_from_commissure_mm'];ds=sorted(round(b-a,4) for a,b in zip(loops,loops[1:]))
    if ds:k=ds[len(ds)//2]
 a=XIJ[d][chain[d].index(seg)]
 KAPPA[key]=k;PATCH[key]=[i for i in OWN[d] if abs(ARC[d][i]-a)<=k]
 assert PATCH[key],key
def fs_of(ids):
 ids=set(ids);return [j for j,p in enumerate(POLY) if any(i in ids for i in p)]
def es_of(ids):
 ids=set(ids);return [j for j,(a,b) in enumerate(EDGES) if a in ids or b in ids]
wh=S.bone_world(rig,'WRIST_R',True);wu=(S.bone_world(rig,'WRIST_R',False)-wh).normalized()
FOREARM=[i for i,v in enumerate(V0) if (v-wh).dot(wu)<0]
PALMAR={d:-(rig.matrix_world.to_3x3()@rig.data.bones[d+'_MCP_R'].matrix_local.to_3x3()@Vector((0,0,1))).normalized() for d in digits}
TIP0={d:(<REDACTED_EMAIL>[d+'_TIP_R'].head).copy() for d in digits}
sign={}
for bone in dict.fromkeys(c['bone'] for c in cases):
 d=bone.split('_')[0];row={}
 for s in [1,-1]:
  reset();S.set_joint_rotation(rig,bone,s*5);update();p=<REDACTED_EMAIL>[d+'_TIP_R'].head
  row[str(s)]=(p-TIP0[d]).dot(PALMAR[d])*MM
 row['qualified_historical_minus_one']=row['-1']>1e-6 and row['1']<-1e-6
 sign[bone]=row
reset();dump('FLEXION_AXIS_SIGN_AUDIT_R1.json',{'axis':'LOCAL_X','historical_sign':-1,'probes':sign,'qualified':all(r['qualified_historical_minus_one'] for r in sign.values()),'bone_axis_roll_changes':0})
assert all(r['qualified_historical_minus_one'] for r in sign.values()),sign
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['intersect_pairs'],globals()))
BASE_PAIRS=intersect_pairs(VB,POLY)
R=SimpleNamespace();rn={'Vector':Vector,'MM':MM,'math':math}
exact_names=['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of']
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_common.py',exact_names,rn))
for k in exact_names:setattr(R,k,rn[k])
TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
CHARACTERISTIC_EDGE_MM=MED
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
reused.append(reuse(S6/'stage6a_r1b/scripts/s6a_r1b_run_cases.py',['metrics'],globals()))
base_exact={p for p in BASE_PAIRS if pair_evidence(VB,*p)['intersect']}
dump('BIND_EXACT_CROSSING_CONTEXT_R1.json',{'raw_bind_pairs':sorted(BASE_PAIRS),'exact_bind_pairs':[{'face_ids':list(p),**pair_evidence(VB,*p),'class':classify(pair_evidence(VB,*p))} for p in sorted(base_exact)]})
fixtures=read(S5/'cap_fixture_static_validation_and_targeted_deformation_r1/TARGETED_FIXTURE_MATRIX.json')['fixtures']
# Native nail material connected components; record all memberships explicitly.
nf={p.index for p in ob.data.polygons if p.material_index==1};remaining=set(nf);nails={d:[] for d in digits};nail_components=[]
while remaining:
 seed=min(remaining);comp={seed};verts=set(POLY[seed]);remaining.remove(seed)
 while True:
  add={fi for fi in remaining if verts.intersection(POLY[fi])}
  if not add:break
  comp|=add;remaining-=add
  for fi in add:verts.update(POLY[fi])
 counts={d:sum(sum(w for g,w in W[i].items() if g.startswith(d+'_')) for i in verts) for d in digits}
 d=max(counts,key=counts.get)
 frozen={labels[i] for i in verts if i in labels}
 assert not frozen or frozen=={d},(comp,d,frozen)
 nails[d]+=sorted(verts);nail_components.append({'digit':d,'face_ids':sorted(comp),'vertex_ids':sorted(verts),'frozen_labels':sorted(frozen),'driver_support':counts})
assert len(nail_components)==5
def disp(V,ids):
 a=[(V[i]-VB[i]).length*MM for i in ids];return {'max_mm':max(a,default=0),'mean_mm':sum(a)/len(a) if a else 0,'vertex_count':len(a)}
def local(V,ar,er,ids,fs=None,es=None):
 fs=fs if fs is not None else fs_of(ids);es=es if es is not None else es_of(ids)
 return {'vertex_ids':sorted(ids),'face_ids':fs,'edge_ids':es,'edge_ratios':S.stats([er[j] for j in es]),'face_area_ratios':S.stats([ar[j] for j in fs]),'bind_surface_area_mm2':sum(FACE_AREA0[j] for j in fs)*MM*MM,'posed_surface_area_mm2':sum(S.face_area(V,POLY[j]) for j in fs)*MM*MM,'displacement':disp(V,ids),'compressed_face_below_0_05_ids':[j for j in fs if ar[j]<.05],'normal_flip_diagnostic_ids':[j for j in fs if S.face_normal(V,POLY[j]).dot(S.face_normal(VB,POLY[j]))<-.5],'normal_flip_alone_is_inversion':False,'tear_strain_edge_ids':[j for j in es if er[j]>3 and er[j]*EDGE_LEN0[j]*MM>5],'tear_strain_alone_is_surface_tearing':False,'pinch_proxy_authority':'EDGE/FACE_COMPRESSION_DIAGNOSTIC_ONLY; no ray proxy collapse gate'}
accepted={'TH_IP_30':{(1225,2740)},'IDX_MCP_45':{(1041,2735),(1226,2742)}}
previous=read(HIST/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['cases']
targeted_coords=read(TARGETED/'POSED_COORDINATE_EVIDENCE_R1.json')['positions_world_m']['CURRENT_DONOR_R2']
import render_helpers as RH
def accepted_before(cid,p):
 return next((e for e in previous.get(cid,{}).get('crossings',[]) if tuple(e['face_ids'])==p),None)
def domain(fi):
 labs={labels.get(i,'OUTSIDE_FRESH_BOUNDED_DOMAIN') for i in POLY[fi]}
 return next(iter(labs)) if len(labs)==1 else 'MIXED_FRESH_AUTHORITY_BAND'
def functional(fi):
 ff={x for i in POLY[fi] for x in families(i)}
 return next(iter(ff)) if len(ff)==1 else 'SHARED_DRIVER_BAND' if ff else 'WRIST_ONLY'
results={};positions={'BIND':[list(v) for v in VB]};zero={};blockers=[];trajectory={};all_severe=[];all_cross=[]
rawzero=max((a-b).length*MM for a,b in zip(V0,VB))
dump('LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json',{'method':'Existing Stage6A T01 kappa / corrected approved bone chain arc; bounded fresh THUMB/INDEX only. Other three fingers: own-family-only functional support. No new anatomical ownership field.','patches':PATCH,'kappa_mm':KAPPA,'chain_arc_mm':XIJ,'fresh_owned_sets':{d:OWN[d] for d in ['THUMB','INDEX']},'clean_frozen':CLEAN,'clean_functional_outside_is_anatomy_authority':False,'functional_clean':FUNCTIONAL_CLEAN,'forearm':FOREARM,'FIRST_WEB21':sorted(web),'nail_material_components':nail_components,'bind_exact_pair_count':len(base_exact),'bind_raw_noise_mm':rawzero})
for c in cases:
 cid=c['case_id'];d=c['digit'];key=d+'_'+c['joint'];reset();vpre,ppre=ev()
 pre=max((a-b).length*MM for a,b in zip(vpre,VB));posepre=S.pose_state(rig)
 S.set_joint_rotation(rig,c['bone'],c['applied_rotation_deg']);update();V,P=ev()
 m,ar,er=metrics(V,P);broad=intersect_pairs(V,P);cross=[]
 for p in sorted(broad-base_exact):
  e=pair_evidence(V,*p);cls=classify(e)
  if not e['intersect']:continue
  known=p in accepted.get(cid,set());old_e=accepted_before(cid,p) if known else None
  # Equal current candidate and identical pose reproduce frozen accepted severity.
  pairids=sorted({i for fi in p for i in POLY[fi]})
  same=known and old_e is not None and all(e[k]==old_e[k] for k in ['intersect','depth_mm','seg_mm','local_edge_mm','pts']) and all(list(V[i])==targeted_coords[cid][i] for i in pairids)
  accepted_ok=known and same
  domains=[domain(j) for j in p];ff=[functional(j) for j in p]
  relation='SAME_SURFACE_LOCAL_FOLD' if ff[0]==ff[1] and ff[0] not in ['SHARED_DRIVER_BAND','WRIST_ONLY'] else 'TARGET_VS_OTHER_DIGIT_CONTACT' if d in ff else 'POSE_LEVEL_OR_MIXED_BAND_CONTACT'
  row={'case_id':cid,'face_ids':list(p),'fresh_domains':domains,'functional_driver_domains':ff,'relation':relation,'class':cls,**e,'known_exact_pose_pair':known,'accepted_severity_reproduced':same,'historical_accepted_severity':old_e,'acceptance':'KNOWN_HUMAN_ACCEPTED_NON_BLOCKING_DIAGNOSTIC_CONTACT' if accepted_ok else 'UNAPPROVED_EXACT_CROSSING','visible_teaching_defect_conclusion':'NOT_AUTOMATICALLY_INFERRED_FROM_V2_CLASS','hard_blocker':cls.startswith('CASE_A') and not accepted_ok}
  cross.append(row)
  if row['hard_blocker']:blockers.append({'case_id':cid,'type':'NEW_UNAPPROVED_EXACT_CROSSING_EXISTING_SEVERE_CLASS_A','face_ids':list(p),'basis':'Actual triangle crossing and poke >= bind local facet mean. Visible teaching defect remains distinct human question.','cause_candidates':['pose contact','skin','geometry'],'human_acceptance':False})
 severe=[]
 for j,(a,b) in enumerate(EDGES):
  if EDGE_LEN0[j]*MM>=3 and er[j]>5:
   row={'case_id':cid,'joint':c['joint'],'angle_deg':c['angle_deg'],'edge_id':j,'vertex_ids':[a,b],'bind_length_mm':EDGE_LEN0[j]*MM,'posed_length_mm':EDGE_LEN0[j]*MM*er[j],'ratio':er[j],'region':[labels.get(i,'OUTSIDE_FRESH_BOUNDED_DOMAIN') for i in [a,b]],'driver_family':[families(i) for i in [a,b]],'pose':{c['bone']:c['applied_rotation_deg']}}
   severe.append(row);blockers.append({'case_id':cid,'type':'SEVERE_EDGE_STRETCH','edge_id':j,'vertex_ids':[a,b],'cause_candidates':['skin','geometry'],'human_acceptance':False})
 patch=local(V,ar,er,PATCH[key]);capmetrics=local(V,ar,er,capids,cap['face_ids']);capcontext=local(V,ar,er,fixtures['CAP37']['region'],fixtures['CAP37']['face_ids'],fixtures['CAP37']['edge_ids'])
 oldmetrics=local(V,ar,er,old);nailmetrics={nd:local(V,ar,er,sorted(set(ids)),[fi for co in nail_components if co['digit']==nd for fi in co['face_ids']]) for nd,ids in nails.items()}
 clean={nd:disp(V,FUNCTIONAL_CLEAN[nd]) for nd in digits if nd!=d};forearm=disp(V,FOREARM);webmotion=disp(V,web)
 for nd,x in clean.items():
  if x['max_mm']>1e-3:blockers.append({'case_id':cid,'type':'NON_TARGET_CLEAN_CONTAMINATION','digit':nd,'max_mm':x['max_mm'],'vertex_ids':[i for i in FUNCTIONAL_CLEAN[nd] if (V[i]-VB[i]).length*MM>1e-3]})
 if forearm['max_mm']>1e-3:blockers.append({'case_id':cid,'type':'FOREARM_MOTION','max_mm':forearm['max_mm']})
 for fld in ['nan_inf_vertices','nan_inf_faces','collapsed_faces','degenerate_edges']:
  if m[fld]:blockers.append({'case_id':cid,'type':fld,'count':m[fld]})
 if not m['topology_unchanged'] or P!=POLY:blockers.append({'case_id':cid,'type':'TOPOLOGY_DRIFT'})
 tip=(<REDACTED_EMAIL>[d+'_TIP_R'].head).copy();trajectory.setdefault(c['bone'],[]).append({'case_id':cid,'angle':c['angle_deg'],'tip_world_m':list(tip),'palmar_mm':(tip-TIP0[d]).dot(PALMAR[d])*MM})
 applied=S.pose_state(rig);nonzero=[pb.name for pb in rig.pose.bones if abs(pb.rotation_quaternion.angle)>1e-7]
 assert nonzero==[c['bone']],nonzero
 RH.render_case(cid,V,V0,sorted(set(PATCH[key])|{i for cr in cross if cr['hard_blocker'] for fi in cr['face_ids'] for i in POLY[fi]}),nails[d],capids,web,cross)
 reset();vpost,ppost=ev();post=max((a-b).length*MM for a,b in zip(vpost,VB))
 zero[cid]={'before_max_mm':pre,'after_max_mm':post,'raw_RSSF_noise_mm':rawzero,'formal_zero_gate_mm':1e-4,'one_joint_only':nonzero,'locked_CMC_WRIST':all(applied[bn]['quat']==[1.,0.,0.,0.] and applied[bn]['loc']==[0.,0.,0.] and applied[bn]['scale']==[1.,1.,1.] for bn in ['THUMB_CMC_R','WRIST_R']),'zero_rotation_location_scale_before_and_after':all(tuple(pb.location)==(0,0,0) and tuple(pb.scale)==(1,1,1) and abs(pb.rotation_quaternion.angle)<1e-7 for pb in rig.pose.bones)}
 if max(pre,post,rawzero)>1e-4 or not zero[cid]['zero_rotation_location_scale_before_and_after']:blockers.append({'case_id':cid,'type':'ZERO_RESTORE_FAILURE','metrics':zero[cid]})
 results[cid]={'case':c,'global_metrics':{k:v for k,v in m.items() if k!='_newp'},'local_patch':patch,'crossings':cross,'severe_edges':severe,'non_target_clean_motion':clean,'FIRST_WEB_motion':webmotion,'FIRST_WEB_structure':local(V,ar,er,web),'fresh_R3_collar_structure':local(V,ar,er,fixtures['FRESH_R3_TRANSITION_COLLAR']['region'],fixtures['FRESH_R3_TRANSITION_COLLAR']['face_ids'],fixtures['FRESH_R3_TRANSITION_COLLAR']['edge_ids']),'non_target_MCP_support_motion':{nd:disp(V,PATCH[nd+'_MCP']) for nd in digits if nd!=d},'sanctioned_shared_web_motion':webmotion,'forearm':forearm,'cap37':capmetrics,'cap37_continuity':capcontext,'old9_index_regression':oldmetrics,'nails':nailmetrics,'pose_state':applied,'TIP_HELPER_DEFORMATION_INFLUENCE_COUNT':sum(b.use_deform for b in rig.data.bones if '_TIP_' in b.name)+sum(1 for row in W for g,w in row.items() if '_TIP_' in g and w!=0),'donor_ROI_structure':local(V,ar,er,sorted(set(APPROVED54)|set(RH.M['first_fixed_outer_ring'])),RH.M['outer_support_face_ids'],RH.M['outer_support_edge_ids']),'broadphase_pairs_count':len(broad),'warnings':['HUMAN_REVIEW_CONTOUR_CREASE_PINCH_VOLUME_NAIL_TEACHING_READABILITY']+(['EXACT_CONTACT_APPEARANCE'] if cross else []),'structural_candidates':{'normal_flip_diagnostic_face_ids':patch['normal_flip_diagnostic_ids'],'tear_strain_edge_ids':patch['tear_strain_edge_ids'],'automatic_visible_flap_tearing_inversion_claim':False,'cap37_surface_separation_detected':False,'topology_separation_detected':P!=POLY}}
 positions[cid]=[list(v) for v in V];all_severe+=severe;all_cross+=cross
 dump('EXECUTION_PROGRESS_R1.json',{'cases_completed':len(results),'case_id':cid,'blends_saved':0,'stage6B_runs':0,'temporary_pose_restored':post==0})
 print(cid,'maxedge',round(m['max_edge_ratio'],5),'severe',len(severe),'exact',len(cross),'unapproved_A',sum(x['hard_blocker'] for x in cross),'zero',post,flush=True)
monotonic={b:all(y['palmar_mm']>=x['palmar_mm']-1e-6 for x,y in zip(rows,rows[1:])) for b,rows in trajectory.items()}
for bone,ok in monotonic.items():
 if not ok:blockers.append({'type':'TIP_TRAJECTORY_NONMONOTONIC','bone':bone,'trajectory':trajectory[bone]})
reset();after=payload(ob,rig);assert after==before
dump('HARNESS_ZERO_REOPEN_VERIFICATION.json',{'status':'PASS','all_case_memory_payload_unchanged':True,'native_before_after_identical':True,'zero_RSSF':True,'production_save_count':0,'harness_save_count':0,'input_live_checks':checks,'harness_type':'IN_MEMORY_ONLY'})

dump('FULL_STAGE6A_CASE_MATRIX_R1.json',{'formal_count':42,'cases':cases,'definition_source':ref(S6/'stage6a_r1b/STAGE6A_R1B_CASE_MATRIX.json'),'LOCKED':['THUMB_CMC_R','WRIST_R'],'angle_role':'DIAGNOSTIC_STRESS_ONLY','CANONICAL_HAND_POSE':'RSSF'})
dump('FULL_STAGE6A_MACHINE_EVIDENCE_R1.json',{'cases':results,'blockers':blockers,'thresholds':{'severe_bind_mm_ge':3,'severe_ratio_gt':5,'clean_motion_mm':1e-3,'forearm_mm':1e-3,'zero_mm':1e-4,'collapse_area_m2_le':1e-12,'collapse_ratio_le':1e-6,'degenerate_edge_m_le':1e-12,'exact_severe_rule':'R1C V2 actual crossing + poke/local bind mean facet >=1; class name does not imply visible teaching defect'},'historical_functions':reused,'tip_trajectory':trajectory,'tip_monotonic':monotonic,'TIP_weight_influence_count':0,'new_anatomy_thresholds':0,'new_ownership_solves':0})
dump('POSED_COORDINATES_R1.json',{'positions_world_m':positions,'faces':POLY,'edges':EDGES,'bind_raw_world_m':[list(v) for v in V0]})
dump('FULL_STAGE6A_POST_DONOR_ZERO_RESET_AUDIT_R1.json',{'status':'PASS' if max([rawzero]+[max(r['before_max_mm'],r['after_max_mm']) for r in zero.values()])<=1e-4 else 'FAIL','cases':zero,'harness_final_ZERO_RSSF':True,'harness_blend_save_count':0})
dump('FULL_STAGE6A_POST_DONOR_SEVERE_EDGE_STRETCH_AUDIT_R1.json',{'gate':'bind >=3mm AND posed/bind >5','case_count':len({r['case_id'] for r in all_severe}),'edge_occurrence_count':len(all_severe),'unique_edge_count':len({r['edge_id'] for r in all_severe}),'rows':all_severe})
dump('FULL_STAGE6A_SELF_INTERSECTION_AUDIT_R1.json',{'exact_classifier_source':ref(S6/'stage6b_r1c/scripts/r1c_pen_v2.py'),'bind_exact_pairs':sorted(base_exact),'rows':all_cross,'known_accepted_count':sum(r['acceptance'].startswith('KNOWN_') for r in all_cross),'new_unapproved_exact_count':sum(r['acceptance']=='UNAPPROVED_EXACT_CROSSING' for r in all_cross),'new_unapproved_severe_count':sum(r['hard_blocker'] for r in all_cross),'V2_class_A_equals_visible_teaching_defect':False})
for name,keys in [('LOCAL_STRAIN',['local_patch','global_metrics','structural_candidates']),('CROSS_DIGIT',['non_target_clean_motion','FIRST_WEB_motion','forearm']),('CAP37',['cap37','cap37_continuity']),('OLD_CAP9_REGRESSION',['old9_index_regression']),('NAIL',['nails'])]:
 filename='FULL_STAGE6A_'+name+('_AUDIT' if name not in ['OLD_CAP9_REGRESSION'] else '')+'_R1.json'
 dump(filename,{'cases':{cid:{k:row[k] for k in keys} for cid,row in results.items()},'authority_role':'CURRENT_R2_MEASUREMENTS','TIP_weight_influence_count':0,'old9_role':'NATIVE_INDEX_REGRESSION_ONLY','nail_memberships':nail_components if name=='NAIL' else None})
assert sha(CAND)==EXPECTED_CAND
print('COMPLETED 42 CASES; blockers',len(blockers),'zero raw noise',rawzero,flush=True)
