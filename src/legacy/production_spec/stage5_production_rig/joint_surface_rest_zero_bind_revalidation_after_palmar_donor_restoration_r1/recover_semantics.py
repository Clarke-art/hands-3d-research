from common import *
def legacy_receipt(p):
 text=Path(p).read_text(encoding='utf-8-sig')
 try:return json.loads(text),'strict JSON'
 except json.JSONDecodeError:
  # The frozen historical receipt contains parenthesized adjacent string literals.
  # Parse only literal structure; never execute it or repair the historical file.
  class Constants(ast.NodeTransformer):
   def visit_Name(self,n):
    assert n.id in ('true','false','null')
    return ast.copy_location(ast.Constant({'true':True,'false':False,'null':None}[n.id]),n)
  tree=Constants().visit(ast.parse(text,mode='eval'))
  return ast.literal_eval(tree),'safe literal AST; frozen JSON-labeled receipt uses parenthesized string concatenation'
sources={
 'R2_joint_table':S5/'stage5a_r2/STAGE5A_R2_PRODUCTION_JOINT_TABLE.json',
 'R2_audit':S5/'stage5a_r2/scripts/stage5a_r2_audit.py',
 'carry_forward_region_rules':S5/'stage5a/scripts/stage5a_audit.py',
 'R2A_audit':S5/'stage5a_r2a/scripts/s5a_r2a_audit.py',
 'R2A_reconciliation':S5/'stage5a_r2a/STAGE5A_R2A_AUTHORITY_RECONCILIATION_REPORT.md',
 'R2A_method_errata':S5/'stage5a_r2b/STAGE5A_R2A_DISTAL_CAP_METHOD_ERRATA.md',
 'freeze_receipt':S5/'stage5a_freeze/STAGE5A_HUMAN_APPROVAL_FREEZE_R1.json',
 'thumb_chord_amendment':S5/'stage5a_freeze/STAGE5A_THUMB_DISTAL_CHORD_GATE_AMENDMENT_R1.md',
 'corrected_thumb_authority':S5/'human_thumb_kinematic_authority_correction_r1/THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json',
 'corrected_thumb_application':S5/'human_thumb_kinematic_authority_correction_r1/THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json',
 'corrected_thumb_tip_contract':S5/'cap_derived_thumb_kinematic_authority_revalidation_r1/THUMB_TIP_HELPER_SEMANTIC_AUDIT.json',
 'corrected_thumb_native_mapping':S5/'cap_derived_thumb_kinematic_authority_revalidation_r1/GEOMETRIC_EVIDENCE_COMPUTATION.json',
 'four_finger_accepted_reference':S5/'stage5a_r2a/FOUR_FINGER_TIP_REFERENCE.json',
 'wrist_region':S5/'stage5a_r2/STAGE5A_R2_WRIST_PROFILE.json',
 'CMC_region':ROOT/'production_spec/stage4_blender/stage4a_r2/R2_CAGE.json',
 'T01_regions':ROOT/'production_spec/stage4_blender/stage4a_t01/T01_FINAL_AUDIT.json',
 'frozen_axial_frames':ROOT/'production_spec/stage4_blender/stage4c_r2/STAGE4B_R2_JOINT_FRAME.json',
 'zero_procedure':ROOT/'production_spec/stage6_deformation/stage6a/scripts/s6a_common.py',
 'original_bind_threshold':S5/'stage5b_r1/scripts/s5b_r1_audit.py',
 'R1B_bind_threshold':S5/'stage5b_r1b/scripts/s5b_r1b_verify.py',
 'current_R2_zero_consumer':ROOT/'production_spec/stage6_deformation/full_stage6a_requalification_r1/run_cases.py'}
