import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
S5=OUT.parent
PRIOR=S5/'joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1'
src=(PRIOR/'common.py').read_text(encoding='utf-8').split("if __name__=='__main__':")[0]
src=src.replace("PROP=S5/'geometry_propagation_after_donor_transfer_r1'", "PROP=S5/'geometry_propagation_after_palmar_donor_restoration_r1'\nOLD=S5/'geometry_propagation_after_donor_transfer_r1'\nPRIOR=S5/'joint_surface_rest_zero_bind_revalidation_after_donor_transfer_r1'\nIDS=list(range(3348,3364))")
src=src.replace("APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1'", "APP=ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_palmar_root_r1'")
src=src.replace('JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1','JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_PALMAR_DONOR_RESTORATION_R1')
start=src.index('FILES=');end=src.index('WEIGHT_HASH=')
src=src[:start]+'''FILES={'STAGE4':APP/'RIGHT_HAND_ENGINEERING_STAGE4C_DONOR_TRANSFER_PALMAR_ROOT_R1.blend','CORRECTED':PROP/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_PALMAR_ROOT_R1.blend','R2':PROP/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend','OLD_CORRECTED':OLD/'RIGHT_HAND_STAGE5A_CORRECTED_RIG_DONOR_TRANSFER_R1.blend','OLD_R2':OLD/'RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'}
EXPECTED={'STAGE4':'0c1831042151a40f87f3779b97ece94cfc29a7831babfa1dda64c9ac0f4ae9c6','CORRECTED':'b7a4fe408ba979ee41f72b1a62e25b7ce292da42da561dc47bbc65b9475d6b8e','R2':'90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa','OLD_CORRECTED':'513323c98a0d2a1c3b45f5543c6738476af7090447e84a0cc510d6e9606adc62','OLD_R2':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d'}
'''+src[end:]
(OUT/'common.py').write_text(src,encoding='utf-8')
sys.path.insert(0,str(OUT))
from common import *
dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
(OUT/'payload.py').write_bytes((PROP/'payload.py').read_bytes())
(OUT/'recover_semantics.py').write_bytes((PRIOR/'recover_semantics.py').read_bytes())
request=Path('<USER_HOME>/.codex/attachments/e2133d61-e03c-4336-b534-55ce628cb096/已粘贴的文本.txt')
(OUT/'USER_PHASE_SCOPE_ORIGINAL.txt').write_bytes(request.read_bytes())
dump('PHASE_INPUT_HASH_RECOVERY_R1.json',{'status':'PASS','inputs':{k:ref(p) for k,p in FILES.items()},'prior_pass':ref(PRIOR/'JOINT_SURFACE_REST_ZERO_BIND_REVALIDATION_AFTER_DONOR_TRANSFER_R1_STATUS.json'),'payload_reader':ref(PROP/'payload.py'),'user_scope':ref(request)})
r=(PRIOR/'revalidate.py').read_text(encoding='utf-8')
r=r.replace("prior_diag=read(PROP/'CORRECTED_JOINT_SURFACE_DELTA_DIAGNOSTIC_R1.json')['measurements']", "prior_diag=[]")
r=r.replace("read(PROP/'STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json')", "read(PROP/'PALMAR_STAGE5A_GEOMETRY_PROPAGATION_AUDIT_R1.json')")
r=r.replace("read(APP/'APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')", "read(APP/'PALMAR_APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')")
(OUT/'revalidate.py').write_text(r,encoding='utf-8')
print('All five actual input hashes verified; fresh phase directory only.')
