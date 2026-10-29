import sys,json,numpy as np
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent
read=lambda n:json.loads((O/n).read_text(encoding='utf8'))
front=read('candidate_front_RESULT.json');right=read('candidate_right_RESULT.json');proof=read('R2_INITIALIZER_IDENTITY_CHECK.json')
assert np.array_equal(np.asarray(front['latents'],np.float32),np.asarray(right['latents'],np.float32))
proof['status']='ROUND_OFF_EQUIVALENT_DETERMINISTIC_INITIALIZERS';proof['float32_control_identity']=True;proof['canonical_preview_controls']='Use solver-returned bound-interior initialization for both diagnostics; right was not solved and no trajectory is accepted';proof['max_double_precision_difference']=proof['max_difference']
(O/'R2_INITIALIZER_IDENTITY_CHECK.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
right['deterministic_reconstructed_preview']=right['latents'];right['latents']=front['latents'];right['canonical_preview_from_front_after_roundoff_identity_check']=True
(O/'candidate_right_RESULT.json').write_text(json.dumps(right,indent=2),encoding='utf8')
print('PREVIEW_CANONICALIZED_FOR_FAILED_DIAGNOSTIC_ONLY',flush=True)
