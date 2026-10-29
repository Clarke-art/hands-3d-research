from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];S5=OUT.parent;H=S5/'human_thumb_kinematic_authority_correction_r1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def canon(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
A=read(S5/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
assert canon({k:v for k,v in A.items() if k!='combined_authority_hash'})==A['combined_authority_hash']=='c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8'
assert A['status']=='HUMAN_APPROVED_FROZEN' and len(A['vertex_ids'])==37 and len(A['face_ids'])==25
B=read(H/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json');P=read(H/'THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json');T=read(H/'HUMAN_THUMB_KINEMATIC_AUTHORITY_CORRECTION_STATUS.json');hs=read(H/'HUMAN_THUMB_KINEMATIC_CORRECTION_HASHES_R1.json')
assert canon({k:v for k,v in B.items() if k!='combined_authority_hash'})==B['combined_authority_hash']==hs['authority_combined_hash']
assert canon({k:v for k,v in P.items() if k!='combined_application_hash'})==P['combined_application_hash']
assert B['status']=='HUMAN_APPROVED' and P['status']=='HUMAN_APPROVED_APPLIED_VERIFIED' and T['THUMB_KINEMATIC_CORRECTION_APPLICATION']=='APPLIED_VERIFIED'
assert sha(ROOT/B['corrected_rig_path'])==hs['corrected_rig']['sha256']=='5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe'
sources={
 'cap_authority':S5/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json',
 'corrected_rig':ROOT/B['corrected_rig_path'],
 'kinematic_authority':H/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json',
 'kinematic_application':H/'THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json',
 'Stage4C_geometry':ROOT/'production_spec/stage4_blender/stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend',
 'native_geometry':ROOT/'production_spec/stage4_blender/stage4a_r2/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend',
 'nail_authority':ROOT/'production_spec/stage4_blender/stage4c_r2/NAIL_AUDIT_R2.json',
 'first_web_membership':S5/'stage5b_r1a/FIRST_WEB_REGION_AUDIT_R1A.json',
 'first_web_human_approval':S5/'stage5b_freeze/STAGE5B_HUMAN_APPROVAL_FREEZE_R1.json',
 'CMC_cage_source':ROOT/'production_spec/stage4_blender/stage4a_r2/CMC_LOCAL_RETOPO_AUDIT_R2.json',
 'CMC_cage_construction':ROOT/'production_spec/stage4_blender/stage4a_r2/R2_CAGE.json',
 'native_partition_evidence':S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/_tmp/native_independent_partition.json',
 'native_thumb_anchor_evidence':S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/NATIVE_THUMB_ANCHOR_SET.json',
 'native_index_anchor_evidence':S5/'stage5b_r1e_thumb_distal_cap_native_branch_identity_audit_r1/NATIVE_INDEX_ANCHOR_SET.json',
 'CLASS_A_geometry':ROOT/'production_spec/stage6_deformation/stage6b_r1a_seam_provenance/STAGE6B_R1A_CLASS_A_VALID_WEB_EDGES.json'}
records={k:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for k,p in sources.items()}
assert records['Stage4C_geometry']['sha256']=='fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7'
assert records['native_geometry']['sha256']==A['native_geometry_hash']
assert records['nail_authority']['sha256']=='0a8388c44792b432512818ea0f8450af8961981df1d487d0ecd5008abc5bcddc'
dump('AUTHORITY_INPUT_VERIFICATION.json',{'cap_verified':True,'cap_vertex_count':37,'cap_face_count':25,'cap_combined_authority_hash':A['combined_authority_hash'],'corrected_kinematic_status':'HUMAN_APPROVED / APPLIED_VERIFIED','corrected_rig_verified':True,'kinematic_combined_authority_hash':B['combined_authority_hash'],'sources':records,'OLD_CAP9':'SUPERSEDED_CONTAMINATED','old_REP':'NOT_AUTHORITY','old_R3_status':'HISTORICALLY_HUMAN_APPROVED; REVALIDATION_REQUIRED_AFTER_CAP_AUTHORITY_CORRECTION','R3_FULL_RECOMPUTE_REQUIRED':True})
external=read(H/'FROZEN_HASHES_BEFORE.json')['external'];files=[p for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts]
dump('FROZEN_HASHES_BEFORE.json',{'workspace':{str(p.relative_to(ROOT)):sha(p) for p in files},'external':{p:sha(Path(p)) for p in external}})
print('AUTHORITY VERIFICATION PASS; protected',len(files),'+',len(external))
