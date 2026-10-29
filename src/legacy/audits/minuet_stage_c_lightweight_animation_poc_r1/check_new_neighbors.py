"""Read-only local regression check; no motion generation."""
import sys,json,itertools
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
man=read(OUT/'SCENE_MANIFEST.json');src=read(C1/'SCENE_MANIFEST.json')
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc;rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
new=rig.animation_data.action;slot=rig.animation_data.action_slot.identifier
with bpy.data.libraries.load(src['path'],link=False) as (a,b):b.actions=['DESIGN_ONLY_STAGE_C_R_rig']
source=bpy.data.actions['DESIGN_ONLY_STAGE_C_R_rig'];rois=read(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/SOURCE_MODEL_MANIFEST.json')['rois']
pairs=[(a,b) for a,b in itertools.combinations(c.DIGITS,2) if a in ['INDEX','MIDDLE','RING'] or b in ['INDEX','MIDDLE','RING']]
rows=[]
for i in range(358):
 row=dict(time=i/60)
 for state,action in [('source',source),('new',new)]:
  rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[slot];settime(sc,i/60);V=mesh_pose(mesh)[0]
  trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in c.DIGITS}
  row[state]={a+'_'+b:len(trees[a].overlap(trees[b])) for a,b in pairs}
 rows.append(row)
summary={a+'_'+b:{s:dict(peak=max(r[s][a+'_'+b] for r in rows),hit_frames=sum(r[s][a+'_'+b]>0 for r in rows)) for s in ['source','new']} for a,b in pairs}
newtypes=[p for p,values in summary.items() if values['source']['peak']==0 and values['new']['peak']>0]
(OUT/'NEIGHBOR_REGRESSION_CHECK.json').write_text(json.dumps(dict(summary=summary,new_intersection_pair_types=newtypes,scope='Actual strong digit skin ROIs beyond MCP, 60Hz; nine pairs involving the three modified digits; diagnostic only',rows=rows),indent=2),encoding='utf8')
print(json.dumps(summary),flush=True)
