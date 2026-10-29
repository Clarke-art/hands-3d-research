from common import *
from datetime import datetime,timezone
samples=read(OUT/'RIGHT_16_EVENTS_48_SAMPLES.json');deep=read(OUT/'INDEX_BLACK_KEY_REAL_GEOMETRY.json');middle=read(OUT/'MIDDLE_ACTIVE_NEIGHBOR_BLACK_DEEP.json');comparison=read(OUT/'B01_SAME_TIME_COMPARISON.json');media=read(OUT/'MEDIA_QC_AND_SHA.json');projection=read(OUT/'INDEPENDENT_CAMERA_PROJECTION_CHECK.json');frameqc=read(OUT/'FRAME_SEQUENCE_AND_NATIVE_RENDER_CHECK.json')
oldqc=read(ROOT/'experiments/hands_b01_visual_animation_refinement_r1/B01_MACHINE_VALIDATION.json')
markers=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json');keys=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];right=[n for n in NOTES if n['hand']=='R']
def link(path,label=None):
    p=safe(path);return '['+(label or p.name)+'](<'+p.as_posix()+'>)'
def art(name,label=None):return link(OUT/name,label)
def role(t,f):
    ns=[n for n in right if n['finger']==f]
    for r,pred in [('ACTIVE',lambda n:n['note_on']<=t<n['note_off']),('RELEASE',lambda n:n['note_off']<=t<n['note_off']+.04),('PREPARE',lambda n:n['note_on']-.18<=t<n['note_on'])]:
        a=[n for n in ns if pred(n)]
        if a:return r,a[0]['note_id']
    return 'IDLE',None
cuts=sorted({0.,5.95,*[max(0,n[x]+delta) for n in right for x,delta in [('note_on',0),('note_off',0),('note_on',-.18),('note_off',.04)]]})
matrix=[]
for n in right:
    segs=[]
    for a,b in zip(cuts,cuts[1:]):
        r,e=role((a+b)/2,n['finger'])
        if e==n['note_id']:
            if segs and segs[-1]['role']==r and abs(segs[-1]['end']-a)<1e-10:segs[-1]['end']=b
            else:segs.append(dict(role=r,start=a,end=b))
    rr=[r for r in samples if r['event']==n['note_id']];k=keys[n['key_index']];ss=k['key_top_playable_surface'];whites=[k for k in keys if k['color']=='WHITE']
    for r in rr:
        f=r['finger'];a=ss[0]
        if k['color']=='WHITE':
            i=whites.index(k);left=f['pad_x_fraction']<.5;other=whites[i-1 if left else i+1]['key_top_playable_surface'][0];x=(a['xmin']+other['xmax'])/2 if left else (a['xmax']+other['xmin'])/2
            f['nearest_front_white_seam_center_distance_mm']=abs(f['pad_key_rest_m'][0]-x)*1000
            f['front_white_seam_width_mm']=(a['xmin']-other['xmax'] if left else other['xmin']-a['xmax'])*1000
    matrix.append(dict(note=n,actual_role_segments=segs,samples=rr))
save('ROLES_AND_ALIGNMENT_MATRIX.json',matrix)
source_paths=[ROOT/'AGENTS.md',ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py',ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/04_diagnostics.py',ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/blender_local.py',ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/06_apply_validate.py',ROOT/'experiments/hands_b01_visual_animation_refinement_r1/blender_support.py',ROOT/'experiments/hands_b01_visual_animation_refinement_r1/FINAL_B01_VISUAL_REVIEW.md',ROOT/'experiments/hands_c1_full_overhead_teaching_review_r1/FINAL_OVERHEAD_REVIEW.md',ROOT/'experiments/hands_role_aware_motion_recomposition_r1/POLICY.json']
for p in source_paths:READS[str(p)]=sha(p)
old_receipts=[OUT/n for n in ['BLENDER_INPUT_SHA_RECEIPT.json','MEDIA_INPUT_SHA_RECEIPT.json','MIDI_INPUT_SHA_RECEIPT.json','SUPPLEMENT_SHA_RECEIPT.json','PROJECTION_CHECK_SHA_RECEIPT.json']]
protected={}
for p in old_receipts:
    for r in read(p)['files']:
        assert r['before']==r['after'];protected[r['path']]=r['before']
