import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
assert sha(CAND)==EXPECTED_CAND,'APPROVED_CANDIDATE_SHA_MISMATCH'
assert all(sha(p)==s for p,s in RIGHTS.items()),'RIGHT_ASSET_SHA_MISMATCH'
assert not DEST.exists() and not POINTER.exists(),'Refuse an existing baseline/pointer'
before=protected();dump('PROTECTED_INPUTS_BEFORE_R1.json',before)
ob,rig=open_asset(CAND)
assert is_zero(rig) and bpy.context.scene.frame_current==1
payload=core(ob,rig)
inventory={'objects':[{'name':o.name,'type':o.type,'props':props(o),'scale':list(o.scale),'determinant':o.matrix_world.to_3x3().determinant(),'constraints':[c.type for c in o.constraints]} for o in bpy.data.objects],'scenes':[{'name':s.name,'props':props(s),'camera':plain(s.camera)} for s in bpy.data.scenes],'collections':[{'name':c.name,'props':props(c),'objects':[o.name for o in c.objects]} for c in bpy.data.collections],'actions':[a.name for a in bpy.data.actions],'camera_datablocks':[c.name for c in bpy.data.cameras],'texts':[t.name for t in bpy.data.texts]}
assert len(bpy.data.objects)==2 and len(bpy.data.scenes)==1
assert len(bpy.data.actions)==0 and len(bpy.data.cameras)==0 and not len(bpy.data.texts)
assert ob.parent==rig and len(ob.modifiers)==1 and ob.modifiers[0].type=='ARMATURE'
assert not len(ob.constraints) and not len(rig.constraints) and all(not len(p.constraints) for p in rig.pose.bones)
pending={o.name:{k:v for k,v in props(o).items() if k in AUDIT_KEYS} for o in [ob,bpy.context.scene]}
assert ob.get('DESIGN_ONLY') and ob.get('HUMAN_APPROVAL_PENDING')
dump('CANDIDATE_CONTAINER_INSPECTION_R1.json',{'PHASE':PHASE,'CANDIDATE_CONTAINER_STATUS':'AUDIT_SCAFFOLDING_PRESENT','reason':'Only scene/mesh-object pending identity labels and candidate scene name. No camera, debug object, comparison object, Action, or runtime audit helper.','inventory':inventory,'permitted_metadata_keys':sorted(AUDIT_KEYS),'pending_metadata':pending,'core_component_sha256':{k:digest(v) for k,v in payload.items()},'saved_ZERO_RSSF':True,'source_candidate_sha256':sha(CAND),'review_or_debug_geometry_to_remove':False})
approval_source=Path('<USER_HOME>/.codex/attachments/6029b3dd-8d8f-4248-84dc-61785a86016a/已粘贴的文本.txt')
dump('HUMAN_APPROVAL_BIND_R1.json',{'authority':'Direct user instruction in this chat, 2026-10-07 Asia/Shanghai','source_request_path':str(approval_source),'source_request_sha256':sha(approval_source),'approved_candidate':{'path':CAND.relative_to(ROOT).as_posix(),'sha256':EXPECTED_CAND},'LEFT_HAND_CANONICAL_MIRROR_BASELINE_R1':'HUMAN_APPROVED','LEFT_HAND_HUMAN_VISIBLE_RESULT':'PASS','WEIGHT_FIELD_MIRROR_PARITY':'EXACT_SEMANTIC_MIRROR_MATCH','CORRECTIVE_MIRROR_PARITY':'PASS','LEFT_HAND_PROMOTION':'AUTHORIZED','reviewed':['ZERO / RSSF','six approved first-web cases','six PALMAR + DORSAL cases'],'scope':'Promote exact approved product payload; clean audit/pending packaging only. Freeze R1 and create left production pointer after identity and minimal smoke PASS. No real motion or Web stage.','historical_reports_rewritten':False})
validate_protected(before)
print('READ_ONLY_INSPECTION_PASS / AUDIT_SCAFFOLDING_PRESENT / pending labels only',flush=True)
