import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from trial_common import *
save('PROTECTED_BEFORE.json',[dict(path=p,sha256=h) for p,h in READS.items()])
sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6)
assert len(mesh.data.vertices)==3300 and len(mesh.data.polygons)==3298
V,TT,FF=coords(mesh);assert np.array_equal(FF,F)
z=np.load(PREV/'ORIGINAL_SNAPSHOT.npz');assert np.array_equal(V,z['V'])
rv=np.array([list(v.co) for v in mesh.data.shape_keys.key_blocks[0].data]);assert np.array_equal(rv,z['RV'])
for k in ['A','B','S']:
 r=PROPOSAL['regions'][k]
 assert all(F[i].tolist()==r['face_vertices'][str(i)] for i in r['core_face_ids']+r['transition_face_ids'])
 movable=set(r['maximum_proposed_movable_vertex_ids']);fixed=set(r['fixed_outer_boundary_vertex_ids']);assert not movable&fixed
 support=set(r['core_face_ids']+r['transition_face_ids']);assert all(i in support for i,f in enumerate(F) if set(map(int,f))&movable)
 # Edge-connected native core, as opposed to a screenshot polygon.
 core=set(r['core_face_ids']);seen={min(core)}
 while True:
  new={j for i in seen for j in core-seen if len(set(F[i])&set(F[j]))>=2}
  if not new:break
  seen|=new
 assert seen==core
save('TOPOLOGY_AND_AUTHORIZATION_PREFLIGHT.json',dict(mesh=mesh.name,rig=rig.name,vertex_count=3300,face_count=3298,source_snapshot_error_mm=0,face_indices_exact=True,core_edge_connected=True,all_support_boundaries_exact=True,A_allowed=A,B_allowed=B,S_forbidden=S,source_sha256=sha(SOURCE),proposal_sha256=sha(PARENT/'CONFIRMED_ROI_PROPOSAL.json'),human_authorization_sha256=sha(OUT/'HUMAN_AUTHORIZATION.txt'),piano_access=False))
J=jacobians(mesh,rig);N=normals(V)
plans={}
delta1=np.zeros_like(rv);delta2=np.zeros_like(rv)
for i in A:
 # Modest lateral reduction centered in the authorized proximal skin band.
 t=float(z['ALONG'][i]);fall=.45+.55*math.exp(-((t-.007)/.007)**2)
 lateral=np.array([.00046*fall,0,0]);delta1[i]=np.linalg.solve(J[i],lateral)
 neigh=np.array(sorted({int(b) if a==i else int(a) for a,b in E if a==i or b==i}))
 lap=V[neigh].mean(0)-V[i]
 # Distinct A2: normal component of fairing, not an all-axis flattening.
 normal=0.78*float(lap@N[i])*N[i];length=np.linalg.norm(normal)
 if length>.00053:normal*=.00053/length
 delta2[i]=np.linalg.solve(J[i],normal)
