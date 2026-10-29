import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,x):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def md(n,t):
 with (OUT/n).open('x',encoding='utf8') as f:f.write(t)
FILES={'A1':'A_BASIS_CANDIDATE_1_NOT_APPROVED.blend','A2':'A_BASIS_CANDIDATE_2_NOT_APPROVED.blend','B1':'B1_WEIGHTS_NOT_APPROVED.blend','B2':'B2_CORRECTIVE_NOT_APPROVED.blend'}
POSES=['NEUTRAL_REST','C1_0_433333','C1_1_100000','C1_2_600000','FIXED_GEOMETRY_PASS','C1_CORRECTIVE_ACTIVE']
NAMES=['原Rig中性 REST','C1 0.433333秒','C1 1.100000秒 / 食指ACTIVE A4','C1 2.600000秒','历史固定几何PASS / 自然性未批准','C1 0.885714秒 / 旧corrective激活']
records={k:{p:read(OUT/(k+'__'+p+'.json')) for p in POSES} for k in ['BASE',*FILES]}
contacts=read(OUT/'RIGHT16_ACTIVE48_SKIN_CONTACTS.json')
reopen=[]
for k,file in FILES.items():
 a=np.load(OUT/(k+'_EDIT.npz'));b=np.load(OUT/(k+'__C1_2_600000.npz'))
 err=float(np.linalg.norm(a['V']-b['V'],axis=1).max()*1000);assert err==0
 assert len(contacts[k])==48 and all(r['skin_contact_delta_mm']==0 and r['contact']['pass_prior_static_strict'] for r in contacts[k])
 assert all(not r['geometry_regression'] and r['outside_allowed_error_mm']==0 and r['S_skin_error_mm']==0 and r['left_skin_error_mm']==0 and r['contact_position_max_delta_mm']==0 for r in records[k].values())
 reopen.append({'candidate':k,'path':str(OUT/file),'sha256':sha(OUT/file),'reopened_evaluated_2_6_max_error_mm':err,'external_linked_libraries':False,'pose_action_rest_uv_and_non_authorized_signature_match':True})
save('SAVED_CANDIDATE_REOPEN_VERIFICATION.json',reopen)
before={r['path']:r['sha256'] for r in read(OUT/'PROTECTED_BEFORE.json')}
receipts=sorted(OUT.glob('*INPUT_RECEIPT.json'))
for p in receipts:
 receipt=read(p);assert receipt['all_unchanged'] and not receipt['piano_access']
 for r in receipt['files']:
  if r['path'] in before:assert before[r['path']]==r['before'],'BETWEEN_STAGE_INPUT_CHANGE'
  else:before[r['path']]=r['before']
checks=[]
for p,h in before.items():
 path=Path(p);assert path.is_relative_to(ROOT) and not path.is_relative_to(OUT)
 h1=sha(path);assert h==h1;checks.append({'path':p,'before':h,'after':h1,'unchanged':True})
save('PROTECTED_SHA256_BEFORE_AFTER.json',{'all_unchanged':True,'count':len(checks),'piano_directory_accessed':False,'files':checks,'input_receipts':[p.name for p in receipts]})
assessment={
 'A1':{'result':'PARTIAL','visual':'Small reduction of thumb-facing proximal contour; lateral-only trim compresses transition edges more than A2. Original coarse bend impression remains.','old_corrective_relative_coupling_unresolved':True,'prefer_for_next_independent_review':False},
 'A2':{'result':'PARTIAL','visual':'Slightly gentler local contour with less transition compression than A1; soft-tissue curvature retained. Improvement depends on original corrective activation.','old_corrective_relative_coupling_unresolved':True,'prefer_for_next_independent_review':True},
 'B1':{'result':'LOCAL_ASSET_POC_PASS_PENDING_HUMAN','visual':'Modest filling of lower first-web dent; normal web concavity and remaining coarse folds preserved. Rest geometry unchanged and no new collision/contact regression at executed samples.','prefer_for_next_independent_review':True},
 'B2':{'result':'PARTIAL','visual':'Direct static relief; constant manual activation adds 0.605mm deformation to already convex neutral skin. Neutral bulge is a shape-regression concern pending Human judgement; no new collision/inversion measured.','general_corrective_trigger_implemented':False,'manual_value_all_tests':1.,'prefer_for_next_independent_review':False}}
