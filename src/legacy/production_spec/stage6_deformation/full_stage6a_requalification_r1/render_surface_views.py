"""Improve cap/nail visibility using measured bind outward normals, same-camera panels."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
script=Path(__file__).with_name('render_evidence.py')
source=script.read_text(encoding='utf-8')
exec(compile(source.split("for cid,row in E['cases'].items():")[0],str(script),'exec'))
existing=read(OUT/'EVIDENCE_RENDER_MANIFEST_R1.json')
for cid,row in E['cases'].items():
 V=[Vector(v) for v in G['positions_world_m'][cid]];d=row['case']['digit']
 save(cid+'_NAIL_ISOLATED_SOLID.png',V,row['nails'][d]['vertex_ids'],outward_view(row['nails'][d]['face_ids']),face_ids=row['nails'][d]['face_ids'])
 if d=='THUMB' or row['case']['bone']=='INDEX_MCP_R':
  save(cid+'_CAP37_ISOLATED_SOLID.png',V,cap['vertex_ids'],outward_view(cap['face_ids']),face_ids=cap['face_ids'])
updates={r['path']:r for r in manifest}
existing['renders']=[updates.get(r['path'],r) for r in existing['renders']]
oldpaths={r['path'] for r in existing['renders']}
existing['renders'] += [r for r in manifest if r['path'] not in oldpaths]
existing['render_count']=len(existing['renders'])
existing['panel_assembly_pending']=True
existing['cap_nail_view']='Actual context + separate isolated native cap25-face/nail-material patches, explicitly labeled; fixed bind outward normals; no axis/rest/geometry changes.'
dump('EVIDENCE_RENDER_MANIFEST_R1.json',existing)
print('UPDATED CAP/NAIL SURFACE VIEWS',len(manifest),flush=True)
