import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
G=read(OUT/'STATIC_BIND_AND_REBASE_R1.json')
assert read(OUT/'STATIC_VISIBLE_GATE_R1.json')['gate']=='PASS_CODEX_PRELIMINARY'
assert sha(CANDIDATE)==G['candidate']['sha256']
ob,rig=open_candidate();native=product_payload(ob,rig);V0,F=evaluate(ob,ob.matrix_world)
E=[list(e.vertices) for e in ob.data.edges];floor=read(S6/'palmar_root_targeted_visual_deformation_r1/MINIMUM_SAFETY_PROCEDURE_R1.json')['automatic_gates']
automatic,A0=safety_check(V0,F,E);L0=[(V0[a]-V0[b]).length for a,b in E]
final='--final' in sys.argv
renderer=Renderer(G['cameras'],'final_renders' if final else 'renders')
if final:renderer.sc.display.shading.shadow_intensity=0.
rows=[];restores=[];positions={};animations=[]
for c in cases():
    cid=c['case_id'];reset_pose(rig);bpy.context.view_layer.update();pre,Fpre=evaluate(ob,ob.matrix_world)
    assert state_zero(rig) and Fpre==F
    pre_error=max((a-b).length*MM for a,b in zip(pre,V0));assert pre_error<=floor['zero_mm']
    apply_case(rig,c);VP,FP=evaluate(ob,ob.matrix_world);assert FP==F
    row,_=safety_check(VP,F,E,A0)
    severe=[i for i,(a,b) in enumerate(E) if L0[i]*MM>=floor['severe_bind_mm_ge'] and (VP[a]-VP[b]).length/L0[i]>floor['severe_ratio_gt']]
    active=[pb.name for pb in rig.pose.bones if abs(pb.rotation_quaternion.angle)>1e-7]
    expected=[c['bone']] if 'bone' in c else ['THUMB_CMC_R']+(['THUMB_MCP_R'] if c['mcp_deg'] else [])+(['THUMB_IP_R'] if c['ip_deg'] else [])
    assert set(active)==set(expected)
    thumb=cid.startswith('THUMB_') or cid.startswith('CMC_') or cid.startswith('FULL_')
    views=['PALMAR_FULL','DORSAL_FULL','THUMB_WEB_OBLIQUE','THENAR_CLOSE'] if thumb else ['PALMAR_FULL','DORSAL_FULL','RADIAL_SIDE','FINGER_ROOTS_CLOSE']
    renderer.draw('REBASED',cid,VP,F,views)
    positions[cid]=[list(v) for v in VP]
    row.update(case_id=cid,definition=c,views=views,active_bones=active,severe_stretch_edge_count=len(severe),
        automatic_minimum='PASS' if row['automatic_status']=='PASS' and not severe else 'FAIL',
        local_quaternions={pb.name:list(pb.rotation_quaternion) for pb in rig.pose.bones if pb.name in active})
    rows.append(row)
    # A visible motion preview follows only this approved case's quaternion
    # path; intermediate frames are not additional qualification cases.
    end={pb.name:pb.rotation_quaternion.copy() for pb in rig.pose.bones}
    motion_view='THUMB_WEB_OBLIQUE' if thumb else 'PALMAR_FULL'
    frame_records=[]
    for index,fraction in enumerate([0.,.2,.4,.6,.8,1.]):
        reset_pose(rig)
        for name,q in end.items():rig.pose.bones[name].rotation_quaternion=Quaternion((1,0,0,0)).slerp(q,fraction)
        bpy.context.view_layer.update();VA,FA=evaluate(ob,ob.matrix_world);assert FA==F
        renderer.draw('REBASED',cid+f'_MOTION_{index:02}',VA,F,[motion_view])
        frame_records.append({'fraction':fraction,'path':renderer.records[-1]['path']})
    animations.append({'case_id':cid,'view':motion_view,'frames':frame_records,'path_semantics':'Quaternion slerp from ZERO to the same authorized case; no new axis/vector search'})
    reset_pose(rig);bpy.context.view_layer.update();Vr,Fr=evaluate(ob,ob.matrix_world)
    err=max((a-b).length*MM for a,b in zip(Vr,V0));assert state_zero(rig) and err<=floor['zero_mm'] and Fr==F
    restores.append({'case_id':cid,'pre_zero_error_mm':pre_error,'post_zero_error_mm':err,'all21_zero':True,'status':'PASS'})
    print('REPRESENTATIVE_CASE_READY',cid,row['automatic_minimum'],'ZERO_PASS',flush=True)
renderer.dispose();assert product_payload(ob,rig)==native
assert sha(CANDIDATE)==G['candidate']['sha256']
dump('REPRESENTATIVE_MOTION_EVIDENCE_R1.json',{'cases':rows,'count':10,'ZERO_RESTORE':'PASS','restores':restores,
    'candidate_native_payload_unchanged':True,'candidate_sha256':sha(CANDIDATE),'machine_scope':'Minimum finite/collapse/degenerate/gross severe stretch and ZERO restore; ordinary visible screen pending',
    'automatic_status':'PASS' if all(r['automatic_minimum']=='PASS' for r in rows) else 'FAIL',
    'axis_vector_definitions_reused':[ref(S6/'full_stage6a_requalification_r1/FULL_STAGE6A_CASE_MATRIX_R1.json'),ref(S6/'stage6b/STAGE6B_CASE_MATRIX.json'),ref(S6/'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json')],
    'bone_local_axes_spatial_fit_only':True,'new_action_definition_or_vector_search':False,'local_weight_tuning_vertex_count':G['local_weight_tuning_vertex_count'],
    'cast_shadow_intensity':0. if final else 1.})
dump('MOTION_RENDER_MANIFEST_R1.json',{'renders':renderer.records,'cameras':G['cameras'],'still_views_per_case':4,'matched_motion_still_count':40,
    'motion_path_preview_frames':60,'representative_case_count':10,'animations':animations,'candidate_saves_during_poses':0})
dump('POSED_DISPLAY_COORDINATES_R1.json',{'ZERO':[list(v) for v in V0],'cases':positions,'faces':[list(f) for f in F]})
print('TEN_CASES_COMPLETE_ZERO_RESTORED',flush=True)
