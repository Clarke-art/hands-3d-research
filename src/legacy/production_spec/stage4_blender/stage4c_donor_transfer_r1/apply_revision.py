import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
import numpy as np
# Position-excluding snapshot helper only. No historical modeling code executes.
exec(compile((DESIGN/'payload.py').read_text(encoding='utf-8-sig'),str(DESIGN/'payload.py'),'exec'),globals())
assert read(OUT/'APPLICATION_PREREQUISITE_GATE_R1.json')['status']=='PASS'
C=read(DESIGN/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');receipt=OUT/'HUMAN_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPROVAL_R1.json'
assert not ASSET.exists(),'FAIL_CLOSED: independently named revision asset already exists; do not overwrite'
assert sha(SOURCE)==EXPECTED_SOURCE and sha(CANDIDATE)==EXPECTED_CANDIDATE
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
assert sha(SOURCE)==EXPECTED_SOURCE
ob=bpy.data.objects['Hand  - Realistic'];me=ob.data;source_payload=protected(ob);source_props={k:plain(ob[k]) for k in ob.keys()};local0=[list(v.co) for v in me.vertices];world0=[list(<REDACTED_EMAIL>) for v in me.vertices]
assert [len(me.vertices),len(me.edges),len(me.polygons)]==[3416,6828,3414]
assert local0==C['source_local_m'] and [list(f.vertices) for f in me.polygons]==C['faces'] and [list(e.vertices) for e in me.edges]==C['edges']
assert len(ob.vertex_groups)==0 and not source_payload['armatures'] and all(not v.groups for v in me.vertices)
topology_signature=digest({k:source_payload[k] for k in ['edges','faces','loops','face_loop_ranges','vertex_count','edge_count','face_count']})
for i in IDS:me.vertices[i].co=C['candidate_local_m'][i]
me.update()
local1=[list(v.co) for v in me.vertices];world1=[list(<REDACTED_EMAIL>) for v in me.vertices]
assert local1==C['candidate_local_m'] and protected(ob)==source_payload
changed=[i for i in range(len(local1)) if local0[i]!=local1[i]];assert changed==IDS
metadata={'PHASE':PHASE,'GEOMETRY_HUMAN_APPROVED':True,'SOURCE_STAGE4C_SHA256':EXPECTED_SOURCE,'APPROVED_FORMAL_CANDIDATE_SHA256':EXPECTED_CANDIDATE,'HUMAN_APPROVAL_RECEIPT_SHA256':sha(receipt),'DONOR_SOURCE_SHA256':EXPECTED_DONOR,'APPROVED_WRITE_SET_FILE_SHA256':sha(DESIGN/'FORMAL_DONOR_TRANSFER_WRITE_SET_R1.json'),'APPROVED_TARGET_COORDINATE_FILE_SHA256':sha(DESIGN/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json'),'APPROVED_54_TARGET_LOCAL_SHA256':digest([[i,local1[i]] for i in IDS]),'DERIVED_LINEAGE':'frozen Stage4C_R2 + exact54 Human-approved native stored target positions -> independent Stage4C donor-transfer revision R1','DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True,'PRODUCTION_PROMOTED':False,'STAGE5_PROPAGATED':False,'STAGE6A_REQUALIFIED':False}
for k,v in metadata.items():ob['AMENDMENT_'+k]=v
assert all(plain(ob[k])==v for k,v in source_props.items())
dump('APPLICATION_BEFORE_SAVE_SNAPSHOT_R1.json',{'source_input':ref(SOURCE),'approved_candidate_input':ref(CANDIDATE),'source_local_m':local0,'source_world_mm':(np.array(world0)*1000).tolist(),'application_before_save_local_m':local1,'application_before_save_world_mm':(np.array(world1)*1000).tolist(),'protected_payload':source_payload,'protected_payload_sha256':digest(source_payload),'topology_signature_sha256':topology_signature,'authorized_metadata':metadata,'source_object_properties':source_props,'actual_changed_ids':changed,'source': 'factory-startup clean source reopen; not candidate/probe scene'})
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET),copy=True,compress=False)
dump('APPLICATION_SAVE_LOG_R1.json',{'status':'SAVED_PENDING_FACTORY_CLEAN_REOPEN','new_asset':ref(ASSET),'saved_from_frozen_source':True,'candidate_file_renamed_or_copied_as_artifact':False,'approved54_native_coordinates_only':True,'no_surface_recompute_or_optimization':True,'metadata_only_legal_exception':metadata,'runtime':bpy.app.version_string})
print('New independent Stage4C revision saved; exact54 approved native positions, no other modeling writes',flush=True)
