import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from shared import *
G=read(OUT/'ITERATION_02_GEOMETRY.json')
assert sha(CURRENT)==EXPECTED
assert not CANDIDATE.exists(),'Do not overwrite a saved candidate'
ob,rig=open_asset(CURRENT);before=snapshot()
assert before['coordinates_local_m']==G['initial_local_m']
for i in G['vertex_ids']:ob.data.vertices[i].co=G['candidate_local_m'][i]
ob.data.update();bpy.context.view_layer.update();pre=snapshot()
assert protected_static(before['protected'])==protected_static(pre['protected'])
assert pre['coordinates_local_m']==G['candidate_local_m']
assert state_zero(rig)
for k,v in {'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'HUMAN_APPROVAL':'PENDING','PRODUCTION_PROMOTION':'NO',
            'SOURCE_SHA256':EXPECTED,'SELECTED_ITERATION':'02','STATIC_ITERATION_COUNT':5,
            'PRELIMINARY_VERDICT':'STATIC_PALM_SHAPE_STILL_INSUFFICIENT'}.items():
    bpy.context.scene['PALMAR_MACRO_'+k]=v
bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),copy=True,compress=False)
ob,rig=open_asset(CANDIDATE);reopened=snapshot()
assert reopened==pre
changed=[i for i,(a,b) in enumerate(zip(before['coordinates_local_m'],reopened['coordinates_local_m'])) if a!=b]
assert changed==G['vertex_ids']
assert all(before['coordinates_local_m'][i]==reopened['coordinates_local_m'][i] for i in G['protected_dorsal54'])
palchanged=[i for i in G['palmar16_visual_sentinel'] if before['coordinates_local_m'][i]!=reopened['coordinates_local_m'][i]]
dump('CANDIDATE_SAVE_REOPEN_PROTECTION_R1.json',{'status':'PASS_POSITION_ONLY_SERIALIZATION',
     'current':ref(CURRENT),'candidate':ref(CANDIDATE),'donor':G['source'],'selected_iteration':'02','static_iteration_count':5,
     'actual_changed_vertex_ids':changed,'RESTORATION_VERTEX_COUNT':len(changed),
     'mesh_positions_only_written':True,'protected_payload_equal_excluding_auto_derived_texspace':True,
     'derived_exception':'use_auto_texspace remains true; texspace_location/size are automatically recomputed from changed position bounds; no texture settings setter used',
     'protected_before_sha256':digest(protected_static(before['protected'])),'protected_after_sha256':digest(protected_static(reopened['protected'])),
     'protected_fields':list(before['protected']),'weights_exact_unchanged':True,'rig_21_bones_exact_unchanged':True,
     'topology_vertex_IDs_UV_materials_groups_modifiers_exact_unchanged':True,'shape_keys_before_after':None,
     'dorsal54_native_coordinate_drift':0,'palmar16_changed_ids':palchanged,'palmar16_is_visual_sentinel':True,
     'outside_write_set_drift':0,'serialization_drift':0,'candidate_save_calls':1,'production_save_calls':0,
     'candidate_final_pose':'ZERO / RSSF','dynamic_pose_cases_executed':0})
records=[];checks=[];restores=[]
views=['HUMAN_PALMAR','FULL_PALM','THENAR_CLOSE','FIRST_WEB_CLOSE','SIDE_VOLUME','SILHOUETTE','DORSAL54_SENTINEL','PALMAR16_SENTINEL']
display={}
for label,path in [('CURRENT',CURRENT),('CANDIDATE',CANDIDATE)]:
    ob,rig=open_asset(path);original=snapshot();V,F=evaluate(ob,ob.matrix_world);E=[list(e.vertices) for e in ob.data.edges]
    row,_=safety_check(V,F,E);row['asset']=label;checks.append(row)
    assert row['automatic_status']=='PASS'
    renderer=Renderer(G['cameras']);renderer.draw(label,'ZERO',V,F,views);records.extend(renderer.records);renderer.dispose()
    reset_pose(rig);bpy.context.view_layer.update();Z,FZ=evaluate(ob,ob.matrix_world)
    err=max((a-b).length*MM for a,b in zip(V,Z))
    assert state_zero(rig) and FZ==F and err<=.0001 and snapshot()==original
    restores.append({'asset':label,'all_21_channels_zero':True,'error_mm':err,'status':'PASS','dynamic_pose_applied':False})
    display[label]=[list(v) for v in V]
bpy.ops.wm.read_factory_settings(use_empty=True)
renderer=Renderer(G['cameras']);renderer.draw('OFFICIAL_L1','NEUTRAL',[Vector(v) for v in G['donor_visual_world_m']],
     [tuple(f) for f in G['donor_faces']],views[:6]);records.extend(renderer.records);renderer.dispose()
dump('MATCHED_RENDER_MANIFEST_R1.json',{'renders':records,'cameras':G['cameras'],'count':len(records),
     'same_camera_scale_material_light':True,'only_static_ZERO':True,'official_native_neutral_thumb_pose_differs_from_RSSF':True,
     'source_registered_by_stable_palm_landmarks':True,'source_scale':1.,'dynamic_pose_cases_executed':0})
dump('MINIMUM_MACHINE_AUTOMATIC_R1.json',{'status':'PASS','rows':checks,'ZERO_RESTORE':'PASS','restores':restores,
     'NaN_Inf':0,'collapsed_faces':0,'degenerate_edges':0,'ordinary_visible_gate':'PENDING_VISUAL_SCREEN'})
dump('FINAL_DISPLAY_COORDINATES_R1.json',{'current':display['CURRENT'],'candidate':display['CANDIDATE'],
     'source':G['donor_visual_world_m'],'faces':G['faces'],'source_faces':G['donor_faces']})
assert sha(CURRENT)==EXPECTED
print('FINAL_STATIC_CANDIDATE_SAVED',len(changed),sha(CANDIDATE),flush=True)
