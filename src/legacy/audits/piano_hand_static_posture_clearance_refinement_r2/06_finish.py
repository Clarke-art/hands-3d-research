from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;R1=P.parent/'piano_hand_four_pose_static_feasibility_r1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
geo=read(P/'STATIC_GEOMETRIC_MEASUREMENTS_R2.json');clear=read(P/'HAND_KEYBOARD_CLEARANCE_R2.json');man=read(P/'STATIC_SCENE_MANIFEST_R2.json');sol=read(P/'SOLVED_STATIC_POSES_R2.json');left=read(P/'LEFT_OCTAVE_REFINEMENT_R2.json');right=read(P/'RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json');diff=read(P/'BASELINE_CANDIDATE_COMPARISON_R2.json')['pose_deltas']
observations={
 'L1':['相同顶视中三闲置指更收拢；侧斜视/近景的曲度较 R1 明显，不是三指统一直伸或蜷向掌心。','共同 root 高度70→45.6mm，掌腕侧视更接近键盘，主动小指仍触 D2。没有通过高抬整手换净空。','小指 MCP32°和 spread25°仍触工程边界，root roll=-6°；不能宣称端点张力全部解决或生理放松获证。'],
 'L2':['三闲置指曲度与 L1 一致、形态无突变；拇指触点在 D3 可奏面内向中心移动，接触仍通过。','thumb MCP 从25°减到约17.68°，但IP仍18°边界；正常图未见反折/新大面积塌陷，边界残余需 Human 判断。','共同掌位较 R1 更低，左手转换几何关系成立候选；未生成或验证动态过渡。'],
 'R1':['掌位、朝向与五指一起协调；食指/无名指准备点移到白键较前区域并调整曲度，未仅抬高两指。','D#5/G#5 >3mm 筛查归零；匹配近景与侧斜视未见原邻键吞入、明显新钩爪或穿键。','五指高度/深度不同，黑键中指保持准备间隙，掌腕无新深度穿键命中。'],
 'R2':['中指仍触真实 F#5 可奏面，固定/皮肤pad均通过；相对 R1 的触点前移约6.75mm，完整坐标变化记录。','其余四指与准备态几乎一致，root不换位；食指/无名指邻黑键空间改善，原筛查归零。','没有把完整网格筛查无命中叫完整三角碰撞证明，也没有将自然度预审叫Human批准。']}
visual={'review_type':'AGENT_MATCHED_NORMAL_VIEW_PRECHECK_NOT_HUMAN_APPROVAL','client_date':'2026-10-09','reviewed_all12_R2_views':True,'matched_R1_views_inherited_without_rerender':True,'same_camera_same_framing':man['same_camera_same_framing'],'material_changes':False,'new_obvious_hook_penetration_floating_reverse_joint_or_palm_collapse':False,'left_idle_clear_relative_improvement':True,'left_palm_wrist_clear_relative_improvement':True,'right_original_neighbor_visible_risk_removed_in_normal_views':True,'remaining_engineering_bound_risks':['Left L1 little MCP32° and spread25°','Left L2 thumb IP18°','Left roll-6° / Right roll6°'],'remaining_bound_risk_is_not_human_approved':True,'Human_visible_obvious_blocker_precheck':False,'observations':observations,'dynamic_transition_proven':False,'human_approval':False,'screen_scope':'Finite3300-vertex rectangular-key-piece screen >3mm plus normal top/side/close; no hidden geometry forensic or full triangle certification.'}
dump('HUMAN_VISIBLE_PRECHECK_R2.json',visual)
assert all(g['STATIC_GEOMETRIC_FEASIBILITY']=='PASS_SCREEN' for g in geo.values())
for pose,g in geo.items():
 g.update({'classification':'PASS_CANDIDATE','HUMAN_VISIBLE_NATURALNESS':'CANDIDATE_PRECHECK_PASS / HUMAN_PENDING','ACTIVE_PAD_CONTACT':'PASS' if g['active_contact'] else 'NOT_APPLICABLE_PREPARATION_ONLY','IDLE_FINGER_CLEARANCE':'PASS_SCREEN','PALM_CLEARANCE':'PASS_SCREEN','WRIST_CLEARANCE':'PASS_SCREEN','NEIGHBOR_KEY_INTERFERENCE':'PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK','JOINT_POSTURE':'BOUNDED / NO_NEW_OBVIOUS_DEFECT / HUMAN_PENDING','observations':observations[pose]})
