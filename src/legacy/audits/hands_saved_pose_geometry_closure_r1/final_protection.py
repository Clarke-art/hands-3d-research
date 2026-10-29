import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
merged={}
for name in ['INPUT_SHA_BEFORE.json','SUPPLEMENT_INPUT_SHA.json','OFFLINE_INPUT_SHA.json','CERTIFICATE_INPUT_SHA.json']:
    for p,h in read(O/name).items():
        if p in merged:assert merged[p]==h,'INPUT_CHANGED_BETWEEN_STAGES'
        merged[p]=h
after={p:sha(path(p)) for p in merged};assert after==merged,'INPUT_CHANGED'
previous=read(R2/'FINAL_PROTECTION_READBACK.json')
assert sha(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz')==previous['original_actual_skin_snapshot_sha256']
historic={p:dict(previous=h,current=after[p],match=h==after[p]) for p,h in previous['input_sha256_after'].items() if p in after}
assert all(x['match'] for x in historic.values())
codes={p.name:sha(p) for p in O.glob('*.py')}
cert=read(O/'DEPTH_CERTIFICATE_READBACK.json');result=read(O/'FINAL_GEOMETRY_RESULT.json')
assert cert['pass_'] and result['RESULT']=='STATIC_GEOMETRY_CLOSED'
dump('FINAL_PROTECTION.json',dict(pass_=True,actual_referenced_historical_files=len(merged),before_sha256=merged,after_sha256=after,all_unchanged=True,
    cached_real_skin_matches_R2_receipt=True,available_R2_historical_matches=historic,current_diagnostic_code_sha256=codes,
    corrected_poses_applied=0,optimizer_calls=0,blender_supplement_launches=1,piano_access=False))
print('FINAL_PROTECTION_PASS',len(merged),'cert_gap_mm',cert['max_stored_interval_width_mm'],flush=True)
