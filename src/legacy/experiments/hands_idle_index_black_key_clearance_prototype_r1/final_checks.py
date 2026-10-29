import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import *
sc,rig,mesh,left,lrig=s.open_scene(OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend');g.init()
data=np.load(OUT/'CANDIDATE_LOCAL_SAMPLES.npz');base=np.load(OUT/'BASELINE_LOCAL_SAMPLES.npz');rows=[]
for t,V,B in zip(data['times'],data['vertices'],base['vertices']):
 c.settime(sc,float(t));L,T,F=s.coords_tri(left)
 changed=np.flatnonzero(np.linalg.norm(V-B,axis=1)>1e-10);CT=g.ALLT[np.any(np.isin(g.ALLT,changed),axis=1)]
 if len(CT):
  P=V[np.unique(CT)];gap=np.maximum(0,np.maximum(P.min(0)-L.max(0),L.min(0)-P.max(0)));distance=float(np.linalg.norm(gap)*1000)
  if distance==0:
   lt=g.tree(L,T);bp=set(g.tree(B,CT).overlap(lt));cp=set(g.tree(V,CT).overlap(lt));new=len(cp-bp)
  else:bp=cp=set();new=0
 else:distance=None;bp=cp=set();new=0
 rows.append(dict(time=t,changed_skin_aabb_separation_mm=distance,baseline_pairs=len(bp),candidate_pairs=len(cp),new_pairs=new))
save('CROSS_HAND_AND_CAMERA_CHECK.json',dict(samples=len(rows),minimum_changed_skin_aabb_separation_mm=min(r['changed_skin_aabb_separation_mm'] for r in rows if r['changed_skin_aabb_separation_mm'] is not None),new_cross_hand_pair_samples=sum(r['new_pairs']>0 for r in rows),rows=rows,camera_exact=read(OUT/'RENDER_SEQUENCE.json')['camera']['matrix']==read(OUT/'MINIMAL_FACTS.json')['camera']['matrix'],piano_access=False))
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
folder=OUT/'tail_candidate_frames';folder.mkdir(exist_ok=False);frames=[]
for ix,frame in enumerate(range(203,218)):
 t=(frame-1)/60;c.settime(sc,t);dest=folder/f'{ix:04d}.png';sc.render.filepath=str(dest);bpy.ops.render.render(write_still=True);frames.append(dict(index=ix,time=t,source_frame=frame,path=str(dest)))
save('TAIL_RENDER_SEQUENCE.json',dict(frames=frames));protection('FINAL_SCENE_INPUT_RECEIPT.json');print('FINAL_SCENE_CHECKS_DONE',flush=True)
