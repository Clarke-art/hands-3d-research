# LEFT_HAND_MULTI_CONTACT_FEASIBILITY · Stage B R1

**对本和弦已有冻结左手自身的实际多指静态接触证据；不宣称所有和弦或自然度已获批准。** 预检没有证明需要修改Rig，也没有要求重建资产。

复用正式左手R1、21骨骼及既有L轴向FK、L指腹marker和批准L1/L2放置根。没有镜像Stage A右手轨迹。三个主动链分别为LITTLE_MCP/PIP/DIP_L、MIDDLE_MCP/PIP/DIP_L、THUMB_CMC/MCP/IP_L，九个骨名无重叠；每指自身屈伸与基部展开自由度可独立参与同一共同root问题。

左右手骨名、rest相对矩阵、局部flex/spread轴与pad局部坐标从各自 `c.SETUPS`/`c.RIG`/`c.MARKERS`读取。不能把右手关节世界运动符号简单反转；本轮批量L FK与原L FK在中性/工程上下界3组确定性输入中误差小于1e−12m。

L1/L2只提供自然关节参考，使用二者关节平均作为先验；共同root的位移由新目标键几何驱动。没有把D2/D3任务或它们的原固定接触点当作G3/B3/D4目标。主动指用既有THUMB/LONG工程域；闲置食指/无名指使用已有LEFT_IDLE_INDEX/RING域与非均匀弯曲参考。

有限预检每个机械阶段都将root平移/必要旋转、五指关节、三接触XY放入一个问题：起音面、三键全下沉、三指预备上方。不是先固定root再做三个单指IK。三个阶段的最大目标偏差分别约0.012、0.033、0.012mm；这只是可行性证据，不是Human批准。

正式Blender静态回读在未保存的场景副本中验证了原左手皮肤、Rig与移动琴键：全下沉三指skin marker间隙G3约0.549mm、B3约0.457mm、D4约0.503mm，全部在实际可奏区域。实际pad与FK最大差约0.00055mm。静态测试0个Action、0个动态候选、0份保存blend；两张正常视角图片仅为STATIC_PREFLIGHT。

同一接口只读接受另一组三音目标57/61/64（含黑键）且产生3个同时任务，拒绝同一手指承担重叠两个目标；不生成第二轨迹或音频，不宣称另一和弦已动态通过。

限制：某些腕旋转/关节接近工程边界，这些域不是生理认证。线性代理不是完整软组织/三角碰撞；真实皮肤和正常动态视频必须复核。小指与中指的曲度、拇指展开及两闲指放松状态留给Human。预检通过只授权本轮唯一动态候选。

证据：`STATIC_FEASIBILITY.json`、`ACTUAL_LEFT_STATIC_READBACK.json`、`GENERIC_CHORD_INTERFACE_CHECK.json`。预检修复过Blender3.13与CLI3.12的SciPy导入边界：求解仅在CLI加载SciPy，Blender只读取FK/已求解数据；未修改动作参数或冻结代码。
