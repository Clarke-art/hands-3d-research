import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import numpy as np
cams=cameras()
cams['FIRST_WEB_CLOSE']={'center':[1.444,.022,.446], 'direction':cams['THENAR_CLOSE']['direction'],'ortho_scale_m':.095,'resolution':[1200,1100]}
cams['WEB_GRAZING']={'center':[1.444,.022,.446], 'direction':[.68,.69,.25],'ortho_scale_m':.095,'resolution':[1200,1100]}
records=[];checks={};payloads={};zeroes={};materials={};key_protection={}
for label,path in [('BEFORE',INPUT),('AFTER',CANDIDATE)]:
    ob,rig=open_file(path);payloads[label]=product_payload(ob,rig)
    materials[label]=[material_payload(m) for m in ob.data.materials if m]
    if ob.data.shape_keys:
        keys=ob.data.shape_keys.key_blocks
        assert [list(v.co) for v in keys[0].data]==payloads[label]['positions_local_m']
        assert len(keys)==2 and keys[1].value==0
        edited=[i for i,(a,b) in enumerate(zip(keys[0].data,keys[1].data)) if a.co!=b.co]
        assert set(edited)<=set(read(OUT/'CORRECTIVE_KEY_R1.json')['changed_vertex_ids'])
        key_protection={'corrective_key_count':len(keys)-1,'basis_shape_key_exact':True,'changed_vertex_ids':edited,'save_zero_values':[float(k.value) for k in keys[1:]],'driver_count':len(ob.data.shape_keys.animation_data.drivers)}
    V0,F=evaluate(ob,ob.matrix_world);zeroes[label]=[list(v) for v in V0]
    E=[list(e.vertices) for e in ob.data.edges]
    _,A0=safety_check(V0,F,E)
    lengths=np.array([(V0[a]-V0[b]).length for a,b in E])
    floor=read(S6/'palmar_root_targeted_visual_deformation_r1/MINIMUM_SAFETY_PROCEDURE_R1.json')['automatic_gates']
    rr=Renderer(cams,'renders');rr.sc.display.shading.shadow_intensity=0
    rows=[]
    for c in CASES:
        pose(rig,c);V,FP=evaluate(ob,ob.matrix_world);assert FP==F
        check,_=safety_check(V,F,E,A0)
        stretch=np.array([(V[a]-V[b]).length for a,b in E])/lengths
        check['gross_tearing_severe_stretch_count']=int(((lengths*1000>=floor['severe_bind_mm_ge'])&(stretch>floor['severe_ratio_gt'])).sum())
        rr.draw(label,c['case_id'],V,F,['PALMAR_FULL','DORSAL_FULL','FIRST_WEB_CLOSE','WEB_GRAZING'])
        reset_pose(rig);bpy.context.view_layer.update();VR,FR=evaluate(ob,ob.matrix_world)
        check['zero_restore_max_mm']=max((a-b).length*1000 for a,b in zip(VR,V0))
        assert state_zero(rig) and FR==F
        check['ZERO_RESTORE']='PASS' if check['zero_restore_max_mm']<=floor['zero_mm'] else 'FAIL'
        check['case_id']=c['case_id'];rows.append(check)
        check['corrective_values']={k.name:float(k.value) for k in ob.data.shape_keys.key_blocks[1:]} if ob.data.shape_keys else {}
        # Values recorded after reset above must be ZERO; capture pose values separately.
        pose(rig,c)
        check['pose_corrective_values']={k.name:float(k.value) for k in ob.data.shape_keys.key_blocks[1:]} if ob.data.shape_keys else {}
        reset_pose(rig);bpy.context.view_layer.update()
    rr.dispose();records+=rr.records;checks[label]=rows
    assert product_payload(ob,rig)==payloads[label]
before,after=payloads['BEFORE'],payloads['AFTER']
for k in before:
    if k!='weights':assert before[k]==after[k],k
assert materials['BEFORE']==materials['AFTER']
region=set(read(OUT/'WEIGHT_ITERATION_1.json')['allowed_vertex_ids']);groupids={before['groups'].index(g) for g in ['WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R']}
changed=[]
for i,(a,b) in enumerate(zip(before['weights'],after['weights'])):
    if a!=b:
        assert i in region
        assert {g:w for g,w in a if g not in groupids}=={g:w for g,w in b if g not in groupids}
        changed.append(i)
        assert abs(sum(w for g,w in b)-sum(w for g,w in a))<2e-7
zero_error=float(np.max(np.linalg.norm(np.array(zeroes['BEFORE'])-np.array(zeroes['AFTER']),axis=1))*1000)
dump('PRESERVATION_AND_MINIMUM_SAFETY_R1.json',{'input':ref(INPUT),'candidate':ref(CANDIDATE),'basis_exact':before['positions_local_m']==after['positions_local_m'],'topology_UV_rig_joint_layout_modifiers_transforms_exact':True,'materials_exact':True,'bone_count':len(after['rest']),'basis_vertex_writes':0,'only_authorized_weights_changed':True,'outside_region_exact':True,'changed_vertex_ids':changed,'changed_vertex_count':len(changed),'shape_key_protection':key_protection,'zero_before_after_max_error_mm':zero_error,'checks':checks,'machine_scope':'Finite, collapsed face, degenerate edge, gross stretch, ZERO restore; gross penetration requires ordinary visual screen. No hidden crossing / normal-dot / edge census.'})
dump('MATCHED_RENDER_MANIFEST_R1.json',{'renders':records,'cameras':cams,'case_ids':CASE_IDS,'case_count':6,'all_faces_visible':True,'neutral_material':True,'cast_shadow_intensity':0})
assert sha(INPUT)==INPUT_SHA
print('COMPARE_READY',len(records),'ZERO_ERROR_MM',zero_error,flush=True)
