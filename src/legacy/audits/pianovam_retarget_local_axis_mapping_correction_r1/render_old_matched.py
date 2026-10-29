import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mapping_core import *
ob,rig=m.open_file(OLD);scene=bpy.context.scene;cams=read(OUT/'FULL_REVIEW_CAMERAS_R1.json');renderer=m.Renderer(cams,'full_motion_frames');renderer.sc.display.shading.shadow_intensity=0
for j in range(210):
 scene.frame_set(j+1);bpy.context.view_layer.update();V,F=m.evaluate(ob,ob.matrix_world);renderer.draw('OLD',f'{j:04}',V,F,list(cams))
renderer.dispose();assert sha(OLD)==OLD_SHA
