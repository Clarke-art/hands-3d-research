import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,urllib.request
AUD=Path(__file__).resolve().parents[1];ROOT=AUD.parents[2]
for d in ['references','renders','_tmp']: (AUD/d).mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted((ROOT/'production_spec').rglob('*')) if p.is_file() and AUD not in p.parents}
before.update({str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (ROOT/'docs').rglob('*') if p.is_file()})
if (AUD/'FROZEN_HASHES_BEFORE.json').exists():
    prior=json.loads((AUD/'FROZEN_HASHES_BEFORE.json').read_text(encoding='utf-8'));assert all(before[k]==h for k,h in prior.items())
else:(AUD/'FROZEN_HASHES_BEFORE.json').write_text(json.dumps(before,indent=1),encoding='utf-8')
print('Protected files before:',len(before),flush=True)
for name,url in [('human_right_front_back.jpg','https://upload.wikimedia.org/wikipedia/commons/3/32/Human-Hands-Front-Back.jpg'),('male_both_sides.jpg','https://upload.wikimedia.org/wikipedia/commons/7/7e/Hand_male_both_sides.jpg'),('right_hand_palm.png','https://upload.wikimedia.org/wikipedia/commons/d/d0/Right_Hand_Palm.png'),('clinical_web_oblique.jpg','https://1.bp.blogspot.com/-sSZPtYy0HJs/XzAg5ikjxrI/AAAAAAAAdWY/RUAsf6TkfbUD4LqVNojSQD1GesTBRgcoQCLcBGAsYHQ/s2048/IMG_3345.JPG')]:
    p=AUD/'references'/name
    if not p.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'AnatomicalReferenceReview/1.0 (local educational research)'})
        with urllib.request.urlopen(req,timeout=30) as r:p.write_bytes(r.read())
    print(name,p.stat().st_size,sha(p),flush=True)
