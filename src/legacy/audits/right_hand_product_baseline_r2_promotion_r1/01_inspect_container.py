"""First action on candidate is read-only container inspection. No product mutation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
before=protected();verify(before)
assert sha(CANDIDATE)==APPROVED_SHA and sha(BASE)==FROZEN_SHA
ob,rig=open_asset(CANDIDATE)
inventory={
 'objects':[{'name':o.name,'type':o.type,'linked_library':o.library.filepath if o.library else None,'collections':[c.name for c in o.users_collection]} for o in bpy.data.objects],
 'collections':[{'name':c.name,'objects':[o.name for o in c.objects],'children':[v.name for v in c.children]} for c in bpy.data.collections],
 'scenes':[{'name':s.name,'frame':s.frame_current,'camera':s.camera.name if s.camera else None,'objects':[o.name for o in s.objects],'metadata':dict(s.items())} for s in bpy.data.scenes],
 'actions':[{'name':a.name,'users':a.users,'fake_user':a.use_fake_user,'linked_library':a.library.filepath if a.library else None} for a in bpy.data.actions],
 'rig_active_action':rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
 'rig_nla_tracks':[{'name':t.name,'mute':t.mute,'strips':[{'name':s.name,'action':s.action.name if s.action else None} for s in t.strips]} for t in rig.animation_data.nla_tracks] if rig.animation_data else [],
 'mesh_metadata':dict(ob.items()),'rig_metadata':dict(rig.items()),
 'geometry_identity':{'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'bones':len(rig.data.bones),'bone_names':[b.name for b in rig.data.bones],'non_deform_TIP':[b.name for b in rig.data.bones if not b.use_deform]},
 'file_sha256':sha(CANDIDATE),'Action_payload_sha256':digest(action_payload(bpy.data.actions[ACTION]))}
assert inventory['Action_payload_sha256']==APPROVED_ACTION_SHA
assert inventory['geometry_identity']['vertices']==3300 and inventory['geometry_identity']['bones']==21
extras=[o.name for o in bpy.data.objects if o not in [ob,rig]]
reasons=[]
if extras:reasons.append({'type':'non_product_objects','names':extras})
if inventory['rig_active_action']==ACTION:reasons.append({'type':'qualification_motion_playback_wrapper','action':ACTION,'saved_frame':bpy.context.scene.frame_current,'reason':'PianoVAM is qualification evidence, not a runtime dependency. Production saves ZERO with no active source motion.'})
if ob.get('DESIGN_ONLY') or any(s.get('DESIGN_ONLY') for s in bpy.data.scenes):reasons.append({'type':'audit_identity_metadata','reason':'DESIGN_ONLY / NOT_PRODUCTION / pending approval metadata are audit container identity, not approved deformation data.'})
status='AUDIT_SCAFFOLDING_PRESENT' if reasons else 'PRODUCTION_CLEAN'
dump('CANDIDATE_CONTAINER_INSPECTION_R1.json',{'PHASE':PHASE,'CANDIDATE_CONTAINER_STATUS':status,'inventory':inventory,'audit_packaging_reasons':reasons,'protected_inputs_before':before,'production_pointer_before':read(POINTER),'production_pointer_before_sha256':sha(POINTER),'read_only':True,'blend_files_written':0,'packaging_decision':'Use clean R2 container only if non-product wrapping is present. Never rebuild weights or core data.'})
verify(before)
print('CANDIDATE_CONTAINER_STATUS',status,'OBJECTS',inventory['objects'],'ACTIONS',inventory['actions'],flush=True)
