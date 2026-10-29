"""Two existing isolated poses, three named pairs, immutable Blender inputs.
Controlled counterfactuals are mathematical LBS evaluations, not hybrid candidates.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from causal_common import *
import bpy,math,numpy as np
from mathutils import Vector,Matrix,Quaternion
sys.path.append(str(S6/'stage6a/scripts'));sys.path.append(str(S6/'stage6b_r1c/scripts'));sys.path.append(str(S5/'stage5b_r1e/scripts'))
import s6a_common as S
import s5b_r1e_common as C
import r1c_pen_common as R
saved=read(R2D/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')
POLY=[tuple(p) for p in saved['mesh']['faces']];EDGES=[tuple(e) for e in saved['mesh']['edges']]
# Preserve the predecessor V2 bind-facet scale and frozen triangulation byte for byte.
V0=[Vector(p)/1000 for p in saved['mesh']['positions_world_mm']]
NATIVE0=[Matrix(saved['mesh']['matrix_world'])@Vector(p) for p in saved['mesh']['positions_local_m']]
TRIS=R.tris_of(POLY,V0);FACE_TRIS={}
for fi,t in TRIS:FACE_TRIS.setdefault(fi,[]).append(t)
MM=1000.;CHARACTERISTIC_EDGE_MM=3.888205
funcs=reuse(S6/'stage6b_r1c/scripts/r1c_pen_v2.py',['tri_of','tri_mean_edge','pair_evidence','classify'],globals())
ns={'bpy':bpy};reuse(R1D/'blender_extract.py',['mesh_payload','rig_payload','weights'],ns)
labels=read(ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json')['membership']['vertex_labels']
adj={i:set() for i in range(len(V0))}
for a,b in EDGES:adj[a].add(b);adj[b].add(a)
patches={};localids=set()
for pair in PAIRS:
    parts=[]
    for fi in pair['faces']:
        ids=set(POLY[fi]);lab={labels.get(str(v)) for v in ids};assert len(lab)==1
        label=next(iter(lab));ring=(ids|{u for v in ids for u in adj[v]})
        ring={v for v in ring if labels.get(str(v))==label}
        fs=[k for k,p in enumerate(POLY) if set(p)<=ring]
        es=[k for k,(a,b) in enumerate(EDGES) if a in ring and b in ring]
        parts.append({'face_id':fi,'label':label,'core_vertex_ids':list(POLY[fi]),'one_ring_same_frozen_label_vertex_ids':sorted(ring),'one_ring_face_ids':fs,'one_ring_edge_ids':es})
        localids.update(ring)
    patches[pair['id']]=parts
LOCAL=sorted(localids)
local_index={v:i for i,v in enumerate(LOCAL)}
poses={'TH_IP_30':('THUMB_IP_R',30.),'IDX_MCP_45':('INDEX_MCP_R',45.)}
extracts={};sweep={};endpoints={};matrices={};kernelerrors={};classifiermatches={}
def apply(rig,bone,ang):S.reset_pose(rig);S.set_joint_rotation(rig,bone,-ang);bpy.context.view_layer.update()
def trans(rig):
    # World-space skin matrix using each rig's own rest inverse. No bind-space edit.
    rm=rig.matrix_world.copy();ri=rm.inverted()
    return {g:np.array(<REDACTED_EMAIL>[g]<REDACTED_EMAIL>[g].matrix_local.inverted()@ri,dtype=np.float64) for g in C.DEFORM}
def calc(W,D,ids):
    P=np.array([list(NATIVE0[i]) for i in ids]);delta=np.zeros_like(P);sumw=np.zeros(len(ids))
    for g,T in D.items():
        w=np.array([W[i].get(g,0) for i in ids]);sumw+=w
        delta+=w[:,None]*(P@T[:3,:3].T+T[:3,3]-P)
    assert np.all(sumw>0)
    return P+delta/sumw[:,None]
def asfull(local):
    v=list(NATIVE0)
    for i,p in zip(LOCAL,local):v[i]=Vector(p)
    return v
def oldproxy(V,fa,fb):
    a=S.face_centroid(V,POLY[fa]);b=S.face_centroid(V,POLY[fb]);na=S.face_normal(V,POLY[fa]);nb=S.face_normal(V,POLY[fb])
    return min(abs((b-a).dot(na)),abs((a-b).dot(nb)))*MM
def dist_segment(a,b,c,d):
    # Geometric closest distance of two closed segments; no visibility gate.
    u=b-a;v=d-c;w=a-c;aa=u@u;bb=u@v;cc=v@v;dd=u@w;ee=v@w;den=aa*cc-bb*bb
    vals=[]
    if aa>0 and cc>0 and den>1e-30:
        s=(bb*ee-cc*dd)/den;t=(aa*ee-bb*dd)/den
        if 0<=s<=1 and 0<=t<=1:vals.append(np.linalg.norm(w+s*u-t*v))
    for p,x,y in [(a,c,d),(b,c,d),(c,a,b),(d,a,b)]:
        q=y-x;t=np.clip(((p-x)@q)/(q@q),0,1) if q@q else 0
        vals.append(np.linalg.norm(p-x-t*q))
    return min(vals)
def minimum_triangle_distance(V,fa,fb,intersect):
    if intersect:return 0.
    best=math.inf
    for ta in FACE_TRIS[fa]:
      for tb in FACE_TRIS[fb]:
        A=[V[v] for v in ta];B=[V[v] for v in tb]
        for p,other in [(p,B) for p in A]+[(p,A) for p in B]:best=min(best,(p-R.closest_point_on_triangle(p,*other)).length)
        for j in range(3):
          for k in range(3):best=min(best,dist_segment(np.array(A[j]),np.array(A[(j+1)%3]),np.array(B[k]),np.array(B[(k+1)%3])))
    return best*MM
def measure(V,pair):
    fa,fb=pair['faces'];e=pair_evidence(V,fa,fb);e.pop('pts',None)
    near=minimum_triangle_distance(V,fa,fb,e['intersect'])
    return {**e,'V2_class':classify(e),'Stage6A_centroid_plane_proxy_mm':oldproxy(V,fa,fb),'minimum_triangle_distance_mm':near,'contact_at_existing_numeric_precision':near<=.001,'geometric_contact_tolerance_is_new_severity_gate':False,'shared_vertices':sorted(set(POLY[fa])&set(POLY[fb]))}
for asset,path in ASSETS.items():
    assert sha(path)==read(OUT/'CAUSAL_INPUT_MANIFEST.json')['assets'][asset]['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    ob=bpy.data.objects[C.MESH_OBJ];rig=bpy.data.objects[C.RIG_OBJ];MW=ob.matrix_world.copy()
    payload={'mesh':ns['mesh_payload'](ob),'rig':ns['rig_payload'](rig),'weights':ns['weights'](ob),'group_order':[g.name for g in ob.vertex_groups]}
    expected=saved if asset=='R2' else read(R1D/'CANDIDATE_CLEAN_REOPEN_PAYLOAD_R1.json') if asset=='CORRECTED_R1' else read(R1D/'LIVE_SOURCE_DATA_R1.json')['R1B']
    assert all(payload[k]==expected[k] for k in payload)
    assert payload['mesh']['positions_local_m']==saved['mesh']['positions_local_m'] and payload['mesh']['edges']==saved['mesh']['edges'] and payload['mesh']['faces']==saved['mesh']['faces']
    assert len(payload['mesh']['modifiers'])==1 and payload['mesh']['modifiers'][0]['type']=='ARMATURE' and not payload['mesh']['modifiers'][0]['use_deform_preserve_volume'] and not payload['mesh']['modifiers'][0]['use_bone_envelopes']
    extracts[asset]=payload;sweep[asset]={};endpoints[asset]={};matrices[asset]={};kernelerrors[asset]={};classifiermatches[asset]={}
    for pose,(bone,limit) in poses.items():
        records=[];Ds={};errs=[];matches=[];cache={}
        def evaluate(ang):
            key=str(ang)
            if key in cache:return cache[key]
            apply(rig,bone,ang);V,P=S.evaluate(ob,MW);assert P==POLY
            D=trans(rig);pred=calc(payload['weights'],D,LOCAL);actual=np.array([list(V[i]) for i in LOCAL])
            err=float(np.linalg.norm(pred-actual,axis=1).max()*MM)
            prs=[p for p in PAIRS if p['pose']==pose]
            out={p['id']:measure(V,p) for p in prs}
            pv=asfull(pred);pm={p['id']:measure(pv,p)['V2_class']==out[p['id']]['V2_class'] and measure(pv,p)['intersect']==out[p['id']]['intersect'] for p in prs}
            item={'angle_deg':ang,'pairs':out,'kernel_max_error_mm':err,'kernel_classification_matches':pm,'local_positions_world_m':actual.tolist()}
            Ds[key]={g:t.tolist() for g,t in D.items()};cache[key]=item
            if ang in [0.,limit]:endpoints[asset][pose+'__'+str(ang)]=[list(p) for p in V]
            return item
        for i in range(int(limit*2)+1):records.append(evaluate(i*.5))
        brackets={}
        for pair in [p for p in PAIRS if p['pose']==pose]:
            pid=pair['id'];b={}
            for name,pred in [('contact',lambda e:e['contact_at_existing_numeric_precision']),('exact_crossing',lambda e:e['intersect']),('V2_Class_A',lambda e:e['V2_class']=='CASE_A_VISIBLE_GEOMETRIC_INTERPENETRATION')]:
                j=next((i for i,r in enumerate(records) if pred(r['pairs'][pid])),None)
                if j is None:b[name]={'status':'NOT_OBSERVED_IN_AUTHORIZED_RANGE','angle_deg':None};continue
                hi=records[j]['angle_deg'];lo=records[j-1]['angle_deg'] if j else hi
                while hi-lo>.03125:
                    mid=(lo+hi)/2
                    if pred(evaluate(mid)['pairs'][pid]):hi=mid
                    else:lo=mid
                b[name]={'status':'BRACKETED' if j else 'PRESENT_AT_BIND','angle_interval_deg':[lo,hi],'first_positive_sample_angle_deg':hi,'measurement_at_hi':evaluate(hi)['pairs'][pid],'local_surface_sample_key':str(hi)}
            brackets[pid]=b
        sweep[asset][pose]={'bone':bone,'local_X_sign':-1,'max_angle_deg':limit,'fixed_step_deg':.5,'refined_first_transition_interval_width_deg':.03125,'scope':'Specified pairs only; not global digit contact census','fixed_grid':records,'additional_refinement_samples':sorted([r for k,r in cache.items() if float(k)%0.5!=0],key=lambda r:r['angle_deg']),'onsets':brackets}
        matrices[asset][pose]=Ds
        kernelerrors[asset][pose]=max(r['kernel_max_error_mm'] for r in cache.values())
        classifiermatches[asset][pose]={pid:all(r['kernel_classification_matches'][pid] for r in cache.values()) for pid in brackets}
        print(asset,pose,'onsets',{k:{a:v.get('angle_interval_deg') for a,v in b.items()} for k,b in brackets.items()},'kernel max mm',kernelerrors[asset][pose],flush=True)
    S.reset_pose(rig);bpy.context.view_layer.update()
    assert ns['weights'](ob)==payload['weights'] and ns['mesh_payload'](ob)==payload['mesh']
    # Reset euler values may serialize differently in memory; rest data and file remain exact.
    assert sha(path)==read(OUT/'CAUSAL_INPUT_MANIFEST.json')['assets'][asset]['sha256']
# Establish valid skinning intervention contract before constructing mathematical hybrids.
donor=extracts['HISTORICAL_R1B_DONOR'];r1=extracts['CORRECTED_R1'];r2=extracts['R2'];changed=[]
for bone,a in donor['rig']['bones'].items():
    b=r1['rig']['bones'][bone]
    for k in ['head_local_m','tail_local_m','matrix_local','parent','use_deform','use_connect','inherit_scale','use_inherit_rotation','use_local_location']:
        if a[k]!=b[k]:changed.append([bone,k])
assert all(b in ['THUMB_IP_R','THUMB_TIP_R'] for b,k in changed)
assert r1['rig']==r2['rig']
assert donor['group_order']==r1['group_order']==r2['group_order']
counter={};cfcoords={};validity={'status':'IDENTIFIABLE_MECHANICAL_LBS_COUNTERFACTUAL_ONLY','same_vertex_positions_topology_and_world_bind_mapping':True,'same_group_order_and_bone_group_names':True,'same_joint_head_parent_driver_meaning':True,'kinematic_slot_differences':changed,'skin_is_saved_scalar_vertex_group_field_not_recomputed_arc_profile':True,'modifier_model':'Single normalized linear armature skinning; preserve_volume false, envelopes false, no corrective/shapekey modifier','counterfactual_semantic_limit':'K_ONLY/W_ONLY are numerical interventions on the Blender skinning mechanism, not anatomically approved skins/rigs and not production candidates. W_ONLY asks what saved corrected vectors would do under historical compatible local-X frames, not whether that skin would have been authorized in that state.','actual_modifier_kernel_max_error_mm':kernelerrors,'actual_vs_kernel_predicate_matches':classifiermatches,'no_bone_or_weight_or_geometry_assignments':True,'counterfactual_production_saves':0}
for pose,(bone,limit) in poses.items():
    old={g:np.array(m) for g,m in matrices['HISTORICAL_R1B_DONOR'][pose][str(limit)].items()};new={g:np.array(m) for g,m in matrices['CORRECTED_R1'][pose][str(limit)].items()}
    cf={'BASE':(donor['weights'],old),'K_ONLY':(donor['weights'],new),'W_ONLY':(r1['weights'],old),'FULL':(r1['weights'],new),'R2_W_ONLY':(r2['weights'],old),'R2_FULL':(r2['weights'],new)}
    counter[pose]={};cfcoords[pose]={}
    for name,(w,d) in cf.items():
        allp=calc(w,d,list(range(len(V0))));V=[Vector(p) for p in allp];cfcoords[pose][name]=[list(p) for p in V]
        counter[pose][name]={p['id']:measure(V,p) for p in PAIRS if p['pose']==pose}
dump('COUNTERFACTUAL_IDENTIFIABILITY_AND_INPUT_CHECK.json',validity)
dump('CONTROLLED_K_W_COUNTERFACTUAL_EVIDENCE.json',{'validity':validity,'terminal_pose_2x2':counter,'actual_candidate_inputs':{a:{'weight_vector_sha256':digest(p['weights']),'rig_snapshot_sha256':digest(p['rig']),'mesh_snapshot_sha256':digest(p['mesh'])} for a,p in extracts.items()},'limitations':'Mechanical cause of a crossing can be identifiable while cause of an unacceptable teaching/skin defect is not; those are different outcomes.'})
dump('CROSSING_ONSET_SWEEP.json',{'scope':PAIRS,'resolution':{'fixed_step_deg':.5,'first_transition_bracket_deg':.03125,'contact_numeric_resolution_mm':.001,'contact_precision_source':'Existing V2 closest-foot comparison <=1e-6m; not a new allowance angle or severity gate'},'triangulation':'Unchanged predecessor V2 frozen bind triangulation; faces do not share vertices; all three absence-at-bind checked','results':sweep,'classifier_source_AST_hashes':funcs,'minimum_onset_means':'First sampled/refined occurrence for THIS EXACT pair within authorized interval; contacts may appear/disappear nonmonotonically; not first global THUMB/INDEX contact','production_saves':0,'other_fixtures_evaluated':[]})
dump('CAUSAL_COORDINATE_EVIDENCE.json',{'native_bind_world_m':[list(p) for p in NATIVE0],'legacy_V2_bind_world_m':[list(p) for p in V0],'faces':POLY,'edges':EDGES,'local_vertex_ids':LOCAL,'patches':patches,'actual_endpoints_world_m':endpoints,'counterfactual_endpoint_world_m':cfcoords,'pose_skin_matrices':matrices})
dump('LIVE_INPUT_PAYLOAD_VERIFICATION.json',{'status':'PASS','live_inputs_exact_saved':True,'R2_file_and_vector_hash':sha(ASSETS['R2']),'R2_vector_sha256':digest(r2['weights']),'kinematic_changes_only_frozen_IP_TIP_slots':changed,'R1_and_R2_all_rig_snapshots_equal':True,'geometry_topology_all_three_exact':True,'production_weight_assignment_calls':0,'rest_bone_assignment_calls':0,'production_save_calls':0})
print('Three-pair controlled causal evidence complete; no production mutations.')
