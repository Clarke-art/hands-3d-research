"""Read saved mesh/rig/weight evidence. No mutations, pose evaluation or saves."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
S5=ROOT/'production_spec/stage5_production_rig'
paths={
 'CORRECTED':S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend',
 'R2A':S5/'stage5a_r2a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend',
 **{s:S5/('stage5b_'+s.lower())/('RIGHT_HAND_STAGE5B_INITIAL_SKIN_'+s+'.blend') for s in ['R1','R1A','R1B','R1C','R1D','R1E']},
 'RSSF':ROOT/'production_spec/stage4_blender/stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R2.blend',
}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
data={}
for name,p in paths.items():
 before=sha(p)
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 ob=bpy.data.objects.get('Hand  - Realistic')
 assert ob and len(ob.data.vertices)==3416,(name,'mesh mismatch')
 groups={g.index:g.name for g in ob.vertex_groups}
 rig=bpy.data.objects.get('RIGHT_HAND_PRODUCTION_RIG')
 entry={'source_path':str(p.relative_to(ROOT)),'source_sha256':before,
  'vertex_positions_world_mm':[list((<REDACTED_EMAIL>)*1000) for v in ob.data.vertices],
  'vertex_positions_local_m':[list(v.co) for v in ob.data.vertices],
  'edges':[list(e.vertices) for e in ob.data.edges],
  'faces':[list(f.vertices) for f in ob.data.polygons],
  'weights':[{groups[g.group]:float(g.weight) for g in v.groups if g.weight>0} for v in ob.data.vertices],
  'vertex_groups':list(groups.values()),'mesh_matrix_world':[list(r) for r in ob.matrix_world],
  'bones':{} if not rig else {b.name:{'head_world_mm':list((<REDACTED_EMAIL>_local)*1000),
      'tail_world_mm':list((<REDACTED_EMAIL>_local)*1000),'head_local_m':list(b.head_local),
      'tail_local_m':list(b.tail_local),'matrix_local':[list(r) for r in b.matrix_local],
      'use_deform':b.use_deform,'parent':None if not b.parent else b.parent.name} for b in rig.data.bones}}
 assert sha(p)==before
 data[name]=entry
 print('Read-only extracted',name,len(entry['weights']),len(entry['bones']),flush=True)
target=OUT/'SAVED_RIG_AND_SKIN_EVIDENCE_R1.json'
assert not target.exists()
target.write_text(json.dumps({'read_only':True,'BLEND_FILES_WRITTEN':0,'weights_written':0,'pose_evaluations':0,'sources':data},indent=2),encoding='utf-8')
