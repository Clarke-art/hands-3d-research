"""Thin read-only adapter over the frozen historical pose and metric functions.
No skin, anatomical selection, joint fitting, ownership solve or blend save.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualification_common import *
assert read(OUT/'CAP_FIXTURE_STATIC_CONFIRMATION.json')['status']=='PASS'
import bpy,math,importlib.util
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
sys.path.append(str(S5/'stage5b_r1e/scripts'))
sys.path.append(str(S6/'stage6a/scripts'))
sys.path.append(str(S6/'stage6b_r1c/scripts'))
import s5b_r1e_common as C
import s6a_common as S
import r1c_pen_common as R
matrix=read(OUT/'TARGETED_FIXTURE_MATRIX.json'); fixtures=matrix['fixtures']
saved=read(OUT/'STATIC_LIVE_REOPEN_PAYLOAD.json')
V0=[Vector(p)/1000 for p in saved['mesh']['positions_world_mm']]
EDGES=[tuple(e) for e in saved['mesh']['edges']];POLY=[tuple(p) for p in saved['mesh']['faces']]
NV=len(V0);MM=1000.;EDGE_LEN0=[(V0[a]-V0[b]).length for a,b in EDGES];FACE_AREA0=[S.face_area(V0,p) for p in POLY]
reuse={}
reuse.update(reuse_functions(S5/'stage5b_r1e/scripts/s5b_r1e_prequal.py',['intersect_pairs','set_s6a','set_s6b'],globals()))
CM6B={c['case_id']:c for c in read(S6/'stage6b/STAGE6B_CASE_MATRIX.json')['cases']}
BASE_PAIRS=intersect_pairs(V0,POLY)
reuse.update(reuse_functions(S6/'stage6a_r1b/scripts/s6a_r1b_run_cases.py',['metrics'],globals()))
TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
for fi,t in TRIS: FACE_TRIS.setdefault(fi,[]).append(t)
CHARACTERISTIC_EDGE_MM=sorted(EDGE_LEN0)[len(EDGE_LEN0)//2]*MM
reuse.update(reuse_functions(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals()))
labels=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')['membership']['vertex_labels']
def face_domain(fi):
    labs={labels.get(str(v),'OUTSIDE_BOUNDED_DOMAIN') for v in POLY[fi]}
    return next(iter(labs)) if len(labs)==1 else 'MIXED_AUTHORITY_BAND'
FD=[face_domain(k) for k in range(len(POLY))]
debt=read(OUT/'INHERITED_DEBT_DEFORMATION_MAPPING.json')['rows']
debtids=[r['debt_id'] for r in debt]
assets={'R1E':S5/'stage5b_r1e/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1E.blend',
 'R1B_DONOR':S5/'stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend',
 'R1_CORRECTED_RIG':R1D/'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend','R2':CAND}
records={};positions={};bone_mats={};assertions={}
def local_metrics(V,m,ratios,er,ids,fs,es):
    fs=set(fs);es=set(es);core=set(ids)
    broad=[(a,b) for a,b in m['_newp'] if a in fs or b in fs]
    exact=[]
    for a,b in broad:
        e=pair_evidence(V,a,b);e.pop('pts',None)
        exact.append({'face_ids':[a,b],'domains':[FD[a],FD[b]],'both_faces_in_patch':a in fs and b in fs,'class':classify(e),**e})
    severe=[k for k in es if EDGE_LEN0[k]*MM>=C.SEVERE_MIN_BIND_MM and er[k]>C.SEVERE_STRETCH_X]
    tear=[k for k in es if er[k]>C.TEAR_X and er[k]*EDGE_LEN0[k]*MM>C.TEAR_MIN_POSED_MM]
    collapsed=[k for k in fs if S.face_area(V,POLY[k])<=1e-12 or ratios[k]<=1e-6]
    under5=[k for k in fs if ratios[k]<.05]
    normals=[k for k in fs if S.face_normal(V,POLY[k]).dot(S.face_normal(V0,POLY[k]))<-.5]
    return {'vertex_count':len(core),'face_count':len(fs),'edge_count':len(es),
       'severe_edge_ids':sorted(severe),'severe_edge_count':len(severe),'tear_strain_edge_ids':sorted(tear),
       'tear_strain_is_automatic_surface_destruction':False,'collapsed_face_ids':sorted(collapsed),
       'degenerate_edge_ids':[k for k in es if (V[EDGES[k][0]]-V[EDGES[k][1]]).length<=1e-12],
       'area_ratio_below_0_05_face_ids':sorted(under5),'normal_flip_diagnostic_face_ids':sorted(normals),
       'normal_flip_alone_is_inversion':False,'min_face_area_ratio':min((ratios[k] for k in fs),default=1),
       'min_edge_ratio_compression_diagnostic':min((er[k] for k in es),default=1),
       'max_edge_ratio':max((er[k] for k in es),default=1),
       'max_displacement_mm':max(((V[i]-V0[i]).length*MM for i in core),default=0),
       'raw_BVH_new_pairs':broad,'intersection_evidence':exact,
       'visible_geometric_crossings_count':sum(e['class']=='CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION' for e in exact),
       'mixed_band_intersections_require_human_review':any('MIXED_AUTHORITY_BAND' in e['domains'] for e in exact)}
for asset,path in assets.items():
    assert path.is_file()
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[C.MESH_OBJ];rig=bpy.data.objects[C.RIG_OBJ];MW=ob.matrix_world.copy()
    original_weights=C.read_weights(ob,NV)
    assert [tuple(e.vertices) for e in ob.data.edges]==EDGES and [tuple(p.vertices) for p in ob.data.polygons]==POLY
    C.reset_pose(rig);C.update()
    vb,pb=C.evaluate(ob,MW)
    positions[asset]={'BIND':[list(p) for p in vb]};records[asset]={};bone_mats[asset]={}
    bind_max=max((a-b).length*MM for a,b in zip(vb,V0))
    for case in matrix['poses']:
        cid=case['case_id']
        if 'bone' in case: set_s6a(rig,case['bone'],case['angle_deg'])
        else: set_s6b(rig,cid)
        C.update();V,P=C.evaluate(ob,MW)
        assert P==POLY
        m,ratios,er=metrics(V,P)
        positions[asset][cid]=[list(p) for p in V]
        bone_mats[asset][cid]={g:[list(r) for r in <REDACTED_EMAIL>[g]<REDACTED_EMAIL>[g].matrix_local.inverted()@rig.matrix_world.inverted()] for g in C.DEFORM}
        patch={n:local_metrics(V,m,ratios,er,f['core'],f['face_ids'],f['edge_ids']) for n,f in fixtures.items()}
        drows={}
        for d in debt:
            k=d['debt_id'];a,b=EDGES[k]
            if cid not in d['historical_pose_ids']: continue
            es=[j for j,(u,v) in enumerate(EDGES) if u in {a,b} or v in {a,b}]
            fs=[j for j,p in enumerate(POLY) if a in p or b in p]
            drows[str(k)]={'edge_id':k,'ratio':er[k],'bind_mm':EDGE_LEN0[k]*MM,'posed_mm':er[k]*EDGE_LEN0[k]*MM,
              'severe':EDGE_LEN0[k]*MM>=C.SEVERE_MIN_BIND_MM and er[k]>C.SEVERE_STRETCH_X,
              'tear_strain':er[k]>C.TEAR_X and er[k]*EDGE_LEN0[k]*MM>C.TEAR_MIN_POSED_MM,
              'endpoint_displacements_mm':[(V[v]-V0[v]).length*MM for v in [a,b]],
              'local':local_metrics(V,m,ratios,er,[a,b],fs,es)}
        allm={k:v for k,v in m.items() if k!='_newp'}
        records[asset][cid]={'run_label':case['run_label'],'global_metrics_context_only':allm,'fixtures':patch,'debts':drows,
          'edge5879':{'ratio':er[5879],'bind_mm':EDGE_LEN0[5879]*MM,'posed_mm':er[5879]*EDGE_LEN0[5879]*MM},
          'pose_state':S.pose_state(rig)}
        print(asset,cid,'edge5879',round(er[5879],5),'fixture severe',{n:f['severe_edge_count'] for n,f in patch.items()},flush=True)
    C.reset_pose(rig);C.update()
    restored,_=C.evaluate(ob,MW)
    assertions[asset]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bind_evaluated_difference_mm':bind_max,
      'zero_restore_max_mm':max((a-b).length*MM for a,b in zip(restored,vb)),
      'all_weights_unchanged_in_memory':C.read_weights(ob,NV)==original_weights,
      'rig_rest_data_not_modified':True,'blend_saves':0}
dump('TARGETED_DEFORMATION_MACHINE_EVIDENCE.json',{'historical_function_AST_hashes':reuse,'thresholds':{'severe_x':C.SEVERE_STRETCH_X,'severe_min_bind_mm':C.SEVERE_MIN_BIND_MM,'tear_strain_x':C.TEAR_X,'tear_strain_min_posed_mm':C.TEAR_MIN_POSED_MM,'collapse_area_m2':1e-12,'collapse_area_ratio':1e-6,'local_surface_destruction_area_ratio':.05},'SI_semantics':'R1C V2 exact crossing/poke-depth versus bind local facet resolution; old cut-component same-surface gate retired, frozen fresh pure-face vs mixed-band labels only','production_save_calls':0,'results':records,'asset_assertions':assertions})
dump('POSED_COORDINATE_EVIDENCE.json',{'positions_world_m':positions,'deform_transform_world':bone_mats})
assert sha(CAND)==EXPECTED
assert all(r['all_weights_unchanged_in_memory'] and r['zero_restore_max_mm']==0 for r in assertions.values())
print('Bounded seven-pose measurement batch complete. No new pose suite, no blend writes.')
