# production_spec/stage1c_c1_qualification

这是历史研究证据导航，不是新增实验或能力认证。原始与公开版本通过SHA映射区分。

## 研究目标

> | **G-15** | `ADULT_NEUTRAL` | **PASS**（附比例说明） | 成人比例：腕→中指尖 **18.6 cm**（成人区间）；掌宽 15.1 cm 中实际掌部约 7–8 cm；**无男性化特征**（无粗壮指节、无突出肌腱、指身匀称）；**无女性化特征**（无纤细指尖、无修饰性指甲——本资产**完全没有指甲**）；**非儿童比例** | 包内 realistic 系列**只有一只 hand 资产**（无 male/female 之分）→ 设计上即为中性基础手，与 `ADULT_NEUTRAL` 目标一致 |

出处：[GEOMETRY_ANATOMY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md)

> | hand topology 是否值得作为 C-1 备选？ | 官方明确把"通用拓扑（universal mesh）+ 手部拓扑演进"作为设计目标，方向与"可 Rig、可复用"一致；但**手部解剖精度是 MakeHuman 的公认弱项**（`SB-R2`） | 方向可信，**精度未验证** |

出处：[C2_MAKEHUMAN_LIGHT_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/C2_MAKEHUMAN_LIGHT_CHECK.md)

## 技术路线

> > **测量方法（可复现）**：在 Blender 4.5.9 中对**环向 edge loop** 做真实遍历

出处：[TOPOLOGY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md)

> - 其是否由"参考图"升级为"母体来源"，属 `STAGE0_ROUTE_C_AMENDMENT` 议题，**本轮不裁定**。

出处：[C1_LICENSE_RECORD.md](../research/production_spec/stage1c_c1_qualification/license/C1_LICENSE_RECORD.md)

## 测试结论

> > 脚本：`scripts/pass9_edge_loops.py`（base 层）、`scripts/pass10_multires_loops.py`（multires L1）。

出处：[TOPOLOGY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md)

> | T-03（指缝不得粘连） | ✅ `PASS` |

出处：[TOPOLOGY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md)

## 失败原因与证据边界

原始优先报告未明确记录该字段；不自动编造根因或推断成功。下面保留完整原报告供审阅。这是历史记录边界，不是需要重新开展研发的指令。

## 后续建议

> **T-07 = PASS**，且**利于后续用同一套权重模板**（`S-07`）。

出处：[TOPOLOGY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md)

>    CC0 声明只存在于**官方分发页面**。→ 后续复用时**必须连同官方页面证据与哈希一起留档**（本目录已保存原始 zip 归档）。

出处：[C1_LICENSE_RECORD.md](../research/production_spec/stage1c_c1_qualification/license/C1_LICENSE_RECORD.md)

## 原报告与关键代码

- [production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/TOPOLOGY_CHECK.md)
- [production_spec/stage1c_c1_qualification/license/C1_LICENSE_RECORD.md](../research/production_spec/stage1c_c1_qualification/license/C1_LICENSE_RECORD.md)
- [production_spec/stage1c_c1_qualification/stats/ASSET_GEOMETRY_STATS.md](../research/production_spec/stage1c_c1_qualification/stats/ASSET_GEOMETRY_STATS.md)
- [production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/GEOMETRY_ANATOMY_CHECK.md)
- [production_spec/stage1c_c1_qualification/stats/C2_MAKEHUMAN_LIGHT_CHECK.md](../research/production_spec/stage1c_c1_qualification/stats/C2_MAKEHUMAN_LIGHT_CHECK.md)
- [production_spec/stage1c_c1_qualification/stats/RSSF_POSE_DELTA_AND_FOREARM.md](../research/production_spec/stage1c_c1_qualification/stats/RSSF_POSE_DELTA_AND_FOREARM.md)
- [production_spec/stage1c_c1_qualification/scripts/pass10_multires_loops.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass10_multires_loops.py)
- [production_spec/stage1c_c1_qualification/scripts/pass11_orientation.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass11_orientation.py)
- [production_spec/stage1c_c1_qualification/scripts/pass12_knuckles.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass12_knuckles.py)
- [production_spec/stage1c_c1_qualification/scripts/pass1_inventory.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass1_inventory.py)
- [production_spec/stage1c_c1_qualification/scripts/pass2_stats_probe.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass2_stats_probe.py)
- [production_spec/stage1c_c1_qualification/scripts/pass3_fingers_renders.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass3_fingers_renders.py)
- [production_spec/stage1c_c1_qualification/scripts/pass4a_centers.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass4a_centers.py)
- [production_spec/stage1c_c1_qualification/scripts/pass4b_rings.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass4b_rings.py)
- [production_spec/stage1c_c1_qualification/scripts/pass5_topology_rings.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass5_topology_rings.py)
- [production_spec/stage1c_c1_qualification/scripts/pass6_loops_unionfind.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass6_loops_unionfind.py)
- [production_spec/stage1c_c1_qualification/scripts/pass7_diag.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass7_diag.py)
- [production_spec/stage1c_c1_qualification/scripts/pass8_dump.py](../../src/legacy/production_spec/stage1c_c1_qualification/scripts/pass8_dump.py)

## 输入、输出与大型证据

该目录原始成员 65 项；拟公开身份记录 65 项。

全部逐文件定位与排除理由见 [原始路径表](../../release-assets/ORIGINAL_PATH_MAP.csv) 和 [公开清单](../../release-assets/R1_PUBLICATION_MANIFEST.csv)。

外部贡献者应先复现最小接口或一个已有失败反例；不要从本卡的关键词摘录推断全部历史流水线可执行。