left['same_reasonable_octave_configuration']='CANDIDATE_PRECHECK_PASS_PENDING_HUMAN; exact shared root, consistent idle shape, both endpoints prepared/active';left['left_idle_naturalness']='CLEAR_RELATIVE_IMPROVEMENT_AGENT_PRECHECK / HUMAN_PENDING';left['palm_wrist_relative_improvement']=True;left['remaining_bound_risks']=visual['remaining_engineering_bound_risks'][:3];right['naturalness']='CANDIDATE_PRECHECK_PASS / HUMAN_PENDING';right['Dsharp_clearance']='PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK';right['Gsharp_clearance']='PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK';dump('LEFT_OCTAVE_REFINEMENT_R2.json',left);dump('RIGHT_NEIGHBOR_KEY_CLEARANCE_R2.json',right)
results={'phase':'PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2','candidate_count':1,'poses':geo,'policy_sha256':sha(P/'STATIC_REFINEMENT_POLICY_R2.json'),'candidate_sha256':sha(P/'STATIC_POSTURE_REFINED_CANDIDATE_R2.blend'),'solver_diagnostics':sol['solver_diagnostics'],'matched_camera_verified':True,'materials_unchanged':True,'full_static_sequence_geometry':'PAIRED_SHARED_ROOT_VERIFIED / NO_DYNAMIC_TRANSITION_PROOF','new_obvious_human_visible_defect':False,'remaining_engineering_bound_risks':visual['remaining_engineering_bound_risks'],'FINAL_STATUS':'STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW','Human_approval':False,'continuous_actions':0,'reference_search':False}
dump('STATIC_POSTURE_RESULTS_R2.json',results)
before=read(P/'PROTECTED_INPUTS_BEFORE_R2.json');changed=[p for p,v in before.items() if not Path(p).is_file() or sha(Path(p))!=v];assert not changed,changed
protect=read(R1/'FINAL_ASSET_PROTECTION_R1.json');protect.update({'checked_file_count':len(before),'changed_files':changed,'candidate_intrinsic_identity':man['intrinsic_identity'],'source_R1_candidate_sha256':sha(R1/'STATIC_POSTURE_CANDIDATE_R1.blend'),'candidate_R2_sha256':man['candidate_sha256'],'same_camera_and_scale':True,'keyboard_rebuilt':False,'material_changes':False,'new_continuous_actions':0,'candidate_count':1,'scope':'Inherited protected corpus plus all immediate R1 files including baseline candidate/evidence/scripts; exact list in PROTECTED_INPUTS_BEFORE_R2.json','HAND_BASELINES_UNCHANGED':True,'PIANO_BASELINE_UNCHANGED':True})
for group in ['hand_baselines','piano_authority']:
 for row in protect[group].values():row['current_sha256']=sha(Path(row['path']));row['matches']=row['current_sha256']==row['expected_sha256'];assert row['matches']
