# TARGETED_RIG_AND_SKIN_DATA_REBUILD_R2

**R2_STATIC_CANDIDATE = PASS_READY_FOR_TARGETED_DEFORMATION**. NEXT = **CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1**. STOP.

R2独立candidate已由R1载入创建；R1和全部历史文件未修改。Static-ready表示可以进入下一轮targeted qualification，不表示no defects、deformation PASS或production promotion。本轮pose/deformation/Stage6/R3/anatomy运行均为0。

## Human与精确权限

唯一Human响应 `SKIN_STATIC_GATE_AND_SCOPE_AMENDMENT_HUMAN_REVIEW_R1_RESPONSE_2026-10-03T14-57-26.511Z.json` 的review/phase、Q1..Q5、accepted/answered、授权phase及三个禁止flag全部精确匹配。proposal SHA256 `b023f12f40f4eb0bbf32ba4944a6d43fe1503c7b8a3051326e983e05727f7e02`；R1 SHA256 `290d2734f80edb25872962bf378dbc4c122d6fafe3fd118b22a6e550ddfcb84a`。原authority bundle及12个组件hash均通过。

唯一write universe为317=244原权限+18连续性修复+55仅清除残留；三个集合互斥。317/317均执行对应rule evaluation。实际变化207，原244变化134、新增18变化18、cleanup55变化55。Outside317 write/drift均0。

55点不进入optimizer，严格按原allowed正分量比例归一化，再float32序列化；列出的forbidden entries全部精确清除，新增driver=0、free smoothing=0。Canonical zero epsilon仍为0。

## 静态solver与authority

复用原正式deterministic harmonic method的MED/edge-length正权系数、0.01几何prior、sorted cyclic simplex updates，扩展为经Human批准的联合自由集合，并让所有三方interface与外pins参加。初始化只来自R1与静态approved bone-distance prior。之后用deterministic Dykstra投影约束本地支持simplex、所有自由点incident edges的L∞≤0.5/L1≤1。Stable ordering/ties、fixed tolerance1e-10、max30000；内部rounding guard使目标略严于正式gate，未放宽threshold。165次harmonic sweeps、100次projection sweeps收敛。两次独立完整求解得到相同vector hash `1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55`。

**110个已正确distal-profile点固定保持R1值**，包含cap37及相邻兼容thumb support；逐点重新按corrected arc quintic计算并匹配float32。cap37 37/37 IP dominant且quintic exact，全部未被solver改动。其余14个原proximal THUMB点与新增5个非web THUMB点在有支持的CMC/WRIST base transition中联合修复；条件IP/MCP driver pair保持corrected-arc quintic比例，不把ownership变成one-hot，不改变cap/真正distal profile。局部base budget依据static topology/support连续优化，而不是把R1失败的proximal vectors当成immutable。

INDEX与web仍使用原approved group families。Old cap9 9/9为native INDEX-compatible，THUMB override未恢复。FIRST_WEB21 membership不变，新增13点加原v3125共14个可写；剩余7点copy-only。FIRST_WEB的THUMB_IP和TIP影响均精确0。Edge5879的v1551/v3125继续原write authority，二者都已重新调整，未导入R1E failure vectors。

## 完整静态closure与因果记录

检查 **2127 edges**：包含上一轮2089、全部317 incident/crossing、FIRST_WEB完整2-ring、fresh-R3 boundary、cap37 2-ring、oldcap9 patch与edge5879原neighborhood。新增checked edges38；不是仅复查原64。

原64个absolute blockers关闭 **48**，剩余 **16** 全部为兩端完全copy-only、R2=R1=donor。R2_INTRODUCED=0，R2_WORSENED=0，TRUE_SCOPE_CONFLICT=0。Driver-family boundary没有自动waive gate。

**INHERITED_QUALIFICATION_DEBT IDs**：`[1130, 1137, 1171, 1172, 1174, 1176, 1555, 4417, 4421, 4425, 4427, 4428, 4431, 4474, 4881, 5474]`。这16条仍超过绝对screen，不能写成“no defects”。它们保留下一轮targeted qualification义务，单独与candidate delta归因。

edge1130：inherited debt，R2/R1/donor相同，L∞=0.655587911605835、L1=1.31117582321167。

edge1234：已关闭，L∞=0.0865461602807045、L1=0.41661688685417175。v338仍只允许INDEX/WRIST，v1448采用shared web groups，不需要增加任何新权限。

edge5879：已关闭，L∞=0.06026959419250488、L1=0.16152597963809967。这里只报告saved weight静态指标，没有deformation改善声明。

所有超过1e-5的增加均保留：R2-vs-R1 222条、R2-vs-donor 302条。它们全部低于absolute gates；boundary/preexisting seam的增加作为明确记录的targeted qualification上下文保留，没有在本轮假装获得deformation qualification。这不改变用户本轮指定的“introduced/worsened absolute blockers为0，可进入下一轮qualification”的条件。

## 全mesh数学、保存与保护

3416点归一化、negative/NaN/Inf、max4、nondeform/TIP、FIRST_WEB IP、freshR3 forbidden guard全部PASS，forbidden-positive residue=0。最大sum error `4.400499165058136e-08`，正式容差1e-5。

R2保存后用独立factory-startup Blender5.1.2 clean reload重新读取所有mesh transforms/topology/UV/material binding、21 bones完整hierarchy/corrected slots及3416 vectors，serialization drift=0。另以只读Blender比较材料properties、shader nodes、socket defaults、links与image配置，exact PASS。Geometry/topology/UV/material/bone/joint delta均0。

保护快照涵盖2128个历史文件/唯一响应：before=after，drift=0；R2 task以外新文件=0。所有文件写入仅在本R2目录，历史blend写入=0，R2 blend保存1次。R2 container不宣称每次另存字节可重复；可重复的是两次deterministic solver的完整float32 weight payload hash。

## Candidate与输出

Candidate：`production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2/RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend`

SHA256：`adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9`

Weight vector SHA256：`1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55`

至少要求的scope、317 evaluation、cleanup、continuity/因果分类、R2/R1/R1B delta、math、FIRST_WEB/cap37/oldcap9/edge5879、geometry/rig与save/reopen JSON均位于本目录；完整指标与向量记录供下一轮使用。

NEXT = **CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1**。本轮deformation=0，Stage6=0，不自动启动下一轮。STOP。
