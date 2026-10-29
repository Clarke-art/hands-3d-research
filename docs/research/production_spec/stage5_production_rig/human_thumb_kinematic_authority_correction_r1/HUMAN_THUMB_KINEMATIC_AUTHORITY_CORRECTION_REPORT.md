# HUMAN_THUMB_KINEMATIC_AUTHORITY_CORRECTION

THUMB_KINEMATIC_AUTHORITY_CORRECTION = **HUMAN_APPROVED**；APPLICATION = **APPLIED_VERIFIED**。

Human 在 2026-10-03（Asia/Shanghai）当前 chat 直接批准此前审阅的 `KINEMATIC_CANDIDATE_R1`：保留 IP head，应用另外 5 个 slot。消息转录保存为 `HUMAN_DECISION_SOURCE_R1.txt`；它的 hash 仅覆盖本地转录，不冒充 chat transport signature。正式批准与 correction authority 分别见 `HUMAN_THUMB_KINEMATIC_APPROVAL_R1.json` 和 `THUMB_DISTAL_IP_TIP_KINEMATIC_CORRECTION_AUTHORITY_R1.json`。

## 应用结果

新建 skeleton-only 修正文件：`RIGHT_HAND_STAGE5A_PRODUCTION_RIG_THUMB_KINEMATIC_CORRECTED_R1.blend`。以历史 R2A 为输入，只执行批准的三项端点赋值和两项 edit-roll 赋值，没有重新构建 skeleton，没有重新拟合或运行 selector。历史 R2A 与此前 review/candidate 文件均未覆盖。

| Slot | Before（位置为 world m） | After（位置为 world m） | Δ |
|---|---|---|---:|
| THUMB_IP_R.head | [1.450860857964, 0.006127120927, 0.464001148939] | [1.450860857964, 0.006127120927, 0.464001148939] | 0.000000000 mm |
| THUMB_IP_R.tail | [1.452817440033, 0.019802358001, 0.493028342724] | [1.451482534409, 0.010474493727, 0.485554456711] | 12.027052718 mm |
| THUMB_IP_R.roll | 2.469186782837 rad | 2.477157831192 rad | 0.456707429 deg |
| THUMB_TIP_R.head | [1.452817440033, 0.019802358001, 0.493028342724] | [1.451482534409, 0.010474493727, 0.485554456711] | 12.027052718 mm |
| THUMB_TIP_R.tail | [1.453404426575, 0.023904928938, 0.501736521721] | [1.451668977737, 0.011778705753, 0.492020428181] | 15.635202111 mm |
| THUMB_TIP_R.roll | 2.469188213348 rad | 2.477157831192 rad | 0.456625467 deg |

所有 actual local endpoint 和 edit-roll 数值与 approved 值的 float32 表示完全一致。IP tail、TIP head 及两个 roll 与批准值无数值偏差；TIP tail 的 world 计算结果存在 **0.0000631503 mm** 存储/世界坐标运算舍入差。该值单列为 storage error，不构成重新选点。完整 world/local/roll before/after、approved 数值及逐 slot SHA256 见 `THUMB_KINEMATIC_BEFORE_AFTER_SLOT_VALUES.json`。

## 无漂移与存盘验证

修正文件保存后重新打开，完整数据 snapshot 与保存前结果精确相同。IP head local/world 逐值相同，19 根无关骨骼的 head/tail/roll/local matrices、parent/connect/deform、继承模式、collections、custom properties 和 pose transforms 完整逐值相同。全量 21 bone hierarchy、16 deform / 5 non-deform 构成不变。IP tail 与 TIP head 完全共点，TIP 仍是 connected non-deform helper。

armature origin/transform、mesh origin/transform 及所有 object transforms 逐值相同。mesh 顶点、edge/polygon topology、UV、material assignment、smooth flags、vertex groups/weights、shape keys、mesh parent 和 modifier inventory 完全相同。详见 `HIERARCHY_ORIGIN_UNRELATED_BONES_DRIFT_VERIFICATION.json` 和 `RIG_BEFORE_AFTER_FULL_SNAPSHOTS.json`；前者含所有 63 bone slots 的 before/after canonical hashes。

## Hash 链

- reviewed candidate SHA256：`c6e31f988ee1608391ebe2a2ea868dfc690b9fbc623cd174348e053320368e17`
- source R2A before SHA256：`c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845`
- source R2A after SHA256：`c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845`
- corrected rig SHA256：`5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe`
- Human approval combined hash：`381c094a5da6786b6b64d149ee68aceca5450fb4ad1a414b70e43672dde9d72f`
- correction authority combined hash：`6325d030cbc1b12369bb208044657cb711aa29af017509cf52ce03c948c080c4`
- cap37 combined authority hash：`c81dd96d6925ed402cdf0ba44c148d7a78c2c60640fe23fb6247fb729f346cc8`

全部文件与 payload hash scope 见 `HUMAN_THUMB_KINEMATIC_CORRECTION_HASHES_R1.json`。本輪保护 1614 个历史工作区文件和 6 个外部输入，before = after 全部通过。保护包括历史 Stage5A/B、R3、Stage6、cap37、Human responses 和此前候选/审计。没有本轮目录以外的新文件。

## 生效范围与停止点

新 authority 仅取代历史 R2A 的 thumb distal IP/TIP kinematic slots；IP head 保留。`THUMB_KINEMATIC_CORRECTION_APPLICATION_RECORD_R1.json` 将新 blend 指定为下一轮 thumb kinematic reconciliation 的正式输入。历史 hardcoded downstream loaders 尚未更新，未来任务必须显式接入该 authority；不得把旧 R2A frozen 数值继续视为这些 distal slots 的 authority。

本次 Human approval 不批准 R2、R3、skin weights、Stage5B、Stage6A、Stage6B 或 strict-bound results。GEOMETRY_DELTA = 0，TOPOLOGY_DELTA = 0，WEIGHT_DELTA = 0，unapproved bone/joint slot delta = 0。只有批准的 5 个 slot 改变。

BLEND_FILES_WRITTEN = **1**（新 skeleton derivative）；historical blend files written = **0**。

R2_runs = **0**；R3_runs = **0**；skin rebuild runs = **0**；Stage5B_runs = **0**；Stage6_runs = **0**；R1F_created = **NO**。

NEXT = **CAP_DERIVED_R2_R3_INPUT_RECONCILIATION_R1**。

STOP = **YES**。
