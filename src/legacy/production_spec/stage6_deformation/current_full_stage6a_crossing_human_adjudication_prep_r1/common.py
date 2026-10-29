import sys
sys.dont_write_bytecode = True
import json, hashlib, ast
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
S5 = ROOT / 'production_spec/stage5_production_rig'
S6 = ROOT / 'production_spec/stage6_deformation'
PHASE = 'CURRENT_FULL_STAGE6A_CROSSING_HUMAN_ADJUDICATION_PREP_R1'
CAP_PATH = S5/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json'
R3_PATH = ROOT/'audits/human_r3_fresh_result_authority_freeze_r1/FRESH_R3_OWNERSHIP_AUTHORITY_R1.json'
CORRECTED = S5/'human_thumb_kinematic_authority_correction_r1/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend'
CAND = S5/'geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend'
HUMAN = S5/'targeted_deformation_final_human_closure_r1/TARGETED_DEFORMATION_FINAL_HUMAN_CLOSURE_R1.json'
FEAS = S5/'stage5b_r1e_feasibility_audit'
SENS = S5/'stage5b_r1e_endpoint_authority_review'
DEP = S5/'stage5b_r1e_cap_dependency_blast_radius_audit_r1'
EXPECTED_CAP = 'c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
EXPECTED_R3 = '361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0'
EXPECTED_MEMBER = 'f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d'
EXPECTED_RIG = '5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'
EXPECTED_CAND = 'd8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d'
EXPECTED_WEIGHTS = '1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(d): return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def digest(d): return hashlib.sha256(canon(d)).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def dump(name,d):
    p=OUT/name; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ref(p): return {'path':Path(p).relative_to(ROOT).as_posix(),'sha256':sha(p)}
def reuse(path,names,ns):
    tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes}==set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
    return {'source':ref(path),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes}}
def inventory(): return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}

HIST=S6/'full_stage6a_requalification_r1'
TARGETED=S5/'targeted_deformation_revalidation_after_donor_transfer_r1'
OLD_CAND=S5/'targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
APPROVED54=[738,2237,2238,2276,2328,2330]+list(range(3300,3348))

FRESH=S6/'full_stage6a_requalification_after_donor_transfer_r1'
REVIEW_ID='CURRENT_FULL_STAGE6A_CROSSING_HUMAN_REVIEW_R1'
