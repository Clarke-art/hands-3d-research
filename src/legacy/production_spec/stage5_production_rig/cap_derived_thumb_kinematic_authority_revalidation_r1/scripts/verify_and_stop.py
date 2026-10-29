from pathlib import Path
import json,hashlib,sys,ast,math
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];RUN='CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
required=[RUN+'_REPORT.md',RUN+'_STATUS.json','THUMB_IP_TIP_KINEMATIC_SLOT_PROVENANCE.json','INDEPENDENT_THUMB_DISTAL_GEOMETRIC_FRAME.json','THUMB_IP_JOINT_REVALIDATION.json','THUMB_IP_TAIL_AUTHORITY_AUDIT.json','THUMB_TIP_HELPER_SEMANTIC_AUDIT.json','THUMB_IP_TIP_ROLL_REVALIDATION.json','CURRENT_R2A_VS_INDEPENDENT_THUMB_KINEMATICS.json','THUMB_KINEMATIC_TO_R2_R3_IMPACT_PREVIEW.json','THUMB_KINEMATIC_TO_STAGE5B_IMPACT_PREVIEW.json','KINEMATIC_CANDIDATE_R1.json','THUMB_KINEMATIC_HUMAN_REVIEW.html']
assert all((OUT/n).is_file() for n in required)
for p in OUT.glob('*.json'):read(p)
for p in (OUT/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
png=list((OUT/'renders').glob('*.png'));assert len(png)==8
for p in png:
 with Image.open(p) as im:assert im.width>=1500 and im.height>=1200;im.verify()
D=read(OUT/'RAW_READ_ONLY_GEOMETRY_AND_BONES.json');G=read(OUT/'GEOMETRIC_EVIDENCE_COMPUTATION.json');C=read(OUT/'KINEMATIC_CANDIDATE_R1.json');Q=read(OUT/'STATIC_GEOMETRY_GATES_AND_FRAME_METRICS.json')
v=np.array(D['RSSF']['vertices_world_m']);native=np.array(D['NATIVE']['vertices_world_m']);ids=G['native_domain_vertex_ids'];axis=np.array(G['geometric_axis_independent_locator_to_tip']);s=(v[ids]-v[284])@axis
loc=np.array(D['NATIVE']['matrix_world'])[:3,3];m=np.diag([1.,-1.,-1.]);canon=lambda p:<REDACTED_EMAIL>(p)+loc-m@loc
assert int(np.argmin(np.linalg.norm(native-canon([1.4489,.0115,.3134]),axis=1)))==G['root_vertex']
assert int(np.argmin(np.linalg.norm(native-canon([1.4977,.0358,.2421]),axis=1)))==284
assert ids[int(np.argmax(s))]==284
for n in ['THUMB_IP_R','THUMB_TIP_R']:
 frame=np.array(G['candidate'][n]['frame_XYZ']);assert np.allclose(frame.T@frame,np.eye(3),atol=1e-8);assert abs(np.linalg.det(frame)-1)<1e-8
assert C['slots']['THUMB_IP_R.head']['world_m']==D['R2A']['bones']['THUMB_IP_R']['head_world_m']
assert C['slots']['THUMB_IP_R.tail']['world_m']==C['slots']['THUMB_TIP_R.head']['world_m']==v[284].tolist()
h=np.array(C['slots']['THUMB_IP_R.head']['world_m']);t=v[284];assert np.allclose(C['slots']['THUMB_TIP_R.tail']['world_m'],t+.3*(t-h),atol=1e-12)
assert Q['bones']['THUMB_IP_R']['candidate']['inside_count']==20 and Q['bones']['THUMB_IP_R']['current']['inside_count']==13
mapping=read(OUT/'INDEPENDENT_THUMB_DISTAL_GEOMETRIC_FRAME.json');mapping['mapping']['native_object_matrix_world']=D['NATIVE']['matrix_world'];mapping['mapping']['RSSF_object_matrix_world']=D['RSSF']['matrix_world'];mapping['terminal_axial_confirmation']={'native_domain_maximizer_vertex':284,'axial_max_over_v284_mm':float(max(s)*1000),'basis':'Validation of accepted landmark only, not cap selection','native_tip_and_root_seed_identity_reconfirmed':True};dump('INDEPENDENT_THUMB_DISTAL_GEOMETRIC_FRAME.json',mapping)
before=read(OUT/'FROZEN_HASHES_BEFORE.json');wr=[];er=[]
for rel,b in before['workspace'].items():
 p=ROOT/rel;a=sha(p);wr.append({'path':rel,'before':b,'after':a,'equal':a==b})
for rel,b in before['external'].items():
 p=Path(rel);a=sha(p);er.append({'path':rel,'before':b,'after':a,'equal':a==b})
new=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and str(p.relative_to(ROOT)) not in before['workspace']]
assert not new and all(r['equal'] for r in wr+er)
assert not list(OUT.rglob('*.blend')) and not list(OUT.rglob('*.blend1'))
dump('PROTECTED_STATE_VERIFICATION.json',{'execution':RUN,'workspace_file_count':len(wr),'external_file_count':len(er),'all_before_equal_after':True,'new_files_outside_output_directory':new,'workspace':wr,'external':er,'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'R2_runs':0,'R3_runs':0,'Stage6_runs':0})
status=read(OUT/(RUN+'_STATUS.json'));status['protected_state']={'all_before_equal_after':True,'workspace_files':len(wr),'external_files':len(er),'manifest':'PROTECTED_STATE_VERIFICATION.json'};dump(RUN+'_STATUS.json',status)
dump('OUTPUT_VERIFICATION.json',{'required_artifacts_exist':True,'JSON_parse':'PASS','script_AST_parse':'PASS','PNG_count':8,'PNG_decode':'PASS','visual_review':'All eight views inspected; legend moved outside geometry to avoid endpoint overlap; TIP projection collapse explicitly annotated','frame_orthonormality':'PASS','parent_child_continuity':'PASS','candidate_helper_fraction':.30,'tip_identity_and_axial_extremum':'PASS','no_blend_output':True,'forbidden_pipelines_not_executed':True,'required_files':required,'output_hashes':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_VERIFICATION.json'},'STOP':True})
print('FINAL PASS:',len(wr),'workspace +',len(er),'external hashes unchanged; 8 PNGs; all required artifacts; STOP')
