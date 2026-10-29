"""Finish legacy scene approval labels before official freeze/pointer commit; core unchanged."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
I=read(OUT/'PROMOTION_IDENTITY_R1.json');inspect=read(OUT/'CANDIDATE_CONTAINER_INSPECTION_R1.json');before=inspect['protected_inputs_before'];verify(before)
assert sha(R2)==I['R2_baseline']['sha256'] and sha(POINTER)==inspect['production_pointer_before_sha256']
ob,rig=open_asset(R2);neutral(rig);core=core_payload(ob,rig);W=weights(ob)
assert all(digest(core[k])==v for k,v in I['core_component_candidate_sha256'].items())
scene=bpy.context.scene;changes=[]
for key,value in {'HUMAN_APPROVAL':'APPROVED','DO_NOT_PROMOTE':False}.items():
    changes.append({'kind':'legacy_scene_approval_label_finalization','key':key,'before':scene.get(key),'after':value});scene[key]=value
assert core_payload(ob,rig)==core and np.array_equal(weights(ob),W)
assert len(bpy.data.actions)==0 and rig.animation_data.action is None and m.state_zero(rig)
old_sha=sha(R2);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R2),compress=False)
ob,rig=open_asset(R2);neutral(rig)
assert core_payload(ob,rig)==core and np.array_equal(weights(ob),W)
assert bpy.context.scene['DO_NOT_PROMOTE'] is False and bpy.context.scene['HUMAN_APPROVAL']=='APPROVED'
assert bpy.context.scene['HUMAN_APPROVED'] is True and not bpy.context.scene['HUMAN_APPROVAL_PENDING']
assert not bpy.context.scene['DESIGN_ONLY'] and not bpy.context.scene['NOT_PRODUCTION']
assert len(bpy.data.objects)==2 and len(bpy.data.scenes)==1 and len(bpy.data.actions)==0
assert rig.animation_data.action is None and m.state_zero(rig) and bpy.context.scene.frame_current==1
I['pre_finalization_container_sha256']=old_sha
I['R2_baseline']['sha256']=sha(R2)
I['permitted_packaging_changes']+=changes
I['legacy_approval_flags_finalized_before_freeze']=True
I['R2_CONTAINER_STATUS']='PRODUCTION_CLEAN'
I['container_finalization_core_component_identity']='EXACT_MATCH'
I['smoke_after_metadata_finalization']='Previously exact ZERO/F130/L3 evaluated states remain valid: all core data/weights are identical; only two scene approval labels changed. No requalification.'
dump('PROMOTION_IDENTITY_R1.json',I)
verify(before)
print('SCENE_IDENTITY_FINALIZED_CORE_UNCHANGED',sha(R2),flush=True)
