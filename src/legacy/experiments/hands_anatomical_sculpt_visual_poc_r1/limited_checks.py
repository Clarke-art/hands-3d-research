import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from sculpt_geometry import *
def install(mesh,kind):
 mesh.data=mesh.data.copy();k=mesh.shape_key_add(name=kind+'_ANATOMICAL_SCULPT_VISUAL_R1_EXPERIMENT',from_mix=False);base=mesh.data.shape_keys.key_blocks['Basis'];delta=np.load(OUT/(kind+'_ROUND_2_SCULPT.npz'))['delta']
 for i in np.flatnonzero(np.linalg.norm(delta,axis=1)>0):k.data[int(i)].co=base.data[int(i)].co+Vector(delta[i])
 k.value=1.;mesh.data.update();bpy.context.view_layer.update()
def pad_region():
 pts=set(m['mesh_vertex'] for m in c.MARKERS['R'])
 for _ in range(2):pts|={int(b) if a in pts else int(a) for a,b in E if a in pts or b in pts}
 return sorted(pts)
padids=pad_region();summary={}
for label,path in [('C1_2_600000',SOURCE),('FIXED_GEOMETRY_PASS',FIXED)]:
 baseline=None
 for kind in ['BASE','A','B']:
  sc,mesh,rig,left=open_scene(path);c.settime(sc,2.6);before=signature(mesh,rig,left);basis=np.array([list(p.co) for p in mesh.data.shape_keys.key_blocks['Basis'].data]);w=weights(mesh)[1]
  if kind!='BASE':install(mesh,kind);assert signature(mesh,rig,left)==before and np.array_equal(basis,np.array([list(p.co) for p in mesh.data.shape_keys.key_blocks['Basis'].data])) and np.array_equal(w,weights(mesh)[1])
  v,tt,ff=coords(mesh);l,lt,_=coords(left);cp=components(sc);keys=keyrows(v,tt,cp,{'A#4','A4','C#5'});selfs=collisions(v,tt);cross=set(map(tuple,tree(v,tt).overlap(tree(l,lt))));contacts=active_contacts(v,l,2.6)
  r={'candidate':kind,'pose':label,'keys':keys,'self_pairs':sorted(selfs),'cross_hand_pairs':sorted(cross),'active_contacts':contacts}
  if kind=='BASE':baseline=dict(v=v,t=tt,l=l,keys={(x['key_index'],x['component']):x for x in keys},selfs=selfs,cross=cross)
  else:
   allowed=A if kind=='A' else B;outside=np.setdiff1d(np.arange(3300),allowed)
   changed=np.linalg.norm(v-baseline['v'],axis=1)*1000;reg=[]
   for key in keys:
    b=baseline['keys'][(key['key_index'],key['component'])]
    if key['depth_mm']>b['depth_mm']+1e-5 or key['bvh_pairs']>b['bvh_pairs']:reg.append(dict(key=key['key'],baseline_depth_mm=b['depth_mm'],new_depth_mm=key['depth_mm'],baseline_pairs=b['bvh_pairs'],new_pairs=key['bvh_pairs']))
   geom=deform_metrics(v,baseline['v'],allowed,tt,baseline['t'])
   r.update(actual_changed_vertices=np.flatnonzero(changed>1e-7),max_skin_shift_mm=float(changed.max()),outside_allowed_shift_mm=float(changed[outside].max()),S_core_shift_mm=float(changed[S].max()),S_collar_shift_mm=float(changed[np.array(SCOPE['S_protected_collar_vertex_ids'])].max()),pad_marker_shift_mm={str(m['mesh_vertex']):float(changed[m['mesh_vertex']]) for m in c.MARKERS['R']},pad_two_edge_ring_shift_mm=float(changed[padids].max()),left_skin_shift_mm=float(np.linalg.norm(l-baseline['l'],axis=1).max()*1000),new_self_pairs=sorted(selfs-baseline['selfs']),new_cross_hand_pairs=sorted(cross-baseline['cross']),new_key_regressions=reg,local_geometry=geom)
   assert r['outside_allowed_shift_mm']==0 and r['S_collar_shift_mm']==0
   r['serious_geometry_regression']=bool(r['new_self_pairs'] or r['new_cross_hand_pairs'] or reg or len(geom['flipped_face_ids']) or r['pad_two_edge_ring_shift_mm']>1e-7)
  save(kind+'__'+label+'__LIMITED_CHECK.json',r);summary[kind+'__'+label]={k:r[k] for k in r if k not in ['keys','self_pairs','cross_hand_pairs']}
  print('CHECK',kind,label,r.get('serious_geometry_regression'),flush=True)
save('LIMITED_GEOMETRY_SUMMARY.json',summary)
compat=[]
for kind in ['A','B']:
 for mode in ['NORMAL_ACTIVE','FORCED_OFF_IN_MEMORY_ONLY']:
  sc,mesh,rig,left=open_scene(SOURCE);c.settime(sc,.88571375)
  old=mesh.data.shape_keys.key_blocks['FIRST_WEB_OPPOSITION_CREASE_R1'];value=old.value
  if mode.startswith('FORCED'):
   # Only this unsaved test instance; frozen file and delivered driver never edited.
   for driver in mesh.data.shape_keys.animation_data.drivers:driver.mute=True
   old.value=0.;bpy.context.view_layer.update()
  original_value=old.value;before,tt,_=coords(mesh);install(mesh,kind);after,_,_=coords(mesh);shift=np.linalg.norm(after-before,axis=1)*1000
  compat.append({'region':kind,'test_time_sec':.88571375,'old_corrective_mode':mode,'normal_driver_value':value,'actual_old_key_value':original_value,'new_key_value':1.,'max_actual_sculpt_shift_mm':float(shift.max()),'sculpt_effect_world_m':(after-before).tolist(),'test_copy_saved':False})
 for a,b in [(compat[-2],compat[-1])]:a['effect_difference_from_old_off_mm']=float(np.linalg.norm(np.array(a['sculpt_effect_world_m'])-np.array(b['sculpt_effect_world_m']),axis=1).max()*1000)
save('OLD_CORRECTIVE_OFF_NORMAL_COMPATIBILITY.json',compat)
save('CHECK_SCOPE.json',{'executed':['C1 2.600s evaluated full-right-hand skin/key check','historical fixed geometry PASS evaluated skin/key check','self intersections, cross-hand, local flips/edge-area deformation','all skin pad marker vertices and two native edge rings','old corrective normal active versus off at original C1 0.88571375s'],'not_run':['complete six-state regression','right16 active48 contact resampling','full-music high-frequency geometry verification','animation rendering','automatic new shape-key activation mechanism'],'new_shape_key_use':'Manual1 in each static test, no automatic trigger','S_edited':False})
protection('LIMITED_CHECK_INPUT_RECEIPT.json')

