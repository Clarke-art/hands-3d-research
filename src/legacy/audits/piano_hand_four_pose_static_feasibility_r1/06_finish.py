from pathlib import Path
import json,hashlib,html
import PIL.Image as Image
from PIL import ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';R2=P.parent/'real_piano_reference_gap_closure_and_static_posture_probe_r2'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
geo=read(P/'STATIC_GEOMETRIC_MEASUREMENTS_R1.json');clear=read(P/'HAND_KEYBOARD_CLEARANCE_R1.json');sol=read(P/'SOLVED_STATIC_POSES_R1.json');scene=read(P/'STATIC_SCENE_MANIFEST_R1.json');left=read(P/'LEFT_OCTAVE_POSE_COMPARISON_R1.json');right=read(P/'RIGHT_FSHARP_POSTURE_R1.json')
visual={
 'review_type':'AGENT_NORMAL_VIEW_PRECHECK_NOT_HUMAN_APPROVAL','reviewed_views':{p:['TEACHING_TOP','SIDE_OBLIQUE','REASONABLE_CLOSE'] for p in geo},'views_selected_before_inspection':True,
 'observations':{
  'L1':['小指指垫接近 D2 前部内侧，拇指在 D3 上方准备。三闲置指沿 RSSF 曲度延伸、相互留间距，未见统一钩爪或强制拉直。','侧斜视/近景未见掌部压入键盘、腕部反折或明显新网格崩塌；70mm wrist root 和有界旋转的自然程度需 Human 判断。','小指 MCP 增量触及 32° 预设边界，不能将候选称为已校准生理手型。'],
  'L2':['拇指皮肤 pad 在 D3 前部内侧，小指处于 D2 准备；三闲置指与 L1 几乎相同。','共同 root 无平移/旋转；拇指弯曲集中到 MCP/IP，触及 25°/18° 工程边界，需 Human 判断是否显得紧张。','未见明确反关节、掌腕压键或新的大面积塌陷；静态接触成立不能证明交替运动自然。'],
  'R1':['五指呈不同前后/高度布局，中指靠近 F#5 黑键；未强迫同时触键。','正常近景显示食指/无名指与相邻黑键边缘空间挤压；D#5/G#5 全网格筛查仍命中，风险不能排除，保守 FAIL_CLEARANCE。','掌腕自身没有深度穿键筛查命中；该事实不能抵消闲置指邻键风险。'],
  'R2':['中指固定 pad 和皮肤 pad 均在 F#5 真实顶面，较 R1 下降约 6.86mm，并适度改变曲度；其他四指和 root 几乎不变。','食指/无名指邻 D#5/G#5 的风险继承，不以中指接触成功掩盖。','没有明显腕部大角度扭转或反关节，但右手整体净空不能 PASS。']},
 'new_obvious_reverse_joint_or_large_mesh_collapse':False,
 'render_boundary':'Workbench studio object color/cavity display emphasizes the existing mesh facets. No smoothing/topology/material/driver editing. These images review posture/contact, not finished realistic skin material. Not a real human performance reference.',
 'full_triangle_or_hidden_geometry_forensics_performed':False,
 'normal_side_view_limit':'Side and close views expose local crowding; 3-vertex conservative box hits are not a certified full-triangle penetration proof. Retain the risk and FAIL_CLEARANCE rather than upgrading it to PASS.',
 'human_approval':False,'dynamic_motion_proven':False}
