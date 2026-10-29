# Human视觉复核 — C01 R1

状态MOTION_FEASIBILITY_PARTIAL；不是Human视觉PASS。只渲染7张720p Workbench静帧；正确显示原对象黑白键颜色，保留网格线便于看交叠。左手若出现在画面边缘，是源场景未改变的既有左手，不是本轮双手生成。

视频未渲染。真实碰撞门禁失败，按任务要求停止；无1x视频、0.5x或0.25x降速文件，不能宣称慢速自然度已经验收。没有临时PNG序列/GB缓存，仅保留这些交付静帧。所有截图都是同一份保存Action的求值结果，没有重算或选择替代动作。

隔离场景：[C01_WHOLE_HAND_MOTION_DESIGN_PROVISIONAL_R1.blend](../../../artifacts/4c4f96974d6b1acb56fe.md)。其中实验场景C01_WHOLE_HAND_MOTION_FEASIBILITY_R1，60fps，原绝对时间轴；新Action为C01_R1_WHOLE_HAND_ROOT_DESIGN_ONLY及C01_R1_FIVE_DIGIT_COORDINATED_DESIGN_ONLY。可由Human在Blender中低速复核，不能替换旧动画。

## 重点判断

1. R07→R08：观察中/无名指明显交叉。R08触键+35ms截图对应80对相交；原同时间为0。不能仅看上行指序就断言该段成功。
2. B02同视角、同时间3.825秒：旧中/无名指明显交叉，新图在该探针分开；数值122→0。但五音前段仍有互穿峰41对，单张新图不能证明整个B02已解决。
3. F♯5四指：用侧斜图看键面高差、指腹侧面及闲置指邻键侵入；接触点到位不等于整指体避障。
4. 八度回位：R14拇指接近G4，但拇指侧面/其他区域侵入邻A4，不能批准回位。
5. 手腕自然度：240Hz实际腕点速度峰277.226mm/s，加速度峰14527.103mm/s²；不是生理门槛或视觉判定。连续Action存在并已测量，但没有视频与慢放自然度通过证据。

### C01 · R07_R08_PREPARE · OVERHEAD

展示时间2.8964260秒，真实求值Action静帧；[原图](../../../artifacts/fd7b31266f482cdf86be.md)

[R07_R08_PREPARE](../../../artifacts/fd7b31266f482cdf86be.md)

### C01 · R08_E5_MIDDLE · OVERHEAD

展示时间2.9564260秒，真实求值Action静帧；[原图](../../../artifacts/2decfeacedd19f67ab6e.md)

[R08_E5_MIDDLE](../../../artifacts/2decfeacedd19f67ab6e.md)

### C01 · B02_E5_HANDOVER · OVERHEAD

展示时间3.8250000秒，真实求值Action静帧；[原图](../../../artifacts/1c1220218b152353e5f5.md)

[B02_E5_HANDOVER](../../../artifacts/1c1220218b152353e5f5.md)

### C01 · R12_FSHARP_RING · OVERHEAD

展示时间4.0278535秒，真实求值Action静帧；[原图](../../../artifacts/8af4f2ef5aed0e659b6c.md)

[R12_FSHARP_RING](../../../artifacts/8af4f2ef5aed0e659b6c.md)

### C01 · R12_FSHARP_RING · SIDE_OBLIQUE

展示时间4.0278535秒，真实求值Action静帧；[原图](../../../artifacts/c0bcde98d42cfea898cf.md)

[R12_FSHARP_RING](../../../artifacts/c0bcde98d42cfea898cf.md)

### C01 · R13_R14_OCTAVE · OVERHEAD

展示时间4.6707100秒，真实求值Action静帧；[原图](../../../artifacts/1cec714ee5a2c71c4cb3.md)

[R13_R14_OCTAVE](../../../artifacts/1cec714ee5a2c71c4cb3.md)

### OLD · B02_E5_HANDOVER · OVERHEAD

展示时间3.8250000秒，真实求值Action静帧；[原图](../../../artifacts/8d5d09addea61c15736a.md)

[B02_E5_HANDOVER](../../../artifacts/8d5d09addea61c15736a.md)

**STOP — HUMAN REVIEW。** 本轮不再优化，不扩展完整23音或双手制作。
