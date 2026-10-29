import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_common import *
import numpy as np, math,bpy
from mathutils import Vector
sys.path.append(str(S6/'stage6b_r1c/scripts'));sys.path.append(str(S6/'stage6a/scripts'))
import r1c_pen_common as R
import s6a_common as S
coords=read(OUT/'CAUSAL_COORDINATE_EVIDENCE.json');sweeps=read(OUT/'CROSSING_ONSET_SWEEP.json')['results']
POLY=[tuple(p) for p in coords['faces']];EDGES=coords['edges'];V0=[Vector(p) for p in coords['legacy_V2_bind_world_m']];MM=1000.
TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals())
P0=np.array(coords['native_bind_world_m']);local=coords['local_vertex_ids'];idx={v:i for i,v in enumerate(local)}
def fit(A,B):
 a=A.mean(0);b=B.mean(0);u,s,vt=np.linalg.svd((A-a).T@(B-b));Q=u@vt
 if np.linalg.det(Q)<0:u[:,-1]*=-1;Q=u@vt
 t=b-a@Q;F=A@Q+t;res=np.linalg.norm(B-F,axis=1)*1000
 return Q,t,F,{'rotation_row_matrix':Q.tolist(),'translation_world_mm':(t*1000).tolist(),'rotation_deg':float(np.degrees(np.arccos(np.clip((np.trace(Q)-1)/2,-1,1)))),'residual_rms_mm':float(np.sqrt(np.mean(res**2))),'residual_max_mm':float(res.max()),'displacement_rms_mm':float(np.sqrt(np.mean(np.sum((B-A)**2,axis=1)))*1000)}
def cross(V,t):return np.cross(V[t[1]]-V[t[0]],V[t[2]]-V[t[0]])
def summarize(vals):return {'min':float(min(vals)),'median':float(np.median(vals)),'max':float(max(vals))}
def patch_metrics(V,part,ids,fs,es):
 Q,t,F,d=fit(P0[ids],V[ids]);ar=[];angles=[]
 for fi in fs:
  a=b=0
  for tri in FACE_TRIS[fi]:
   n0=cross(P0,tri);n1=cross(V,tri);a+=np.linalg.norm(n0)/2;b+=np.linalg.norm(n1)/2
   angles.append(float(np.degrees(np.arccos(np.clip((n0@Q)@n1/(np.linalg.norm(n0)*np.linalg.norm(n1)),-1,1)))))
  ar.append(b/a)
 strains=[float(np.linalg.norm(V[a]-V[b])/np.linalg.norm(P0[a]-P0[b])) for a,b in [EDGES[k] for k in es]]
 if not strains:
  p=POLY[part['face_id']];strains=[float(np.linalg.norm(V[p[j]]-V[p[(j+1)%4]])/np.linalg.norm(P0[p[j]]-P0[p[(j+1)%4]])) for j in range(4)]
 d.update({'vertex_ids':ids,'face_ids':fs,'edge_ids':es,'face_area_ratio':summarize(ar),'edge_length_ratio':summarize(strains),'triangle_normal_change_after_best_fit_rigid_deg':summarize(angles),'area_collapse_or_degenerate':bool(min(ar)<=1e-6 or min(strains)<=1e-12),'gross_fivefold_edge_expansion':bool(max(strains)>=5),'thickness':'NOT_IDENTIFIABLE: these patches are not authority-paired opposite skin surfaces; gap/area strain does not establish anatomical thickness.','in_plane_compression_proxy_min_edge_ratio':float(min(strains))})
 return d,Q,t,F
results={}
for pair in PAIRS:
 pid=pair['id'];pose=pair['pose'];results[pid]={}
 for asset in ASSETS:
  V=np.array(coords['actual_endpoints_world_m'][asset][pose+'__'+str(pair['max_angle'])]);parts=[];rigid=P0.copy()
  for part in coords['patches'][pid]:
   ids=part['core_vertex_ids'];core,Q,t,F=patch_metrics(V,part,ids,[part['face_id']],[]);rigid[ids]=F
   ri=part['one_ring_same_frozen_label_vertex_ids'];ring,*_=patch_metrics(V,part,ri,part['one_ring_face_ids'],part['one_ring_edge_ids'])
   # Track residual throughout the permitted sweep rather than only its endpoint.
   track=[]
   for row in sweeps[asset][pose]['fixed_grid']+sweeps[asset][pose]['additional_refinement_samples']:
    B=np.array(row['local_positions_world_m'])[[idx[v] for v in ids]]
    _,_,_,d=fit(P0[ids],B);track.append({'angle_deg':row['angle_deg'],'residual_rms_mm':d['residual_rms_mm'],'residual_max_mm':d['residual_max_mm']})
   parts.append({'face_id':part['face_id'],'label':part['label'],'core':core,'same_label_one_ring':ring,'core_residual_sweep':sorted(track,key=lambda x:x['angle_deg'])})
  e=pair_evidence([Vector(p) for p in rigid],*pair['faces']);e.pop('pts',None)
  results[pid][asset]={'patches':parts,'independent_core_best_fit_rigid_only_pair':{**e,'V2_class':classify(e)},'rigid_only_limit':'Separate patch best fits preserve actual centroid approach; diagnostic removal of each patch residual, not a new pose or approved skin.'}
dump('LOCAL_RIGID_VS_NONRIGID_DECOMPOSITION.json',{'method':'Proper Kabsch transform bind -> posed; nonrigid residual is posed minus fitted rigid. Triangle normals compared AFTER rigid rotation. Same frozen-label one ring only.','scope':PAIRS,'results':results,'new_severity_thresholds':False,'anatomy_or_qualification_authority':False,'thickness_inference_permitted':False})
# Full mesh samples at the already measured R2 first crossing / Class-A angles only.
selected={}
for pair in PAIRS:
 onset=sweeps['R2'][pair['pose']]['onsets'][pair['id']]
 selected[pair['id']]=sorted({onset[k]['first_positive_sample_angle_deg'] for k in ['exact_crossing','V2_Class_A']})
visual={}
for asset,path in ASSETS.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 ob=bpy.data.objects['Hand  - Realistic'];rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];mw=ob.matrix_world.copy();visual[asset]={}
 for pair in PAIRS:
  for ang in selected[pair['id']]:
   key=pair['pose']+'__'+str(ang)
   if key in visual[asset]:continue
   S.reset_pose(rig);S.set_joint_rotation(rig,pair['bone'],-ang);bpy.context.view_layer.update();v,p=S.evaluate(ob,mw);assert p==POLY
   visual[asset][key]=[list(x) for x in v]
 assert sha(path)==read(OUT/'CAUSAL_INPUT_MANIFEST.json')['assets'][asset]['sha256']
dump('SELECTED_ONSET_VISUAL_COORDINATES.json',{'selected_angles_by_pair':selected,'full_mesh_positions_world_m':visual,'selection':'First positive R2 exact crossing / V2-A samples from the existing onset bisection; same angle for every asset. No additional pose family.','production_saves':0})
for pid,assets in results.items():
 print(pid,{a:{'core_rms':[p['core']['residual_rms_mm'] for p in x['patches']],'ring_rms':[p['same_label_one_ring']['residual_rms_mm'] for p in x['patches']],'rigid_cross':x['independent_core_best_fit_rigid_only_pair']['intersect']} for a,x in assets.items()},flush=True)