freeze,parse=legacy_receipt(sources['freeze_receipt']);assert freeze['PRODUCTION_BONE_COUNT']==21 and freeze['STAGE5A_HUMAN_REVIEW']=='APPROVED'
correction=read(sources['corrected_thumb_authority']);assert correction['status']=='HUMAN_APPROVED' and correction['old_cap_REP_authority']=='SUPERSEDED_CONTAMINATED; NOT_AUTHORITY'
joints=read(sources['R2_joint_table'])['joints'];t01=read(sources['T01_regions']);frames=read(sources['frozen_axial_frames'])['bones']
four=read(sources['four_finger_accepted_reference'])['fingers'];wrist=read(sources['wrist_region']);cage=read(sources['CMC_region'])
regions={**t01['T01_MCP'],**t01['OTHER_T01_JOINTS']}
rules={}
for name,row in joints.items():
 rule={'name':name,'role':'NON_DEFORM_TIP_HELPER' if '_TIP_' in name else 'DEFORM_JOINT_HEAD','inside_required':'_TIP_' not in name,
 'coordinate_authority':'Actual corrected rig native stored head/tail/matrices/roll; previous R2/R2A coordinate authority only where not superseded',
 'historical_current_requalification_lineage':row['authority'],'ray_parity_semantics':None if '_TIP_' in name else {'directions':64,'distribution':'golden-angle 2.399963229728653*k; z=1-2*(k+0.5)/64','max_crossings':48,'ray_distance_m':1.0,'after_hit_step_m':2e-7,'inside_gate':'odd crossing votes > 32 / 64','source':'R2_audit::parity'},
 'nearest_surface_semantics':'Actual raw Blender closest_point_on_mesh; native polygon ID, local normal transformed to world; parity defines deform inside independently of normal sign'}
 if name=='WRIST_R':
  rule['region']={'type':'FROZEN_WRIST_PALM_TRANSITION','approved_world_m':wrist['selected']['candidate'],'approved_s_mm':wrist['selected']['s_transition_mm'],'s_band_mm':[wrist['selected']['s_transition_onset_mm'],wrist['selected']['s_palm_body_entry_mm']],'e_long':wrist['frame']['e_long'],'historical_authority':'Stage5A R2; decoupled from object origin','locator_rerun':False}
 elif name=='THUMB_CMC_R':
  rule['region']={'type':'FROZEN_CMC_LOCALITY_SPHERE','anchor_native_vertex':cage['cmc_vertex'],'radius_mm':max(cage['locality']['euclidean_radius_mm']),'authority':'R2 approved CMC cage locality, not earliest R1 surface-anchor joint','clearance_rule':'Report actual current surface clearance; no newly imposed deep-joint threshold'}
 elif name.endswith('_TIP_R'):
  digit=name.split('_')[0]
  if digit=='THUMB':
   rule['coordinate_authority']='Human-approved corrected thumb terminal native v284 in RSSF; old R2A cap representative and roll superseded'
   rule['region']={'type':'CORRECTED_NATIVE_TERMINAL_SURFACE_LANDMARK','terminal_native_vertex':284,'surface_max_mm':1.5,'terminal_position_gate':'exact equality with current corrected stored terminal and actual native v284; no selector rerun','digit_identity':'approved native thumb domain and cap37 membership corroboration only','apex_vertex_threshold':'NOT_APPLICABLE_SUPERSEDED; corrected native terminal authority','helper_tail':'connected non-deform 0.30 extension; outside-skin tail expected, not inside-gated'}
  else:
   f=four[digit.lower()];land=f['approved_landmark']
   rule['region']={'type':'CARRY_FORWARD_APPROVED_FOUR_FINGER_SURFACE_APEX','surface_max_mm':1.0,'apex_max_mm':15.0,'frozen_apex_native_vertex':land['geodesic_from_distal_most_vertex']['vertex'],'frozen_accepted_native_surface_face':land['nearest_face'],'frozen_digit_identity':land['owner_of_nearest_face'],'semantics':'R2 explicitly carries accepted four fingers forward; R1 region rule applied to accepted fixed coordinates. R2A four-finger evidence corroborates own surface/apex; no cap/geodesic/ownership solve','digit_identity_gate':'nearest new native face agrees with frozen accepted own-digit face, and that exact face topology is unchanged'}
 else:
  digit=name.split('_')[0];key=name[:-2];r=regions[key];first='CMC' if digit=='THUMB' else 'MCP'
  rule['region']={'type':'FROZEN_T01_AXIAL_ZONE','anchor_world_m':frames[digit+'_'+first+'_R']['head'],'tip_frame_world_m':frames[digit+'_TIP_R']['head'],'center_mm':r['joint_axial_center_mm'],'half_width_mm':r['zone_half_width_mm'],'axis_rule':'normalize(frozen Stage4B TIP head - frozen first-joint head); current fixed joint projection only','locator_rerun':False}
  if name=='THUMB_IP_R':rule['corrected_thumb_head_authority']='Human-approved REVALIDATED_UNCHANGED IP head; frozen approved T01 region retained'
 rules[name]=rule
dump('CURRENT_JOINT_QUALIFICATION_SEMANTICS_R1.json',{'status':'RECOVERED','formal_joint_count':21,'deform_joint_count':16,'TIP_helper_count':5,'rules':rules,'sources':{k:ref(p) for k,p in sources.items()},
 'freeze_receipt_parse_method':parse,'historical_files_not_repaired':True,
 'authority_precedence':['R2 wrist/CMC/INDEX_MCP requalification replaces earliest R1 failed positions','R2 carry-forward accepted four-finger and IP head region rules','R2A + freeze/errata establish thumb cap semantics; historical diagnostic retained','Human corrected thumb authority supersedes old cap REP and distal endpoint/roll; native terminal v284 is current','Current geometry propagation changes surface only; none of these joint coordinates or rules are refitted'],
 'zero_bind':{'zero_procedure':'AST-reuse s6a_common.reset_pose only: all 21 channels QUATERNION identity, location zero, scale one; temporary memory, no save','bind_gate_mm':0.0001,'bind_comparator':'<=','original_R1_comparator':'<','current_R2_applicability':'FullStage6A current R2 consumer uses reset_pose/evaluate and raw_RSSF_noise_mm <= 1e-4, not solely return-to-baseline; original Stage5B and R1B share this 0.0001mm numerical floor','pose_quaternion_angle_max_rad':1e-7,'pose_location_and_scale':'exact (0,0,0) / (1,1,1)','independent_bind_matrix':'Blender Armature modifier uses current object frame mapping and bone rest inverse internally; asset has no dedicated user-authored modifier bind matrix. Capture actual object matrix_parent_inverse only; no new bind fields'},
 'anatomy_ownership_locator_cap_or_RSSF_authority_recomputed':False,'deformation_functions_will_not_be_loaded_or_run':True})
print('CURRENT SEMANTICS RECOVERED 21 / 16 DEFORM / 5 TIP; ZERO RAW BIND <= 0.0001mm')
