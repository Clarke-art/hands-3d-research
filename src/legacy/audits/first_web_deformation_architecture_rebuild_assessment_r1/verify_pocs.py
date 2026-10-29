import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
ob0,rig0=fresh();native=m.product_payload(ob0,rig0);shape0=core.shape_payload(ob0);materials=[m.material_payload(x) for x in ob0.data.materials if x];rest0={b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None,'use_deform':b.use_deform,'inherit_scale':b.inherit_scale,'inherit_rotation':b.use_inherit_rotation} for b in rig0.data.bones};results={}
for label,name in [('A','LOCAL_RETOPOLOGY'),('B','HELPER_BONE'),('C','LOCAL_CAGE')]:
    path=OUT/f'ROUTE_{label}_{name}_POC_R1.blend';ob,rig=load(path);neutral(rig);p=m.product_payload(ob,rig);shape=core.shape_payload(ob)
    assert [m.material_payload(x) for x in ob.data.materials if x]==materials
    assert len(shape['keys'])==2 and shape['drivers']==shape0['drivers']
    for n,r in rest0.items():
        b=rig.data.bones[n];actual={'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(r) for r in b.matrix_local],'parent':b.parent.name if b.parent else None,'use_deform':b.use_deform,'inherit_scale':b.inherit_scale,'inherit_rotation':b.use_inherit_rotation};assert actual==r,n
    assert digest(action_payload(bpy.data.actions[ACTION]))==read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['actions_before'][ACTION]
    outside=[i for i in range(3300) if i not in PATCH_IDS]
    if label in ['B','C']:
        assert p['positions_local_m']==native['positions_local_m'] and p['faces']==native['faces'] and p['UV']==native['UV']
        assert shape==shape0
    else:
        assert all(p['positions_local_m'][i]==native['positions_local_m'][i] for i in outside)
        deltaold=np.array(shape0['keys'][1]['coords'])-np.array(shape0['keys'][0]['coords']);deltanew=np.array(shape['keys'][1]['coords'][:3300])-np.array(shape['keys'][0]['coords'][:3300]);assert np.max(abs(deltaold-deltanew))<2e-7
    # A rebuilt datablock may omit zero-valued sparse memberships. All actual weights must match.
    for i in outside:assert {g:w for g,w in p['weights'][i] if w!=0}=={g:w for g,w in native['weights'][i] if w!=0}
    if label=='C':assert [[g for g in row if g[0]<len(native['groups'])] for row in p['weights']]==native['weights']
    result={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'existing_21_rest_semantics_exact':True,'source_action_hash_exact':True,'outside_patch_basis_weights_exact':True,'materials_exact':True,'approved_driver_exact':True,'corrective_count':1,'new_corrective_count':0,'approved_corrective_content':('EXACT' if label in ['B','C'] else 'SAME_RELATIVE_FIELD_RETAINED_INTERPOLATED_TO_NEW_TOPOLOGY')}
    if label=='B':
        # Compare saved derived helper animation to the declared formula at actual screen frames.
        rest=rig.data.bones['INTERNAL_FIRST_WEB_BRIDGE_R1'].matrix_local.copy();err=[]
        for f in FRAMES:
            motion(rig,f);T=[rig.pose.bones[n]<REDACTED_EMAIL>[n].matrix_local.inverted() for n in ['INDEX_MCP_R','THUMB_CMC_R']];q=T[0].to_quaternion().slerp(T[1].to_quaternion(),.5);H=q.to_matrix().to_4x4()@rest;H.translation=(T[0]@rest.translation+T[1]@rest.translation)*.5
            err.append(float(np.max(np.abs(np.array(rig.pose.bones['INTERNAL_FIRST_WEB_BRIDGE_R1'].matrix)-np.array(H)))))
        assert max(err)<1e-5;result['saved_helper_formula_matrix_max_abs_error']=max(err)
    if label=='C':
        mod=next(m for m in ob.modifiers if m.type=='LATTICE');cage=mod.object;layer=[]
        for f in FRAMES:
            motion(rig,f);active=coords(ob);mod.show_viewport=False;bpy.context.view_layer.update();off=coords(ob);mod.show_viewport=True;bpy.context.view_layer.update()
            evaluated=cage.evaluated_get(bpy.context.evaluated_depsgraph_get())
            layer.append({'frame':f,'max_mesh_displacement_mm':float(np.linalg.norm(active-off,axis=1).max()*1000),'control_Y_range':[min(p.co_deform.y for p in evaluated.data.points),max(p.co_deform.y for p in evaluated.data.points)],'invalid_driver_count':sum(not d.driver.is_valid for d in cage.data.animation_data.drivers)})
        result['lattice_actual_effect']=layer
        assert all(r['invalid_driver_count']==0 for r in layer)
    results[label]=result
dump('POC_PROTECTED_CONTENT_VERIFICATION_R1.json',{'status':'PASS','routes':results,'source_inputs_unchanged':inputs(),'production_pointers_written':False,'no_poc_file_saved_during_verification':True})
print('PROTECTED_POC_CONTENTS_VERIFIED',results,flush=True)
