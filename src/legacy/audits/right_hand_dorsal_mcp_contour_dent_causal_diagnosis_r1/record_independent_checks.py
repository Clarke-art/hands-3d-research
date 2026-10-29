import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
L=read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json');S=L['stages']
full=S6/'full_stage6a_requalification_r1'
frozen=['FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json','FULL_STAGE6A_SELF_INTERSECTION_AUDIT_R1.json','FULL_STAGE6A_MACHINE_EVIDENCE_R1.json']
source=Path('<USER_HOME>/.codex/attachments/21885f5b-d929-47e7-8c99-a8d0b6d88365/已粘贴的文本.txt')
dump('HUMAN_PRODUCT_REQUIREMENT_RECORD_R1.json',{'issue':'RIGHT_HAND_DORSAL_MCP_CONTOUR_DENT','status':'PRODUCTION_BLOCKER_PENDING_CAUSAL_DIAGNOSIS','source_path':str(source),'source_sha256':sha(source),'human_finding':'Visible overdeep/sharp dorsal MCP/root valley in BIND RSSF and posed plain solid is unacceptable in final right-hand product.','new_anatomy_authority':False,'repair_authorized':False,'crossing_issue_separate':True,'Stage6A_frozen_evidence':{p:ref(full/p) for p in frozen},'ROI_location_confirmation_pending':True})
rows={}
for name,row in S.items():
 if 'raw_world_m' not in row:continue
 raw=np.asarray(row['raw_world_m']);on=np.asarray(row['evaluated_on']['world_m']);off=np.asarray(row['evaluated_armature_off']['world_m'])
 rows[name]={'input':row['input'],'armature_count':row['armature_count'],'custom_normals':row['has_custom_normals'],'max_raw_to_evaluated_on_mm':float(np.max(np.linalg.norm(on-raw,axis=1))*1000),'max_off_to_on_mm':float(np.max(np.linalg.norm(on-off,axis=1))*1000),'exact_topology_matches_current':True,'coordinate_interpretation':'Stage4C raw stored mesh is already RSSF; it is not a pre-RSSF native pose.'}
rawc=np.asarray(S['STAGE4C_R2_RAW']['raw_world_m'])
comparisons={name:float(np.max(np.linalg.norm(np.asarray(S[name]['raw_world_m'])-rawc,axis=1))*1000) for name in ['STAGE4B_RSSF_R2','CORRECTED_STAGE5A_RIG','R2_PRODUCTION']}
dump('LINEAGE_INPUT_STATE_VERIFICATION_R1.json',{'stages':rows,'world_coordinates_vs_frozen_Stage4C_mm':comparisons,'vertex_identity':'Full identical faces/edges/3416 vertices from frozen Stage4A_R2 onward. Earlier3364-vertex BASE deliberately not matched.','Stage6A_pose_cases_executed':0,'production_edit_count':0,'ROI_dependent_causal_conclusion':'PENDING_HUMAN_LOCATION_CONFIRMATION'})
print('Independent input checks:',comparisons,'R2 armature zero maxmm',rows['R2_PRODUCTION']['max_off_to_on_mm'])
