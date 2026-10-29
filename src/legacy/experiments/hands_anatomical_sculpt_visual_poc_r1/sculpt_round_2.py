import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpt_common import *
sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);v,t0,f0=coords(mesh);z=np.load(PREV/'ORIGINAL_SNAPSHOT.npz');J=jacobians(mesh,rig);n=normals(v)
first=read(OUT/'ROUND_1_SCULPT_INTENT_AND_STROKES.json')
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
plans={}
for kind,ids in [('A',A),('B',B)]:
 world=np.array(first[kind]['world_target_displacements_m'])
 if kind=='A':
  # Last sculpt revision: soften the upper/lower termination, not a stronger drag.
  for i in ids:
   along=float(z['ALONG'][i]);feather=float(smooth((along+.003)/.010)*smooth((.022-along)/.011))
   world[i,0]*=.82*feather;world[i,2]*=feather
  reason='Round1 introduced an upper termination kink. Reduce lateral strength and use a long proximal/distal feather within the same fixed boundary. No additional region or increased displacement.'
 else:
  # Last sculpt revision: retain stroke footprint but redirect its depth, avoiding side inflation.
  for i in ids:
   x,z0=world[i,0],world[i,2];world[i,0]=x*.42;world[i,2]=z0*1.40
   length=np.linalg.norm(world[i])
   if length>.00150:world[i]*=.00150/length
  reason='Round1 overemphasized lateral push. Redirect existing local fan displacement toward surface depth with smaller lateral movement; same points, peak bounded below round1.'
 delta=np.zeros_like(world)
 for i in ids:delta[i]=np.linalg.solve(J[i],world[i])
 plans[kind]={'reason':reason,'world_target_displacements_m':world,'shape_key_displacements_local_m':delta}
save('ROUND_2_SCULPT_INTENT_AND_STROKES.json',plans)
for kind,ids in [('A',A),('B',B)]:
 sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,2.6);sig=signature(mesh,rig,left);w=weights(mesh)[1];frozen={k.name:np.array([list(p.co) for p in k.data]) for k in mesh.data.shape_keys.key_blocks};base=frozen['Basis'];mesh.data=mesh.data.copy();key=mesh.shape_key_add(name=kind+'_ANATOMICAL_SCULPT_VISUAL_R1_EXPERIMENT',from_mix=False);key.relative_key=mesh.data.shape_keys.key_blocks['Basis']
 for i in ids:key.data[int(i)].co=Vector(base[i]+plans[kind]['shape_key_displacements_local_m'][i])
 key.value=1.;mesh.data.update();bpy.context.view_layer.update();assert signature(mesh,rig,left)==sig and np.array_equal(weights(mesh)[1],w)
 for name,co in frozen.items():assert np.array_equal(co,np.array([list(p.co) for p in mesh.data.shape_keys.key_blocks[name].data]))
 delta=np.array([list(p.co) for p in key.data])-base;changed=np.flatnonzero(np.linalg.norm(delta,axis=1)>1e-10);assert set(changed)<=set(ids)
 vv,tt,ff=coords(mesh);outside=np.setdiff1d(np.arange(3300),ids);assert np.max(abs(vv[outside]-v[outside]))==0
 report={'region':kind,'round':2,'substantive_sculpt_rounds_total':2,'round1_visual_observation_and_revision':plans[kind]['reason'],'actual_changed_vertices':changed,'actual_changed_count':len(changed),'max_local_shape_delta_mm':float(np.linalg.norm(delta,axis=1).max()*1000),'max_evaluated_shift_2_6_mm':float(np.linalg.norm(vv-v,axis=1).max()*1000),'outside_allowed_shift_mm':0.,'S_and_collar_shift_mm':float(np.linalg.norm(vv[np.array(SCOPE['S_protected_collar_vertex_ids'])]-v[np.array(SCOPE['S_protected_collar_vertex_ids'])],axis=1).max()*1000),'frozen_basis_weights_corrective_driver_unchanged':True,'manual_shape_value':1.,'automatic_trigger':False,'vertices':[dict(vertex=int(i),basis_local_m=base[i],sculpt_delta_local_mm=delta[i]*1000,evaluated_delta_world_mm=(vv[i]-v[i])*1000) for i in changed]}
 dest=OUT/(kind+'_SCULPT_ROUND_2_NOT_APPROVED.blend');assert not dest.exists();sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];bpy.ops.wm.save_as_mainfile(filepath=str(dest),check_existing=True)
 save(kind+'_ROUND_2_EDIT_RECEIPT.json',report);np.savez_compressed(OUT/(kind+'_ROUND_2_SCULPT.npz'),delta=delta,V=vv,T=tt,baseline_V=v)
 print('SCULPTED',kind,'round2','points',len(changed),'maxshift',report['max_evaluated_shift_2_6_mm'],flush=True)
protection('SCULPT_ROUND_2_INPUT_RECEIPT.json')

