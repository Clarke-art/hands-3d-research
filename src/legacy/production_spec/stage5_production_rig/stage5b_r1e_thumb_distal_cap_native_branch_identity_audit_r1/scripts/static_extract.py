"""Read saved mesh coordinates and rest bone data only. Never evaluate a pose or save a blend."""
import sys
sys.dont_write_bytecode=True
import bpy, json, hashlib
from pathlib import Path

out=Path(__file__).resolve().parents[1];root=out.parents[2]
for name in ['_tmp','renders']:(out/name).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
paths={p for name in ['production_spec','docs'] for p in (root/name).rglob('*') if p.is_file() and out not in p.parents}
paths.update(root.rglob('*.blend'))
before={str(p.relative_to(root)).replace('\\','/'):sha(p) for p in sorted(paths)}
snap=out/'FROZEN_HASHES_BEFORE.json'
if snap.exists():assert json.loads(snap.read_text(encoding='utf8'))==before
else:snap.write_text(json.dumps(before,indent=1),encoding='utf8')
raw=json.loads((out.parent/'stage5b_r1e_endpoint_authority_review/_tmp/review_raw.json').read_text(encoding='utf8'))
result={}
for tag,path in [('NATIVE',root/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend'),('R2_SELECTOR_STATE',out.parent/'stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    ob=bpy.data.objects['Hand  - Realistic'];mw=ob.matrix_world
    faces=[list(f.vertices) for f in ob.data.polygons]
    assert faces==raw['R1B']['faces']
    result[tag]={'path':str(path.relative_to(root)),'sha256':sha(path),'vertices_world_m':[list(<REDACTED_EMAIL>) for v in ob.data.vertices],'matrix_world':[list(row) for row in mw],'faces':faces,'edges':[list(e.vertices) for e in ob.data.edges],'face_material_indices':[f.material_index for f in ob.data.polygons],'materials':[m.name if m else None for m in ob.data.materials],'armatures':{a.name:{b.name:{'head_world':list(<REDACTED_EMAIL>_local),'tail_world':list(<REDACTED_EMAIL>_local)} for b in a.data.bones} for a in bpy.data.objects if a.type=='ARMATURE'},'objects':[{'name':a.name,'type':a.type} for a in bpy.data.objects]}
    print('READ',tag,len(ob.data.vertices),'vertices',flush=True)
(out/'_tmp/static_mesh_states.json').write_text(json.dumps(result),encoding='utf8')
assert all(sha(root/p)==h for p,h in before.items())
print('Protected',len(before),'files unchanged. Poses evaluated=0; BLEND writes=0.',flush=True)
