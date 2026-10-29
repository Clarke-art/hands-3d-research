import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'));import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc
T=json.loads(Path(P['source_input']['timeline']).read_text(encoding='utf-8-sig'));notes=[n for n in T['notes'] if n['note_id'] in ['R05','R06','R07','R08']]
boundary=2.492855;times=sorted(set([1.914284,2.064284,2.492855,2.921426,3.349997]+np.round(np.arange(boundary-.045,boundary+.0451,.001),9).tolist()));rows=[]
for t in times:
 u.settime(sc,t);a=u.keyangles();rows.append(dict(display_time_sec=t,source_time_sec=t-.35,G4_angle_rad=float(a[46]),G4_press_fraction=float(a[46]/u.c.KEYS[46]['press_angle_rad']),D5_press_fraction=float(a[53]/u.c.KEYS[53]['press_angle_rad']),E5_press_fraction=float(a[55]/u.c.KEYS[55]['press_angle_rad'])))
window=[r for r in rows if boundary-.045<=r['display_time_sec']<=boundary+.045];minimum=min(window,key=lambda r:r['G4_press_fraction']);payload={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()}
result=dict(status='ENTRY_BOUNDARY_UNVERIFIED',reason='Static gate failed; actual key Action inspected but no new thumb release/re-contact trajectory or R05-R06 hand entry generated',notes=notes,presentation_lead_sec=.35,original_key_action_hashes=payload,current_action_samples=rows,G4_minimum_press_fraction_near_repeat=minimum,R05_still_held_at_old_initial_time=next(r for r in rows if r['display_time_sec']==1.914284)['D5_press_fraction']>.99,source_scene_read_only=True)
(O/'ENTRY_CONTEXT_READONLY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print('ENTRY_CONTEXT_READ_ONLY',minimum,'R05_HELD',result['R05_still_held_at_old_initial_time'],flush=True)
