# Human视觉复核

BRIDGE_MOTION_PARTIAL · DESIGN_PROVISIONAL · STOP — HUMAN REVIEW。

动态技术检查失败，因此没有1倍速或0.5倍速视频。保留6张1280×720实际Blender静帧用于诊断；没有PNG序列缓存。端点两图与Action四图使用相同视向，后者为容纳整手扩大了视野，不能按像素直接量距。

| 文件（stills目录） | 时刻/内容 |
|---|---|
| ENDPOINT_OVERHEAD.png | 新E5端点，ON+35ms，俯视 |
| ENDPOINT_SIDE_OBLIQUE.png | 同端点，侧斜 |
| BRIDGE_START_OVERHEAD.png | B2实际Action起点2.527855秒 |
| EXCHANGE_OVERHEAD.png | 精确换音2.921426秒，失败 |
| EXCHANGE_SIDE_OBLIQUE.png | 同换音，侧斜，失败 |
| PLUS35MS_OVERHEAD.png | 2.956426秒，局部触键通过但不能补偿ON失败 |

待审：新端点的主动中指屈曲与掌腕姿态是否自然；拇指在换位中的打开是否过快；整体准备路线是否像自然手部协调。Human对B2中指的初审认可不扩展到新端点或整个候选。

数据支持的风险：腕部峰值速度217.355mm/s、峰值加速度8969.162mm/s²；拇指spread控制峰值约256.912°/s。没有足够临床依据把这些设为统一舒适阈值，保留为视觉风险指标。原始root速度是远离腕部的对象原点速度，应使用汇总JSON中明确区分的腕部、控制平移与对象原点指标。

中指spread全程约−6.732至−7.196°，PIP/DIP没有独立侧向自由度，参考族检查0失败；这不代表Human自然度已通过。中/无名最小精确间隙2.896212mm也不能单独宣称连续动作安全。

图中穿键与接触丢失以实际几何记录为准；静帧不能显示完整速度、加速度或证明动作连续。所有图仅支持失败诊断，不用于教学发布。
