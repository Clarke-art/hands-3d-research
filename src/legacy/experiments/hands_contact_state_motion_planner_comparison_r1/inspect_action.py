import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;PRE=O.parent/'hands_c01_g4_e5_natural_motion_bridge_r2';sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));import blender_utils as u
P=json.loads((PRE/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc
expected=json.loads((PRE/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').read_text())['original_action_payloads'];cur={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()};assert cur==expected
N=json.loads((O/'SOURCE_MIDI_REVALIDATION.json').read_text())['notes'];times=set([2.527855,2.72,2.921426,2.956426,3.349997])
for n in N:
 for base in [n['display_on'],n['display_off']]:times.update(base+d for d in [-.0001,0,.0001,.0175,.035,.07,.1])
rows=[]
for t in sorted(times):
 u.settime(sc,t);rows.append(dict(display_time=t,angles=u.keyangles().tolist()))
fc={}
for i,n in u.man['key_pivots'].items():
 ob=bpy.data.objects[n];fc[str(i)]=[dict(path=f.data_path,index=f.array_index,points=[dict(display_time=(float(k.co.x)-1)/60,angle=float(k.co.y),interpolation=k.interpolation) for k in f.keyframe_points]) for f in u.curves(ob.animation_data.action)] if ob.animation_data and ob.animation_data.action else []
# exact finite test states, not curve generation
T=[2.527855,2.72,2.921426,2.956426];KA=[]
for t in T:u.settime(sc,t);KA.append(u.keyangles())
np.savez_compressed(O/'DISCRETE_KEY_STATES.npz',times=T,angles=KA)
rig=bpy.data.objects[M['mapping']['R']['rig']];mesh=bpy.data.objects[M['mapping']['R']['mesh']];assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
(O/'ORIGINAL_ACTION_INSPECTION.json').write_text(json.dumps(dict(source=M,action_payloads=cur,all_original_action_payloads_match=True,native_frozen_identity=True,rows=rows,fcurves=fc,source_saved=False),indent=2));print('ORIGINAL_ACTION_REEVALUATED',len(rows),'times')
