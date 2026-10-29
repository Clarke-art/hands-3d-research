import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];OLD=ROOT/'experiments/hands_local_skin_asset_repair_poc_r1/roi_approved_asset_trials_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def put(n,s):
 with (OUT/n).open('x',encoding='utf8') as f:f.write(s)
scope=read(OUT/'SCULPT_SCOPE_BEFORE_EDIT.json')
p=ROOT/'experiments/hands_index_root_webspace_anatomy_repair_r1'
z=np.load(p/'ORIGINAL_SNAPSHOT.npz');top=read(p/'NATIVE_TOPOLOGY.json');F=np.array(top['faces']);E=np.array(top['edges'])
ef={}
for i,f in enumerate(F):
 for a,b in zip(f,np.roll(f,-1)):ef.setdefault(tuple(sorted(map(int,[a,b]))),[]).append(i)
adj={i:set() for i in range(len(F))}
for fs in ef.values():
 for i in fs:adj[i].update(set(fs)-{i})
core=set(scope['patches']['B']['original_core_face_ids']);fs=core.copy();rings=[]
for step in range(3):
 more=set().union(*(adj[i] for i in fs))-fs;rings.append(sorted(more));fs|=more
counts={}
for i in fs:
 f=F[i]
 for a,b in zip(f,np.roll(f,-1)):
  e=tuple(sorted(map(int,[a,b])));counts[e]=counts.get(e,0)+1
edge=[list(e) for e,n in counts.items() if n==1];vv=set(map(int,F[list(fs)].flat));fixed=set(v for e in edge for v in e)
editable=vv-fixed-set(scope['S_protected_collar_vertex_ids'])
editable={i for i in editable if -.052<=z['C'][i,0]<=-.021 and .044<=z['C'][i,1]<=.083}
r=scope['patches']['B'];r.update(expanded_face_rings=rings,display_context_face_ids=sorted(fs),faces_potentially_affected=[i for i,f in enumerate(F) if set(map(int,f))&editable],core_editable_vertex_ids=sorted(editable&set(map(int,F[list(core)].flat))),soft_transition_vertex_ids=sorted(editable-set(map(int,F[list(core)].flat))),all_editable_vertex_ids=sorted(editable),fixed_boundary_and_excluded_vertex_ids=sorted(vv-editable),outer_boundary_edges=edge,vertex_coordinates_basis_m={str(i):z['RV'][i].tolist() for i in sorted(vv)},vertex_coordinates_original_C1_world_m={str(i):z['V'][i].tolist() for i in sorted(vv)},face_vertices={str(i):F[i].tolist() for i in sorted(fs)})
r['scope_refinement_reason']='Third local edge-neighbour ring supplies actual soft transition vertices; restricted to same lower first-web fan in canonical coordinates. Original S core plus collar remain fixed. Recorded before any sculpt.'
scope.update(status='ACTIVE_SCOPE_RECORDED_BEFORE_ANY_SCULPT',instruction_tail_received=True,scope_prior_draft_preserved=True)
assert not editable&set(scope['S_protected_collar_vertex_ids'])
write('SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json',scope)
old=(OLD/'trial_common.py').read_text(encoding='utf8')
new=old.replace("OUT=Path(__file__).resolve().parent; PARENT=OUT.parent; ROOT=OUT.parents[2]","OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]; PARENT=ROOT/'experiments/hands_local_skin_asset_repair_poc_r1'")
new=new.replace("for r in read(PARENT/'ROI_INPUT_SHA256_BEFORE.json'):READS[r['path']]=sha(r['path'])","for r in read(OUT/'PROTECTED_BEFORE.json'):\n assert sha(r['path'])==r['sha256'];READS[r['path']]=r['sha256']")
start=new.index("A=np.array(PROPOSAL['regions']")
end=new.index("T=np.r_[F[:,[0,1,2]]",start)
new=new[:start]+"SCOPE=read(OUT/'SCULPT_SCOPE_ACTIVE_BEFORE_EDIT.json')\nA=np.array(SCOPE['patches']['A']['all_editable_vertex_ids']);B=np.array(SCOPE['patches']['B']['all_editable_vertex_ids']);S=np.array(SCOPE['S_core_vertex_ids'])\nassert not (set(A)&set(S) or set(B)&set(S))\n"+new[end:]
new=new[:new.index("POSES=[")]
put('sculpt_common.py',new)
put('sculpt_geometry.py',(OLD/'trial_geometry.py').read_text(encoding='utf8').replace('from trial_common import *','from sculpt_common import *'))
put('run_stage.py',(OLD/'run_stage.py').read_text(encoding='utf8'))
write('TOOLING_REUSE_RECEIPT.json',[{'path':str(OLD/n),'sha256':hashlib.sha256((OLD/n).read_bytes()).hexdigest(),'use':'Existing direct Blender IO / geometry measurement helpers only; no optimizer'} for n in ['trial_common.py','trial_geometry.py','run_stage.py']])
print(json.dumps({k:{'editable':len(v['all_editable_vertex_ids']),'core':len(v['core_editable_vertex_ids']),'transition':len(v['soft_transition_vertex_ids']),'S_overlap':0} for k,v in scope['patches'].items()}))

