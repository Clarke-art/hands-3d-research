import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));from stage_common import *
man=read(P/'SCENE_MANIFEST.json');bind=read(P/'R1_REVIEW_CAMERA_BIND.json');assert sha(man['path'])==man['sha256']
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];result={}
for view,name in man['cameras'].items():
    ob=bpy.data.objects[name];cfg=bind['cameras'][view]
    err=float(np.max(abs(np.array(ob.matrix_world)-np.array(cfg['matrix_world']))))
    print('CAMERA_SERIALIZED_MATRIX_DIFFERENCE',view,err,ob.data.ortho_scale-cfg['ortho_scale'],flush=True)
    assert err<1e-6 and ob.data.ortho_scale==cfg['ortho_scale'] and ob.data.type==cfg['type']
    result[view]=dict(world_matrix_difference=err,ortho_scale_equal=True,type_equal=True)
assert sc.render.engine==bind['render_engine'] and sc.render.fps==bind['fps']
assert [sc.render.resolution_x,sc.render.resolution_y]==bind['dimensions']
dump('ACTUAL_CAMERA_VERIFICATION.json',dict(all_actual_R1_R2_camera_transforms_equal=True,
    equality_scope='Same bound camera poses; float32 matrix decomposition/serialization tolerance 1e-6, not bitwise matrix equality',views=result,same_render_engine=True,same_dimensions=True,same_fps=True,
    new_candidate_saved=False,read_only=True))
print('ACTUAL_ALL_THREE_COMPARISON_CAMERAS_BOUND_WITH_FLOAT32_PRECISION')
