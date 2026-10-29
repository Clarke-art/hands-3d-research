# 清理后保护检查 R1

**PASS**。没有启动Blender、动画求解、重渲染、模型训练或安装依赖。全部检查为文件清单/哈希和只读HTTP/浏览器访问。

## 正式保护资产

| 文件 | 角色 | SHA256 | 结果 |
|---|---|---|---|
| <HANDS_ROOT>\production_spec\right_hand_product_baseline_r2\RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R2.blend | HUMAN_APPROVED_FROZEN | c946fed318fa88c238d9aacc30cfb4e52f268848f0ad65a4dcbf594754d791f0 | PASS |
| <HANDS_ROOT>\production_spec\right_hand_product_baseline_r1\RIGHT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend | HISTORICAL_FROZEN_FALLBACK | 4aa26e3aa6b1f5e61f392650a597812cdc5548fade3b24805133682f77c6e7d2 | PASS |
| <HANDS_ROOT>\production_spec\left_hand_product_baseline_r1\LEFT_HAND_OFFICIAL_L1_PRODUCT_BASELINE_R1.blend | HUMAN_APPROVED_FROZEN | 54307bb199a75a5e684c29d346de9ca6bf2f8e7696911d9d69c57559516ad1a7 | PASS |
| <HANDS_ROOT>\audits\piano_hand_static_posture_clearance_refinement_r2\STATIC_POSTURE_REFINED_CANDIDATE_R2.blend | FOUR_HUMAN_APPROVED_STATIC_SCENES_STATIC_L1_STATIC_L2_STATIC_R1_STATIC_R2 | 18359b1c2c6e8abaa1a4444f342e7672a1f1fda35d96cc95146bc8d1161b551c | PASS |
| <HANDS_ROOT>\audits\minuet_stage_a_r2_natural_continuous_motion\STAGE_A_R2_COORDINATED_RIGHT_DESIGN_ONLY.blend | HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN | e932b6ec47b0ee8822149cf232157d0a28e95b9878a91abdaca9bf8c62f48185 | PASS |
| <HANDS_ROOT>\audits\minuet_stage_b_r3_budget_policy_candidate_recovery_r1\STAGE_B_R3_RECOVERED_CONTACT_DESIGN_ONLY.blend | HUMAN_VISUAL_APPROVED_WITH_ENGINEERING_WARN | a4c51e660725335922916c179d65883146eb249848f95793c566d1e2d5ebfe63 | PASS |

四个静态姿态STATIC_L1/L2/R1/R2的R2源容器和求解/策略/scene manifest完整；右手R2、左手R1生产指针及来源完整；Stage A R2/B R3批准动画源哈希完整。当前C1/C2等保留Blend亦在全部Blend哈希核对范围。

## 核心程序与必要输入

2186个Manifest受保护源码SHA全部相同。19779个保留文件的fileID/device/nlink/size/mtime全部保持；600个重要保留文件（全部Blend/NPZ/MIDI/WAV/MP4、页面及关键JSON等）与删除前实测SHA全部一致。

| 保留类别 | 数量 | 检查 |
|---|---:|---|
| .blend | 90 | SHA-256 before/after一致 |
| .npz | 98 | SHA-256 before/after一致 |
| .mid | 3 | SHA-256 before/after一致 |
| .wav | 55 | SHA-256 before/after一致 |
| .mp4 | 121 | SHA-256 before/after一致 |

MIDI驱动、performance_core、双手融合、琴键动作和音频接口，以及_deps实际代码和二进制，均保留。全文件元数据无变化；2186项指定源码逐项SHA匹配，第三方依赖中仅获批且有.py的字节码缓存删除。

## 审核页面

两套HTML源哈希保持。lightweight和pedagogical两套_frames共2142张PNG逐一SHA相同；2174个必要HTTP白名单资源访问均PASS，视频Range请求206，4097条原有静态HTML引用仍存在。浏览器实际测试原速播放、音符六阶段定位、俯视/侧斜切换、逐帧前进、同期旧新图对照、0.5倍速与末帧356滑块，PNG naturalWidth=1280、加载完整，第二页控制台错误0。没有进行声音听感或动画质量重新批准。

## 精确例外

实际缺失18409文件与账本SUCCESS集合完全一致，未发现其他缺失/新增/保留文件变化；所有KEEP/HUMAN_REVIEW/OUT_OF_SCOPE文件仍在。C1/_frames仅删除1069个批准成员，两张OVERHEAD/0024.png、SIDE_OBLIQUE/0024.png保留。没有删除目录，1239个目录骨架均保留。

原Manifest/基线SHA仍锁定。旧历史全目录校验将出现获批缓存缺失；本轮不冒称原始全目录校验PASS。只有账本DELETE_RESULT且result=SUCCESS的精确路径能作为例外，其他缺失仍必须FAIL_CLOSED。
