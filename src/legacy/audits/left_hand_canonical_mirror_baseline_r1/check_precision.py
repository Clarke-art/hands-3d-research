import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent
src=json.loads((P/'SOURCE_R2_INSPECTION_R1.json').read_text())
plane=json.loads((P/'CANONICAL_MIRROR_PLANE_R1.json').read_text());S=Matrix(plane['reflection_armature_matrix']);H=Matrix.Diagonal(Vector((-1,1,1,1)))
bpy.ops.wm.open_mainfile(filepath=str(P/'LEFT_HAND_OFFICIAL_L1_MIRROR_CANDIDATE_R1.blend'),load_ui=False,use_scripts=False)
rig=bpy.data.objects['LEFT_HAND_PRODUCTION_RIG']
for r in src['bones']:
 b=rig.data.bones[r['name'][:-2]+'_L'];target=S@Matrix(r['matrix'])@H
 print(r['name'], 'matrix_error',max(abs(b.matrix_local[i][j]-target[i][j]) for i in range(4) for j in range(4)), 'head_m',(b.head_local-S@Vector(r['head'])).length,'tail_m',(b.tail_local-S@Vector(r['tail'])).length)
