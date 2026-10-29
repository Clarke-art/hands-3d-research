# Human静态视觉复核 — R1

状态STATIC_FEASIBILITY_PARTIAL，全部DESIGN_PROVISIONAL。仅8张1280×720静帧，未制作视频或PNG序列。已有左手若在画面边缘，仅为原场景参考，不是本轮新求解。

| 测试 | 实际指/键 | 状态 | pad距键mm | 真表面接触距mm | 目标实体侵入mm | 非目标/非指腹最大侵入mm | 指面相交 | 近接触面积mm² |
|---|---|---|---|---|---|---|---|---|
| S1 | 1指/G4 | FAIL两组初始化 | 0.322696 | 0.000000 | 0.549002 | 0.003682 | 0 | 0.924262 |
| S2 | 3指/E5 | PASS静态门禁/待Human | 0.880341 | 0.000000 | 0.001812 | 0.000000 | 0 | 0.774231 |
| S3 | 1指/C5 | PASS静态门禁/待Human | 1.574503 | 0.000000 | 0.070706 | 0.000000 | 0 | 1.559265 |
| S4 | 4指/F♯5 | PASS静态门禁/待Human | 0.175342 | 0.000000 | 0.001658 | 0.000000 | 0 | 1.002064 |
| S5 | 1指/G4 | 仅探索，前置条件不成立 | 1.580820 | 0.000000 | 0.075409 | 0.000000 | 0 | 1.559960 |


## 审查要点

- INITIAL红色位置：食指远节/A♯4、无名指远节/C♯5真实侵入。顶点深度约1.590/0.666mm，面内部深度约1.740/0.842mm。
- S1图采用第一次C01初始化，目标G4面侵入0.549mm，最小顶点看似尚有+0.006mm间隙，却不是合法整体接触。第二批准R1初始化也未过，目标侵入0.278mm；两组都保留在Blend和JSON。拇指白键前缘/侧缘及三角面3869见证点为重点。
- S2 E5中指：实际触点在键面，非目标侵入0、指面交叉0；但中/无名指采样间隙约0.138mm，是微小安全余量，须侧斜/Blend复核，不据此推断动态安全。
- S3 C5拇指：目标内数值侵入约0.071mm，在事前0.25mm合同内；真实面上接触存在，不能误用pad高约1.575mm判它悬空。此解达到迭代上限未宣称收敛，最终依据真实几何门禁。
- S4 F♯5无名指：侧斜观察黑键高差，实际触点存在，非目标侵入/指面交叉0。近接触面积不是力学承载面积。
- S5未列图：在代理检查通过后先算过，但更严格面检测使S1失败，故只保留探索数据，不算正式前置通过后的八度验证。

诊断Blend：[SKIN_COLLISION_STATIC_DIAGNOSTIC_R1.blend](../../../artifacts/9cd8a95766757606da7b.md)。场景S1_INIT_1/2、S2_INIT_1/2、S3_INIT_1/2、S4_INIT_1/2、S5_INIT_1/2均是STATIC_ONLY：当前按压键状态取自原Action，各实验场景对象动画已解绑、无新关键帧。原动画datablock可能作为继承参考存在，不代表本轮生成了连续动画。不要通过播放这些静态场景推断动作可行。

### INITIAL · OVERHEAD

C01 INITIAL - FAIL: INDEX / A#4; RING / C#5。红色引线起点是真实侵入见证点；标记抬高15mm仅为可见，不代表移动手部。

[INITIAL OVERHEAD](../../../artifacts/231f3a42fbf896b82bcf.md)

### S1 · OVERHEAD

S1: MIDI 67, FINGER 1 -- FAIL: TARGET DEPTH 0.549 mm。红色引线起点是真实侵入见证点；标记抬高15mm仅为可见，不代表移动手部。

[S1 OVERHEAD](../../../artifacts/142b15ab794afa678859.md)

### S1 · SIDE_OBLIQUE

S1: MIDI 67, FINGER 1 -- FAIL: TARGET DEPTH 0.549 mm。红色引线起点是真实侵入见证点；标记抬高15mm仅为可见，不代表移动手部。

[S1 SIDE_OBLIQUE](../../../artifacts/04fca76d34cce0426f44.md)

### S2 · OVERHEAD

S2: MIDI 76, FINGER 3 -- STATIC SCREEN PASS, HUMAN PENDING。真实静态求值网格。

[S2 OVERHEAD](../../../artifacts/cf2229637fa22c2200ef.md)

### S3 · OVERHEAD

S3: MIDI 72, FINGER 1 -- STATIC SCREEN PASS, HUMAN PENDING。真实静态求值网格。

[S3 OVERHEAD](../../../artifacts/ad52854bc05da5a41bdf.md)

### S4 · OVERHEAD

S4: MIDI 78, FINGER 4 -- STATIC SCREEN PASS, HUMAN PENDING。真实静态求值网格。

[S4 OVERHEAD](../../../artifacts/86843db257e99faf8191.md)

### S4 · SIDE_OBLIQUE

S4: MIDI 78, FINGER 4 -- STATIC SCREEN PASS, HUMAN PENDING。真实静态求值网格。

[S4 SIDE_OBLIQUE](../../../artifacts/f27277aca2926f68221a.md)

### S2 · SIDE_OBLIQUE

S2: MIDI 76, FINGER 3 -- STATIC SCREEN PASS, HUMAN PENDING。真实静态求值网格。

[S2 SIDE_OBLIQUE](../../../artifacts/6ca865f18a5c87444da6.md)

**STOP — HUMAN REVIEW。** 不自动进入连续动作求解。
