import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PROPOSAL=ROOT/'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'
RESPONSE=Path(r'<USER_HOME>\Downloads\SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T13-24-31-414Z.json')
CORRECTED=ROOT/'production_spec/stage5_production_rig/human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend'
DONOR=ROOT/'production_spec/stage5_production_rig/stage5b_r1b/RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend'
STAGE4=ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend'
CANDIDATE=OUT/'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R1.blend'
PHASE='TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(d):return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def inventory():
    result={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
    previous=read(PROPOSAL/'FROZEN_HASHES_AFTER.json')
    for s in list(previous)+[str(RESPONSE)]:
        p=Path(s)
        if p.is_absolute() and p.is_file():result[str(p)]=sha(p)
    return result
