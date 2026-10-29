from pathlib import Path
import json,hashlib,math,struct,sys,ast
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];RUN='HUMAN_THUMB_KINEMATIC_AUTHORITY_CORRECTION'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def canon(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def f32(n):return struct.unpack('<f',struct.pack('<f',n))[0]
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
AUTH=read(OUT/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json');DEC=read(OUT/'HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json')
assert canon({k:v for k,v in AUTH.items() if k!='combined_authority_hash'})==AUTH['combined_authority_hash']
assert canon({k:v for k,v in DEC.items() if k!='combined_approval_hash'})==DEC['combined_approval_hash']
assert sha(OUT/'HUMAN_DECISION_SOURCE_R1.txt')==DEC['source_copy_sha256']
assert sha(ROOT/AUTH['approved_candidate_path'])==AUTH['approved_candidate_sha256']
RAW=read(OUT/'RIG_BEFORE_AFTER_FULL_SNAPSHOTS.json');B=RAW['before'];A=RAW['after_saved_reloaded'];SLOTS=read(OUT/'THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json')
allowed=set(DEC['authorized_slot_writes']);assert len(allowed)==5
changed=[];allslot=[]
for n,b in B['bones'].items():
 a=A['bones'][n]
 for k in ['head','tail','roll']:
  fields=['roll_rad'] if k=='roll' else [k+'_local_m',k+'_world_m']
  before={f:b[f] for f in fields};after={f:a[f] for f in fields};same=before==after;slot=n+'.'+k
  if not same:changed.append(slot)
  allslot.append({'slot':slot,'before_hash':canon(before),'after_hash':canon(after),'equal':same,'authorized_change':slot in allowed})
assert set(changed)==allowed
unrelated=[n for n in B['bones'] if n not in ['THUMB_IP_R','THUMB_TIP_R']]
assert all(B['bones'][n]==A['bones'][n] for n in unrelated)
assert len(unrelated)==19 and len(B['bones'])==len(A['bones'])==21
assert B['bones']['THUMB_IP_R']['head_local_m']==A['bones']['THUMB_IP_R']['head_local_m']
assert B['bones']['THUMB_IP_R']['head_world_m']==A['bones']['THUMB_IP_R']['head_world_m']
assert all(B[k]==A[k] for k in ['rig_matrix_world','rig_location','rig_rotation_euler','rig_scale','mesh_matrix_world','object_transforms','geometry','geometry_signature'])
for n,b in B['bones'].items():
 for k in ['parent','use_connect','use_deform','inherit_scale','use_inherit_rotation','use_local_location','collections','custom_properties','pose_location','pose_rotation_mode','pose_rotation_quaternion','pose_rotation_euler','pose_scale']:assert b[k]==A['bones'][n][k]
assert A['bones']['THUMB_IP_R']['tail_local_m']==A['bones']['THUMB_TIP_R']['head_local_m']
assert not A['bones']['THUMB_TIP_R']['use_deform'] and A['bones']['THUMB_TIP_R']['use_connect']
for r in SLOTS['slots']:
 name,slot=r['slot'].split('.')
 if slot=='roll':
  assert r['after_rad']==f32(r['approved_rad']);before={'roll_rad':r['before_rad']};after={'roll_rad':r['after_rad']};approved={'roll_rad':r['approved_rad']}
 else:
  assert r['after_local_m']==[f32(x) for x in r['approved_local_m']]
  r['delta_mm']=dist(r['after_world_m'],r['before_world_m'])*1000
  assert r['approval_storage_error_mm']<.0001
  before={'local_m':r['before_local_m'],'world_m':r['before_world_m']};after={'local_m':r['after_local_m'],'world_m':r['after_world_m']};approved={'local_m':r['approved_local_m'],'world_m':r['approved_world_m']}
 r['before_value_hash']=canon(before);r['after_value_hash']=canon(after);r['approved_value_hash']=canon(approved)
SLOTS['hash_method']='SHA256 of UTF-8 JSON, sort_keys=True, separators comma/colon, ensure_ascii=False, allow_nan=False; hashes cover each slot value payload'
SLOTS['float32_storage_verification']='PASS: actual local positions and rolls are exactly the float32-rounded approved values; world-space arithmetic rounding reported separately'
dump('THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json',SLOTS)
input_path=ROOT/AUTH['input_rig_path'];output_path=ROOT/AUTH['corrected_rig_path']
assert sha(input_path)==SLOTS['input_rig_sha256']==AUTH['input_rig_sha256']
assert sha(output_path)==SLOTS['output_rig_sha256']==RAW['output_rig_sha256']
drift={'validation':'PASS','IP_head_bitwise_equal':True,'unrelated_bone_count':19,'unrelated_bones':unrelated,'unrelated_bones_entire_snapshots_bitwise_equal':True,'hierarchy_equal':True,'rig_origin_and_transform_bitwise_equal':True,'all_object_transforms_bitwise_equal':True,'geometry_topology_UV_material_weights_shape_keys_parenting_equal':True,
 'bone_count_before':21,'bone_count_after':21,'deform_bone_count':sum(b['use_deform'] for b in A['bones'].values()),'nondeform_helpers':sum(not b['use_deform'] for b in A['bones'].values()),'parent_child_IP_tail_TIP_head_continuity_mm':0,'actual_changed_slots':sorted(changed),'all_63_bone_slot_hashes':allslot,
 'geometry_signature_before':B['geometry_signature'],'geometry_signature_after':A['geometry_signature'],'rig_origin_before_hash':canon(B['rig_matrix_world']),'rig_origin_after_hash':canon(A['rig_matrix_world']),'unrelated_bone_data_before_hash':canon({n:B['bones'][n] for n in unrelated}),'unrelated_bone_data_after_hash':canon({n:A['bones'][n] for n in unrelated})}
dump('HIERARCHY_ORIGIN_UNRELATED_BONES_DRIFT_VERIFICATION.json',drift)
before=read(OUT/'FROZEN_HASHES_BEFORE.json');wr=[];er=[]
for rel,h in before['workspace'].items():
 p=ROOT/rel;after=sha(p);wr.append({'path':rel,'before':h,'after':after,'equal':after==h})
for rel,h in before['external'].items():
 after=sha(Path(rel));er.append({'path':rel,'before':h,'after':after,'equal':after==h})
new=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and str(p.relative_to(ROOT)) not in before['workspace']]
assert not new and all(r['equal'] for r in wr+er)
blend_files=list(OUT.rglob('*.blend'));assert blend_files==[output_path]
assert not list(OUT.rglob('*.blend1')) and not any('r1f' in p.name.lower() for p in OUT.rglob('*'))
cap=read(OUT.parent/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
assert canon({k:v for k,v in cap.items() if k!='combined_authority_hash'})==AUTH['cap37_combined_authority_hash']
protection={'execution':RUN,'all_before_equal_after':True,'workspace_file_count':len(wr),'external_file_count':len(er),'workspace':wr,'external':er,'new_files_outside_output_directory':new,'historical_R2A_unchanged':True,'cap37_membership_unchanged':True,'prior_review_and_candidate_files_unchanged':True}
dump('PROTECTED_STATE_VERIFICATION.json',protection)
hashes={'source_rig':{'path':AUTH['input_rig_path'],'before_sha256':SLOTS['input_rig_sha256'],'after_sha256':sha(input_path),'equal':True},'corrected_rig':{'path':AUTH['corrected_rig_path'],'sha256':sha(output_path)},'human_decision_source_sha256':DEC['source_copy_sha256'],'human_approval_file_sha256':sha(OUT/'HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json'),'human_approval_combined_hash':DEC['combined_approval_hash'],'authority_file_sha256':sha(OUT/'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json'),'authority_combined_hash':AUTH['combined_authority_hash'],'reviewed_candidate_sha256':AUTH['approved_candidate_sha256'],'cap37_combined_authority_hash':AUTH['cap37_combined_authority_hash']}
dump('HUMAN_THUMB_KINEMATIC_CORRECTION_HASHES_R1.json',hashes)
application={'record_id':'THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1','execution':RUN,'status':'HUMAN_APPROVED_APPLIED_VERIFIED','approval_record':'HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json','authority_record':'THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json','authority_combined_hash':AUTH['combined_authority_hash'],'corrected_rig':hashes['corrected_rig'],'slot_results':{r['slot']:('HUMAN_APPROVED_CORRECTION_APPLIED' if r['changed_authorized'] else 'KEEP_CURRENT_REVALIDATED_UNCHANGED') for r in SLOTS['slots']},'source_candidate_classifications_remain_historical':True,'candidate_storage_errors':'see THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json; exact float32 local values; TIP tail world error 0.0000631503 mm','output_saved_reloaded_exact_match':True,'hierarchy_origin_unrelated_bones_verification':'PASS','historical_protected_state_verification':'PASS','effective_thumb_kinematic_input_for_next_reconciliation':AUTH['corrected_rig_path'],'current_hardcoded_downstream_loaders_updated':False,'downstream_approval_not_granted':DEC['scope_exclusions'],'downstream_reconciliation_required':True,'NEXT':DEC['NEXT'],'STOP':True}
application['combined_application_hash']=canon(application);dump('THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json',application)
status={'execution':RUN,'THUMB_KINEMATIC_AUTHORITY_CORRECTION':'HUMAN_APPROVED','THUMB_KINEMATIC_CORRECTION_APPLICATION':'APPLIED_VERIFIED','changed_slot_count':5,'changed_slots':sorted(changed),'THUMB_IP_R.head':'KEEP_CURRENT_REVALIDATED_UNCHANGED','hierarchy_origin_unrelated_bones_drift':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'WEIGHT_DELTA':0,'unapproved_bone_slot_delta':0,'approved_position_slot_change_count':3,'approved_roll_slot_change_count':2,'BLEND_FILES_WRITTEN':1,'historical_blend_files_written':0,'rig_rebuild_runs':0,'R2_runs':0,'R3_runs':0,'skin_rebuild_runs':0,'Stage5B_runs':0,'Stage6_runs':0,'R1F_created':False,'cap_selector_runs':0,'cap37_membership_unchanged':True,'corrected_rig_path':AUTH['corrected_rig_path'],'corrected_rig_sha256':SLOTS['output_rig_sha256'],'max_actual_position_delta_mm':max(r.get('delta_mm',0) for r in SLOTS['slots']),'max_actual_roll_delta_deg':max(abs(r.get('delta_deg',0)) for r in SLOTS['slots']),'protected_workspace_files':len(wr),'protected_external_files':len(er),'all_before_equal_after':True,'scope_exclusions':DEC['scope_exclusions'],'NEXT':DEC['NEXT'],'STOP':True}
dump(RUN+'_STATUS.json',status)
def xyz(v):return '['+', '.join(f'{n:.12f}' for n in v)+']'
table=[]
for r in SLOTS['slots']:
 if r['slot'].endswith('.roll'):b=f"{r['before_rad']:.12f} rad";a=f"{r['after_rad']:.12f} rad";delta=f"{r['delta_deg']:.9f} deg"
 else:b=xyz(r['before_world_m']);a=xyz(r['after_world_m']);delta=f"{r['delta_mm']:.9f} mm"
 table.append(f"| {r['slot']} | {b} | {a} | {delta} |")
report=f'''# {RUN}

THUMB_KINEMATIC_AUTHORITY_CORRECTION = **HUMAN_APPROVED**；APPLICATION = **APPLIED_VERIFIED**。

Human 在 2026-10-03（Asia/Shanghai）当前 chat 直接批准此前审阅的 `KINEMATIC_CANDIDATE_R1`：保留 IP head，应用另外 5 个 slot。消息转录保存为 `HUMAN_DECISION_SOURCE_R1.txt`；它的 hash 仅覆盖本地转录，不冒充 chat transport signature。正式批准与 correction authority 分别见 `HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json` 和 `THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json`。

## 应用结果

新建 skeleton-only 修正文件：`{output_path.name}`。以历史 R2A 为输入，只执行批准的三项端点赋值和两项 edit-roll 赋值，没有重新构建 skeleton，没有重新拟合或运行 selector。历史 R2A 与此前 review/candidate 文件均未覆盖。

| Slot | Before（位置为 world m） | After（位置为 world m） | Δ |
|---|---|---|---:|
'''+ '\n'.join(table)+f'''

所有 actual local endpoint 和 edit-roll 数值与 approved 值的 float32 表示完全一致。IP tail、TIP head 及两个 roll 与批准值无数值偏差；TIP tail 的 world 计算结果存在 **0.0000631503 mm** 存储/世界坐标运算舍入差。该值单列为 storage error，不构成重新选点。完整 world/local/roll before/after、approved 数值及逐 slot SHA256 见 `THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json`。

## 无漂移与存盘验证

修正文件保存后重新打开，完整数据 snapshot 与保存前结果精确相同。IP head local/world 逐值相同，19 根无关骨骼的 head/tail/roll/local matrices、parent/connect/deform、继承模式、collections、custom properties 和 pose transforms 完整逐值相同。全量 21 bone hierarchy、16 deform / 5 non-deform 构成不变。IP tail 与 TIP head 完全共点，TIP 仍是 connected non-deform helper。

armature origin/transform、mesh origin/transform 及所有 object transforms 逐值相同。mesh 顶点、edge/polygon topology、UV、material assignment、smooth flags、vertex groups/weights、shape keys、mesh parent 和 modifier inventory 完全相同。详见 `HIERARCHY_ORIGIN_UNRELATED_BONES_DRIFT_VERIFICATION.json` 和 `RIG_BEFORE_AFTER_FULL_SNAPSHOTS.json`；前者含所有 63 bone slots 的 before/after canonical hashes。

## Hash 链

- reviewed candidate SHA256：`{AUTH['approved_candidate_sha256']}`
- source R2A before SHA256：`{SLOTS['input_rig_sha256']}`
- source R2A after SHA256：`{sha(input_path)}`
- corrected rig SHA256：`{SLOTS['output_rig_sha256']}`
- Human approval combined hash：`{DEC['combined_approval_hash']}`
- correction authority combined hash：`{AUTH['combined_authority_hash']}`
- cap37 combined authority hash：`{AUTH['cap37_combined_authority_hash']}`

全部文件与 payload hash scope 见 `HUMAN_THUMB_KINEMATIC_CORRECTION_HASHES_R1.json`。本輪保护 {len(wr)} 个历史工作区文件和 {len(er)} 个外部输入，before = after 全部通过。保护包括历史 Stage5A/B、R3、Stage6、cap37、Human responses 和此前候选/审计。没有本轮目录以外的新文件。

## 生效范围与停止点

新 authority 仅取代历史 R2A 的 thumb distal IP/TIP kinematic slots；IP head 保留。`THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json` 将新 blend 指定为下一轮 thumb kinematic reconciliation 的正式输入。历史 hardcoded downstream loaders 尚未更新，未来任务必须显式接入该 authority；不得把旧 R2A frozen 数值继续视为这些 distal slots 的 authority。

本次 Human approval 不批准 R2、R3、skin weights、Stage5B、Stage6A、Stage6B 或 strict-bound results。GEOMETRY_DELTA = 0，TOPOLOGY_DELTA = 0，WEIGHT_DELTA = 0，unapproved bone/joint slot delta = 0。只有批准的 5 个 slot 改变。

BLEND_FILES_WRITTEN = **1**（新 skeleton derivative）；historical blend files written = **0**。

R2_runs = **0**；R3_runs = **0**；skin rebuild runs = **0**；Stage5B_runs = **0**；Stage6_runs = **0**；R1F_created = **NO**。

NEXT = **CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1**。

STOP = **YES**。
'''
(OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf-8')
for p in OUT.glob('*.json'):read(p)
for p in (OUT/'scripts').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
dump('OUTPUT_VERIFICATION.json',{'status':'PASS','approved_changed_slot_count':5,'all_unapproved_slots_unchanged':True,'saved_reload_exact_match':True,'float32_candidate_application_exact_match':True,'all_historical_and_external_hashes_preserved':True,'new_blend_count':1,'R2_R3_skin_Stage6_runs':0,'R1F_created':False,'output_hashes':{str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='OUTPUT_VERIFICATION.json'},'STOP':True})
print('FINAL PASS: five slots applied; IP head + 19 unrelated bones/hierarchy/origin exact; historical',len(wr),'+ external',len(er),'hashes preserved; one new blend; STOP')