save('CANDIDATE_ASSESSMENT.json',{'overall':'PARTIAL','candidates':assessment,'human_naturality_approved':False,'no_combined_AB_asset':True,'S_independent_issue_unchanged':True,'new_collision_or_contact_regression_measured':False,'shape_quality_caveats':['A effect attenuated about94% with frozen corrective active','B2 adds neutral bulge and has no automatic trigger'],'stop':'STOP — HUMAN REVIEW'})
visual={
 'NEUTRAL_REST':['略收窄，保留弧度','局部更柔和，仍有粗面感','与基线完全一致','额外外凸约0.605mm，回退疑虑'],
 'C1_0_433333':['轻微改善，边界收紧','轻微改善，未全拉直','下部折陷减轻','折陷减轻；手动1'],
 'C1_1_100000':['轻微改善，A4触键保持','轻微改善，A4触键保持','折陷减轻，仍有折面','折陷减轻；手动1'],
 'C1_2_600000':['侧缘收整，仍有折线感','初步优于A1，改善有限','局部较饱满，正常凹面保留','静态填充略强，无触发机制'],
 'FIXED_GEOMETRY_PASS':['轻微改善，自然性未批准','轻微改善，自然性未批准','下部折陷减轻，S不变','下部折陷减轻，S不变'],
 'C1_CORRECTIVE_ACTIVE':['效果衰减约94%，不稳定','效果衰减约94%，不稳定','仍有局部改善，最大位移0.742mm','仍有局部改善；手动1']}
table='''# 多姿态比较

五种指定姿态，加一个原C1动作中原corrective最高启用的活动接触样本；没有创建新动作。
“新增几何0”指相对同姿态未修改基线，无新增非邻接自交、跨手碰撞、琴键相交／深度增加或局部面翻转；不等于原C1全手无缺陷。
所有候选S核心、左手及授权范围外皮肤坐标误差均为0。

| 状态 | A1视觉 | A2视觉 | B1视觉 | B2视觉 | 新增几何 / 皮肤触点变化 |
|---|---|---|---|---|---|
'''
for p,n in zip(POSES,NAMES):table+='| '+n+' | '+' | '.join(visual[p])+' | 0 / 0mm |\n'
table+='''
中性REST不作演奏触键合格宣称。A的激活态效果衰减、B2的中性凸起，不能被“无新增碰撞”掩盖。

| 候选 | 六态局部面面积比 | 六态边长比 | 旧corrective激活态最大位移mm | 右手活动皮肤触点 |
|---|---|---|---|---|
'''
for k in FILES:
 rs=list(records[k].values());ar=[min(r['deformation']['face_area_ratio_min_max'][0] for r in rs),max(r['deformation']['face_area_ratio_min_max'][1] for r in rs)];er=[min(r['deformation']['edge_length_ratio_min_max'][0] for r in rs),max(r['deformation']['edge_length_ratio_min_max'][1] for r in rs)]
 table+=f"| {k} | {ar[0]:.4f}–{ar[1]:.4f} | {er[0]:.4f}–{er[1]:.4f} | {records[k]['C1_CORRECTIVE_ACTIVE']['max_skin_shift_mm']:.6f} | 48/48，位置变化0 |\n"