dump('HUMAN_VISIBLE_PRECHECK_R1.json',visual)
for pose,g in geo.items():
 g['HUMAN_VISIBLE_NATURALNESS']='HUMAN_PENDING' if pose.startswith('L') else 'FAIL_NEIGHBOR_CLEARANCE_RISK'
 g['classification']='PASS_CANDIDATE' if pose.startswith('L') else 'FAIL_CLEARANCE'
 g['ACTIVE_PAD_CONTACT']='PASS' if g['all_required_fixed_pad_contacts_pass'] and g['all_required_skin_pad_contacts_pass'] else 'FAIL'
 g['IDLE_FINGER_CLEARANCE']='PASS_SCREEN' if clear['poses'][pose]['idle_digit_deep_key_vertices']==0 else 'FAIL_RISK'
 g['PALM_CLEARANCE']='PASS_SCREEN' if clear['poses'][pose]['palm_deep_key_vertices']==0 else 'FAIL_SCREEN'
 g['WRIST_CLEARANCE']='PASS_SCREEN' if clear['poses'][pose]['wrist_deep_key_vertices']==0 else 'FAIL_SCREEN'
 g['NEIGHBOR_KEY_INTERFERENCE']='PASS_SCREEN' if not clear['poses'][pose]['key_intersections'] else 'FAIL_RISK'
 g['JOINT_POSTURE']='BOUNDED_NO_OBVIOUS_REVERSE / HUMAN_PENDING'
 g['observations']=visual['observations'][pose]
