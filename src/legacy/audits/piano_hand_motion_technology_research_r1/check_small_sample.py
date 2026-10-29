"""Read two public visualizer JSON lines, retain schema only; no pickle or code execution."""
from pathlib import Path
import urllib.request,json
P=Path(__file__).resolve().parent
base='https://for-elise.github.io/static_visualizer/data/100/'
req=urllib.request.Request(base+'metadata.json',headers={'User-Agent':'Codex-readonly-research-R1'})
with urllib.request.urlopen(req,timeout=20) as r:
 raw=r.read(65537)
 assert len(raw)<=65536
 meta=json.loads(raw)
(P/'evidence/furelise_demo_100_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
req=urllib.request.Request(base+'motion.json',headers={'User-Agent':'Codex-readonly-research-R1','Range':'bytes=0-131071'})
summary=[];consumed=0
with urllib.request.urlopen(req,timeout=20) as r:
 status=r.status
 for _ in range(2):
  line=r.readline(65537);consumed+=len(line)
  assert len(line)<=65536
  x=json.loads(line)
  summary.append({k:dict(type=type(v).__name__,length=len(v) if hasattr(v,'__len__') else None,inner_length=len(v[0]) if isinstance(v,list) and v and isinstance(v[0],list) else None) for k,v in x.items()})
(P/'SMALL_SAMPLE_ACCESS_CHECK.json').write_text(json.dumps(dict(url=base+'motion.json',http_status=status,bytes_read=consumed,lines_read=2,retained_coordinates=False,schema=summary,note='Web preview exposes vertex frames, not raw 21-joint motion.pkl. No full archive, raw dataset or MANO model downloaded; response closed after two lines.'),indent=2),encoding='utf8')
print('METADATA',meta,'SCHEMA',summary,'BYTES',consumed)