table+='\n面积、边长与法向射线厚度代理是形变描述，不是人体阈值、解剖评分或体积认证。每点厚度代理、碰撞对、实际键体三角形深度证书见各候选__姿态.json。\n'
md('MULTIPOSE_COMPARISON.md',table)
report=f'''# HANDS_LOCAL_SKIN_ASSET_REPAIR_POC_R1 — ROI批准后的隔离资产实验

总结果：**PARTIAL**。A1/A2：**PARTIAL**；B1：**LOCAL_ASSET_POC_PASS_PENDING_HUMAN**；B2：**PARTIAL**。最终状态：**STOP — HUMAN REVIEW**。

制作4个真实、独立、未批准的Blend候选，均从未修改原C1重新打开并复制右手mesh数据。A未叠到B，B1未混合B2。正式资产未修改，S仅观察。

## 实际编辑

编号唯一来源为上级CONFIRMED_ROI_PROPOSAL.json，本轮授权另存HUMAN_AUTHORIZATION.txt。原C1 2.600000秒再次核验：实际对象RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH.002，3300顶点／3298原生面；逐点与ORIGINAL诊断快照完全相同。面序、方向、核心连通性、过渡与固定边界均匹配。编号从0开始。

A1、A2均只修改10个授权Basis顶点：158、656、1074、1075、1076、2073、2192、2576、2577、2591。外围、其他顶点、UV、拓扑、flat标志、权重、骨骼、rest数据和Action保持。A1采用有限侧向收整，2.6秒最大求值位移0.454627mm；A2采用单次局部法向形体收整，最大0.529896mm，未做全轴平滑或把近节拉成直圆柱。两版从相同基线分别制作。A2过渡初步比A1温和，但改善有限，原粗面和大尺度曲率仍在。

**A存在明确的旧corrective相对差分耦合。** 原FIRST_WEB_OPPOSITION_CREASE_R1的绝对点坐标和driver未改写。Basis变化使该key相对差分在A的10点变化，A1最大0.456314mm、A2最大0.532155mm，详见A*_EDIT_RECEIPT.json。旧key值为v时，Basis修补约剩(1−v)·δBasis。补查原C1 0.88571375秒，原key=0.942156：A1/A2修补只剩0.026306／0.030619mm，约94%被抵消。没有通过同步改写冻结corrective来掩盖问题；A不能宣称稳定通用修复。

B1只改变1375、1376、1444、2793四点的既有权重，将少量THUMB_CMC_R权重转移到WRIST_R，其他骨组逐项不变。不是平均分配。

| 顶点 | CMC→WRIST转移量 |
|---|---|
|1375|0.025|
|1376|0.060|
|1444|0.015|
|2793|0.030|

完整真实前后权重见B1_EDIT_RECEIPT.json；没有Basis或原corrective编辑，权重总和保持，归一化误差小于2e−7。2.6秒最大位移0.546534mm，六态最大0.742265mm，中性REST位移严格为0。下部内折小幅减轻，正常虎口凹面与其他粗面折线保留。B1是本轮更适合优先审核的B方法。

B2从另一未修改基线新增临时key：EXPERIMENT_ROI_B_RELIEF_R1_NOT_APPROVED。仅改1375、1376、1444、2793四点，在2.6秒的向外软组织补偿目标分别0.18、0.60、0.12、0.22mm。Basis、原key坐标／差分和driver均不动，没有新driver。六态和48活动采样均手动固定value=1，绝非自动触发机制。2.6秒最大位移0.600069mm。静态填充更直接，但中性也发生0.605337mm局部形变，原凸面进一步外凸，有形态回退疑虑；因此仅为方法验证PARTIAL。没有测得新增碰撞或面翻转，不把形态疑虑冒充已证实碰撞。

描述量v1376有符号一环法向残差在2.6秒由1.177536mm变为B1的0.646626mm、B2的0.576083mm；中性基线约−0.4368mm，B1不变，B2约−0.9595mm。这不是人体评分、体积测量或“越小越好”目标。自然性初评同时查看真实俯视、侧视、反向、骨段与软组织上下文、六态稳定性，最终由Human判断。

## 回归与安全

每个候选完成：原Rig中性REST；原C1 0.433333、1.100000、2.600000秒；历史固定几何PASS；旧corrective激活的原C1 0.885714秒，共6态。中性测试保持C1 2.6秒对象/root变换，临时将Armature置REST；没有改rest骨数据、Pose Bone或Action。所有候选保存状态仍为原C1 2.6秒POSE。

每状态重新读取actual evaluated mesh及实际三角化，检查全右手与实际键体的BVH相交、三角面在凸键体中的内部深度上下界、全手非邻接自交、跨手碰撞。左手逐点与基线相同。没有沿用旧PASS。六态均未发现新增碰撞对、键体深度增加或局部面翻转。局部面面积、边长、法向射线厚度代理逐项保留。A1局部边长最多收缩约10.17%，A2约4.52%，是A1过渡较紧的风险依据，不是人体阈值。没有声称量得真实软组织厚度或体积。

**固定几何PASS姿态重新计算结果，四个候选完全相同：**

| 项目 | 结果 |
|---|---|
|A♯4全手精确表面净空|0.282075256mm|
|A4全手精确表面净空|1.487484568mm|
|C♯5全手精确表面净空|1.234825804mm|
|A♯4/A4/C♯5侵入|0；BVH对0|
|G4拇指真实skin pad|可奏区域内；水平miss0，gap0.785998408mm|
|左手B3真实skin pad|可奏区域内；水平miss0，gap0.506925902mm|
|新增自交／跨手碰撞|0／0|

精确净空包括顶点到三角面及边到边距离。G4原活动触键允许的皮肤相交保留，不冒充全手零侵入或取消触键。以上仅覆盖所测姿态，不代表Human自然性批准。

原C1既有缺陷未被局部资产修补消除：0.433333秒仍有G♯4侵入约4.3283mm；1.1秒G4约2.7130mm的既有非目标关系保留；2.6秒A4约0.7450mm、A♯4约5.6371mm、C♯5约4.2527mm侵入保留。它们与同姿态基线比较后无新增，未用总PASS遮蔽历史问题。

**右手16音×3活动时刻=48个真实skin pad采样已逐候选重算。** 时间为NOTE_ON+35ms、活动中点、NOTE_OFF前10µs。四候选分别48/48通过既有严格静态contact检查：点在可奏面内，水平≤0.03mm，绝对垂直gap≤3mm，比旧正式水平2mm更严。皮肤触点位置相对基线最大误差0mm。不是只用刚性marker替代真实皮肤。48采样仅是触点回归，不是48次全手碰撞证明或连续全时段认证。

## S与限制

S核心1245、1246、2728、2729的全部顶点／权重没有编辑。六态所有候选S核心求值误差为0；侧视原有局部折面观感仍在，保留为独立待审问题。B邻面／阴影微变不等于解决S，没有扩张S或其他手指ROI。

没有新增骨骼、rest编辑、关节调整、MIDI／指法／琴键Action修改、连续动画、组合资产或大型求解器。实际显示保留flat shading，没有用smooth shading遮蔽几何。

## 交付与保护

仅7张核心图：A_OFFICIAL_OVERHEAD.png、B_OFFICIAL_OVERHEAD.png、A_LOCAL_MULTIVIEW.png、B_LOCAL_MULTIVIEW.png、A_MULTIPOSE.png、B_MULTIPOSE.png、S_MULTIPOSE.png。

同组／同行相机矩阵、投影和倍率已核对相同。多姿态局部镜头仅依据BASE中心平移，各候选不独立美化。A真侧视方向相对原C1骨平面；相机采用原诊断的55mm近距离、clip_start=0.1mm避免远处前景键遮挡，没有隐藏琴键。遮挡工作图和排版草稿留存，不作为核心交付。

渲染将已验证actual evaluated坐标逐点复制到显示网格，保留原UV／材质／flat标志，没有重塑或修图。候选重开后2.6秒与建模时网格误差均0。所有非授权属性、rest与Action内容摘要匹配。

四个独立候选：
- A_BASIS_CANDIDATE_1_NOT_APPROVED.blend
- A_BASIS_CANDIDATE_2_NOT_APPROVED.blend
- B1_WEIGHTS_NOT_APPROVED.blend
- B2_CORRECTIVE_NOT_APPROVED.blend

多姿态视觉／几何／回退表见MULTIPOSE_COMPARISON.md；完整点坐标、权重与key差分见各EDIT_RECEIPT.json和EDIT.npz；逐态真实网格、碰撞对、键体深度证书、接触与相机来源全部保留。

冻结源与实际读取输入共{len(checks)}项前后SHA256全部不变，见PROTECTED_SHA256_BEFORE_AFTER.json。原C1仍为d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7。独立piano目录未访问。此前定位图、JSON、停止记录、历史FAIL未覆盖；新写入仅在本子目录。

## 六个结论

1. A轮廓轻微改善，A2初步优于A1；但旧corrective会抵消效果，结果PARTIAL。
2. B下部折陷局部改善，并非整个虎口或S已修复。
3. B1获得随骨运动改善、中性零位移，所测几何／触点回归通过待Human；B2仅证明手动补偿可行，有中性凸起和触发未定义问题。
4. S独立观感未解决，核心坐标完全不变。
5. 没有测得新增碰撞／接触回退；存在A激活态改善衰减、B2中性额外外凸的形态回退疑虑，不能写成全姿态自然性PASS。
6. **暂不进入A+B组合。** 先由Human判断A2、B1的实际幅度；A还需单独明确新Basis与旧corrective差分的兼容策略。本轮不继续改写冻结key，不替换正式资产。

**STOP — HUMAN REVIEW**
'''
md('TECHNICAL_REPORT.md',report)
review=f'''# Human审核

总结果PARTIAL；A1/A2 PARTIAL；B1 LOCAL_ASSET_POC_PASS_PENDING_HUMAN；B2 PARTIAL。所有候选未批准，正式资产未替换。

1. **A2初步比A1自然，但改善有限。** 保留近节弧度，局部过渡较温和。旧corrective在0.885714秒启用0.942时，A效果被抵消约94%，尚不稳定。
2. **B1更适合优先独立审核。** 4点少量CMC→WRIST转移，2.6秒最大位移约0.547mm，中性位置不变；局部折陷减轻，正常虎口凹面保留。
3. **B2只是手动方法验证。** 静态填充略直接，但全部测试value=1；中性增加约0.605mm额外外凸，有形态回退疑虑，也没有自动触发机制。
4. **S仍为独立待审问题。** 核心顶点与权重未改，六态求值位置不变；B邻面变化不能证明S解决。
5. **未发现新增碰撞／触点回退。** 四候选各完成6态网格检查、右手16音48活动皮肤触点采样。固定姿态A♯4净空0.282075mm保持。原C1既有穿键、A效果衰减、B2中性凸起均明确保留。
6. **暂不进入A+B组合。** 请先审核A2、B1幅度；A的Basis／原corrective兼容问题尚未解决。没有正式替换或组合资产。

先看：
- [A局部俯视与真侧视](A_LOCAL_MULTIVIEW.png)
- [B局部／侧视／反向](B_LOCAL_MULTIVIEW.png)
- [A六态](A_MULTIPOSE.png)、[B六态](B_MULTIPOSE.png)、[S侧视](S_MULTIPOSE.png)
- [多姿态比较表](MULTIPOSE_COMPARISON.md)、[技术报告](TECHNICAL_REPORT.md)

四个独立Blend名称均含NOT_APPROVED。冻结源与实际读取输入{len(checks)}项哈希不变，独立piano目录未访问。

**STOP — HUMAN REVIEW**
'''
md('HUMAN_REVIEW.md',review)
save('RESULT.json',{'result':'PARTIAL','per_candidate':{k:r['result'] for k,r in assessment.items()},'source_C1_modified':False,'human_approved':False,'representative_pose_count':6,'right_contact_samples_per_candidate':48,'new_collision_regressions':0,'A_relative_corrective_coupling_unresolved':True,'B2_trigger_implemented':False,'S_core_changed':False,'protected_files':len(checks),'all_original_inputs_unchanged':True,'combined_asset_created':False,'stop':'STOP — HUMAN REVIEW'})
artifacts=[*FILES.values(),'TECHNICAL_REPORT.md','HUMAN_REVIEW.md','MULTIPOSE_COMPARISON.md','RESULT.json','CANDIDATE_ASSESSMENT.json','PROTECTED_SHA256_BEFORE_AFTER.json','SAVED_CANDIDATE_REOPEN_VERIFICATION.json']+[Path(r['path']).name for r in read(OUT/'CORE_REVIEW_IMAGE_MANIFEST.json')['images']]
save('DELIVERY_SHA256.json',[{'path':str(OUT/n),'sha256':sha(OUT/n)} for n in artifacts])
print(json.dumps({'result':'PARTIAL','per_candidate':{k:r['result'] for k,r in assessment.items()},'protected_files':len(checks),'all_original_inputs_unchanged':True,'stop':'STOP — HUMAN REVIEW'}))

