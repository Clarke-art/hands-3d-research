import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
rows=[]
for path in sorted(ROOT.rglob('*.blend')):
    if path==OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend':continue
    try:
        with bpy.data.libraries.load(str(path),link=False) as (src,dst):
            rows.append({'path':path.relative_to(ROOT).as_posix(),'actions':list(src.actions),'armatures':list(src.armatures),'read_mode':'Library datablock names only; no mesh evaluation or save'})
    except Exception as e:rows.append({'path':path.relative_to(ROOT).as_posix(),'error':str(e)})
(OUT/'LOCAL_BLEND_MOTION_INVENTORY_R1.json').write_text(json.dumps({'files':rows,'file_count':len(rows),'files_with_actions':[r for r in rows if r.get('actions')],'source_files_modified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('MOTION_LIBRARY_INVENTORY',len(rows),'WITH_ACTIONS',[(r['path'],r['actions']) for r in rows if r.get('actions')],flush=True)
