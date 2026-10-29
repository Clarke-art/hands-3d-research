import bpy,json,hashlib
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent;dest=P/'PIANO_KEYBOARD_SPATIAL_ANCHOR_VALIDATION_CANDIDATE_R1.blend';A=np.load(P/'spatial_evaluations.npz')
bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False)
cam=bpy.data.objects['CONTACT_CLOSE'];V=np.concatenate([A[s+'_verts'].reshape(-1,3) for s in ['R','L']]);axes=np.array(cam.matrix_world.to_3x3());pr=(V-np.array(cam.location))@axes
scale=max(np.ptp(pr[:,0]),np.ptp(pr[:,1])*1200/660)*1.12;old=cam.data.ortho_scale;cam.data.ortho_scale=float(scale)
# Translate screen center only; keep the fixed near-view angle.
shift=np.array([.5*(pr[:,0].min()+pr[:,0].max()),.5*(pr[:,1].min()+pr[:,1].max()),0]);cam.location=np.array(cam.location)+axes@shift
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest))
p=P/'ACTION_IDENTITY_R1.json';i=json.loads(p.read_text());i['candidate_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();i['post_verification_change']='CONTACT_CLOSE camera framing only; no object, key, root or Action mutations';p.write_text(json.dumps(i,indent=2))
(P/'CAMERA_FRAMING_REPAIR_R1.json').write_text(json.dumps({'camera':'CONTACT_CLOSE','old_scale':old,'new_scale':scale,'method':'full421-observation both-hand projected union +12% margin; fixed angle; no per-frame camera motion','camera_only':True},indent=2))
print('CAMERA_ONLY_FRAMING',old,scale)
