# KEY043 前止挡机械职责

2026-10-11 · FRONT_STOP_COMPATIBILITY_DIAGNOSTIC_ONLY · STOP — HUMAN REVIEW

基线：SCIENTIFICALLY_CONSTRAINED_REPRESENTATIVE_INSTALLED_INTERFACE。仅读取历史记录和解析计算；未启动 Blender，未执行历史脚本，未创建新姿态。

## 结论

FRONT_STOP_ROLE = CONFIRMED。R8_KEY_043_FRONT_STOP 是前端按下行程的有限柔性下止挡，承担终程缓冲和限位的预期职责。它不是 REST 后支承、平衡支点、Capstan 传动件，也不是把键杆往上推回 REST 的已验证回弹机构。

预期接触是 CP2K1_KEY_043_STICK 底面与止挡斜顶面，传力路径为键杆→毛毡垫→R8_FRONT_RAIL→保留 keybed。REST 时顶面与键杆分离；按下时从靠支点的后缘开始接近并接触。当前失败是后缘区域实际实体相交。

## 模型与原始意图

R8/declare_design.py 第65–66行把顶面直接定义为完整转角下键杆底面再向上加2 mm；function=FINITE_FRONT_COMPLIANT_DOWNSTOP，material=REPRESENTATIVE_FELT，unloaded_reserve_mm=2。P01.stop_limit 明确声明仅解析容积余量，完整原生键程、恢复力及 felt law 未合格。

这是明确的 Representative Design 意图，不是已验证的2 mm材料压缩能力。R9派生保留KEY043止挡；保存的R11 REST与教育失败现场中，其顶点、拓扑和矩阵逐项一致。安装没有在这次按键中漂移。

失败身份记录显示该止挡无父级、无约束、无modifier；保存的实际几何保持不变。材料名称并没有提供形变、力—位移、迟滞、压实上限或回弹模型。现有碰撞检查实际把它作为未变形的有限实体处理。

## 科学来源与适用边界

1. [Kawai Vertical Piano Regulation Manual](https://portal.kawaius.com/api/media/file/Kawai_Upright_Piano_Regulation_Manual_EN.pdf)，项目已有原件 v1_2c1a_candidate/references/S06_regulation.pdf；直接检查已有渲染 v1_2e_cp1r20/evidence/authority/kawai_p010.png，印刷页10：通过纸垫片调整白键下沉，并强调一致按压力。支持“止挡堆叠高度和受力条件决定有效键程”。本轮在线PDF截图获取失败，证据采用本地已有页图。其10.3 mm白键数值不适用于KEY043黑键，不引入项目参数。
2. [Baldwin US4127051A](https://patents.google.com/patent/US4127051A/en)，背景说明：前轨是按键下止挡，键底与轨间的毛毡垫用于缓冲消声，纸垫调整键程。仅使用传统键框原理；专利主体是三角琴改进结构，不把其结构尺寸或新结构移植成立式琴权威。
3. [Howard Piano Industries：Front Rail Felt Punchings](https://www.howardpianoindustries.com/piano-front-rail-felt-punchings/)，供应商第一手材料资料：firm felt、纸/卡垫调键程，多种厚度，并提示旧毛毡压实。仅支持材料与维修形式；不提供本垫的载荷—压缩曲线或可逆2 mm能力，产品厚度不作为本项目尺寸标准。
4. [Masoudi 立式琴机械研究论文](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/8b1f5033-3619-46b4-8083-833cbd07e4f5/content)，项目已有 extracted/B01_masoudi_thesis/p118.txt（印刷94页）Table4.2：front rail punching为key-ground接触2，rest rail与balance rail为不同接触；同页说明毛毡压缩非线性及迟滞。p126.txt（印刷102页）说明调节前垫可改变key dip。只用于接触拓扑和建模要求；不能把论文锤毡试验或其原型尺寸直接用于本前垫。

矩形8×8 mm、斜顶、2 mm余量、当前坐标均是工程假设。真实前轨常见的是带孔毛毡垫配合导向销和纸垫，不意味着本代表性方垫必须复制OEM形状；也不能据名称授予任意网格重叠豁免。
