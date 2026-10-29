import sys,importlib.util,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('helpers',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.old.lib.OUT=OUT
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'RAW'
ob,rig=m.open_file(OUT/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend');scene=bpy.context.scene
action=bpy.data.actions['PIANOVAM_PHYSICAL_RIGHT_RAW_R1' if mode=='RAW' else 'PIANOVAM_PHYSICAL_RIGHT_SMOOTHED_R1'];rig.animation_data.action=action
cams=json.loads((OUT/'REVIEW_CAMERAS_R1.json').read_text());renderer=m.Renderer(cams,mode.lower()+'_motion_frames');renderer.sc.display.shading.shadow_intensity=0
for j in range(210):
 scene.frame_set(1+j);bpy.context.view_layer.update();V,F=m.evaluate(ob,ob.matrix_world);renderer.draw(mode,f'{j:04}',V,F,list(cams))
renderer.dispose()
