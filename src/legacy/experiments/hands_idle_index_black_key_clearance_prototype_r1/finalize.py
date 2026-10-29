from common import *
import csv
import numpy as np
from datetime import datetime,timezone,timedelta
v=read(OUT/'DENSE_GEOMETRY_AND_REGRESSION.json');tr=read(OUT/'TRANSITION_SUBFRAME_CHECK.json');media=read(OUT/'FINAL_MEDIA_QC_AND_METADATA.json');cross=read(OUT/'CROSS_HAND_AND_CAMERA_CHECK.json');st=read(OUT/'STILL_GEOMETRY_PROJECTIONS.json')
# Earliest observed digest for every protected/read input. No old manifest is
# executed or followed into other projects. This receipt is restricted to Hands.
hashes={r['path']:r['sha256'] for r in read(OUT/'PROTECTED_BEFORE.json')['files']}
for p in sorted(OUT.glob('*INPUT_RECEIPT.json')):
 for r in read(p)['files']:
  assert str(safe(r['path']))==r['path'];hashes.setdefault(r['path'],r['before']);assert hashes[r['path']]==r['before']
receipts=[dict(path=p,before=h,after=sha(p),unchanged=sha(p)==h) for p,h in hashes.items()]
assert all(r['unchanged'] for r in receipts)
save('PROTECTED_AFTER_AND_SHA256_RECEIPT.json',dict(all_unchanged=True,files=receipts,scope='All protected/read task inputs captured before candidate creation or on first read, including original C1, both native frozen hand baseline Blends, formal MIDI, timelines/fingering, key table, marker/Rig records, acceptance policy, prior diagnostic evidence and B01 failed candidate/evidence. Embedded key Actions and native skin/rest/correctives additionally verified in memory. This is not a recursive hash audit of unrelated historical experiments.',independent_piano_access=False))
newkey=[dict(time=r['time'],**a,increase_mm=a['candidate_mm']-a['baseline_mm']) for r in v['new_key_samples'] for a in r['collisions']]
introduced=[a for a in newkey if a['baseline_mm']<=1e-5]
assert not introduced
base=np.load(OUT/'BASELINE_LOCAL_SAMPLES.npz');cand=np.load(OUT/'CANDIDATE_LOCAL_SAMPLES.npz');diff=np.linalg.norm(cand['vertices']-base['vertices'],axis=2)*1000
roi=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json');skin={d:float(diff[:,r['vertices']].max()) for d,r in roi.items()}
metrics=[]
for name,row in zip(['A','B','A_CONTEXT','B_CONTEXT'],v['windows']):
 metrics.append(dict(window=name,start_sec=row['range'][0],end_sec=row['range'][1],samples=row['samples'],max_step_sec=row['maximum_step_sec'],base_max_penetration_mm=row['baseline_peak']['depth_mm'],candidate_max_penetration_mm=row['candidate_peak']['depth_mm'],new_key_collision_count=0,worse_existing_collision_samples=row['new_or_worse_key_samples'],new_self_collision_samples=row['new_self_pair_samples'],active_contacts='48/48 PASS globally sampled',joint_limit_raw_min_deg=v['joint_summary']['candidate_min'][1][0],transition='PREPARE/A4 retained; RELEASE/scope bake discrepancy remains'))