dump('FINAL_ASSET_PROTECTION_R2.json',protect)
questions=[('Q1','唯一 R2 静态候选建立','YES','一个新blend，四静态场景；一次政策/初始化，R1未重跑。'),('Q2','L1 小指 D2 接触保持','YES','固定0.523mm / 皮肤0.541mm，正确可奏区域。'),('Q3','L2 拇指 D3 接触保持','YES','固定/皮肤约0.579mm，正确可奏区域。'),('Q4','左手三闲置指比 R1 明显自然','YES','相同视角下收拢且曲度更明显；Agent相对预审，不代替Human批准。'),('Q5','左手掌腕比 R1 更放松合理','YES','root z70→45.6mm、掌位更低；正常视角无压键。生理张力未测。'),('Q6','L1/L2 共享合理八度手型','YES','候选级：同一root、相同三闲置指形态，端点接触/准备成立；动态未证。'),('Q7','右手五指准备自然','YES','候选级正常图未见新钩爪/异常伸指；五指协调调整，非孤立抬指。'),('Q8','R2 中指 F#5 接触保持','YES','固定0.498mm / 皮肤0.507mm，正确黑键可奏面。'),('Q9','原 D#5/G#5 干扰解决','YES','两右姿态原1/2顶点深度筛查→0；正常对照无明显邻键吞入。'),('Q10','出现新明显钩爪/穿键/悬空/反关节/掌部异常','NO','12正常视角预审未见；全部键体>3mm筛查0。'),('Q11','仍有明显 Human-visible blocker','NO','Agent匹配视角预审未见；部分端点边界饱和仍供Human审查。'),('Q12','必须修改正式 hand mesh/rig 的证据','NO','旋转/root修正已得到候选；无硬几何不可达证明。'),('Q13','最终状态','STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW','这是候选资格，未自动Human-approved。')]
status={'Q1_Q13':{q:{'question':t,'answer':a,'reason':why} for q,t,a,why in questions},'LEFT_L1_STATUS':'PASS_CANDIDATE','LEFT_L2_STATUS':'PASS_CANDIDATE','LEFT_IDLE_FINGER_NATURALNESS':'IMPROVED_CANDIDATE / HUMAN_PENDING','LEFT_OCTAVE_SHARED_POSTURE':'PASS_CANDIDATE / HUMAN_PENDING','RIGHT_R1_STATUS':'PASS_CANDIDATE','RIGHT_R2_STATUS':'PASS_CANDIDATE','RIGHT_DSHARP_CLEARANCE':'PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK','RIGHT_GSHARP_CLEARANCE':'PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK','PALM_WRIST_CLEARANCE':'PASS_SCREEN_AND_NORMAL_VIEW_PRECHECK','NEW_HUMAN_VISIBLE_DEFECT':'NO_OBVIOUS_DEFECT_IN_AGENT_PRECHECK','FINAL_STATUS':results['FINAL_STATUS'],'HAND_BASELINES_UNCHANGED':'YES','PIANO_BASELINE_UNCHANGED':'YES','Human_approval':False,'STOP':'HUMAN REVIEW'};dump('FINAL_STATUS_R2.json',status)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20);big=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',34);provenance=[]
for side,poses,file in [('左手',['L1','L2'],'EVIDENCE_LEFT_BEFORE_AFTER_R2.png'),('右手',['R1','R2'],'EVIDENCE_RIGHT_BEFORE_AFTER_R2.png')]:
 im=Image.new('RGB',(2640,1890),(242,240,234));draw=ImageDraw.Draw(im);draw.text((20,18),side+' · R1未获批准 → R2候选 · 同相机/同尺度/同材质',font=big,fill=(38,49,47));draw.text((20,66),'上两行：教学顶视与侧斜视；末行：合理近景。候选仍待Human，不证明动态演奏。',font=small,fill=(84,88,78));entries=[]
 for row,pose in enumerate(poses):
  for col,(version,view,label) in enumerate([('R1','TEACHING_TOP','顶视 baseline'),('R2','TEACHING_TOP','顶视 candidate'),('R1','SIDE_OBLIQUE','侧斜 baseline'),('R2','SIDE_OBLIQUE','侧斜 candidate')]):entries.append((row,col,pose,version,view,label))
 for col,(pose,version) in enumerate([(poses[0],'R1'),(poses[0],'R2'),(poses[1],'R1'),(poses[1],'R2')]):entries.append((2,col,pose,version,'REASONABLE_CLOSE','近景 '+('baseline' if version=='R1' else 'candidate')))
 for row,col,pose,version,view,label in entries:
  x=col*660;y=112+row*580;draw.text((x+10,y),pose+' · '+version+' '+label,font=font,fill=(56,73,66));source=(R1 if version=='R1' else P)/'renders'/f'{pose}__{view}.png';img=Image.open(source).convert('RGB');img.thumbnail((644,520));im.paste(img,(x+8,y+43));provenance.append({'sheet':file,'pose':pose,'version':version,'view':view,'source':str(source),'source_sha256':sha(source)})
 im.save(P/file)
