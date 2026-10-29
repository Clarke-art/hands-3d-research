import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'VIDEO_VERIFICATION.json').read_text(encoding='utf8'))
assert all(sha(p/n)==r['sha256'] for n,r in v.items())
(p/'EXPORT_REPAIR.json').write_text(json.dumps({'issue':'PIL cannot write RGBA poster as JPEG','repair':'Poster-only RGB conversion and corrected export script','candidate_unchanged_sha256':sha(p/'SHORT_PHRASE_DESIGN_ONLY_R1.blend'),'all_three_video_hashes_unchanged':True,'new_motion_fit_runs':0,'new_candidates':0},indent=2),encoding='utf8')
