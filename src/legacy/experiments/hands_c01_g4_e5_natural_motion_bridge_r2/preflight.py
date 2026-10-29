import sys,json,math,ast
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));sys.path.insert(0,str(O.parent/'hands_c01_whole_hand_motion_feasibility_r1'))
from geometry_detector import *
from triangle_distance import *
import blender_utils as u
P=json.loads((O/'POLICY_LOCK.json').read_text());M=P['source_action_scene'];PRE=O.parent/'hands_c01_anatomy_preparation_audit_r1';B=json.loads((PRE/'B_ACTUAL_2.json').read_text())
# Read unchanged B2, no optimization or state correction.
bpy.ops.wm.open_mainfile(filepath=str(PRE/'S1_ANATOMY_PREPARATION_DIAGNOSTIC_R1.blend'),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes[B['scene']]
rig=bpy.data.objects[B['rig']];mesh=bpy.data.objects[B['mesh']];V,F=u.coords(mesh);snap=np.load(PRE/'B_ACTUAL_SKIN_2.npz');assert np.max(abs(V-snap['vertices']))<1e-7;assert u.digest(u.native(mesh,rig))==u.pf['right_native_sha256']
bm=detect(V,snap['key_angles'],dict(midi=67,finger=1));assert bm['contact']['top_surface_crossing_triangles']>0 and bm['target_key_max_depth_mm']<=.25 and bm['wrong_key_or_nonpulp_max_depth_mm']==0 and bm['nonadjacent_self_triangle_pairs']==0
# Original full Action supplies all exact key states, including previous entrance context.
bpy.ops.wm.open_mainfile(filepath=M['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[M['scene']];bpy.context.window.scene=sc
old=json.loads((O.parent/'hands_c01_g4_e5_skin_safe_bridge_r1/ENTRY_CONTEXT_READONLY.json').read_text())['original_key_action_hashes']
hashes={str(i):u.digest(u.payload(bpy.data.objects[n].animation_data.action)) if bpy.data.objects[n].animation_data and bpy.data.objects[n].animation_data.action else None for i,n in u.man['key_pivots'].items()};assert old==hashes
start,exchange,full,end=2.527855,2.921426,2.956426,3.349997
regular=np.arange(start,end+1/120,1/120);regular=regular[regular<=end]
events=[2.492855,start,exchange,full,end]
near=[v+d for v in [exchange,full,end] for d in [-.008,-.004,-.001,-.0001,0,.0001,.001,.004,.008] if start<=v+d<=end]
context=[1.914284,2.064284,2.492855]+[2.492855+d for d in [-.045,-.02,-.001,0,.001,.02,.035]]
times=np.unique(np.r_[regular,events,near,context]);angles=[]
for t in times:
 u.settime(sc,float(t));angles.append(u.keyangles().copy())
angles=np.array(angles);np.savez_compressed(O/'ORIGINAL_KEY_ACTION_SAMPLES.npz',times=times,key_angles=angles)
u.settime(sc,start);diff=float(np.max(abs(u.keyangles()-snap['key_angles'])));assert diff<1e-6
eidx=int(np.argmin(abs(times-full)));eang=angles[eidx];np.savez_compressed(O/'ENDPOINT_KEY_ANGLES.npz',angles=eang)
# Existing S2 is geometrically qualified but its audited spread is outside the new reference family.
audit=json.loads((PRE/'ACTUAL_RIG_ANATOMY.json').read_text());s2=next(r for r in audit['rows'] if r['label']=='S2_STATIC_QUALIFIED');mid=next(d for d in s2['digits'] if d['digit']=='MIDDLE')
keyrows=[dict(display_time=float(t),music_time=float(t-.35),G4_angle_rad=float(a[46]),E5_angle_rad=float(a[55]),D5_angle_rad=float(a[53])) for t,a in zip(times,angles)]
out=dict(status='START_VERIFIED_END_REQUIRED',B2_actual_geometry=bm,B2_vertex_error_mm=float(np.linalg.norm(V-snap['vertices'],axis=1).max()*1000),B2_key_angle_error_rad=diff,B2_human_preliminary='Accepted for isolated research only',old_S2=dict(state=s2['source_state'],actual_anatomy=s2,middle_spread_deg=mid['controls_recovered_deg'][3],middle_heading_deg=mid['joints'][0]['palm_heading_deg'],middle_ring_previous_exact_mm=.11774766739016501,new_reference_family_gate=False,reason='Middle MCP spread ~-25deg vs approved R1/R2 ~-6.73..-7.20; geometrical qualification does not supply natural dynamic endpoint'),original_action_payloads=hashes,key_action_rows=keyrows,entry_context='Read-only original key Action inspection; R05/R06/R07 hand entry trajectory not newly produced or validated',endpoints_time=full,exchange_exact_key_angles=dict(G4=float(angles[np.argmin(abs(times-exchange)),46]),E5=float(angles[np.argmin(abs(times-exchange)),55])),end_press_key_angles=dict(G4=float(eang[46]),E5=float(eang[55])),new_optimization_runs=0,sources_saved=False)
(O/'PREFLIGHT_AND_ENDPOINT_DIAGNOSIS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print('B2_READBACK_PASS',diff,'OLD_S2_NATURAL_REJECT',mid['controls_recovered_deg'][3],'EXCHANGE',out['exchange_exact_key_angles'],'FULL',out['end_press_key_angles'],flush=True)