im=Image.new('RGB',(1800,2940),(242,240,234));draw=ImageDraw.Draw(im);draw.text((20,18),'四姿态侧面净空 · 同相机 R1 → R2',font=big,fill=(38,49,47));draw.text((20,64),'左列R1 baseline（未批准），右列R2 candidate（待Human）',font=small,fill=(84,88,78))
for row,pose in enumerate(['L1','L2','R1','R2']):
 for col,version in enumerate(['R1','R2']):
  x=col*900;y=110+row*700;draw.text((x+15,y),pose+' · '+version+' '+('baseline' if version=='R1' else 'candidate'),font=font,fill=(56,73,66));source=(R1 if version=='R1' else P)/'renders'/f'{pose}__SIDE_OBLIQUE.png';img=Image.open(source).convert('RGB');img.thumbnail((880,650));im.paste(img,(x+10,y+44));provenance.append({'sheet':'EVIDENCE_SIDE_CLEARANCE_R2.png','pose':pose,'version':version,'view':'SIDE_OBLIQUE','source':str(source),'source_sha256':sha(source)})
im.save(P/'EVIDENCE_SIDE_CLEARANCE_R2.png');dump('EVIDENCE_IMAGE_PROVENANCE_R2.json',{'new_unique_render_count':12,'R1_rerendered':False,'matched_camera_verified':True,'material_changes':False,'composite_only_whole_frame_resize_and_labels':True,'no_AI_images_or_external_photos':True,'panels':provenance})
rows='\n'.join(f'|{q}|{t}|**{a}**|{why}|' for q,t,a,why in questions);lines='\n'.join(f'{k} = {v}' for k,v in status.items() if k not in ['Q1_Q13','Human_approval'])
report=f'''# PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT

2026-10-09 · DESIGN_ONLY · HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST

**FINAL_STATUS = STATIC_POSTURE_CLEARANCE_READY_FOR_HUMAN_REVIEW**。一个新R2候选中四姿态主动接触/准备与有限净空筛查通过；匹配正常视角显示左手三闲置指更弯曲、收拢且掌腕更低，右手原D#5/G#5邻键风险已去除。**这是Agent候选资格，Human_approval=false**；未把上一轮失败直接改成批准，也未证明动态演奏或生理张力。

## 继承与一次固定政策

继承R1完整blend、政策、结果、网格/权重、键盘、固定pads及12原视角，不重跑R1、不搜索参考、不改材质。Human纠正权威完整保存：LEFT_NATURALNESS=NOT_APPROVED、RIGHT_NEIGHBOR_CLEARANCE=FAIL、FOUR_POSE_HUMAN_APPROVAL=NOT_GRANTED。

R2事前政策 [STATIC_REFINEMENT_POLICY_R2.json](STATIC_REFINEMENT_POLICY_R2.json) SHA `{sha(P/'STATIC_REFINEMENT_POLICY_R2.json')}`；脚本SHA与政策同时在结果前锁定。左手非统一曲度和向内base spread、共同掌位更低；右手root/朝向/五指联合调整，食指/无名指在白键较前区域准备。没有左手三闲置指home-key IK，没有只抬高两指。

净空目标从R1少数低顶点代理改为冻结权重对完整3300顶点的预测与矩形键体距离，覆盖先前漏检指侧点；保存后实测仍独立检查全部88键。数值范围/权重执行前确定，未放宽；左/右各一次确定初始化联合两姿态求解，分别{sol['solver_diagnostics']['L']['nfev']} / {sol['solver_diagnostics']['R']['nfev']} evaluations收敛。无restart、sweep、第二候选或连续Action。

## 接触保持与触点变化

容差原封不动：vertical≤3mm、horizontal≤2mm，且严格在实际可奏区域；固定pad和实际皮肤点分别检查。F#5静置高差15.444mm、前端49.421mm继承。没有重建或修改键盘。

|姿态|任务|固定pad gap R1→R2|R2皮肤gap|水平误差|结果|
|---|---|---|---:|---:|---|
|L1|小指D2|0.586→0.523mm|0.541mm|0|PASS|
|L2|拇指D3|1.556→0.579mm|0.578mm|0|PASS|
|R1|五指准备|无主动触点|准备区/高度通过|按实际可奏面|PASS_SCREEN|
|R2|中指F#5|0.497→0.498mm|0.507mm|0|PASS|

主动触点R2−R1位移XYZ（mm）：L1约[+0.001,-2.199,-0.063]；L2[+10.297,-5.660,-0.977]；R2[+0.595,-6.749,+0.001]。这是在允许键面中选择新触点，不是改琴键或marker。完整固定/皮肤坐标与五指变化见 [BASELINE_CANDIDATE_COMPARISON_R2.json](BASELINE_CANDIDATE_COMPARISON_R2.json)。

## 左手三闲置指与掌腕

同相机顶视三指更收拢；侧斜与近景曲度较R1更明显，未见统一钩爪或指尖蜷向掌心。Index/Middle/Ring增量约[8,11,5]、[8.67,13.43,6.86]、[8.56,11.81,5.96]°，分别使用不同基部收拢旋转；这些是RSSF-relative工程增量，不是照片反推的标准人体角度。

闲置指相邻pad空间距R1约38.435/32.691mm，R2约30.027/25.958mm。间距只是几何佐证，自然性来自匹配正常画面的Agent预审，最终由Human判断。共同root高度70→45.6mm，pitch约-6.79→+4.16°；正常侧视掌腕更低，没有高抬整手换净空。

L1/L2 root仍相差0mm/0°，三闲置指形态一致，两个端点主动/准备成立。Thumb MCP饱和从25°减到约17.68°；但L2 thumb IP18°、L1 little MCP32°及spread25°、左roll-6°仍在边界，**没有声称端点紧张全部消除**。边界风险保留给Human，不当成生理极限或新技术阻断。静态共同配置为候选级通过，动态转换未生成/未验证。

## 右手邻键与全局净空

两右姿态D#5旧命中1顶点（3.666mm）、G#5旧命中2顶点（5.619mm）均变为0。保存后全部3300顶点对全部88键部件的>3mm有限筛查：四姿态总命中、掌部、腕部、各指与非目标pad接触均0。没有新增邻键命中。

相同正常近景显示食指/无名指与黑键边缘有了空间；调整包含root/朝向/曲度/准备前后位置，未仅孤立抬指。中指接触点前移且保持F#顶面接触。右手root约[223.68,-124.34,42.22]mm，yaw/pitch/roll约[-7.07,4.40,6.0]°；两姿态root不换位，其他四指几乎不变。

筛查归零不是完整三角碰撞认证；本轮不做hidden geometry forensic。正常三视图未见新明显穿键、悬空、反关节、钩爪或掌部异常。材质和分面显示与R1保持相同，本轮不升级皮肤质感。

## 唯一候选、匹配证据与保护

[STATIC_POSTURE_REFINED_CANDIDATE_R2.blend](STATIC_POSTURE_REFINED_CANDIDATE_R2.blend) 直接打开R1候选后，只改root与现有骨骼旋转，并另存R2。88键对象/顶点/三角面、材质、相机世界矩阵/orthographic尺度/裁剪及渲染尺寸原样继承。四场景frame1，Action数0。保存重新打开后FK最大差<0.000463mm、pad-skin最大漂移<0.036mm，完整intrinsic identity neutral检查均匹配。

[review.html](review.html) 四姿态/三视角均可切换，左右并排R1 baseline与R2 candidate，同视角同尺度；原R1全部未获Human批准。本轮12个必要新视角加3张有价值合成对照：[左手](EVIDENCE_LEFT_BEFORE_AFTER_R2.png)、[右手](EVIDENCE_RIGHT_BEFORE_AFTER_R2.png)、[侧面](EVIDENCE_SIDE_CLEARANCE_R2.png)。R1原图复用，无旧轮重渲染、无AI/外部图片、无视频。

最终保护 **{len(before)} 个冻结/继承输入**变化0；三份正式手SHA、钢琴权威、production pointers、旧R1候选/政策/图、MIDI/指法/音频均未改。没有mesh/rest/weights/corrective/driver/helperbone更新或Web集成。详情 [FINAL_ASSET_PROTECTION_R2.json](FINAL_ASSET_PROTECTION_R2.json)。

## Q1–Q13（Agent候选预审，非Human批准）

|编号|问题|答案|依据|
|---|---|---|---|
{rows}

## 停止状态

```text
{lines}
```

**STOP — HUMAN REVIEW**。未自动进入完整动态演奏生成。Human可继续拒绝自然度；本轮不再调政策或生成第二候选。
'''
(P/'PIANO_HAND_STATIC_POSTURE_CLEARANCE_REFINEMENT_R2_REPORT.md').write_text(report,encoding='utf-8');print('R2_READY_FOR_HUMAN_REVIEW',len(before),'UNCHANGED')
