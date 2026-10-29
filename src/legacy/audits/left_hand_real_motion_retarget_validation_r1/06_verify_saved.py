import sys,importlib.util,json,numpy as np
from pathlib import Path
sys.dont_write_bytecode=True;P=Path(__file__).resolve().parent;ROOT=P.parents[1]
spec=importlib.util.spec_from_file_location('identity_reader',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
import bpy
meta=r.read(P/'LEFT_REAL_MOTION_ACTION_R1.json');ob,rig=r.open_asset(ROOT/meta['candidate']);act=rig.animation_data.action
assert act.name==meta['action'];curves=[f for l in act.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
assert len(curves)==64 and all(len(f.keyframe_points)==421 and f.data_path.endswith('.rotation_quaternion') for f in curves)
assert all('TIP' not in f.data_path and '_R"' not in f.data_path for f in curves)
expected=np.load(P/'evaluated_motion.npz')['vertices'];maximum=0.0;exact=True
for i in range(421):
 bpy.context.scene.frame_set(1+i//2,subframe=(i%2)*.5);v,_=r.coords(ob);exact=exact and np.array_equal(v,expected[i]);maximum=max(maximum,float(np.max(np.abs(v-expected[i]))))
assert exact
proof={'status':'PASS','saved_Action':act.name,'quaternion_FCurves':64,'keys_per_FCurve':421,'all_421_evaluated_geometry_exact_after_reopen':exact,'max_difference_m':maximum,'saved_candidate_sha256':r.sha(ROOT/meta['candidate'])}
(P/'SAVED_ACTION_VERIFICATION_R1.json').write_text(json.dumps(proof,indent=2),encoding='utf-8');print('SAVED_421_OBSERVATION_ACTION_EXACT')