protected.update(READS);sha_rows=[]
for p,before in protected.items():
    after=sha(p);assert before==after;sha_rows.append(dict(path=p,before=before,after=after,unchanged=True))
save('FINAL_INPUT_SHA_RECEIPT.json',dict(all_unchanged=True,piano_access=False,files=sha_rows))
def fmtseg(row,r):
    xs=[s for s in row['actual_role_segments'] if s['role']==r]
    return '; '.join(f"{s['start']:.6f}–{s['end']:.6f}" for s in xs) or '—（被原角色优先级覆盖）'
table=[]
for row in matrix:
    n=row['note'];rr=row['samples'];h=rr[1]['finger'];margin=min(r['finger']['pad_lateral_margin_mm'] for r in rr);depth=max([x['depth_mm'] for r in rr for x in r['black_vertex_checks']]+[0])
    table.append(f"| {n['note_id']} | {n['note_name']} / {n['midi_note']} | {n['finger']} | {n['note_on']:.6f}–{n['note_off']:.6f} | {margin:.3f} | {h['pad_x_fraction']*100:.1f}% | {h['distal_cap_xy_outside_fraction']*100:.1f}% | {depth:.3f} |")
role_table=['| '+row['note']['note_id']+' | '+fmtseg(row,'PREPARE')+' | '+fmtseg(row,'RELEASE')+' |' for row in matrix]
marktable=[f"| {m['finger']} {m['digit']} | {m['mesh_vertex']} | {m['distal_frame']} | {m['distance_to_tip_mm']:.3f} | {m['palmar_projection_mm']:.3f} |" for m in markers['markers']['R']]
image_rows=read(OUT/'STILL_PROJECTIONS.json');image_names=[r['name']+'_DIAGNOSTIC_ONLY.png' for r in image_rows]+['09_MIDDLE_ACTIVE_E5_DIAGNOSTIC_ONLY.png']
titles=['食指ACTIVE / A4，1.100000s','中指ACTIVE / B4，1.300000s','中指ACTIVE / C5，3.450000s','食指IDLE / G♯4，0.433333s','食指IDLE / A♯4，2.600000s','原C1 B01交接前，1.416667s','B01失败候选B4持键，1.300000s','B01失败候选提前入C5，1.420833s','中指ACTIVE / E5及D♯5真实侵入，3.885711s']
images='\n'.join(f"{i+1}. {art(n,t)}" for i,(n,t) in enumerate(zip(image_names,titles)))
start=datetime(2026,10,15,12,14,32,tzinfo=timezone.utc);now=datetime.now(timezone.utc);elapsed=(now-start).total_seconds()
costs={p.name:read(p) for p in OUT.glob('*_PROCESS.json')};save('COST_AND_SCOPE.json',dict(start_utc=start.isoformat(),report_utc=now.isoformat(),elapsed_minutes=elapsed/60,blender_stage_processes=costs,media_seconds=media['seconds'],software_bug_failures=['Empty certified triangle list at no-hit time: treated as zero, not collision PASS for unsampled states.','Stale bpy object reference after opening candidate: resolve actual key object by name in newly opened scene.'],human_edit_minutes=0,motion_edit_minutes=0,scope='48 event snapshots + 5 deep times + original 357-frame coordinate projection. No whole-phrase high-rate collision audit.'))
text=f'''**HANDS_FINGERTIP_KEY_ALIGNMENT_DIAGNOSTIC_R1**

日期：2026-10-15（Asia/Shanghai）。诊断完成，未修改动作。**映射正确；落指表现为MIXED；食指黑键真实穿入及接触验收缺口均已确认。**

核心原因是：原检测测量“固定palmar skin顶点到合法运动键面的距离”，并不验收整根手指的皮肤位置、末端轮廓、入键方向或邻键净空。当前48个活动接触采样全部PASS，与闲置食指深穿黑键、活动中指邻键侵入同时成立。没有证据把这些问题归咎于MIDI键身份或指法串位，也不能把它们都解释为俯视错觉。

完整原C1标注视频：{art('C1_OVERHEAD_ALIGNMENT_DIAGNOSTIC_1X.mp4','DIAGNOSTIC_ONLY · 完整23音正俯视1×')}。1280×720、60fps、357帧、5.950秒；保留原生画面及原音轨。所有图片和视频供诊断，不是正式教学成品。原C1与B01 NOT_APPROVED候选始终分开。

**1．真实触键定义与来源**

读取原marker JSON及实际Rig、LBS/corrective后的网格。两手的五个顶点编号相同；左手对应骨名后缀为_L，右手如下。编号是各自网格中的编号，不是同一个空间点。

| 指号 / 手指 | 真实mesh顶点 | 远端局部坐标系 | canonical距语义TIP mm | 掌侧投影 mm |
|---|---:|---|---:|---:|
{chr(10).join(marktable)}

原选择文字是“Closest canonical surface vertex to TIP-3mm distal +4mm palmar, constrained to distal17mm palmar hemisphere; fixed once before action evaluation. No bone-head proxy.” 它们是既有指腹侧表面点，不是指尖最前端，也不是测得的压力中心或接触斑。食指、中指marker距语义TIP约5.620、6.025mm；不能用TIP骨点替代实际皮肤。资料：{link(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')}。

历史计算有两种身份：生成FK以远端骨矩阵变换local_pad_point得到虚拟marker；真实验收读取变形网格V[mesh_vertex]。本轮实际测两者，48采样最大差仅**0.067697mm**，不足以解释数毫米的偏边/穿键，不支持“骨点代替真实pad导致全部错误”的结论。

设p为真实skin pad，先用原琴键Action的实际旋转绕press_pivot反变换到键的中性坐标；在注册的可奏面矩形并集中选最近面。横向误差为 `1000 × ||p.xy − clip(p.xy, rectangle)||`；垂向gap为 `1000 × (p.z − surface.z)`。面内任意位置横向误差都为零。现沿用的0.03mm是**面外距离容差**，不是离键中心的误差；3mm是gap的绝对上限，允许有限悬空或入面，不是物理接触/压力证明。本轮48采样gap范围**−0.017307～+0.916530mm**。生产/B01实现还要求inside为真，所以并没有利用0.03mm允许在面外通过。

来源必须分阶段：原A2 `{link(source_paths[2],'04_diagnostics.py')}` 中工程失败列表曾用横向>2mm及虚拟marker绝对gap>3mm；后续C2 `{link(source_paths[4],'06_apply_validate.py')}` 明确同时检查marker/skin绝对gap≤3mm、横向<0.03mm；本轮复用的是B01 `{link(source_paths[5],'blender_support.contact')}` 的实际skin、inside、0.03/3mm口径。不能把后续较严的局部检查追溯写成原C1整曲已获批准的安全合同。

合法面不是整键AABB：白键由前部宽矩形与后部避让黑键的窄矩形组成，前后分界中性Y约49.421377mm；黑键是实际顶面矩形。矩形包含贴近边界的位置，没有教学用边缘余量要求。例：A4前部X=108.147872～131.236922mm；后部X=113.360283～126.024511mm。相邻白键前部缝宽约0.849430mm。原生成器曾对白键目标加3mm横向/7mm纵向inset、黑键加2/2mm，但那是**单marker生成目标**，不能当作整指皮肤的安全余量。见{link(source_paths[1],'EventCoordinator.__init__/target/tasks')}。

接触函数不要求主要指腹接触区域整体落面，不测pad法线/末端朝向，也不包含邻键或指间碰撞。这些属于另行几何门禁。因而“marker PASS而指尖整体偏向边缘”确实可能发生。本轮没有改marker、阈值、合法面或正式合同。

**2．右手16音轻量核查**

重新解析原MIDI（PPQ384，tempo428571µs/quarter），逐项匹配23音的轨道、通道、音高、力度、ON/OFF tick，再核对右手16音与冻结单手来源的指法/键索引。全部一致。指法档案原标记仍为`DESIGN_PROVISIONAL_UNCHANGED`，本轮确认映射一致，不新增指法教学审批。{art('FORMAL_MIDI_AND_FINGERING_MAPPING.json','MIDI与指法实读证据')}。

每事件取精确ON、中点HOLD、OFF前1ms，共48个真实Blender姿态。下表侧边余量是三采样最小值；X比例与末端包络超出比例取HOLD。比例是canonical末端5mm皮肤顶点的XY投影统计，不是接触面积或穿模比例；不得把所有轮廓越界自动判为碰撞。

| 事件 | 目标 / MIDI | 指号 | ACTIVE展示时间 s | pad最小侧边余量 mm | HOLD pad横向比例（左0%） | HOLD末端顶点投影面外比例 | 三采样邻黑键顶点深度峰值 mm |
|---|---|---:|---|---:|---:|---:|---:|
{chr(10).join(table)}

全部48个pad在合法面内，横向误差为0。每点世界坐标、键局部坐标、末端真实顶点、pad周边7mm皮肤投影、可奏面边界、最近黑键边缘距离、远端骨方向和实际pad法线均有机器数据：{art('RIGHT_16_EVENTS_48_SAMPLES.json')}、{art('PAD_NORMAL_AND_BLACK_PROJECTION.json')}。法线和骨方向是诊断读数，没有新增姿态PASS阈值。48点不能证明点间连续无碰撞。

原角色优先级为ACTIVE→RELEASE→PREPARE→IDLE；PREPARE名义提前180ms，RELEASE最多跟随40ms，会被同指新ACTIVE覆盖。下面列实际优先级后的区间；ACTIVE见上表，其余同指时间为IDLE。这避免把连续同指G4重击的前一ACTIVE误标成下一音PREPARE。

| 事件 | 实际PREPARE区间 s | 实际RELEASE区间 s |
|---|---|---|
{chr(10).join(role_table)}

完整事件、角色区间、键缝中心距离及3点读数见{art('ROLES_AND_ALIGNMENT_MATRIX.json')}。

**3．食指/中指偏键缝证据：点正确不代表整指居中**

- R02 A4食指HOLD 1.099999s：pad世界坐标约(111.163,41.003,−5.705)mm，中性X在前键宽的13.06%；距左面边3.015mm、距相邻白键缝中心3.440mm。真实末端顶点1228中性坐标约(113.139,47.522,1.962)mm，末端皮肤采样23.26%投影在目标键面外。**偏左证据成立；pad本身未落进缝内**。三个活动采样的食指ROI未检出黑键内部顶点，1.100秒A♯4真实BVH与面深度也为零；不推广为整段连续清障PASS。
- R03 B4中指HOLD 1.314285s：pad约(151.396,41.298,−5.870)mm，X比例83.63%，距右面边3.779mm、右侧白键缝中心4.204mm；末端投影有26.83%超出。与无名指接近/粘连是另一个真实历史问题。此时不能把偏右自动说成错按C5。
- R09 C5中指HOLD 3.457140s：pad X比例81.49%，侧边余量4.274mm；末端顶点到C♯5投影边缘仅1.935mm。3.450000秒深查证实中指皮肤与C♯5相交10面对，面内深度**0.849885mm**，见证不是单纯二维重叠。
- R11 E5中指HOLD 3.885711s：pad X比例17.77%，侧边余量4.103mm；末端顶点距D♯5投影边缘约1.041mm。真实皮肤与D♯5相交17面对，顶点深度0.517910mm，而三角面内部深度**1.341358mm**。最大面见证世界坐标约(207.217,50.763,1.341)mm，三角形88、顶点[25,862,2491]。pad仍PASS，证明教学/邻键安全不由这个点接触合同覆盖。

偏边不等于必须移到键中心。原动作既有目标位置、皮肤宽度及多关节朝向共同造成末端投影越边；不同音的状态不同，因此总判定为MIXED，而不是所有落指都错误。对“主要承压接触面积是否合理”仍为UNKNOWN：未建立物理压力模型，也未伪造接触斑。姿态法线/方向数据只能支持后续人工判断，不能单凭角度宣布不自然。

**4．食指黑键穿模：真实终端皮肤，发生于IDLE**

| 时刻 s | 角色 / 当时右手活动音 | 碰撞键 | 真实内部顶点峰值 | 三角面内部深度 | BVH面对 |
|---:|---|---|---:|---:|---:|
| 0.433333 | 食指IDLE；R00 D5/小指ACTIVE | G♯4 | 4.328348mm，v27 | 4.328348mm | 28 |
| 2.600000 | 食指IDLE；R07 G4/拇指ACTIVE | A♯4 | 5.603865mm，v35 | 5.637124mm | 40 |

v27世界坐标(106.607564,53.749725,9.214992)mm，canonical距语义TIP前方回溯1.852mm；v35=(131.628379,55.700190,6.684491)mm，回溯2.871mm，两者都在预先固定的末端5mm皮肤区域内，不能归为仅手掌代理或纯侧面轮廓。本轮深查重现历史见证。

深度定义是实际凸键体归一化面半空间的最小内部距离；三角面用既有primal/dual证书求面上最大内部深度，不是仅减顶面Z，也不是运动优化。上下界差约6×10⁻⁹mm，包含完整顶点/三角形索引、重心坐标、见证世界坐标。实际键网格已与注册几何按原键Action运动交叉核对。见{art('INDEX_BLACK_KEY_REAL_GEOMETRY.json')}、{art('MIDDLE_ACTIVE_NEIGHBOR_BLACK_DEEP.json')}。

俯视中可见食指与黑键前沿关系异常，内部顶点会被键面遮挡，单张无标注图难以判断深度。红点是穿入皮肤的真实三维投影，可能位于被遮挡表面的屏幕位置，**不是声称那些点在原渲染中裸露可见**。E类投影遮挡可以同时存在，但不能推翻上述真实侵入。

**5．原C1与B01失败候选：只对实际编辑窗口对照**

对1.133333、1.300000、1.420833、1.4214275、1.4914275、1.675000秒打开两套真实数据，未重新编辑。{art('B01_SAME_TIME_COMPARISON.json')}。Human本次明确认可的只是中/无名指视觉分离改善，候选仍NOT_APPROVED。

| 时刻 | 实际角色 | 原C1→B01候选读数 | 含义 |
|---|---|---|---|
| 1.133333 | 食指ACTIVE A4；中指PREPARE B4；无名指IDLE | 中指B4侧边3.454→5.410mm；无名指C5侧边2.228→7.426mm | 两者均向键内部移动；此刻不是中指已持B4，也不是无名指已活动C5 |
| 1.300000 | 中指ACTIVE B4；无名指PREPARE C5；食指IDLE | 中指pad移0.938mm、侧边3.665→4.544mm；无名指移4.656mm、侧边4.777→9.296mm | 抽样不支持“分离后更靠边”；准备pad不能冒充活动接触通过 |
| 1.420833 | 中指ACTIVE B4；无名指PREPARE C5 | 无名指gap +0.226→−0.532mm；历史真实面深度0.646920mm | 比C5 NOTE_ON提前0.594ms入键；普通60fps视频无法独立分辨这个亚帧时差，图08用精确subframe |
| 1.4214275 | 中指RELEASE B4；无名指ACTIVE C5 | 无名指pad移4.487mm，侧边4.554→8.881mm；gap +0.158→−0.600mm | 绝对gap≤3mm仍PASS，不能证明没有提前入键 |
| 1.4914275 | 中指IDLE；无名指ACTIVE C5 | 中指MCP屈曲约−0.386964°，低于0°下限 | 历史域超限保留；不是由本轮接触点诊断修复 |
| 1.675000及之后 | 中指IDLE；无名指RELEASE | 既有QC记录1.675–1.691667新增中/无名指相交面，峰值5对 | 退出段回退仍FAIL，未生成第二候选 |

六个对照时刻食指pad位移均0，食指强权重ROI最大皮肤差仅0.000186mm，不能说全部皮肤数学上逐顶点完全不动，但此微小量不足以解释毫米级黑键穿入。原C1已有食指问题不由B01候选创造。B01历史630/630接触PASS检查的是活动点与距离，不覆盖提前入键、合法域和退出穿插；本轮没有重跑整套高频验收或更改其FAIL身份。

**6．标注图与完整诊断视频**

{images}

青十字=真实skin pad；黄圈=canonical末端方向极值所选的固定真实皮肤顶点；白线=真实末端皮肤采样投影凸包，**不是完整真实轮廓重建或接触面积**；绿线=合法可奏面；粉虚线=相邻白键缝中心；红色=指定黑键/真实侵入点。IDLE图中的黑键是碰撞对象，不是该指目标音。右侧2×区域是同一画面的局部放大，完整键面与手指可在左侧全画幅核查。

全部几何标记由原STAGE_C_OVERHEAD投影生成。实际正交相机约(0.0839353,−0.0547938,0.9)m，光轴(0,0,−1)，正交宽0.673316896m。独立`bpy_extras.world_to_camera_view`复核18个pad/末端点，最大差**{projection['max_error_px']:.8f}px**。源视频与6张同刻原生渲染逐像素抽查一致（仅编码误差）；没有移动相机或藏键。

完整视频只叠加诊断，不重渲染全曲；每帧按真实357帧场景投影活动目标键和该指标记，0.40–0.48及2.50–2.70秒显示食指黑键见证。全部357帧保持原顺序，未标注区域与原帧最大MAE {frameqc['max_unannotated_region_mae']:.3f}/255，无新增黑屏/冻结/剪切；音频AAC直接复用，解码PCM逐字节一致、PTS=0。首NOTE_ON0.35秒、末NOTE_OFF5.492852秒、准备与尾段完整保留。{art('MEDIA_QC_AND_SHA.json')}、{art('FRAME_SEQUENCE_AND_NATIVE_RENDER_CHECK.json')}、{art('INDEPENDENT_CAMERA_PROJECTION_CHECK.json')}。

**7．A–G诊断回答与后续建议（未执行）**

A．**触键映射PASS**：正式MIDI音高、键身份、冻结采用指法与pad所属手指一致；没有发现串键、错八度或marker指号错配。

B．**落指MIXED**：48点本身在合法键面，未发现pad落入缝隙；R02 A4偏左、R03 B4/R09 C5偏右、R11 E5偏左及整指投影越边有数值证据。不能因此宣布所有落指都教学合理，尤其R09/R11还确认真实邻键侵入。

C．**接触验收缺口CONFIRMED**：单skin点的面内/±3mm合同不评价主要皮肤接触面积、边缘余量、朝向和邻键净空；PASS与可见偏边、真实穿模可以并存。原白键3mm生成inset也不足以自动容纳整个指尖宽度。

D．**食指穿黑键CONFIRMED**：0.433333s/G♯4末端皮肤深4.328mm；2.600000s/A♯4面深5.637mm，均IDLE。不能误报为食指正在错按黑键；食指真正活动音只有R02 A4。

E．原因分类：A映射错误**未发现**；B接触目标定义/教学覆盖缺口**确认**；C整指姿态与皮肤宽度造成边缘/黑键关系问题**有几何证据**，但自然度与最理想入键方向仍须Human判断；D非活动指避障不足**确认**；E二维遮挡**同时存在**，但这几处已证明不是仅投影。未对整曲全部遮挡逐一判真伪，未测真实压力接触面积。

F．如未来另行授权，先把活动pad任务与整指皮肤/非活动指避障分开处理：优先解决IDLE食指已确认的深穿黑键；同时在R09/R11检查活动中指末端及侧面与邻黑键的真实净空。再评估目标点在可奏面上的位置与多关节入键方向，保留正确时钟与自然动作。不要先改MIDI/指法/Rig，也不要无条件把所有pad移到键中心。B01单次视觉分离不能替代这些门禁。

G．**建议未来合同增加教学落指评价，但本轮不修订**：分别报告pad距离、真实末端/指腹采样区域与实际键面边缘关系、入键方向、ACTIVE与PREPARE/RELEASE/IDLE邻键碰撞、Human俯视可辨性；保留真实面级深度，不能只看顶点。皮肤投影越界不直接等于不合格，应结合高度、实际表面相交与Human判断；具体区域、余量/朝向容差需另行审批。现有0.03mm、3mm和其他门禁完全未变。

**8．范围、成本与冻结保护**

本轮仅48个事件姿态轻查、5个高风险时刻真实面/BVH深查、357帧必要坐标投影及两段指定黑键顶点标注。未整曲重复高频全网格碰撞审计。没有调用SciPy、IK、动作优化器，没有新增动作候选/Action/Blend，没有改变B01候选。

截至报告生成实际墙钟约**{elapsed/60:.1f}分钟**（包含阅读、编写隔离诊断脚本、视觉核对与报告）；Blender主成功阶段约15.57秒、补充几何4.20秒，媒体编码/验证约6.45秒，另有逐帧核对等短过程。两个普通诊断Bug（无命中时空证书集合、重开Blend后RNA对象引用失效）均在新目录修复并保留失败日志，失败进程合计约22秒；没有因此调整任何动作或反复搜索候选。精确进程成本见{art('COST_AND_SCOPE.json')}；没有虚构人工编辑时间。

关键源SHA256前后相同：

| 文件 | SHA256 |
|---|---|
| 原C1 Blend | d8e0f5a85e71323739bfcd4de485ff7a2b4096f8e59bbd4c578ee9d76d3e51a7 |
| B01 NOT_APPROVED Blend | 1984d92bf437c5f833b2ad62e3aaeed5abd16e3e2979e5356b120a14af6a44ed |
| 原C1俯视视频 | 08a5ccc7cf679722f6a5fdde4c1c77de41b6ac1ce2d19c71bc0df8354ceb6da4 |
| 正式MIDI | fd87a6673e18104047842a1c858d2c9d8eb9ad845d7a8fa46e3664b17642cb75 |

{art('FINAL_INPUT_SHA_RECEIPT.json','完整输入前后SHA收据')}覆盖marker、键表、Rig、源MIDI/指法、原Blend、候选及实际读取的工具/证据；原C1内存中全场景Action payload及双手rest/蒙皮/corrective摘要亦前后一致。所有新增内容仅写本审计目录；独立piano未扫描、读取、运行或修改，不经重解析点访问。原并发保护FAIL及B01失败证据均保留，未改写。

```text
HANDS_FINGERTIP_KEY_ALIGNMENT_DIAGNOSTIC_R1
MIDI_KEY_MAPPING = PASS
FINGERTIP_ALIGNMENT = MIXED
INDEX_BLACK_KEY_PENETRATION = CONFIRMED
CONTACT_VALIDATION_GAP = CONFIRMED
MOTION_MODIFICATION = NOT_EXECUTED
STOP — HUMAN REVIEW
```
'''
path=OUT/'FINAL_FINGERTIP_ALIGNMENT_DIAGNOSTIC.md';assert not path.exists();path.write_text(text,encoding='utf8')
artifacts=[path,OUT/'C1_OVERHEAD_ALIGNMENT_DIAGNOSTIC_1X.mp4',*[OUT/n for n in image_names]]
save('FINAL_DELIVERY_MANIFEST.json',dict(status='STOP — HUMAN REVIEW',motion_modification='NOT_EXECUTED',files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in artifacts],image_count=9,video_frames=357,video_duration_sec=5.95))
print('FINAL_REPORT_WRITTEN',elapsed/60,'minutes',len(sha_rows),'protected files')
