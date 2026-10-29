import sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];R3=ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance'
exec(compile((R3/'diagnose.py').read_text(encoding='utf8').split('results={};witnesses={}')[0],str(R3/'diagnose.py'),'exec'))
sys.path.insert(0,str(OUT))
from local_spatial_constraints import boundary_key_constraint
policy=read(OUT/'PRECHECK_POLICY.json');man,sc,rig,mesh=open_stage(C1);assert man['sha256']==policy['source_sha256'];rois=read(R3/'LOCAL_SKIN_ROI.json')
rows=[]
for wi,window in enumerate(policy['windows_video_sec']):
 for edge,t in zip(['start','end'],window):
  settime(sc,t);V,F=mesh_pose(mesh);keys=key_geometry(sc);hits=[];contacts=[]
  active={n['finger']:n for n in tl['notes'] if n['hand']=='R' and n['note_on']<=t<n['note_off']}
  for digit,roi in rois.items():
   finger=c.DIGITS.index(digit)+1
   for midi,key in keys.items():
    # No active black note at these boundaries; do not implement broad exemptions.
    assert not (finger in active and active[finger]['midi_note']==midi)
    metric=boundary_key_constraint(V,roi,key['V'],key['F'],policy['non_target_internal_depth_limit_mm'])
    if metric['inside_vertices'] or metric['intersecting_face_pairs']:hits.append(dict(digit=digit,midi=midi,note=key['name'],**metric))
  for finger,n in active.items():
   k=c.KEYS[n['key_index']];angle=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x
   contacts.append(dict(note=n['note_name'],finger=finger,**contact(V[c.MARKERS['R'][finger-1]['mesh_vertex']],k,angle)))
  rows.append(dict(window=wi,edge=edge,video_sec=t,music_sec=t-.35,hits=hits,contacts=contacts,violation=any(h['hard_violation'] for h in hits)))
  print('EXACT_BOUNDARY',wi,edge,t,[(h['digit'],h['note'],round(h['max_internal_depth_mm'],5)) for h in hits],flush=True)
save('EXACT_BOUNDARY_GEOMETRY.json',dict(samples=rows,source_unchanged=True,pose_edits=0,new_actions=0,new_blends=0,new_static_solves=0,new_dynamic_solves=0,scope='4 exact immutable boundary poses, 4 saved distal skin patches, 7 known local black keys; source scene read only',gate='FAIL' if any(r['violation'] for r in rows) else 'CONTINUE_PRECHECK'))
