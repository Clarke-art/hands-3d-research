import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
ob,rig=load(SOURCE);motion(rig,130)
V,F=m.evaluate(ob,ob.matrix_world)
cams=read(ROOT/'audits/pianovam_first_web_joint_contribution_isolation_r1/MACHINE_CHECK_R1.json')['frames'][0]['same_camera']
region=set(read(FIX/'WEIGHT_ITERATION_2.json')['allowed_vertex_ids'])
rr=m.Renderer(cams,'support_preview');rr.sc.display.shading.shadow_intensity=0
rr.draw('SUPPORT','F130',V,F,[])
mat=bpy.data.materials.new('UNSAVED_WEIGHT_REGION_COLOR');mat.diffuse_color=(.55,.12,.10,1)
rr.active.data.materials.append(mat)
for face in rr.active.data.polygons:
    face.material_index=2 if any(i in region for i in face.vertices) else 0
for view in cams:
    job=cams[view];center,direction=Vector(job['center']),Vector(job['direction'])
    rr.cam.location=center+direction*.7;rr.cam.rotation_euler=(center-rr.cam.location).to_track_quat('-Z','Y').to_euler()
    rr.cd.ortho_scale=job['ortho_scale_m'];rr.sc.render.resolution_x,rr.sc.render.resolution_y=job['resolution']
    rr.sc.render.filepath=str(OUT/'support_preview'/f'SUPPORT__F130__{view}.png')
    bpy.ops.render.render(write_still=True,scene=rr.sc.name)
rr.dispose()
print('LOCAL_SUPPORT_VISIBLE')
