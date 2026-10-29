import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_local import *
from bpy_extras.object_utils import world_to_camera_view
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==man['sha256']
tl=read(C1/'PERFORMANCE_TIMELINE.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False);sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']];camera=bpy.data.objects[man['cameras']['OVERHEAD']]
settime(sc,1.05);rois={d:finger_roi(mesh,rig,d) for d in ['MIDDLE','RING']};dump('LOCAL_SKIN_ROI.json',rois)
boneinfo={d:{name:dict(parent=rig.data.bones[name].parent.name if rig.data.bones[name].parent else None,head=list(rig.data.bones[name].head_local),tail=list(rig.data.bones[name].tail_local)) for name in [d+'_'+j+'_R' for j in ['MCP','PIP','DIP','TIP']]} for d in ['MIDDLE','RING']}
camcfg={view:dict(location=list(bpy.data.objects[name].location),rotation_euler=list(bpy.data.objects[name].rotation_euler),matrix_world=[list(v) for v in bpy.data.objects[name].matrix_world],ortho_scale=bpy.data.objects[name].data.ortho_scale,name=name) for view,name in man['cameras'].items()}
rows=[];refs={};states=[]
def phase(d,t):
    finger=3 if d=='MIDDLE' else 4
    near=[n for n in tl['notes'] if n['hand']=='R' and n['finger']==finger]
    for n in near:
        if n['note_on']<=t<n['note_off']:return dict(phase='ACTIVE_HOLD_OR_PRESS',note_id=n['note_id'],note=n['note_name'])
        if n['note_on']-.12<=t<n['note_on']:return dict(phase='APPROACH',note_id=n['note_id'],note=n['note_name'])
        if n['note_off']<=t<n['note_off']+.20:return dict(phase='RELEASE_RECOVERY',note_id=n['note_id'],note=n['note_name'])
    return dict(phase='NON_ACTIVE_PREPARATION',note_id=None)
for frame in range(1,201):
    t=(frame-1)/60;v=snapshot(sc,info,'R',t);rel=local_relation(v['V'],rois,camera)
    rows.append(dict(frame=frame,presentation_sec=t,music_sec=t-.35,**rel,phases={d:phase(d,t) for d in rois}))
    if frame in [37,49,61,64,67,73,79,85,91,103,121,145,169,181,193]:
        refs[str(t)]={'R':v,'L':snapshot(sc,man['mapping']['L'],'L',t)}
        # Visible semantic bone overlay to confirm which skin is under arrow.
        if frame in [61,64,67]:
            for view,name in man['cameras'].items():
                sc.camera=bpy.data.objects[name];folder=P/'readonly_renders';folder.mkdir(exist_ok=True);sc.render.filepath=str(folder/f'{view}_{frame:04d}.png');bpy.ops.render.render(write_still=True)
    if frame%40==0:print('FINITE_DISTAL_PATCH_DIAGNOSTIC',frame,flush=True)
# Numeric Action DOFs are saved data, not a new motion solve.
num=dict(np.load(A/'motion.npz'));Q=np.degrees(num['R_q']);source_times=num['times']+.05
np.savez_compressed(P/'source_numeric.npz',times=source_times,qdeg=Q)
dump('OVERLAP_TIMES_AND_GEOMETRY.json',dict(rows=rows,reference_source_sha256=man['sha256'],same_hand=True,hand='R',fingers=['MIDDLE','RING'],bones=boneinfo,cameras_actual=camcfg,scope='Finite identified distal finger patches only; no global collision optimization',solver_calls=0))
parity={}
for side,folder in [('R',A),('L',B)]:
    src=read(folder/'SCENE_MANIFEST.json');assert sha(src['path'])==src['sha256']
    bpy.ops.wm.open_mainfile(filepath=src['path'],load_ui=False,use_scripts=False);scene=bpy.data.scenes[src['scene']];bpy.context.window.scene=scene
    checked=[]
    for ts,references in refs.items():
        reference=references[side]
        t=float(ts);sv=snapshot(scene,src['mapping'],side,t-(.05 if side=='R' else 0))
        if side=='R':
            err=float(np.max(np.linalg.norm(sv['V']-reference['V'],axis=1))*1000);berr=float(np.max(abs(sv['basis']-reference['basis'])));rerr=float(np.max(abs(sv['root']-reference['root'])))
            assert err<.03 and berr<1e-5 and rerr<1e-5
            # Projection comparison uses the same actual C1 camera, not the
            # stale identity-matrix camera metadata in the original manifest.
            checked.append(dict(presentation_sec=t,music_sec=t-.35,skin_max_difference_mm=err,basis_max_difference=berr,root_max_difference=rerr))
        else:
            err=float(np.max(np.linalg.norm(sv['V']-reference['V'],axis=1))*1000);berr=float(np.max(abs(sv['basis']-reference['basis'])));rerr=float(np.max(abs(sv['root']-reference['root'])))
            assert err<.03 and berr<1e-5 and rerr<1e-5
            checked.append(dict(presentation_sec=t,music_sec=t-.35,skin_max_difference_mm=err,basis_max_difference=berr,root_max_difference=rerr))
    parity[side]=dict(path=src['path'],sha256=src['sha256'],samples=checked)
dump('SINGLE_HAND_CAUSE_PARITY.json',parity)
dump('DIAGNOSTIC_GATE.json',dict(only_readonly=True,source_identity_verified=True,target_hand='R',target_pair=['MIDDLE','RING'],candidate_count=0,solver_calls=0))
print('READONLY_OVERLAP_IDENTITY_AND_CAUSE_READY',flush=True)
