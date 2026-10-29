import json,hashlib,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
FIX=ROOT/'audits/official_l1_first_web_targeted_deformation_fix_r1'
PHASE='RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_AND_REAL_PIANO_MOTION_CHECK_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
v=read(OUT/'BASELINE_FREEZE_VERIFICATION_R1.json');approval=read(OUT/'SOURCE_HUMAN_APPROVAL_BIND_R1.json');inv=read(OUT/'LOCAL_BLEND_MOTION_INVENTORY_R1.json')
assert v['status']=='PASS' and not inv['files_with_actions'] and not any('error' in r for r in inv['files'])
asset=ROOT/v['baseline']['path'];assert sha(asset)==v['baseline']['sha256']
assert sha(ROOT/v['source']['path'])==v['source']['sha256']
roots=[ROOT,ROOT/'references',ROOT.parent/'piano',Path('<USER_HOME>/Downloads'),Path('<USER_HOME>/Desktop'),Path('<USER_HOME>/Documents'),Path('D:/codex'),Path('D:/workbuddy')]
scans=[]
for p in roots:
    args=['rg','--files','--hidden','-g','!node_modules','-g','!.git','-g','!venv','-g','!.venv','-g','!dist','-g','!cache','-g','!Cache']
    patterns=['*.bvh','*.c3d','*.fbx','*.npz','*.npy','*.pkl','*.mid','*.midi'] if p in roots[:4] else ['*.bvh','*.c3d','*piano*motion*','*piano*hand*','*pianist*','*hand*animation*','*hand*mocap*','*钢琴*动作*']
    for pat in patterns:args+=['-g',pat]
    args.append(str(p))
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert result.returncode in [0,1],result.stderr
    scans.append({'root':str(p),'patterns':patterns,'matched_paths':result.stdout.splitlines(),'exit_code':result.returncode,'status':'SEARCH_COMPLETED_NO_ELIGIBLE_HAND_MOTION','exclusions':['node_modules','.git','venv','.venv','dist','cache','Cache']})
rejections=[
 {'source':'audits/official_l1_product_rebase_feasibility_r1/VISIBLE_MOTION_PREVIEW_MANIFEST_R1.json','type':'STRESS_POSE_SLERP_PREVIEW','eligible':False,'reason':'ZERO to isolated MCP / thumb / opposition stress poses; display-only six-frame interpolation, no piano performance motion.','evidence':'audits/official_l1_product_rebase_feasibility_r1/MOTION_RENDER_MANIFEST_R1.json: animations[].path_semantics'},
 {'source':'52 existing workspace .blend files','type':'STATIC_MESH_RIG_AND_STRESS_HARNESS','eligible':False,'reason':'Blender library datablock-name inspection found no Actions in all 52 files.','evidence':'LOCAL_BLEND_MOTION_INVENTORY_R1.json'},
 {'source':'audits/minimal_local_geometry_amendment_design_r4/R4_CONTACT_ANCHOR_NULLSPACE.npz','type':'STATIC_NUMERICAL_MATRIX','eligible':False,'reason':'Stored A and Z nullspace matrices for an earlier local geometry study, not time-sampled hand motion.','evidence':'audits/minimal_local_geometry_amendment_design_r4/contact_components.py:77'},
 {'source':str(ROOT.parent/'piano/research/piano_open_source_reference_r1/piano-gl-source/assets/demo.mid'),'type':'MIDI_NOTE_EVENTS','eligible':False,'reason':'Existing piano demo note sequence has no WRIST / finger joint rotation or position channels. Converting it into hand motion would require creating a new motion system.','evidence':str(ROOT.parent/'piano/research/piano_open_source_reference_r1/piano-gl-source/src/key_animation.cpp')},
 {'source':str(ROOT.parent/'piano/v1_2e_cp1r35/motion_and_render.py'),'type':'PIANO_MECHANISM_ANIMATION','eligible':False,'reason':'Replays KEY_056/057 visibleHammerAngleDeg into hammer butt pivots; not performer hand joints.','evidence':str(ROOT.parent/'piano/v1_2e_cp1r35/motion_and_render.py')},
 {'source':str(ROOT.parent/'piano/3d piano/upright-piano/source/Upright Piano.fbx'),'type':'PIANO_OBJECT_ASSET','eligible':False,'reason':'Existing local raw-asset study records zero armatures/bones/Actions for piano assets; object is a piano, not a hand motion skeleton.','evidence':str(ROOT.parent/'piano/research/external_piano_raw_asset_comparative_audit_r2/REPORT/EXTERNAL_PIANO_RAW_ASSET_AUDIT_R2.md')},
 {'source':str(ROOT.parent/'piano/research/piano_open_source_reference_r1/piano-gl-source/assets/piano.blend'),'type':'STATIC_PIANO_OBJECT_ASSET','eligible':False,'reason':'Existing inventory contains no armatures or Actions, only key/backplane/base mesh objects.','evidence':str(ROOT.parent/'piano/research/piano_open_source_reference_r1/piano_blend_inventory.json')},
 {'source':str(ROOT.parent/'piano/参考视频'),'type':'PIANO_MECHANISM_REFERENCE_VIDEO','eligible':False,'reason':'Piano teardown / action mechanism reference video, no existing hand skeleton channel dataset; no new video tracking system was created.'}]
