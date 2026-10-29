"""One read-only inspection, after unchanged visual A/B. No new poses or channel writes."""
import sys,json,hashlib,math,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Quaternion,Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];PREV=ROOT/'audits/pianovam_single_sample_right_hand_retarget_r1'
SOURCE=PREV/'RIGHT_HAND_PIANO_MOTION_TEST_R1.blend'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rotation(q):
 q=q.copy();q.normalize()
 if q.w<0:q.negate()
 e=q.to_euler('XYZ');v=q.to_exponential_map()
 return {'quaternion_WXYZ':list(q),'local_Euler_XYZ_rad':list(e),'local_Euler_XYZ_deg':[math.degrees(x) for x in e],'local_rotation_vector_XYZ_deg':[math.degrees(x) for x in v],'magnitude_deg':math.degrees(q.angle),'axis_local_XYZ':list(q.axis) if q.angle>1e-7 else [0,0,0]}
selection=read(OUT/'FIRST_WEB_DEFECT_FRAME_SELECTION_R1.json');assert sha(SOURCE)==selection['SOURCE_RETARGET']['sha256']
names=['THUMB_CMC_R','THUMB_MCP_R','THUMB_IP_R','INDEX_MCP_R']
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];scene=bpy.context.scene;action=rig.animation_data.action
assert action.name==selection['action']
motion=[]
for row in selection['frames']:
 if row['role']!='DEFECT':continue
 scene.frame_set(row['frame']);bpy.context.view_layer.update()
 motion.append({'frame':row['frame'],'time_sec':row['time_sec'],'human_visible_severity':row['human_visible_severity'],'bones':{name:rotation(rig.pose.bones[name].rotation_quaternion) for name in names}})
# The prior Human-approved fixture definitions are read, never applied to the rig.
spec=importlib.util.spec_from_file_location('approved_fixture_metadata',ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
axis_doc=ROOT/'production_spec/stage6_deformation/stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json';axis=Vector(read(axis_doc)['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ']).normalized()
approval=read(ROOT/'production_spec/right_hand_product_baseline_r1/SOURCE_HUMAN_APPROVAL_BIND_R1.json');assert approval['HUMAN_APPROVED']=='YES'
reference=[]
for c in m.CASES:
 if c['case_id']=='ZERO':continue
 qs={name:Quaternion() for name in names}
 if c['case_id']=='INDEX_MCP_45':qs['INDEX_MCP_R']=Quaternion((1,0,0),math.radians(c['applied_rotation_deg']))
 else:
  qs['THUMB_CMC_R']=Quaternion(axis,math.radians(c['cmc_deg']))
  qs['THUMB_MCP_R']=Quaternion((1,0,0),math.radians(-c['mcp_deg']))
  qs['THUMB_IP_R']=Quaternion((1,0,0),math.radians(-c['ip_deg']))
 reference.append({'case_id':c['case_id'],'fixture_parameters':c,'bones':{name:rotation(q) for name,q in qs.items()}})
component_ranges={name:{'reference_Euler_XYZ_deg_min':[min(r['bones'][name]['local_Euler_XYZ_deg'][j] for r in reference) for j in range(3)],'reference_Euler_XYZ_deg_max':[max(r['bones'][name]['local_Euler_XYZ_deg'][j] for r in reference) for j in range(3)],'motion_defect_Euler_XYZ_deg_min':[min(r['bones'][name]['local_Euler_XYZ_deg'][j] for r in motion) for j in range(3)],'motion_defect_Euler_XYZ_deg_max':[max(r['bones'][name]['local_Euler_XYZ_deg'][j] for r in motion) for j in range(3)],'reference_magnitude_deg_min':min(r['bones'][name]['magnitude_deg'] for r in reference),'reference_magnitude_deg_max':max(r['bones'][name]['magnitude_deg'] for r in reference),'motion_magnitude_deg_min':min(r['bones'][name]['magnitude_deg'] for r in motion),'motion_magnitude_deg_max':max(r['bones'][name]['magnitude_deg'] for r in motion)} for name in names}
out={'inspection_reason':'Selected-frame corrective off leaves visibly unchanged first-web defect; user Case B','inspection_count':1,'SOURCE_RETARGET':selection['SOURCE_RETARGET'],'action':action.name,'MOTION_WINDOW':selection['MOTION_WINDOW'],'pose_channels_written':0,'new_pose_applied':False,'frames':motion,'Human_approved_reference_poses':reference,'reference_authority':'production_spec/right_hand_product_baseline_r1/SOURCE_HUMAN_APPROVAL_BIND_R1.json','reference_definition_sources':['audits/official_l1_first_web_targeted_deformation_fix_r1/common.py','audits/official_l1_product_rebase_feasibility_r1/common.py',axis_doc.relative_to(ROOT).as_posix()],'CMC_reference_local_axis':list(axis),'rough_component_summary':component_ranges,'interpretation_scope':'Rough comparison to five sampled Human-approved representative fixtures only. Component spans are descriptive; not a continuous validated ROM, angle authority, anatomical limit or proof of impossible movement. Quaternion/rotation-vector directions included to avoid treating Euler spans alone as physical limits.','ROM_qualification_performed':False,'stress_cases_rendered_or_run':False,'source_sha_after':sha(SOURCE)}
assert out['source_sha_after']==selection['SOURCE_RETARGET']['sha256']
(OUT/'FIRST_WEB_DEFECT_ROTATION_COMPARISON_R1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
for name,value in component_ranges.items():print(name,json.dumps(value),flush=True)
