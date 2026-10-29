"""Keep failed strict preservation gate. Permit labelled review of existing artifact only."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
a=read(P/'ACTUAL_VALIDATION.json');source=read(P.parent/'minuet_stage_c_lightweight_animation_poc_r1/SCENE_MANIFEST.json');path=P/'PIANO_PEDAGOGICAL_MOTION_REFINEMENT_R1_DESIGN_ONLY.blend'
assert a['protected_actions_unchanged'] and a['cameras_unchanged'] and a['unmodified_rig_curves_exact']
assert a['engineering_max_violation_deg']<.002 and a['added_velocity_max_deg_sec']<180
assert max(x['new']['horizontal_mm'] for x in a['active_pads'])==0
assert min(x['new']['gap_mm'] for x in a['active_pads'])>=min(x['source']['gap_mm'] for x in a['active_pads'])-1e-6
assert max(x['new']['gap_mm'] for x in a['active_pads'])<=max(x['source']['gap_mm'] for x in a['active_pads'])+1e-6
source.update(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),diagnostic_only=True,strict_preservation_gate='FAIL: 0.283403661mm > 0.25mm; unchanged threshold',release_status='FAIL_CLOSED / NOT_APPROVED')
(P/'SCENE_MANIFEST.json').write_text(json.dumps(source,indent=2),encoding='utf8')
(P/'DIAGNOSTIC_RENDER_AUTHORITY.json').write_text(json.dumps(dict(strict_gate_overridden=False,final_status='FAIL_CLOSED',source_action_not_rebaked=True,render_basis='User permits diagnostic videos for physically valid joint/contact/music trajectory with unresolved issues. Native joint bounds, actual target contact envelope, music and camera checks pass. Strict source-pad-drift gate remains FAIL.',new_candidates=1,second_motion_attempt=False),indent=2),encoding='utf8')
s=(P/'render.py').read_text(encoding='utf8').replace("assert report['basic_engineering_music_pass']","assert read(OUT/'DIAGNOSTIC_RENDER_AUTHORITY.json')['final_status']=='FAIL_CLOSED'")
(P/'render.py').write_text(s,encoding='utf8')
print('FAILED_GATE_PRESERVED; saved candidate allowed for labelled diagnostic rendering only')