plans['A1']={'basis_delta':delta1,'description':'Lateral contour trim only, 0.46mm peak world target with proximal falloff; no sagittal flattening.'}
plans['A2']={'basis_delta':delta2,'description':'Single normal-only fairing of authorized points, 78% of native one-ring normal residual, capped at 0.53mm world; all-axis Laplacian movement rejected.'}
plans['B1']={'weight_transfer_CMC_to_WRIST':{1375:.025,1376:.060,1444:.015,2793:.030},'description':'Transfer small vertex-specific CMC fractions to existing WRIST group to reduce thumb-root pull at lower web connector. Preserve all other group memberships and total weight.'}
deltaB=np.zeros_like(rv)
for i,mm in {1375:.18,1376:.60,1444:.12,2793:.22}.items():deltaB[i]=np.linalg.solve(J[i],N[i]*mm/1000)
plans['B2']={'corrective_delta':deltaB,'description':'Independent local outward soft-tissue relief on four B points; manual experimental shape key at value 1, no driver or automatic trigger.'}
save('MODELING_PLANS.json',plans)
all_edits={}
for kind,plan in plans.items():
 sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);before=signature(mesh,rig,left);names,w0=weights(mesh)
 oldmesh=mesh.data;mesh.data=oldmesh.copy();base=np.array([list(v.co) for v in mesh.data.shape_keys.key_blocks[0].data]);shapes0={k.name:np.array([list(v.co) for v in k.data]) for k in mesh.data.shape_keys.key_blocks}
 if kind.startswith('A'):
  delta=plan['basis_delta']
  for i in A:
   mesh.data.shape_keys.key_blocks[0].data[int(i)].co=Vector(base[i]+delta[i]);mesh.data.vertices[int(i)].co=Vector(base[i]+delta[i])
 elif kind=='B1':
  for i,t in plan['weight_transfer_CMC_to_WRIST'].items():
   wi=w0[i,names.index('WRIST_R')];ci=w0[i,names.index('THUMB_CMC_R')];assert ci>=t
   mesh.vertex_groups['WRIST_R'].add([i],float(wi+t),'REPLACE');mesh.vertex_groups['THUMB_CMC_R'].add([i],float(ci-t),'REPLACE')
 else:
  key=mesh.shape_key_add(name='EXPERIMENT_ROI_B_RELIEF_R1_NOT_APPROVED',from_mix=False);key.relative_key=mesh.data.shape_keys.key_blocks[0]
  for i in B:key.data[int(i)].co=Vector(base[i]+plan['corrective_delta'][i])
  key.value=1.0
 mesh.data.update();bpy.context.view_layer.update();after=signature(mesh,rig,left);assert before==after,'UNAUTHORIZED_ATTRIBUTE_MUTATION'
 names,w1=weights(mesh);b1=np.array([list(v.co) for v in mesh.data.shape_keys.key_blocks[0].data]);changed_basis=np.flatnonzero(np.linalg.norm(b1-base,axis=1)>1e-10);changed_weights=np.flatnonzero(np.max(abs(w1-w0),axis=1)>1e-9)
 assert set(changed_basis)<=set(A) if kind.startswith('A') else len(changed_basis)==0
 assert set(changed_weights)<=set(B) if kind=='B1' else len(changed_weights)==0
 assert np.max(abs(w1.sum(1)-w0.sum(1)))<2e-7
 assert np.array_equal(b1[S],base[S]) and np.array_equal(w1[S],w0[S])
 for name,co in shapes0.items():
  if name!='Basis':assert np.array_equal(co,np.array([list(v.co) for v in mesh.data.shape_keys.key_blocks[name].data])),'FROZEN_CORRECTIVE_COORDINATES_CHANGED'
 V1,tt,ff=coords(mesh);allowed=A if kind.startswith('A') else B;outside=np.setdiff1d(np.arange(3300),allowed);assert np.max(abs(V1[outside]-V[outside]))==0
 shape_report={}
 for name,co in shapes0.items():
  if name=='Basis':continue
  now=np.array([list(v.co) for v in mesh.data.shape_keys.key_blocks[name].data]);shape_report[name]={'absolute_coordinates_unchanged':np.array_equal(co,now),'relative_difference_change_max_mm':float(np.linalg.norm((now-b1)-(co-base),axis=1).max()*1000),'relative_difference_changed_vertex_ids':np.flatnonzero(np.linalg.norm((now-b1)-(co-base),axis=1)>1e-10),'value_at_2_6':mesh.data.shape_keys.key_blocks[name].value,'driver_unchanged':True}
 changes={'candidate':kind,'rationale':plan['description'],'actual_basis_vertex_ids':changed_basis,'actual_weights_vertex_ids':changed_weights,'basis_changes':[dict(vertex=int(i),before=base[i],after=b1[i],delta_mm=(b1[i]-base[i])*1000) for i in changed_basis],'weight_changes':[dict(vertex=int(i),before={n:float(w0[i,j]) for j,n in enumerate(names) if w0[i,j] or w1[i,j]},after={n:float(w1[i,j]) for j,n in enumerate(names) if w0[i,j] or w1[i,j]}) for i in changed_weights],'frozen_shape_key_relative_effect':shape_report,'max_evaluated_shift_2_6_mm':float(np.linalg.norm(V1-V,axis=1).max()*1000),'S_max_evaluated_shift_mm':float(np.linalg.norm(V1[S]-V[S],axis=1).max()*1000),'outside_allowed_max_error_mm':0.,'protected_attribute_signature':after,'new_corrective':dict(name=key.name,value=1.,activation='MANUAL_CONSTANT_1_ALL_TEST_POSES_NO_DRIVER') if kind=='B2' else None}
 if kind=='B2':changes['corrective_changes']=[dict(vertex=int(i),delta_local_mm=plan['corrective_delta'][i]*1000) for i in np.flatnonzero(np.linalg.norm(plan['corrective_delta'],axis=1)>0)]
 sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];dest=OUT/FILES[kind];assert not dest.exists();bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 np.savez_compressed(OUT/(kind+'_EDIT.npz'),basis_delta=b1-base,weights_before=w0,weights_after=w1,V=V1,baseline_V=V,corrective_delta=plan.get('corrective_delta',np.zeros_like(base)))
 save(kind+'_EDIT_RECEIPT.json',changes);all_edits[kind]={k:changes[k] for k in ['actual_basis_vertex_ids','actual_weights_vertex_ids','max_evaluated_shift_2_6_mm','S_max_evaluated_shift_mm','frozen_shape_key_relative_effect']}
 print('BUILT',kind,json.dumps(all_edits[kind],default=encode),flush=True)
save('BUILD_SUMMARY.json',all_edits);protection('BUILD_INPUT_RECEIPT.json')
