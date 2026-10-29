import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PREV=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
PARENT=ROOT/'experiments/hands_local_skin_asset_repair_poc_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,o):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
proposal=read(PARENT/'CONFIRMED_ROI_PROPOSAL.json')
top=read(PREV/'NATIVE_TOPOLOGY.json');F=np.array(top['faces']);E=np.array(top['edges']);z=np.load(PREV/'ORIGINAL_SNAPSHOT.npz')
ef={}
for i,f in enumerate(F):
 for a,b in zip(f,np.roll(f,-1)):ef.setdefault(tuple(sorted(map(int,[a,b]))),[]).append(i)
adj={i:set() for i in range(len(F))}
for fs in ef.values():
 for i in fs:adj[i].update(set(fs)-{i})
def bounds(fs):
 counts={}
 for i in fs:
  f=F[i]
  for a,b in zip(f,np.roll(f,-1)):
   e=tuple(sorted(map(int,[a,b])));counts[e]=counts.get(e,0)+1
 return [list(e) for e,n in counts.items() if n==1]
S=set(proposal['regions']['S']['core_vertex_ids'])
Sguard=S|{int(b) if int(a) in S else int(a) for a,b in E if a in S or b in S}
patches={}
for k,steps in [('A',3),('B',2)]:
 core=set(proposal['regions'][k]['core_face_ids']);fs=core.copy();rings=[]
 for step in range(steps):
  more=set().union(*(adj[i] for i in fs))-fs;rings.append(sorted(more));fs|=more
 edge=bounds(fs);fixed=set(v for e in edge for v in e);vertices=set(map(int,F[list(fs)].flat));editable=vertices-fixed-Sguard
 if k=='A':
  editable={i for i in editable if -.003<=z['ALONG'][i]<=.022 and z['RADIUS'][i]<.016}
 fixed=vertices-editable
 support={i for i,f in enumerate(F) if set(map(int,f))&editable}
 assert support<=fs and not editable&Sguard
 patches[k]={'anatomical_structure':'Thumb-facing proximal index soft-tissue sidewall and immediate MCP transition, PIP region fixed' if k=='A' else 'Lower first-web fan joining thumb/index bases to palm, S protected collar fixed','original_core_face_ids':sorted(core),'expanded_face_rings':rings,'display_context_face_ids':sorted(fs),'faces_potentially_affected':sorted(support),'core_editable_vertex_ids':sorted(editable&set(map(int,F[list(core)].flat))),'soft_transition_vertex_ids':sorted(editable-set(map(int,F[list(core)].flat))),'all_editable_vertex_ids':sorted(editable),'fixed_boundary_and_excluded_vertex_ids':sorted(fixed),'outer_boundary_edges':edge,'original_maximum_movable_vertices_are_not_current_limit':True,'S_core_and_one_edge_ring_fixed':True,'vertex_coordinates_basis_m':{str(i):z['RV'][i].tolist() for i in sorted(vertices)},'vertex_coordinates_original_C1_world_m':{str(i):z['V'][i].tolist() for i in sorted(vertices)},'face_vertices':{str(i):F[i].tolist() for i in sorted(fs)}}
save('SCULPT_SCOPE_BEFORE_EDIT.json',{'task':'HANDS_ANATOMICAL_SCULPT_VISUAL_POC_R1','status':'SCOPE_RECORDED_BEFORE_SCULPT','vertex_count':3300,'native_face_count':3298,'source_proposal_sha256':sha(PARENT/'CONFIRMED_ROI_PROPOSAL.json'),'indexing':'zero based original native IDs','S_core_vertex_ids':sorted(S),'S_protected_collar_vertex_ids':sorted(Sguard),'patches':patches,'topology_changes_allowed':False,'rest_weights_original_corrective_changes_allowed':False,'new_experimental_shape_key_on_private_copy_only':True,'maximum_substantive_sculpt_rounds_per_region':2,'instruction_tail_received':False})
refs=[ROOT/'audits/piano_hand_posture_reference_and_static_feasibility_r1/_research/right_source_view.png',ROOT/'audits/piano_hand_posture_reference_and_static_feasibility_r1/_research/left_source_view.png',ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1/overlay420.png']
save('REAL_REFERENCE_OBSERVATIONS.json',{'references':[{'path':str(p),'sha256':sha(p),'type':'Existing project photograph / photographed performance, not AI-generated','use':'Internal qualitative observation only; existing source attribution/usage limitations preserved'} for p in refs],'observations':['Proximal index sidewall carries a gentle soft-tissue profile between actual joints; do not interpret skin curvature as a new bone joint.','The first web joins thumb/index bases as a broad concave transition rather than a pinched notch or a solid inflated ball.','Photographs support qualitative silhouette and tissue continuity, not a unique metric sculpt target or pose transfer.'],'original_sources':['MusicRadar / Daniel Griffiths right hand reference','PiaDOOR left-hand octave static photograph','PianoVAM 2024-03-04_03-46-36, source frame420 (7.0s), internal noncommercial validation, CC BY-NC-SA4.0'],'previous_candidates_human_status':'ALL_REJECTED_FOR_PERCEPTIBLE_NATURAL_FORM_IMPROVEMENT; prior machine results retained as historical evidence only.'})
paths=[Path(r['path']) for r in read(PARENT/'roi_approved_asset_trials_r1/PROTECTED_SHA256_BEFORE_AFTER.json')['files']]
paths+=[PREV/'ORIGINAL_SNAPSHOT.npz',PREV/'NATIVE_TOPOLOGY.json',PARENT/'CONFIRMED_ROI_PROPOSAL.json',*refs]
save('PROTECTED_BEFORE.json',[{'path':str(p),'sha256':sha(p)} for p in dict.fromkeys(paths)])
print(json.dumps({k:{'editable_vertices':len(v['all_editable_vertex_ids']),'core_vertices':len(v['core_editable_vertex_ids']),'transition_vertices':len(v['soft_transition_vertex_ids']),'affected_faces':len(v['faces_potentially_affected']),'S_overlap':0} for k,v in patches.items()}))