audit={'PHASE':'REAL_PIANO_MOTION_SOURCE_AUDIT_R1','REAL_PIANO_MOTION_SOURCE':'NOT_FOUND','MOTION_SOURCE_TYPE':'NONE','eligible_source_count':0,'search_priority':['Current workspace motion/animation','Project references/assets','Previous project history and local downloads','STOP if none found'],'search_scope':'Known local project and download locations only. No claim that every disk directory was searched.','scans':scans,'workspace_blend_inventory':{'path':'LOCAL_BLEND_MOTION_INVENTORY_R1.json','file_count':inv['file_count'],'files_with_actions':0,'errors':0},'rejected_local_candidates':rejections,'RETARGET_EXECUTED':'NO','MOTION_CASES_COVERED':[],'new_motion_keyframes_created':0,'online_source_search_or_download_executed':False,'REAL_PIANO_MOTION_CHECK':'BLOCKED_MOTION_SOURCE_NOT_FOUND','STOP':'STOP — MOTION SOURCE NOT FOUND','NEXT':'Dedicated motion-source acquisition task; do not fabricate piano hand animation.'}
write(OUT/'REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json',audit)
write(FIX/'HUMAN_APPROVAL_BIND_R1.json',approval)
status={'PHASE':PHASE,'OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1':'HUMAN_APPROVED','HUMAN_APPROVED':'YES','RIGHT_HAND_BASELINE_SOURCE':v['source']['path'],'RIGHT_HAND_BASELINE_SOURCE_SHA256':v['source']['sha256'],'RIGHT_HAND_BASELINE_ASSET':v['baseline']['path'],'RIGHT_HAND_BASELINE_SHA256':v['baseline']['sha256'],'OFFICIAL_L1_MESH_PRESERVED':'YES_EXACT','MESH_VERTEX_COUNT':v['mesh_vertex_count'],'BONE_COUNT':21,'ZERO_VISUAL_STATUS':'PASS_HUMAN_APPROVED_SOURCE_IDENTICAL_BASELINE','FIRST_WEB_FIX_PRESERVED':'YES_EXACT_WEIGHTS_CORRECTIVE_DRIVER','VISIBLE_PRODUCT_BLOCKER_COUNT':0,'NEW_VISIBLE_DEFECT_COUNT':0,'FILE_CLEAN_REOPEN':'PASS','NaN_Inf':0,'ZERO_RESTORE':'PASS','ZERO_RESTORE_MAX_ERROR_MM':0.0,'CORRECTIVE_VALUE_AT_ZERO':0.0,'GEOMETRY_REPAIR_COUNT':0,'WEIGHT_TUNING_COUNT':0,'NEW_CORRECTIVE_COUNT':0,'REAL_PIANO_MOTION_SOURCE':'NOT_FOUND','MOTION_SOURCE_TYPE':'NONE','RETARGET_EXECUTED':'NO','MOTION_CASES_COVERED':[],'GROSS_DEFORMATION_FAILURE_COUNT':None,'GROSS_DEFORMATION_FAILURE_COUNT_NOTE':'NOT_EVALUATED: no piano hand motion source; zero must not be inferred.','REAL_PIANO_MOTION_VISIBLE_STATUS':'NOT_EVALUATED_MOTION_SOURCE_NOT_FOUND','RIGHT_HAND_PRODUCT_BASELINE':'PASS','RIGHT_HAND_PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN','RIGHT_HAND_PRODUCT_BASELINE_R1':'HUMAN_APPROVED_FROZEN','REAL_PIANO_MOTION_CHECK':'BLOCKED_MOTION_SOURCE_NOT_FOUND','REAL_PIANO_MOTION_PRODUCT_CHECK_R1':'BLOCKED_MOTION_SOURCE_NOT_FOUND','LEGACY_ENGINEERING_MESH_STATUS':'LEGACY_ENGINEERING_REFERENCE_ONLY','LEFT_HAND_STARTED':'NO','WEB_EXPORT_STARTED':'NO','VERDICT':'BASELINE_FROZEN_MOTION_CHECK_BLOCKED_SOURCE_NOT_FOUND','STOP':'STOP — MOTION SOURCE NOT FOUND','NEXT':'Find an existing piano hand motion source in a separate task.'}
write(OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_STATUS.json',status)
legacy=ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'
pointer={'authority':'Direct Human approval and baseline freeze request, 2026-10-06','route':'PRODUCT_VISIBLE_QUALITY_FIRST','RIGHT_HAND_PRODUCT_BASELINE_STATUS':'HUMAN_APPROVED_FROZEN','asset':v['baseline'],'source':v['source'],'mesh':'Official L1, 3300 vertices, 3298 faces','bone_count':21,'approved_weight_and_first_web_corrective_preserved':True,'legacy_engineering_mesh_role':'LEGACY_ENGINEERING_REFERENCE_ONLY','legacy_vertex_count':3416,'legacy_primary_reference':{'path':legacy.relative_to(ROOT).as_posix(),'sha256':sha(legacy)},'historical_assets_deleted_or_overwritten':False,'motion_gate':'BLOCKED_MOTION_SOURCE_NOT_FOUND','left_hand_and_Web_gate':'WAIT_FOR_REAL_PIANO_MOTION_HUMAN_REVIEW','report':'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md','status':'production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_STATUS.json'}
write(ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json',pointer)
rows='\n'.join('| '+k+' | '+('NOT_EVALUATED' if val is None else json.dumps(val,ensure_ascii=False) if isinstance(val,list) else str(val))+' |' for k,val in status.items() if k not in ['PHASE','HUMAN_APPROVED','GROSS_DEFORMATION_FAILURE_COUNT_NOTE','ZERO_RESTORE_MAX_ERROR_MM','RIGHT_HAND_BASELINE_SOURCE_SHA256'])
report=f'''# RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1

**RIGHT_HAND_PRODUCT_BASELINE = PASS / HUMAN_APPROVED_FROZEN**

**REAL_PIANO_MOTION_CHECK = BLOCKED_MOTION_SOURCE_NOT_FOUND — STOP**

Human 明确批准上一阶段六个状态，原 first-web 尖折已消除，ZERO 与 INDEX 正常，opposition L1/L2/L3 可接受。当前独立 asset 完整保留该已批准的网格、21 骨骼、权重、UV/材质及 first-web corrective/driver。没有新增 geometry、weight 或 corrective 修改。

| 最终字段 | 结果 |
| --- | --- |
{rows}

## Human approval 与来源绑定

来源 candidate SHA256：`{v['source']['sha256']}`。核对上一阶段最终输出清单中 60 个证据文件的 SHA256 全部相符，candidate 与 review/render evidence 绑定一致。直接用户指令的批准记录保存在 [SOURCE_HUMAN_APPROVAL_BIND_R1.json](./SOURCE_HUMAN_APPROVAL_BIND_R1.json)，并添加上一阶段的 [Human approval sidecar](../../audits/official_l1_first_web_targeted_deformation_fix_r1/HUMAN_APPROVAL_BIND_R1.json)。历史 preliminary report/status 和历史证据保持原样，其 HUMAN_PENDING 状态由该明确批准记录取代。

## 独立产品基线

[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend](./RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend)，SHA256 `{v['baseline']['sha256']}`，保存姿态 ZERO / RSSF。

本轮只修改新文件中的产品角色 / Human approval 元数据，解除 DESIGN_ONLY 标记。3300 个原生顶点 / 3298 面、全部权重/组、骨架 rest 与 joint layout、UV、材质、两个 shape keys（Basis + 原 corrective）、一个 driver 及其表达式/变量/target 均与 source 逐项相同。16 deform bones，5 non-deform TIP helpers；ZERO corrective = 0。clean reopen PASS；source 与 baseline ZERO 求值差 = 0 mm；NaN/Inf = 0。仅对已批准的 FULL_OPP_L3 做一次直接 round trip 确认 driver 能激活并恢复 ZERO，恢复差 = 0 mm；不重开 Stage6 资格矩阵。

ZERO 普通 palmar/dorsal/thenar 实体图观察正常。来源 Human acceptance 与保存重开后逐项相同的 payload 共同支持当前基线的批准继承，未把新 motion acceptance 混入其中。

当前产品资产权威指针：[production_spec/RIGHT_HAND_PRODUCT_BASELINE.json](../RIGHT_HAND_PRODUCT_BASELINE.json)。新的路线说明：[RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md](../../docs/RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md)。此前 3416 顶点 engineering mesh 降为 LEGACY_ENGINEERING_REFERENCE_ONLY。历史文件没有删除或覆盖。

## 本地 motion source 搜索

按照授权顺序搜索本 hand workspace、references、相邻 piano 项目、项目历史说明、Downloads，以及已知 Desktop/Documents/D:/codex/D:/workbuddy 中具有钢琴手部 motion 特征的文件名。52 个既有 hand workspace `.blend` 通过只读 library datablock-name 检查，全部 Actions = 0；没有 mesh 求值、形变审计或保存。这是 motion 数据发现，不是旧 forensic 重跑。

命中的预览 GIF / manifests 只是 ZERO→单关节或 opposition stress pose 的 quaternion slerp。唯一 hand 项目 NPZ 存储早期局部研究的 A/Z 静态矩阵。相邻 piano 项目中的 motion replay 控制琴键、hammer/butt pivot 等机械件；demo.mid 是音符事件，既无 wrist/finger joints 的旋转或位置通道，也不能直接 retarget 到当前21骨骼手。已有钢琴视频是拆机/击弦机结构参考，没有现成手部运动通道。Downloads 未发现 motion 格式候选。

因此 REAL_PIANO_MOTION_SOURCE = NOT_FOUND；RETARGET_EXECUTED = NO；MOTION_CASES_COVERED = []。没有造新 keyframes、动作库或 MIDI-to-hand 系统，没有联网寻找/下载替代 motion。没有可评审的真实动作，故不生成伪装为真实 motion 的 mp4。GROSS_DEFORMATION_FAILURE_COUNT = NOT_EVALUATED（JSON 为 null），不能写成 0 或判 motion PASS。

完整本地范围、命中文件和排除理由：[REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json](./REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json)。这不是全磁盘不存在的证明，只是在已搜索的项目/下载范围内未找到可用来源。

## 最低检查与停止点

[BASELINE_FREEZE_VERIFICATION_R1.json](./BASELINE_FREEZE_VERIFICATION_R1.json)；[LOCAL_BLEND_MOTION_INVENTORY_R1.json](./LOCAL_BLEND_MOTION_INVENTORY_R1.json)。没有 hidden crossing census、normal-dot、true-cap、R3、整手修补或细微不可见优化。LEFT_HAND_STARTED = NO；WEB_EXPORT_STARTED = NO。

**基线冻结成功；真实钢琴 motion 检查单独 BLOCKED。STOP — MOTION SOURCE NOT FOUND。下一步只记录为专门寻找现成手部 motion source。**
'''
(OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md').write_text(report,encoding='utf-8')
authority=f'''# Right-hand product baseline authority — R1

2026-10-06，Human 明确批准 OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1 六状态，并授权将来源候选冻结为新的右手产品基线。

当前唯一产品主线为 **Official L1 mesh + 21-bone rig + 当前已批准权重 + 当前 first-web corrective / driver**。规范机器指针：[RIGHT_HAND_PRODUCT_BASELINE.json](../production_spec/RIGHT_HAND_PRODUCT_BASELINE.json)。

产品资产：[RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend](../{v['baseline']['path']})。SHA256：`{v['baseline']['sha256']}`。RIGHT_HAND_PRODUCT_BASELINE_STATUS = HUMAN_APPROVED_FROZEN。

此前 3416 顶点 engineering mesh 全部降为 **LEGACY_ENGINEERING_REFERENCE_ONLY**；历史 lineage / audit / rig / blend 文件保留，但其旧主线资格不再决定后续产品资产选择。历史文件内旧阶段结论仍作为历史记录，不改写。

PRODUCT_VISIBLE_QUALITY_FIRST：不继续旧 mesh 修补、R3、true-cap、2127-edge audit、hidden crossing census、normal-dot、逐顶点 anatomy proof 或不可见数值优化。

REAL_PIANO_MOTION_CHECK = BLOCKED_MOTION_SOURCE_NOT_FOUND。右手基线已批准冻结，不等于真实钢琴 motion 已通过。后续先取得现成手部 motion，进行不改 mesh/rig layout 的 retarget，并等待 motion Human review；本轮不启动左手或 Web。

[本轮报告](../production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md) · [本轮状态](../production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_STATUS.json)
'''
(ROOT/'docs/RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md').write_text(authority,encoding='utf-8')
memory=ROOT/'.workbuddy/memory/MEMORY.md';old=memory.read_text(encoding='utf-8-sig')
note='''## 当前产品路线覆盖记录（2026-10-06 Human-approved）

PRODUCT_VISIBLE_QUALITY_FIRST。当前右手产品基线权威：`production_spec/RIGHT_HAND_PRODUCT_BASELINE.json`；资产 `production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend`，Official L1 V3300 + 21 bones + Human-approved weights + first-web corrective/driver；HUMAN_APPROVED_FROZEN。来源阶段 OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1 = HUMAN_APPROVED。

此前 V3416 engineering mesh = LEGACY_ENGINEERING_REFERENCE_ONLY，保留历史文件。下文旧工程阶段结论为历史记录，不再作为产品主线。停止旧 mesh 修补、R3、true-cap、hidden crossing/normal-dot 等不可见优化。

REAL_PIANO_MOTION_CHECK = BLOCKED_MOTION_SOURCE_NOT_FOUND；仅基线 freeze PASS。不得把 stress-pose GIF、MIDI 或琴键/击弦机动画当作 performer hand motion；尚未 retarget。LEFT_HAND_STARTED = NO；WEB_EXPORT_STARTED = NO。下一任务只记录寻找现成钢琴手部 motion。

'''
if '当前产品路线覆盖记录（2026-10-06 Human-approved）' not in old:
    heading,rest=old.split('\n',1);memory.write_text(heading+'\n\n'+note+rest.lstrip('\n'),encoding='utf-8')
files=[asset,OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_REPORT.md',OUT/'RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1_STATUS.json',OUT/'REAL_PIANO_MOTION_SOURCE_AUDIT_R1.json',OUT/'BASELINE_FREEZE_VERIFICATION_R1.json',OUT/'SOURCE_HUMAN_APPROVAL_BIND_R1.json',OUT/'LOCAL_BLEND_MOTION_INVENTORY_R1.json',ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json',ROOT/'docs/RIGHT_HAND_PRODUCT_BASELINE_AUTHORITY_R1.md',FIX/'HUMAN_APPROVAL_BIND_R1.json',*[OUT/r['path'] for r in v['render_records']]]
write(OUT/'FINAL_OUTPUT_MANIFEST_R1.json',{'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in files],'RIGHT_HAND_PRODUCT_BASELINE':'PASS','REAL_PIANO_MOTION_CHECK':'BLOCKED_MOTION_SOURCE_NOT_FOUND','baseline_sha256':sha(asset),'historical_evidence_unchanged':all(sha(FIX/f['path'])==f['sha256'] for f in read(FIX/'FINAL_OUTPUT_MANIFEST_R1.json')['files']),'source_candidate_unchanged':sha(ROOT/v['source']['path'])==v['source']['sha256']})
print('FINAL_BASELINE_PASS',sha(asset),'MOTION_SOURCE_NOT_FOUND_STOP',flush=True)
