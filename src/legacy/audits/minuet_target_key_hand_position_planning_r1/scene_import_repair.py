from stage_common import *
lock=read(P/'PLANNING_LOCK.json');old=lock['scripts']['03_scene.py'];new=sha(P/'03_scene.py')
assert old!=new and not (P/'STAGE_A_RIGHT_TARGET_KEY_DESIGN_PROVISIONAL_R1.blend').exists()
dump('SCENE_IMPORT_REPAIR.json',dict(reason='Missing re import in AST-reused structural identity helper; failed before save/bake.',
    old_scene_script_sha256=old,new_scene_script_sha256=new,
    motion_sha256=sha(P/'motion.npz'),fingering_changed=False,planner_changed=False,
    trajectory_regenerated=False,new_candidate=False,change='Add import re only'))
lock['scripts']['03_scene.py']=new;dump('PLANNING_LOCK.json',lock)
