"""Read-only native reopen, two assets, ten distinct authorized endpoint probes.
Historical primitives/metrics/classifier are loaded as definitions only.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math,numpy as np,os
from types import SimpleNamespace
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
MM=1000.;reused=[]
assert read(OUT/'PREREQUISITE_GATE_R1.json')['status']=='PASS'
def module(p,names):
 ns={'bpy':bpy,'math':math,'Vector':Vector,'Quaternion':Quaternion,'MM':MM,'np':np,'os':os}
 reused.append(reuse(p,names,ns));return SimpleNamespace(**{n:ns[n] for n in names})
C=module(S5/'stage5b_r1e/scripts/s5b_r1e_common.py',['reset_pose','set_joint_rotation','update','evaluate','read_weights'])
C.SEVERE_MIN_BIND_MM=3.;C.SEVERE_STRETCH_X=5.;C.TEAR_X=3.;C.TEAR_MIN_POSED_MM=5.;C.MM=MM
S=module(S6/'stage6a/scripts/s6a_common.py',['face_area','face_normal','pose_state'])
R=module(S6/'stage6b_r1c/scripts/r1c_pen_common.py',['ray_triangle','tri_tri_intersection','seg_len','closest_point_on_triangle','poke_depth','tris_of'])
extract=module(S5/'targeted_rig_and_skin_data_rebuild_after_approval_r1/blender_extract.py',['mesh_payload','rig_payload','weights'])
matrix=read(HIST/'TARGETED_FIXTURE_MATRIX.json');fixtures=matrix['fixtures']
cases=matrix['poses']+[{'case_id':f'RING_MCP_{a}','bone':'RING_MCP_R','angle_deg':a,'run_label':'DONOR_TRANSFER_LOCAL_REGRESSION'} for a in [15,30,45]]
CM6B={c['case_id']:c for c in read(S6/'stage6b/STAGE6B_CASE_MATRIX.json')['cases']}
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['intersect_pairs','set_s6a','set_s6b'],globals()))
reused.append(reuse(S6/'stage6a_r1b/scripts/s6a_r1b_run_cases.py',['metrics'],globals()))
reused.append(reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
reused.append(reuse(HIST/'run_targeted.py',['local_metrics'],globals()))
labels=read(R3_PATH)['membership']['vertex_labels']
debts=read(HIST/'INHERITED_DEBT_DEFORMATION_MAPPING.json')['rows']
oldnative=read(OLD_CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
POLY=[tuple(p) for p in oldnative['mesh']['faces']];EDGES=[tuple(e) for e in oldnative['mesh']['edges']];NV=3416
FD=[]
for p in POLY:
 labs={labels.get(str(v),'OUTSIDE_BOUNDED_DOMAIN') for v in p};FD.append(next(iter(labs)) if len(labs)==1 else 'MIXED_AUTHORITY_BAND')
core=set(APPROVED54);roi_fs=[i for i,p in enumerate(POLY) if core.intersection(p)];roi_es=[i for i,e in enumerate(EDGES) if core.intersection(e)]
ring=set(v for fi in roi_fs for v in POLY[fi])-core
support=core|ring;outer_fs=[i for i,p in enumerate(POLY) if support.intersection(p)];outer_es=[i for i,e in enumerate(EDGES) if support.intersection(e)]
assert (len(roi_fs),len(roi_es))==(95,148)
domain=read(S6/'full_stage6a_requalification_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json')
sentinels={d:{'clean_shaft_support':domain['functional_clean'][d],'MCP_support':domain['patches'][d+'_MCP']} for d in ['MIDDLE','LITTLE']}
dump('MEASUREMENT_DOMAIN_MANIFEST_R1.json',{'fixtures':fixtures,'approved54':sorted(core),'incident_faces':roi_fs,'incident_edges':roi_es,'first_fixed_outer_ring':sorted(ring),'outer_support_face_ids':outer_fs,'outer_support_edge_ids':outer_es,'sentinels':sentinels,'sentinel_source':ref(S6/'full_stage6a_requalification_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json'),'not_new_anatomical_labels':True})
# Recover full z-buffered historical solid renderer without legacy top-level imports.
rpath=S6/'stage6b_r1c/scripts/r1c_pen_common.py'
rns={'bpy':bpy,'math':math,'np':np,'Vector':Vector,'MM':MM,'os':os}
tree=ast.parse(rpath.read_text(encoding='utf-8-sig'))
rn=['ortho_basis','View','Canvas','face_normals','save']
nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in rn]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(rpath),'exec'),rns)
RASP=SimpleNamespace(**{n:rns[n] for n in rn})
reused.append({'source':ref(rpath),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes},'top_level_executed':False})
LIGHT=Vector((.42,-.30,.85)).normalized();W_,H_=1200,900;SEV_MIN=3.
reused.append(reuse(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['fit_view','shade','draw_solid','strain_fn'],globals()))
frame=read(ROOT/'audits/right_hand_dorsal_mcp_contour_dent_causal_diagnosis_r1/DENT_RENDER_GEOMETRY_R1.json')['frame']
views={};render_rows=[];REND=OUT/'renders';REND.mkdir(exist_ok=True)
def render_pose(asset,cid,V):
 jobs=[]
 if cid.startswith('RING_'):
  for style in ['FULL_SOLID','DORSAL_CLOSE_SOLID','GRAZING_SOLID','WIRE_STRAIN']:jobs.append(('DONOR_ROI',style))
 else:
  reviewed={'CAP37':['TH_IP_30','IDX_MCP_45'],'OLD_CAP9':['TH_IP_45'],'FIRST_WEB':['FULL_OPP_L3'],'FRESH_R3_TRANSITION_COLLAR':['CMC_OPP_30'],'EDGE5879':['CMC_MCP_L3']}
  jobs=[(n,'SOLID') for n,cs in reviewed.items() if cid in cs]
  if not jobs:jobs=[('CAP37','SOLID_CONTEXT')]
 for name,style in jobs:
  key=cid+'__'+name+'__'+style
  if key not in views:
   if name=='DONOR_ROI':
    ids=list(range(NV)) if style=='FULL_SOLID' else sorted(support)
    direction=-Vector(frame['outward'])
    if style=='GRAZING_SOLID':direction=(direction*.22+Vector(frame['x'])*.98).normalized()
    up=Vector(frame['y'])
   else:
    ids=fixtures[name]['region'];direction=Vector({'CAP37':(.62,.35,.70),'OLD_CAP9':(.62,.35,.70),'FIRST_WEB':(.92,.25,.30),'FRESH_R3_TRANSITION_COLLAR':(.30,.72,.62),'EDGE5879':(.92,.25,.30)}[name]);up=Vector((0,0,1))
   pts=[V[i] for i in ids];cen=sum(pts,Vector())/len(pts)
   # Include possible donor displacement in the common view without per-asset fit.
   vw=fit_view(cen,direction,up,pts,1.45 if name=='DONOR_ROI' else 1.75)
   views[key]=vw
  vw=views[key];cv=RASP.Canvas(W_,H_)
  draw_solid(cv,vw,V,TRIS,strain_fn(V) if style=='WIRE_STRAIN' else None)
  if style=='WIRE_STRAIN':
   for ei in outer_es:
    a,b=EDGES[ei];pa=vw.proj(V[a]);pb=vw.proj(V[b]);cv.line(pa,pb,(.10,.10,.12),0,.7)
  fn=key+'__'+asset+'.png';RASP.save(cv,fn,str(REND))
  render_rows.append({'asset':asset,'pose':cid,'fixture':name,'style':style,'file':'renders/'+fn,'view_key':key,'camera_centre_m':list(vw.c),'camera_direction':list(vw.d),'camera_up':list(vw.u),'half_width_mm':vw.hw*MM,'resolution':[W_,H_],'full_native_surface_z_buffered':True})
def separation(V,f):
 # Vertex-to-surface distance to the mesh outside this entire fixture patch.
 # Exact crossing pair distances are also retained independently in local metrics.
 excluded=set(f['face_ids']);ps=[p for i,p in enumerate(POLY) if i not in excluded]
 b=BVHTree.FromPolygons(V,ps,all_triangles=False,epsilon=0.)
 ds=[b.find_nearest(V[i])[3]*MM for i in f['core']]
 return {'method':'Core vertices to nearest full surface outside fixture face support; not an anatomy/severity gate','min_mm':min(ds),'max_mm':max(ds),'vertex_distances_mm':dict(zip(map(str,f['core']),ds))}
def zero_state(rig):
 state=S.pose_state(rig)
 return all(r['quat']==[1.,0.,0.,0.] and r['loc']==[0.,0.,0.] and r['scale']==[1.,1.,1.] for r in state.values())
records={};positions={};resets=[];asset_assertions={}
bpy.ops.wm.open_mainfile(filepath=str(CORRECTED),load_ui=False,use_scripts=False)
corrected_rig=extract.rig_payload(bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'])
for asset,path in [('PRE_DONOR_R2',OLD_CAND),('CURRENT_DONOR_R2',CAND)]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
 native=extract.mesh_payload(ob);w=extract.weights(ob);rest=extract.rig_payload(rig)
 livechecks={'weight_hash':digest(w)==EXPECTED_WEIGHTS,'rig_authority':rest==corrected_rig,'topology':native['faces']==oldnative['mesh']['faces'] and native['edges']==oldnative['mesh']['edges'],'3416':len(w)==3416}
 dump(asset+'_LIVE_PREFLIGHT.json',{'checks':livechecks,'status':'PASS' if all(livechecks.values()) else 'FAIL_CLOSED','asset':ref(path),'weight_vector_hash':digest(w)})
 assert all(livechecks.values()),livechecks
 C.reset_pose(rig);C.update();VB,PB=C.evaluate(ob,MW);assert PB==POLY and zero_state(rig)
 # Same historical world-mm snapshot conversion for unchanged native points.
 V0=[Vector(p)/MM for p in native['positions_world_mm']]
 EDGE_LEN0=[(V0[a]-V0[b]).length for a,b in EDGES];FACE_AREA0=[S.face_area(V0,p) for p in POLY]
 BASE_PAIRS=intersect_pairs(V0,POLY);TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
 for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
 CHARACTERISTIC_EDGE_MM=sorted(EDGE_LEN0)[len(EDGE_LEN0)//2]*MM
 records[asset]={};positions[asset]={'BIND':[list(p) for p in VB],'RAW_BIND':[list(p) for p in V0]}
 for case in cases:
  cid=case['case_id'];C.reset_pose(rig);C.update();Vz,Pz=C.evaluate(ob,MW)
  pre=max((a-b).length*MM for a,b in zip(Vz,VB));assert pre==0 and zero_state(rig)
  if 'bone' in case:set_s6a(rig,case['bone'],case['angle_deg'])
  else:set_s6b(rig,cid)
  C.update();V,P=C.evaluate(ob,MW);assert P==POLY
  m,ratios,er=metrics(V,P)
  patches={}
  for n,f in fixtures.items():
   z=local_metrics(V,m,ratios,er,f['core'],f['face_ids'],f['edge_ids']);z['surface_separation']=separation(V,f)
   z['face_area_ratio_by_id']={str(i):ratios[i] for i in f['face_ids']};z['edge_ratio_by_id']={str(i):er[i] for i in f['edge_ids']}
   z['normal_cosine_by_face']={str(i):S.face_normal(V,POLY[i]).dot(S.face_normal(V0,POLY[i])) for i in f['face_ids']}
   patches[n]=z
  drows={}
  for d in debts:
   if cid not in d['historical_pose_ids']:continue
   k=d['debt_id'];a,b=EDGES[k];es=[j for j,(u,v) in enumerate(EDGES) if u in {a,b} or v in {a,b}];fs=[j for j,p in enumerate(POLY) if a in p or b in p]
   drows[str(k)]={'edge_id':k,'ratio':er[k],'bind_mm':EDGE_LEN0[k]*MM,'posed_mm':er[k]*EDGE_LEN0[k]*MM,'local':local_metrics(V,m,ratios,er,[a,b],fs,es),'incident_face_ids':fs,'incident_edge_ids':es}
  pairrows=[]
  for pose,pair in [('TH_IP_30',[1225,2740]),('IDX_MCP_45',[1041,2735]),('IDX_MCP_45',[1226,2742])]:
   if pose==cid:pairrows.append({'pose':cid,'face_ids':pair,'evidence':pair_evidence(V,*pair),'V2_class':classify(pair_evidence(V,*pair))})
  roi=local_metrics(V,m,ratios,er,sorted(support),outer_fs,outer_es)
  roi['incident95_face_area_ratios']={str(i):ratios[i] for i in roi_fs};roi['incident148_edge_ratios']={str(i):er[i] for i in roi_es}
  motion={d:{n:{'vertex_count':len(ids),'max_displacement_mm':max((V[i]-VB[i]).length*MM for i in ids),'mean_displacement_mm':sum((V[i]-VB[i]).length*MM for i in ids)/len(ids)} for n,ids in domains.items()} for d,domains in sentinels.items()}
  records[asset][cid]={'run_label':case['run_label'],'fixtures':patches,'debts':drows,'accepted_pair_fresh_evidence':pairrows,'ROI':roi,'non_target_motion':motion,'edge5879':{'ratio':er[5879],'bind_mm':EDGE_LEN0[5879]*MM},'pose_state':S.pose_state(rig),'global_metrics_context_only':{k:v for k,v in m.items() if k!='_newp'}}
  positions[asset][cid]=[list(p) for p in V]
  render_pose(asset,cid,V)
  C.reset_pose(rig);C.update();Vr,Pr=C.evaluate(ob,MW);post=max((a-b).length*MM for a,b in zip(Vr,VB))
  z={'asset':asset,'pose':cid,'pre_zero_max_mm':pre,'post_zero_max_mm':post,'all_bones_identity':zero_state(rig),'topology_exact':Pr==POLY};resets.append(z)
  assert post==0 and zero_state(rig)
  dump('TARGETED_ZERO_RESET_AUDIT_R1.json',{'status':'PASS','rows':resets,'HARNESS_FINAL_POSE':'ZERO / RSSF','max_restore_mm':max(z['post_zero_max_mm'] for z in resets)})
  dump('FRESH_MACHINE_EVIDENCE_R1.json',{'results':records,'reused':reused})
  dump('POSED_COORDINATE_EVIDENCE_R1.json',{'positions_world_m':positions,'faces':POLY,'edges':EDGES,'asset_sources':{'PRE_DONOR_R2':ref(OLD_CAND),'CURRENT_DONOR_R2':ref(CAND)}})
  dump('VISUAL_EVIDENCE_MANIFEST_R1.json',{'outputs':render_rows,'matched_cameras':True,'historical_z_buffer_renderer':ref(rpath),'production_modifications':0})
  print(asset,cid,'edge5879',er[5879],'ROI collapse',roi['collapsed_face_ids'],'ROI ClassA',roi['visible_geometric_crossings_count'],flush=True)
 C.reset_pose(rig);C.update()
 checks={'native_geometry_topology_UV_material_groups_modifiers':native==extract.mesh_payload(ob),'weights':w==extract.weights(ob),'rig_rest_and_zero_pose':rest==extract.rig_payload(rig),'asset_hash':sha(path)==(EXPECTED_OLD if asset=='PRE_DONOR_R2' else EXPECTED_CAND),'final_zero':zero_state(rig)}
 asset_assertions[asset]=checks;assert all(checks.values()),checks
dump('IN_MEMORY_NO_DRIFT_R1.json',{'checks':asset_assertions,'status':'PASS','blends_saved':0,'geometry_weight_rest_group_modifier_mutations':0})
print('TARGETED MEASUREMENT COMPLETE: two immutable assets, ten distinct authorized endpoint poses; ZERO/RSSF',flush=True)