left['same_reasonable_octave_configuration']='UNCERTAIN_HUMAN_PENDING; exact shared root and prepared endpoints verified; naturalness at saturated engineering bounds not certified'
left['static_poses_individually_feasible']='PASS_CANDIDATE_PENDING_HUMAN'
right['naturalness']='FAIL_NEIGHBOR_CLEARANCE_RISK; middle contact itself passes';right['neighbor_risk']={'D#5':{'vertices':1,'depth_mm':3.6660321466357813},'G#5':{'vertices':2,'depth_mm':5.618622567477952}}
dump('LEFT_OCTAVE_POSE_COMPARISON_R1.json',left);dump('RIGHT_FSHARP_POSTURE_R1.json',right)
results={'phase':'PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1','candidate_count':1,'candidate_created':True,'policy_sha256':sha(P/'STATIC_POSTURE_POLICY_R1.json'),'candidate_sha256':sha(P/'STATIC_POSTURE_CANDIDATE_R1.blend'),'poses':geo,'solver_diagnostics':sol['solver_diagnostics'],'FINAL_STATUS':'STATIC_FEASIBILITY_PARTIAL','failure_layers':{'technical_runtime':'NONE: all four saved/reopened/rendered','IK_SOLVER_FAILURE':'NOT_OBSERVED: both shared-root solves converged','POSTURE_CONSTRAINT_LIMIT':'One fixed proxy/prior policy yielded right neighbor clearance risks and left bound saturation; no follow-up tuning','GEOMETRY_LIMIT':'NOT_PROVEN; no claim frozen hand absolutely unreachable','REFERENCE_EVIDENCE_LIMIT':'Still incomplete but not an execution blocker under current Human authorization'},'dynamic_transition_proven':False,'human_approval':False}
dump('STATIC_POSTURE_RESULTS_R1.json',results)
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed,changed
expected={'RIGHT_R2':('production_spec/right_hand_product_baseline_r2/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend','c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0'),'LEFT_R1':('production_spec/left_hand_product_baseline_r1/LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend','54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7'),'RIGHT_R1_fallback':('production_spec/right_hand_product_baseline_r1/RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend','4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2')}
hands={n:{'path':str(ROOT/p),'expected_sha256':v,'current_sha256':sha(ROOT/p),'matches':sha(ROOT/p)==v} for n,(p,v) in expected.items()};assert all(x['matches'] for x in hands.values())
authority=read(OLD/'KEYBOARD_AUTHORITY_R1.json');piano={n:{'path':authority[n],'current_sha256':sha(Path(authority[n])),'expected_sha256':authority[k],'matches':sha(Path(authority[n]))==authority[k]} for n,k in [('source_manifest','KEYBOARD_SOURCE_SHA256'),('runtime','runtime_sha256')]};assert all(x['matches'] for x in piano.values())
protection={'status':'UNCHANGED','checked_file_count':len(before),'changed_files':[],'hand_baselines':hands,'piano_authority':piano,'candidate_intrinsic_identity':scene['intrinsic_after_pose_save_reopen_reset_checks'],'candidate_shader_or_mesh_changes':'Workbench object color only; immutable source components match before/after pose/reset','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True,'production_pointer_changed':False,'new_continuous_actions':0,'candidate_count':1,'static_scene_count':4,'scope':'Inherited full protected corpus plus both immediately preceding audit directories; exact path/hash list in PROTECTED_INPUTS_BEFORE_R1.json. Not a full unrelated-drive claim.'}
dump('FINAL_ASSET_PROTECTION_R1.json',protection)
questions=[('Q1','四个静态候选真实生成？','YES','一个 blend 内四独立静态场景，保存后重新打开并渲染。'),('Q2','左手小指 D2 满足接触？','YES','固定 pad 0.586mm，皮肤 pad 0.601mm，正确可奏区域。'),('Q3','左手拇指 D3 满足接触？','YES','固定/皮肤 pad 1.556mm，正确可奏区域。'),('Q4','左手中间三指自然？','HUMAN_PENDING','Agent 未见统一钩爪/强制拉直；保留 RSSF 不同曲度，待 Human。'),('Q5','左手 L1/L2 掌腕合理？','HUMAN_PENDING','共同 root；70mm root 高度和部分关节边界饱和待审。'),('Q6','左手掌部无明显键体碰撞？','YES','深度>3mm 掌部命中0；正常侧斜视/近景未见压键。'),('Q7','右手五指准备自然？','NO','食指/无名指邻黑键干扰风险未排除。'),('Q8','右手中指 F#5 正确触键？','YES','固定 pad 0.497mm、皮肤 pad 0.506mm，正确黑键可奏面。'),('Q9','右手掌腕及其他四指合理？','NO','掌腕自身筛查无深度穿键，但另外两指邻键风险不能抵消。'),('Q10','四姿态有明显新变形或反关节？','NO','正常三视图未见明确反关节/新大面积塌陷；源组件身份匹配。'),('Q11','左手两姿态有合理共同八度关系？','UNCERTAIN','root 位移/转角均0，准备区域成立；边界饱和的自然性待 Human，过渡未证。'),('Q12','必须修改正式 mesh/rig 的证据？','NO','单次有界政策结果，不是硬几何不可达证明。'),('Q13','最终状态','STATIC_FEASIBILITY_PARTIAL','左手为候选通过待 Human；右手净空失败。')]
status={'Q1_Q13':{q:{'question':t,'answer':ans,'reason':why} for q,t,ans,why in questions},'STATIC_CANDIDATE':'CREATED','LEFT_L1_STATUS':'PASS_CANDIDATE','LEFT_L2_STATUS':'PASS_CANDIDATE','RIGHT_R1_STATUS':'FAIL_CLEARANCE','RIGHT_R2_STATUS':'FAIL_CLEARANCE','LEFT_OCTAVE_SHARED_POSTURE':'SHARED_ROOT_VERIFIED / NATURALNESS_HUMAN_PENDING','LEFT_IDLE_FINGERS':'HUMAN_PENDING','RIGHT_FSHARP_CONTACT':'PASS_FIXED_AND_SKIN_PAD','PALM_WRIST_CLEARANCE':'PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK; RIGHT_NEIGHBOR_CLEARANCE_FAIL','HUMAN_VISIBLE_QUALITY':'PARTIAL / LEFT_HUMAN_PENDING / RIGHT_CLEARANCE_RISK','FINAL_STATUS':'STATIC_FEASIBILITY_PARTIAL','HAND_BASELINES_UNCHANGED':'YES','PIANO_BASELINE_UNCHANGED':'YES','STOP':'HUMAN REVIEW'}
dump('FINAL_STATUS_R1.json',status)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);titlefont=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',36)
viewlabels={'TEACHING_TOP':'教学顶视','SIDE_OBLIQUE':'侧斜视','REASONABLE_CLOSE':'合理近景'};evidences=[]
for side,poses,name,title in [('L',['L1','L2'],'EVIDENCE_LEFT_L1_L2_R1.png','左手八度 · 新静态候选'),('R',['R1','R2'],'EVIDENCE_RIGHT_R1_R2_R1.png','右手五指与 F# · 新静态候选')]:
 im=Image.new('RGB',(2400,1430),(243,240,234));draw=ImageDraw.Draw(im);draw.text((24,18),title+' · DESIGN_ONLY',font=titlefont,fill=(38,42,46));draw.text((24,76),'固定政策，一次求解；自然性未获 Human 批准，动态过渡未验证。',font=small,fill=(91,84,77))
 for r,pose in enumerate(poses):
  y=122+r*647;draw.text((24,y),pose+'  '+geo[pose]['classification'],font=font,fill=(34,75,77) if side=='L' else (141,55,43))
  for col,view in enumerate(viewlabels):
   x=col*800;draw.text((x+24,y+44),viewlabels[view],font=small,fill=(76,70,65));src=Image.open(P/'renders'/f'{pose}__{view}.png').convert('RGB');src.thumbnail((776,570));im.paste(src,(x+12,y+80))
 im.save(P/name);evidences.append({'name':name,'source_poses':poses,'views':list(viewlabels),'sha256':sha(P/name)})
