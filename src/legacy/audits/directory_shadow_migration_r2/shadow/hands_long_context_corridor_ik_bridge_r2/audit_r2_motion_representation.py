from bridge_model import *
import hashlib
diff=Q1-Q0;support=[]
for finger,name in enumerate(c.DIGITS):
 if finger==0:control='4 independent thumb engineering controls'
 elif finger==I['next']['finger']-1:control='lambda reference interpolation plus alpha preparing flex'
 else:control='lambda reference interpolation only; no independent digit flex controls'
 support.append(dict(finger=finger+1,digit=name,reference_difference_deg=diff[finger].tolist(),current_control_support=control))
facts=json.loads((O/'R2_FINAL_FACTS.json').read_text(encoding='utf8'));save('R2_MOTION_REPRESENTATION_AUDIT.json',dict(authority='DESIGN_PROVISIONAL — STOP — HUMAN REVIEW',frozen_Rig_has_hand_joint_controls=20,implemented_family_latents=12,source_mapping='rig_model.py:state(z)',support=support,passive_INDEX_flex_reference_difference=diff[1,:3].tolist(),passive_INDEX_flex_can_be_independently_lifted=False,worst_actual_preview_failure=facts['worst_keys'],conclusion='The interface cannot independently prepare INDEX within this reference family. Different palm routes may still avoid the collision; no proof of all-path or human/fingering impossibility.',domain_or_reference_family_not_expanded=True))
for r in support:print(r['digit'],r['current_control_support'],r['reference_difference_deg'],flush=True)
