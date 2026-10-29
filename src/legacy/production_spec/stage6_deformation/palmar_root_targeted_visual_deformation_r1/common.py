import sys
sys.dont_write_bytecode=True
import json,hashlib,ast,math
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
S5=ROOT/'production_spec/stage5_production_rig'
S6=ROOT/'production_spec/stage6_deformation'
DESIGN=ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1'
PHASE='PALMAR_ROOT_TARGETED_VISUAL_DEFORMATION_R1'
FILES={'PRE_PALMAR':S5/'geometry_propagation_after_donor_transfer_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_GEOMETRY_R1.blend','REPAIRED_PALMAR':S5/'geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'}
EXPECTED={'PRE_PALMAR':'d8ea48d5d09635a46aebabb7a6e516f2a2a8599c92f2ca68489cdbeb0ec6866d','REPAIRED_PALMAR':'90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa'}
REQUEST=Path('<USER_HOME>/.codex/attachments/d0c0375d-4c83-446b-b63c-b85ed7f5df3f/已粘贴的文本.txt')
WEIGHT_HASH='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
CASES=['MID_MCP_15','MID_MCP_30','MID_MCP_45']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def inventory():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse(p,names,ns):
 nodes=[n for n in ast.parse(Path(p).read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
 return {'source':ref(p),'function_AST_sha256':{n.name:digest(ast.dump(n)) for n in nodes},'top_level_executed':False}
if __name__=='__main__':
 dump('PROTECTED_HISTORY_HASHES_BEFORE.json',inventory())
 assert all(sha(p)==EXPECTED[k] for k,p in FILES.items())
 (OUT/'USER_REQUEST_ORIGINAL.txt').write_bytes(REQUEST.read_bytes())
 matrix=S6/'full_stage6a_requalification_r1/FULL_STAGE6A_CASE_MATRIX_R1.json'
 cases=[c for c in read(matrix)['cases'] if c['case_id'] in CASES]
 assert [c['case_id'] for c in cases]==CASES
 assert all(c['bone']=='MIDDLE_MCP_R' and c['axis']=='bone_local_X' and c['sign']==-1 and c['applied_rotation_deg']==-c['angle_deg'] for c in cases)
 dump('AUTHORIZED_THREE_POSES_R1.json',{'case_definitions':cases,'source':ref(matrix),'distinct_pose_count':3,'applications_per_asset':3,'asset_count':2,'other_pose_authorization':False})
 floor=read(S6/'full_stage6a_requalification_r1/FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')['thresholds']
 dump('MINIMUM_SAFETY_PROCEDURE_R1.json',{'product_acceptance':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','user_authority':ref(REQUEST),'automatic_gates':{k:floor[k] for k in ['severe_bind_mm_ge','severe_ratio_gt','zero_mm','collapse_area_m2_le','collapse_ratio_le','degenerate_edge_m_le']},'threshold_source':ref(S6/'full_stage6a_requalification_r1/FULL_STAGE6A_MACHINE_EVIDENCE_R1.json'),'visible_penetration_and_neighbor_gross_contamination':'Direct inspection of matched full / root close / alternate / grazing ordinary solid renders; no hidden-triangle census or normal-dot audit. Final Human visual authority retained.','minor_compression_crease_low_poly_style_are_not_automatic_blockers':True,'static_skin_truecap_R3_2127_normal_dot_impact_Full42_runs':0})
 dump('INPUT_HASH_AND_SCOPE_R1.json',{'status':'PASS','inputs':{k:ref(p) for k,p in FILES.items()},'new_user_acceptance_policy_applies_this_phase':True,'historical_closed_reports_not_rewritten':True,'minimum_safety_only':True,'full42_or_impact_audit_not_required_before_this_user_authorized_phase':True})
 print('Two actual assets verified; only MID MCP15/30/45 localX -1; visual-first policy recorded.')