im=Image.new('RGB',(2200,1860),(243,240,234));draw=ImageDraw.Draw(im);draw.text((22,20),'掌腕与邻键净空 · 四姿态正常侧斜视',font=titlefont,fill=(38,42,46))
for i,pose in enumerate(['L1','L2','R1','R2']):
 x=(i%2)*1100;y=85+(i//2)*880;draw.text((x+22,y),pose+' · '+geo[pose]['classification'],font=font,fill=(38,70,72));src=Image.open(P/'renders'/f'{pose}__SIDE_OBLIQUE.png').convert('RGB');src.thumbnail((1070,810));im.paste(src,(x+15,y+52))
im.save(P/'EVIDENCE_SIDE_CLEARANCE_R1.png');evidences.append({'name':'EVIDENCE_SIDE_CLEARANCE_R1.png','source_poses':['L1','L2','R1','R2'],'views':['SIDE_OBLIQUE'],'sha256':sha(P/'EVIDENCE_SIDE_CLEARANCE_R1.png')})
dump('EVIDENCE_IMAGE_PROVENANCE_R1.json',{'source_candidate_sha256':scene['candidate_sha256'],'source_render_manifest_sha256':sha(P/'RENDER_MANIFEST_R1.json'),'sheets':evidences,'external_photos_used':False,'image_composition':'Only labels and whole-frame resizing of actual candidate renders; no retouch, deformation, masked collisions or AI image generation.'})
rows='\n'.join(f'|{q}|{t}|**{ans}**|{why}|' for q,t,ans,why in questions)
summary='\n'.join(f'{k} = {v}' for k,v in status.items() if k!='Q1_Q13')
report=f'''# PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT

2026-10-08 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = STATIC_FEASIBILITY_PARTIAL**。本轮已按 Human 新授权真实生成一个包含四个静态场景的候选，不再用外部视频缺失阻止实验。L1/L2 为 PASS_CANDIDATE，等待 Human 自然度审核；R1/R2 为 FAIL_CLEARANCE，右手食指/无名指邻黑键风险保留。全部正式资产保持不变。

## 授权、继承与事前政策

继承前两轮参考清单、八类姿态合同、88键实际几何、canonical RSSF 网格、固定指腹 marker 与旧失败图。REFERENCE_SEARCH_STOP_LOSS=REACHED，本轮未重新联网搜索。原始参考不足仍明确保留，但 Human 已授权 GEOMETRIC / PRODUCT FEASIBILITY PROBE；不是完整人体生物力学证明或完整演奏生成。

求解前锁定 [STATIC_POSTURE_POLICY_R1.json](STATIC_POSTURE_POLICY_R1.json)，SHA256 `{sha(P/'STATIC_POSTURE_POLICY_R1.json')}`；锁同时记录求解脚本 SHA。工程 bounds 未根据结果放宽，既有 3mm/2mm 接触容差不变。正向 flex + 基部 spread 从已经弯曲的 RSSF rest 增量设置，不称为人体生理极限。左手闲置三指强 prior、较小增量边界，避免统一伸直/钩爪。两手每对共享一个 XYZ/yaw/pitch/roll 变换，使用现有21骨旋转；没有新 helper bone、逐顶点修改、scale 或 corrective。

一套政策内对左/右共享-root 的两姿态各联合求解一次，共一个四姿态候选。两次求解分别 {sol['solver_diagnostics']['L']['nfev']} / {sol['solver_diagnostics']['R']['nfev']} evaluations 收敛，初始化各1次、重启0次、参数 sweep0次。蒙皮 proxy 来自冻结现有权重，用于计划；最终接触/净空来自保存后重新打开的实际 Blender 皮肤，未复用旧动态 IK。

## 新静态候选与实际接触

[STATIC_POSTURE_CANDIDATE_R1.blend](STATIC_POSTURE_CANDIDATE_R1.blend) 内为 STATIC_L1/L2/R1/R2，frame_start=frame_end=1，没有绑定连续 Action。每场景使用正式88键表的全部原顶点/三角面；相机只取局部产品尺度。琴键保持静置，此轮证明静置表面接触，不声称已证明按键下沉、触键力量或发声过程。

|姿态|任务|固定 pad 垂直差|实际皮肤 pad 差|可奏区域|分类|
|---|---|---:|---:|---|---|
|L1|小指 D2 / 拇指 D3 准备|0.586mm|0.601mm|inside|PASS_CANDIDATE|
|L2|拇指 D3 / 小指 D2 准备|1.556mm|1.556mm|inside|PASS_CANDIDATE|
|R1|D5/E5/F#5/G5/A5 五指准备|无主动触点|无强制同时触键|五准备区域成立|FAIL_CLEARANCE|
|R2|中指 F#5 / 其他四指准备|0.497mm|0.506mm|inside|FAIL_CLEARANCE|

三个主动 pad 水平误差均0，皮肤点也在真实可奏区域。R1 五指准备 gap 分别约9.199、6.862、7.356（相对黑键顶）、6.941、9.754mm；R2 中指下降约6.859mm 后触 F#5，另外四指与共同 root 几乎不变。黑键正式高差15.444mm、前端后移49.421mm均沿用。准备高度/前后位置没有排成同一条线。指序仍 DESIGN_PROVISIONAL，未称教师批准真值。

## 左手八度与三闲置指

L1/L2 root 相差 **0mm / 0°**。两姿态 thumb–little pad 实际空间跨度分别 **{left['actual_pad_span_mm']['L1']:.3f} / {left['actual_pad_span_mm']['L2']:.3f}mm**。D2/D3中心距167.569mm不是唯一触点距：使用键面前部内侧位置，记录实际坐标，不改变琴键或手尺度。L1拇指准备 gap约8.048mm，L2小指准备 gap约6.926mm。

三闲置指增量和外观在两姿态几乎相同，Agent 三视图未见明显统一钩爪/强迫拉直。左手 root z=70mm、roll=-6°，L1 little MCP=32°、L2 thumb MCP/IP=25°/18° 达到锁定工程边界；Human 须判断这是否自然或显得紧张。相同 root 不自动证明自然，拇指最大关节增量差约17.223°、小指约11.775°也未验证连续过渡。

共同配置关系结论为 **UNCERTAIN / HUMAN_PENDING**，并非八度动态演奏通过。[LEFT_OCTAVE_POSE_COMPARISON_R1.json](LEFT_OCTAVE_POSE_COMPARISON_R1.json) 保留全部接触、准备、root 和关节差。

## 掌腕与右手邻键净空

使用保存后3300顶点评估，对所有88键实际矩形部件做 >3mm 深度的 vertex-volume 筛查，辅以键面投影距离和正常侧斜视/近景。没有恢复复杂 hidden-geometry forensic；没有宣称完整三角碰撞认证。

|姿态|深度穿键顶点|掌部命中|腕部命中|结论|
|---|---:|---:|---:|---|
|L1|0|0|0|通过有限机器筛查；正常视角未见掌腕压键|
|L2|0|0|0|通过有限机器筛查；正常视角未见掌腕压键|
|R1|3|0|0|食指邻 D#5、无名指邻 G#5 风险保留|
|R2|3|0|0|同样风险，F# 接触成功不能抵消|

右手 D#5 命中1顶点，盒内深度3.666mm；G#5命中2顶点，深度5.619mm。正常近景仍见边缘空间挤压，风险不能排除，保守判 FAIL_CLEARANCE。它不是宣称经全三角算法证实重大穿透。掌/腕自身无深度筛查命中；左手掌投影最小gap约7.187mm，右手约7.279mm；腕部没有投影落在实际键面，不把该 null 值写成0mm。

## 可见自然性与失败层级

四姿态12个正常视角已逐一检查。未见明确反关节或新大面积网格塌陷；左手曲度与掌腕仍待 Human。右手接触/准备局部可测成立，但邻键风险导致整体未通过。画面为 Workbench 姿态查看，既有分面被 studio/cavity显示强调；没有网格 smoothing 或真实皮肤材质升级，不作为真人参考图。

技术阻断 NONE；IK_SOLVER_FAILURE 未观察（两次联合解收敛）；当前归因是单次固定姿态/代理净空政策的限制，保留左手边界饱和与右手邻键风险。**GEOMETRY_LIMIT 未证明**，没有必须重建正式 hand mesh/rig 的证据。不再调参或生成第二候选。

## Human-visible 审核与资产保护

[review.html](review.html) 支持切换四姿态及三视图，显示接触/净空/自然度不同状态，提供原始真人来源链接、旧失败对比与三个必要证据总图。未嵌入外部照片；本轮全部新图来自实际候选，非AI手型或NOT_RUN占位。

三张证据图：[左手](EVIDENCE_LEFT_L1_L2_R1.png)、[右手](EVIDENCE_RIGHT_R1_R2_R1.png)、[侧面净空](EVIDENCE_SIDE_CLEARANCE_R1.png)。共12个唯一原始角度，合成3张总图；没有视频、完整3.4秒动作、音频重制、PianoVAM或Web正式集成。

最终保护检查覆盖 **{len(before)} 个冻结/继承输入**，变化0；三份手 SHA 与用户指定值一致。候选四姿态中，pose→保存→重新打开→仅内存neutral 的完整 intrinsic 身份均匹配导入前，骨数21/顶点3300不变。钢琴权威、production pointers、MIDI、指法、音频、旧失败资产及前两轮文件未改。详见 [FINAL_ASSET_PROTECTION_R1.json](FINAL_ASSET_PROTECTION_R1.json)。最大保存后FK差约0.000303mm、最大pad–skin漂移约0.039mm。

## Q1–Q13

|编号|问题|答案|依据|
|---|---|---|---|
{rows}

## 停止状态

```text
{summary}
```

**STOP — HUMAN REVIEW**。候选与失败视角保持供审。未自动进入连续演奏动作生成；静态接触和同一 root 不能升级为动态可行性或教师批准。
'''
(P/'PIANO_HAND_FOUR_POSE_STATIC_FEASIBILITY_R1_REPORT.md').write_text(report,encoding='utf-8')
print('RESULTS_FINALIZED',results['FINAL_STATUS'],len(before),'UNCHANGED')
