"""Static Blender data reads only. No pose evaluation, weight edits or blend saving."""
import sys
sys.dont_write_bytecode=True
import json, hashlib, datetime
from pathlib import Path
import bpy

AUD=Path(__file__).resolve().parents[1]
ROOT=AUD.parents[2]
S5=ROOT/'production_spec/stage5_production_rig'
PREV=S5/'stage5b_r1e_endpoint_authority_review'
AUD.joinpath('_tmp').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(AUD/n).write_text(json.dumps(x,indent=1,ensure_ascii=False),encoding='utf-8')
dirs=[S5/'stage5a_r2a',S5/'stage5b_r1b',S5/'stage5b_r1e',ROOT/'production_spec/stage6_deformation/stage6b_r3_thumb_tip_ownership_boundary',S5/'stage5b_r1e_feasibility_audit',PREV]
files={p for d in dirs for p in d.rglob('*') if p.is_file()}|set(ROOT.rglob('*.blend'))
files.update(p for p in ROOT.joinpath('docs').glob('*.md'))
files.update(p for d in [S5/'stage5b_r1',S5/'stage5b_r1a'] for p in d.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md'])
before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(files)}
if (AUD/'FROZEN_HASHES_BEFORE.json').exists():
    original=json.loads((AUD/'FROZEN_HASHES_BEFORE.json').read_text(encoding='utf-8'))
    assert all(before[k]==v for k,v in original.items())
else:write('FROZEN_HASHES_BEFORE.json',before)
print('Frozen static snapshot',len(before),flush=True)
raw=json.loads((PREV/'_tmp/review_raw.json').read_text(encoding='utf-8'))
out={'generated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'runtime':bpy.app.version_string,'data_reads':[],'historical':{}}
for tag,path in [('STAGE4A_R2_PRE_RSSF',ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend'),('STAGE5B_R1',S5/'stage5b_r1/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend'),('STAGE5B_R1A',S5/'stage5b_r1a/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend'),('STAGE5B_R1B',S5/'stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    ob=bpy.data.objects['Hand  - Realistic']
    topo=[list(p.vertices) for p in ob.data.polygons]
    assert topo==raw['R1B']['faces'],tag+' face-index correspondence not established'
    verts=[list(<REDACTED_EMAIL>) for v in ob.data.vertices]
    weights=[{ob.vertex_groups[g.group].name:float(g.weight) for g in v.groups if g.weight>0} for v in ob.data.vertices]
    material=[p.material_index for p in ob.data.polygons]
    out['historical'][tag]={'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'face_vertex_order_identical_to_R1B':True,'vertices_world_m':verts,'full_weights':weights,'face_material_indices':material}
    out['data_reads'].append(tag)
    print('Read static',tag,len(verts),'vertices',flush=True)
write('_tmp/anatomy_static_extract.json',out)
assert all(sha(ROOT/k)==h for k,h in before.items())
print('Static extraction complete. Pose evaluations=0; blend writes=0.',flush=True)