with (OUT/'QUANTITATIVE_TABLE.csv').open('x',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
worst=max(newkey,key=lambda x:x['increase_mm']);contacts=max(r['pad_shift_mm'] for r in v['contacts']);speed=max(v['joint_summary']['max_added_joint_speed_deg_s'])
result=dict(result='PARTIAL',human_review_required=True,approved_for_production=False,reason='Both windows improve but retain real skin-black-key intersections; some inherited G#4 penetration worsens; baked transition has small new boundary deviations. No third configuration or repair candidate.',windows=v['windows'][:2],new_collision_count=len(introduced),worse_existing_samples=len(newkey),worst_worsening=worst,new_self_collision_samples=len(v['new_self_samples']),new_cross_hand_collision_samples=cross['new_cross_hand_pair_samples'],contacts_pass=sum(r['candidate']['pass_'] for r in v['contacts']),contacts_total=48,max_active_pad_shift_mm=contacts,other_digit_skin_max_mm=skin,limits=dict(frozen_bounds_deg=read(OUT/'STRATEGY_AND_ENVELOPE.json')['bounds_deg'],index_min_deg=v['joint_summary']['candidate_min'][1],index_max_deg=v['joint_summary']['candidate_max'][1],raw_domain_roundoff_deg=max(0,-v['joint_summary']['candidate_min'][1][0])),protected_files=len(receipts),source_sha256=sha(SOURCE),candidate_sha256=sha(OUT/'IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend'),max_added_joint_speed_deg_s=speed,stop='STOP — HUMAN REVIEW')
save('RESULT.json',result)
def link(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S +08:00')
text=f'''# HANDS_IDLE_INDEX_BLACK_KEY_CLEARANCE_PROTOTYPE_R1

结果：**PARTIAL**。{now}。同一套局部姿态机制改善两个窗口，但真实碰撞仍在，且出现既有侵入加深及烘焙边界偏差。候选仅供失败/部分改善证据与 Human Review，不能合并原 C1。

实际策略：从原 C1 的 LBS/corrective 后食指皮肤三角面，与原 Action 驱动黑键网格的保守 3mm AABB 邻近关系检测威胁区间。在 IDLE 内以 MCP 伸展抬指，配合 PIP/DIP 少量屈曲。A 静态探针增量为 −10/+4/+2°，B 为 −16/+6/+3°，展指不主动调整，按原合法域裁剪。仅 B 制成时间候选；没有第三组配置、IK、全手求解或逐音特判。两个指定时刻不参与触发条件，音名也不参与姿态选择。详见 {link('STRATEGY.md')} 与 {link('STRATEGY_AND_ENVELOPE.json')}。

时间门控采用 180ms 五次 smoothstep 进入/退出，并在 PREPARE 前 40ms 归零。食指唯一 ACTIVE 为 A4 0.9928565–1.207142s，PREPARE 0.8128565–0.9928565s。修改三骨的四元数曲线，掌/root、腕、其他手指骨骼曲线、全部琴键 Action 与时钟不改。源曲线为 LINEAR，240Hz 插入姿态，其他动画路径逐项摘要一致。局部实验支持域为 0–1.35s、2.10–3.35s；视频另显示至 3.60s 以观察回归。

**真实几何结果**

| 范围 | 原 C1 最大穿入 mm | B 最大穿入 mm | 实际采样 | 新键碰撞 / 既有加深采样 |
|---|---:|---:|---|---|
'''
for name,r in zip(['A 0.35–0.80s','B 2.45–2.90s','前后连接 0–1.35s','前后连接 2.10–3.35s'],v['windows']):
 text+=f"| {name} | {r['baseline_peak']['depth_mm']:.6f} | {r['candidate_peak']['depth_mm']:.6f} | {r['samples']}点；最大步长{r['maximum_step_sec']*1000:.6f}ms | 0 / {r['new_or_worse_key_samples']} |\n"
text+=f'''
基线与候选共用 {len(v['times'])} 个精确时间，240Hz 常规采样，高风险时刻及角色/事件边界附近 ±12.5ms 加密至 960Hz；另有 ±0.1/1/2ms 的连接采样。实际 evaluated mesh 包含 LBS、shape-key/corrective；真实键网格与注册几何按原 Action 运动逐点核对误差 <1µm。BVH 检查真实三角面相交，凸键网格归一化面半空间加三角面 primal/dual 深度证书检测内部穿入，不只看顶点、TIP 或 pad。检查整根食指 ROI 及所有实际变动顶点关联面，包含混合蒙皮边界，并覆盖所有邻近白/黑键。

0.433333s G♯4：4.328348 → 1.945472mm；2.600000s A♯4：5.637124 → 1.761794mm。两处仍相交，净空为 0。窗口 A 的 211 点中候选 196 点仍穿键；窗口 B 的 202 点中候选 53 点仍穿键，直到 2.620833s。不能用后来部分采样无交宣布整段安全，也没有连续时间安全证明。

**新增回退与继承问题**

新出现的键身份碰撞为 0；新增非相邻皮肤三角面自交采样为 0，跨手新增面对采样为 {cross['new_cross_hand_pair_samples']}。这并不表示没有回退：原有 G♯4 碰撞在 {len(newkey)} 个上下文采样中加深，最大增加 {worst['increase_mm']:.6f}mm（{worst['time']:.6f}s，{worst['baseline_mm']:.6f} → {worst['candidate_mm']:.6f}mm）；窗口 A 内有 18 点加深，最大约 0.017223mm。数值峰值降低不能抵销这些局部回退。

保存后亚帧核查发现烘焙实现缺陷：浮点时间网格遗漏精确 3.35s 端点，原关键帧值又使用网格插值，导致 3.35s 最大皮肤偏差 0.111793mm，至 3.36s 才恢复；1.247142s RELEASE 退出点偏差 0.016292mm。PREPARE 起点和 A4 NOTE_ON 的真实皮肤偏差为 0。故“严格只在 IDLE 生效并完整归零”尚未闭合。此缺陷由本次烘焙引入，不归咎原 C1。保留原候选及证据，没有追加导出修复或第三参数配置。见 {link('TRANSITION_SUBFRAME_CHECK.json')}、{link('BAKE_BOUNDARY_DIAGNOSIS.json')}。

**演奏、合法域与观感**

右手 16 音 ON/HOLD/OFF前1ms 共 **48/48** 原合同接触 PASS；最大活动 pad 位移 {contacts:.9f}mm。全部 23 音时钟、原 MIDI/指法和键 Action 由文件 SHA 与未编辑 Action payload 一致性保持。A4 准备与实际触键保持；原 C1 其他历史缺陷不宣称已修复。三根食指骨的改动通过原有混合权重传至拇指 ROI，最大皮肤位移 {skin['THUMB']:.6f}mm；中/无名/小指 ROI 位移均为 0，拇指骨曲线不变，pad 保持。所有这类真实变动面均参与新增碰撞对照。

原食指合法域 MCP/PIP/DIP=0–32/0–32/0–20°，展指±25°，未修改。候选范围 MCP {v['joint_summary']['candidate_min'][1][0]:.9f}–{v['joint_summary']['candidate_max'][1][0]:.6f}°、PIP {v['joint_summary']['candidate_min'][1][1]:.6f}–{v['joint_summary']['candidate_max'][1][1]:.6f}°、DIP {v['joint_summary']['candidate_min'][1][2]:.6f}–{v['joint_summary']['candidate_max'][1][2]:.6f}°。MCP 下界有约 4.28×10⁻⁷° 的浮点负值，原始读数保留，不改域。既有 B01 检查代码采用 0.002° 数值域容差，本轮该读数在其内；未另行放宽。新增关节速度峰值 {speed:.3f}°/s，略超过 B01 历史代码的 180°/s 参考线；不把该候选描述为自然度通过。

五次包络本身平滑，但多个区间取 max、关节裁剪、240Hz LINEAR 烘焙不构成全局 C2 保证。正交俯视静帧及解码视频已检查；抬起/持续翘指、僵硬、复位节奏仍由 Human 评价。当前已有几何与连接失败，机器没有自然观感批准。正式 STAGE_C_OVERHEAD 相机、正交参数、模型显示和键几何保持原样；画面只加外围标签及独立图中的几何标注。

**交付与保护**

{link('FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4')}；{link('FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4')}。左右均原生 1280×720 同源时刻，完整显示 0–1.35s 与 2.10–3.60s 两段，切换明确标注；173/346 帧、60fps，原 C1 同范围音轨，慢速使用 atempo 0.5。解码抽帧、时间标签、切换与尾段均经像素误差核对。早期无 FINAL 前缀媒体为保留过程证据，Human 以 FINAL 版本为准。

{link('A_BEFORE_AFTER_GEOMETRY.png')}；{link('B_BEFORE_AFTER_GEOMETRY.png')} 标出实际内部三角面见证与深度。红点可能被键遮挡，只是三维点投影；局部放大来自同一相机。

定量 CSV：{link('QUANTITATIVE_TABLE.csv')}；完整机器数据：{link('DENSE_GEOMETRY_AND_REGRESSION.json')}。隔离候选：{link('IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')}，SHA256 `{result['candidate_sha256']}`。原 C1 SHA256 `{sha(SOURCE)}`。

{len(receipts)} 项受保护/实际读取输入的前后 SHA256 全部一致：{link('PROTECTED_AFTER_AND_SHA256_RECEIPT.json')}。原 C1、双方冻结 baseline、正式 MIDI、源指法/时间表、琴键表/marker/Rig记录、既有验收 policy、B01 失败候选/证据与前轮诊断均保留；原 C1 内嵌全部键 Action、rest Rig、顶点/面、蒙皮权重和 corrective driver 摘要亦保持。本收据不是对无关历史目录的大规模递归审计。独立 piano 目录没有扫描、读取或运行；旧脚本仅选择已读过的纯辅助函数，未执行历史任务入口或跟随外部项目路径。

背景 Blender CLI 可复现；脚本和进程日志均在本隔离目录。首次连接器未连接；一次关键帧 API 插入错误、一次用全手 AABB 断言分离的过强假设、一次媒体阶段先于尾帧完成的依赖错误均保留过程证据，之后只修正工具执行/检查逻辑，没有增加动作参数配置。源 Blend 从未保存覆盖。

**STOP — HUMAN REVIEW**。本轮两种轻量参数已用完；不修中/无名指，不修整段 C1，不扩展 88 键求解器，不改合同，不合并候选。静态与密集证据只说明这两组局部抬指/屈曲参数不足，不能证明原 Rig 所有合法姿态都无解。
'''
with (OUT/'TECHNICAL_REPORT.md').open('x',encoding='utf8') as f:f.write(text)
human=f'''# HUMAN REVIEW · PARTIAL · NOT_APPROVED

{now}。两个窗口均改善但真实穿模未消失；另有 G♯4 既有侵入加深与小幅烘焙边界偏差。请以以下 FINAL 媒体审核。本轮已停止，候选没有并回原 C1。

- {link('FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4')}
- {link('FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4')}
- {link('A_BEFORE_AFTER_GEOMETRY.png')}：0.433333s，4.328 → 1.945mm，仍相交。
- {link('B_BEFORE_AFTER_GEOMETRY.png')}：2.600000s，5.637 → 1.762mm，仍相交。
- {link('IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend')}
- {link('TECHNICAL_REPORT.md')}
- {link('QUANTITATIVE_TABLE.csv')}
- {link('PROTECTED_AFTER_AND_SHA256_RECEIPT.json')}

视频左右为原 C1 / 实验 B；第一段源时间 0–1.35s（含 PREPARE 与 A4），第二段 2.10–3.60s（含退出后回归）。无需用俯视遮挡猜测碰撞，红圈见证与实际三角面深度在图和 JSON 中。

Human 重点观察持续抬起、食指曲度、进入/退出速度、A4 前复位及其他指的视觉关系。48 接触 PASS 不代表整指安全；当前结果不具备生产批准条件。请保留 PARTIAL 与历史 FAIL 身份。

原 C1（只读）：[{SOURCE.name}](<{SOURCE.as_posix()}>)。

STOP — HUMAN REVIEW
'''
with (OUT/'HUMAN_REVIEW.md').open('x',encoding='utf8') as f:f.write(human)
save('FINAL_DELIVERY_MANIFEST.json',dict(result='PARTIAL',files=[dict(path=str(OUT/n),sha256=sha(OUT/n)) for n in ['TECHNICAL_REPORT.md','HUMAN_REVIEW.md','RESULT.json','QUANTITATIVE_TABLE.csv','FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_1X.mp4','FINAL_C1_VS_IDLE_INDEX_B_OVERHEAD_0_5X.mp4','A_BEFORE_AFTER_GEOMETRY.png','B_BEFORE_AFTER_GEOMETRY.png','IDLE_INDEX_CLEARANCE_B_NOT_APPROVED.blend','PROTECTED_AFTER_AND_SHA256_RECEIPT.json']],stop='HUMAN REVIEW'))
print('FINALIZED PARTIAL',len(receipts),'protected inputs unchanged',flush=True)
