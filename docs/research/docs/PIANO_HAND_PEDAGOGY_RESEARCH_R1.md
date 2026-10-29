# 钢琴基础手型教学研究 · R1

> `docs/PIANO_HAND_PEDAGOGY_RESEARCH_R1.md`
> 项目：钢琴教学双手 3D 交互资产 · 第一阶段（研究 + 规范，不生产资产）
> 版本：R1 　日期：2026-09-27 　状态：**READY_FOR_HUMAN_REVIEW**
>
> **本文档只建立教学依据。本阶段不创建 mesh、不做 Rig、不做动画、不启动混元 3D 生成。**

---

## 0. 阅读约定

| 标记 | 含义 |
| --- | --- |
| `CONSENSUS` | 多个独立权威来源一致支持，可作为 3D 资产的硬性约束 |
| `HUMAN_REVIEW_REQUIRED` | 存在流派 / 情境差异，或证据不足，**必须由人工（钢琴教学专业人士）裁定后才可进入下游** |
| `REFERENCE_GAP` | 资料缺口，未获取或不可自由使用 |
| `CONSTRAINT→3D` | 由教学结论直接推导出的 3D 资产约束 |

来源权威分级见 §6，完整清单见 `reference_manifest/REFERENCE_MANIFEST_R1.json`。

---

## 1. 研究范围与方法

**范围**：钢琴基础教学中的**规范手型**、**手指编号**、**常见错误手型**。不涉及进阶技巧（八度、震音、踏板、指法编排策略）。

**方法**：
1. 按用户给定优先级检索：音乐院校 → 权威教材/协会 → 专业教师/机构 → 厂商教育资料 → 其他（仅辅助）。
2. 对每一项结论标注支持来源与权威等级。
3. **凡出现来源间冲突，不强行统一**，标记为 `HUMAN_REVIEW_REQUIRED` 并列出各方主张。

**已获取的最高级别证据**（两条，构成全文主要科学依据）：
- **Baylor University Open Books《Baylor Piano Basics》** — Michael Clark，大学开放教材（CC BY-NC-SA 4.0），第 1 章 "Fundamentals of Piano Technique"。权威等级 **L1**。
- **同行评审文献综述**：*An analysis of musculoskeletal disorder risk factors associated with common pedagogical principles of the Lhevinne and Taubman piano schools: A literature review*，SAGE Journals，2023。权威等级 **L1**。该文系统对比了两个钢琴学派在**指骨弯曲度**、**腕关节背伸**、**技术练习观**上的对立主张，是本文判断"哪些内容存在流派差异"的核心依据。

**重要声明**：本次检索**未能直接访问中央音乐学院、上海音乐学院、Royal Conservatory、ABRSM、Juilliard 等院校官方站点的一手教材**。检索到的中文内容均来自转载站或聚合站（权威等级 L5），仅用于交叉验证中文教学口径，**不足以作为最终教学依据**。见 §6.3 与 `REFERENCE_GAP-03`。

---

## 2. A. 基础手指编号

### 2.1 结论

```
                    右手（掌心朝下，手指朝前）

       5    4    3    2    1
      小指 无名 中指 食指 拇指
       │    │    │    │    │
                                   ← 拇指在内侧（靠近身体中线与中央 C）

                    左手（掌心朝下，手指朝前）

       1    2    3    4    5
      拇指 食指 中指 无名 小指
       │    │    │    │    │
                                   ← 拇指在内侧（靠近身体中线与中央 C）
```

| 编号 | 手指 | 英文名 |
| --- | --- | --- |
| **1** | 拇指 | Thumb |
| **2** | 食指 | Index finger |
| **3** | 中指 | Middle finger |
| **4** | 无名指 | Ring finger |
| **5** | 小指 | Little finger / Pinky |

**左右手是否采用完全相同的编号规则：是，完全相同。**

Baylor（L1）原文："Thumbs are 1, index fingers are 2, middle fingers are 3, ring fingers are 4, and little fingers are 5."
piano.org（L2）原文："This system is identical on the right hand and the left hand — there is no separate numbering for each hand."
WPTA（L2）、CMUSE（L5）、PianoRanked（L5）一致。
中文教学材料（L5）同样为"大拇指叫一指……小拇指叫五指"，且明确"无论左手还是右手，以下规定都适用"。

> 判定：`CONSENSUS`。**这是本阶段确定性最高的结论，可直接固化进 Finger ID 系统。**

### 2.2 历史注记（不影响本项目，仅供术语对齐）

19 世纪英国曾使用 "English fingering"：拇指记为 `+`，其余四指记为 1–4；欧洲大陆使用 1–5 的 "Continental fingering"。20 世纪起英国亦改用 1–5，现代教材、乐谱、教学法**统一采用 1–5**。
→ 数字教材中**只使用 1–5 制**，不使用 `+` 记号。

### 2.3 `CONSTRAINT→3D`

- **C-ID-01**：左右手共享同一套 Finger ID 语义：1=Thumb、2=Index、3=Middle、4=Ring、5=Little。
- **C-ID-02**：Finger ID 是**语义 ID，不是几何索引**。镜像生成左手后，几何上最靠近拇指侧的骨骼仍必须映射为 Finger ID 1。禁止用"顶点序号 / 骨骼数组下标"隐式表达指号。
- **C-ID-03**：UI 指号标注与骨骼命名必须一一对应且可双向查询（见 `PIANO_HAND_MASTER_ASSET_SPEC_R1.md` §5）。
- **C-ID-04**：拇指在双手自然置于键盘时**彼此相对、朝向中央 C**。这是左右手摆放的语义基准，也是镜像后校验左右手是否正确的**首要人工检查项**。

---

## 3. B. 标准初学者钢琴手型

### 3.1 判定总表

| # | 项目 | 判定 | 依据 |
| --- | --- | --- | --- |
| B-01 | 手指自然弯曲、手呈拱形 | `CONSENSUS` | Baylor(L1)、WPTA(L2)、Music Academy(L3)、Better World(L3)、中文材料(L5) |
| B-02 | 掌指关节（MCP / 第三关节）构成拱顶并凸起，不得塌陷 | `CONSENSUS` | WPTA(L2)、Baylor(L1)、中文材料(L5) |
| B-03 | 指尖（非指肚 / 指腹平面）触键 | `CONSENSUS`（粗粒度） | Baylor(L1)、中文材料(L5) |
| B-04 | 触键的**精确部位**（指尖末端 vs 远节指骨中段 vs 指腹） | `HUMAN_REVIEW_REQUIRED` | SAGE 综述(L1)：Lhevinne vs Taubman 直接对立 |
| B-05 | 拇指以**侧面 / 指甲侧边缘**触键，与四指结构不同 | `CONSENSUS` | Baylor(L1)、WPTA(L2)、Music Academy(L3)、中文材料(L5) |
| B-06 | 手指第一关节（DIP，靠指甲那节）不得塌陷 / 反折 | `CONSENSUS` | Baylor(L1)、WPTA(L2)、Better World(L3)、中文"折指"(L5) |
| B-07 | 手指自然分开，一指对应一键 | `CONSENSUS` | WPTA(L2)、中文材料(L5) |
| B-08 | 手腕处于**中立位**（不前屈、不过伸、不尺偏/桡偏），且与前臂大致成一直线 | `CONSENSUS`（中立位是共识） | Baylor(L1)、Music Academy(L3)、Noble Academy(L3) |
| B-09 | 手腕的**具体高度**（略高于掌指关节 / 与掌指关节齐平 / 松垂） | `HUMAN_REVIEW_REQUIRED` | SAGE 综述(L1)：Lhevinne vs Taubman 对立；各 L3 来源表述亦不一致 |
| B-10 | 手腕必须保持**柔顺可动**，不得锁死 | `CONSENSUS` | Music Academy(L3)、Better World(L3)、Noble Academy(L3)、SAGE(L1) 引 Sandor |
| B-11 | 手指是否应**主动抬高**（高抬指训练） | `HUMAN_REVIEW_REQUIRED` | Taubman 明确反对(L1/L2)；传统/俄派主张（间接证据，一手来源不足） |
| B-12 | 前臂—手腕—手掌作为**一个联动单元**协同 | `CONSENSUS` | Baylor(L1)、WPTA(L2)、SAGE(L1) |
| B-13 | 拇指与食指间形成开口（"C" 形 / 虎口张开），不得夹紧 | `CONSENSUS` | WPTA(L2)、中文"虎口夹紧"列为错误(L5) |
| B-14 | 手背（掌背）不得向小指侧倾斜 | `CONSENSUS`（中文教学口径） | 中央音乐学院教学材料转载(L5)，**权威待提升** |

### 3.2 共识部分详解（`CONSENSUS`）

#### B-01 手指自然弯曲 / 手呈拱形
- Baylor（L1）给出**可操作的获取方法**："let your hand hang loosely by your side. Notice its natural shape: the fingers are gently curved and the knuckles that join the fingers to the palm mark the peak of a gentle arc. Bring this natural hand shape up to the keys."
  → **这对 3D 资产极有价值：它定义了一个不依赖主观判断的"自然放松手型"基准。**
- WPTA（L2）："The hand position on the keyboard should resemble the hand in a relaxed position"。
- 常用比喻："手握小球 / 苹果 / 鸡蛋"、"空握球状"、"手中握一枚鸡蛋"。

> `CONSTRAINT→3D` **C-SH-01**：3D 手资产必须存在一个可复现的 **RELAXED** 姿态，其定义取自"手臂自然下垂时手的自然形状"，而非任意美术设定。

#### B-02 掌指关节拱顶
- WPTA（L2）用词最强："The large knuckles of the hand form a very powerful arch — they are the 'powerhouse' of the hand and of piano technique."；"These four knuckles are the bridge which forms an arch on the top of the hand."
- Baylor（L1）图示对比 "Collapsing Knuckles" 与正确形态，并给出训练法（拇指与其余指做 O 形、指卧撑）。
- 中文材料（L5）："掌关节（通常叫第三关节）及所有手指关节都应凸起，应避免和纠正最易出现的手指第 1 关节和第三关节（指掌关节）塌陷呈凹状"。

> `CONSTRAINT→3D` **C-SH-02**：掌指关节（MCP）区域的几何**必须在标准手型姿态下保持凸起轮廓**，且在俯视 / 斜前视角下可被学生清晰识别。这是本组件最重要的教学可视特征之一，Retopo 与 Skin Weight 不得破坏该区域在屈曲时的体积感。

#### B-05 拇指结构区别
- Baylor（L1）："The thumb is the shortest finger."；并指出弹拇指时整只手需向琴内移动以避免扭转。
- Music Academy（L3）："Thumb lies on its side, playing with the corner of the nail area."
- 中文材料（L5）："拇指是指尖的外侧触键"；"两手的拇指指甲应该是面对面"。
- WPTA（L2）：拇指"hanging at the side of the hand"；"The correct position of the arch forms a 'C' between thumb and forefinger."

> `CONSTRAINT→3D` **C-SH-03**：拇指几何必须具备**与其余四指明显不同的朝向与旋前角度**（拇指指甲面与四指指甲面不共面）。这是防止 AI 生成"猿手"（拇指方向与四指趋同）的关键验收点。
> `CONSTRAINT→3D` **C-SH-04**：拇指长度最短，且**只有两节指骨**（近节 + 远节），四指各有三节。几何与 Rig 都必须遵守（见资产规范 §4）。

#### B-06 第一关节（DIP）不得塌陷
- Baylor（L1）明确指出这是初学者的高发问题，尤其**无名指与食指**："their first knuckle (the one directly above the fingernail) bends backward as they play the key"。
- 中文"折指"（L5）列为第 1 号常见错误。

> `CONSTRAINT→3D` **C-SH-05**：DIP 关节必须支持**独立弯曲**，且在标准手型下**不得出现反折（hyperextension）几何**。Rig 的关节角度限制须禁止 DIP 负向过伸。

#### B-08 / B-10 手腕：中立位 + 柔顺可动
- Music Academy（L3）："Wrist level with hand and arm—neither dropped nor raised；Flexible, not locked；Aligned with the forearm."
- Baylor（L1）：手腕与前臂、手构成"drawbridge"（吊桥）单元，以肘为支点。
- Better World（L3）："The wrist acts as a shock absorber… It should remain flexible and level with the forearm, floating with the phrase rather than staying locked in a rigid horizontal position."
- WPTA（L2）引 Sándor：固定不动的手/腕位置长期会导致"tension, fatigue, pain, and acute or chronic ailments"。

> **关键表述**：共识是"**中立、柔顺、与乐句协同的动态中立位**"，**不是"绝对刚性的水平"**。教学组件若要表达"手腕水平"，应表达为**中立位 + 允许微调**，而非锁死。

#### B-12 前臂—手腕—手掌联动
- Baylor（L1）："the hand, wrist, and forearm can work together as one unit"；并强调**每根手指弹奏时，该单元要做轻微的水平与垂直调整**（对齐），使手指与其屈肌/伸肌成一直线。
- WPTA（L2）同义表述，并强调"**弹哪个指，就调整到哪个指的最佳位置**"。

> `CONSTRAINT→3D` **C-SH-06**：单指触键动画（FINGER_n_PRESS）不应只有手指动，手腕/掌部应有**轻微的伴随位移与对齐调整**。这一点直接决定动画的可信度。

### 3.3 争议与流派差异（`HUMAN_REVIEW_REQUIRED`）

以下四项**不得由 WorkBuddy 自行裁定**。核心依据为 SAGE 同行评审综述（L1）。

#### ⚠ HUMAN_REVIEW_REQUIRED · HR-01：手指弯曲程度与触键部位

| | **Lhevinne 学派（俄派重量演奏）** | **Taubman 学派** |
| --- | --- | --- |
| 指骨弓 | 保守性指骨弓（conservative phalangeal arch）；部分实践者以腕背伸补偿，保留一定指间屈曲 | 充分指骨弓（extensive phalangeal arch）：**所有指间关节与掌指关节均屈曲** |
| 触键部位 | 远节指骨**中段**（mid-shaft of the distal phalanx），让手指最柔软的部位接触琴键 | 远节指骨**末端**（distal aspect of the DP）；腕骨与远节指骨**垂直** |
| 原理 | 重量演奏，减少受伤、产生饱满音色 | 关节尽量在其活动范围中段工作，最小化关节负荷与疲劳 |

**影响**：这直接决定 3D 模型中**指尖触键点的位置**（指尖末端 vs 指尖稍内侧的指腹）以及**标准手型的弯曲角度数值**。两者差异在 3~6 mm 量级，在放大的教学 3D 视图中**肉眼可辨**。

**需人工裁定**：本数字教材采用哪一种（或是否采用"介于两者之间的教学折中"）？并给出各关节的目标角度数值。

#### ⚠ HUMAN_REVIEW_REQUIRED · HR-02：手腕高度

| | **Lhevinne** | **Taubman** |
| --- | --- | --- |
| 手腕 | 由指骨支撑前臂，**手腕松垂于键盘之上**（腕背伸 dorsiflexion）；腕与前臂构成"suspension bridge"（悬索桥），以肩与键盘为两端支撑 | 腕部**主动稳定**，与尺骨成一直线（carpals linear with the ulnar），作为传递下压力的**杠杆支点**；腕关节主动稳定（open-chain） |
| 力学 | closed-chain | open-chain |

**各 L3 来源的表述也不一致**：
- Music Academy："Wrist level with hand and arm"
- Musoca（L5）："wrist should be level with or slightly higher than your knuckles"
- Better World（L3）：forearms "parallel to the floor or slope very slightly downward"
- Noble Academy（L3）："keep your wrist slightly elevated above the keys"

**需人工裁定**：标准手型演示中手腕的**具体高度**（相对掌指关节 / 相对键面），以及是否允许随情境变化。

#### ⚠ HUMAN_REVIEW_REQUIRED · HR-03：是否主动抬指

- Taubman 明确反对：Montclair State University（David Witten，键盘研究协调人，L2）："[Taubman] was against unnaturally curling fingers. She was against a rigid sitting position."；"fingers should gently curve"而非刻意卷曲。
- Taubman 亦**反对手指独立性练习**，认为增加张力与受伤风险（SAGE L1；BlitzBooks L3 记录）。
- 传统 / 俄派存在高抬指训练（本项目**未获取到足够的一手权威资料**直接支持，仅有间接与 L5 来源）。
- 中文材料（L5）提到"弹琴时，首先抬指，然后下击"。

**影响**：直接决定 `FINGER_n_PRESS` 动画的**抬指高度**与是否包含"抬指—下击"两段式。

**需人工裁定**：单指触键动画是否包含明显抬指阶段？抬多高？

#### ⚠ HUMAN_REVIEW_REQUIRED · HR-04：手腕是否"必须保持水平"

严格说这是 B-08/B-09/B-10 的交叉项。共识是"中立 + 柔顺"，但**"手腕应该保持水平"这句话本身在多家 L3/L5 来源中被表述为一条硬性规则**（如 Musoca、Noble Academy），而 SAGE(L1) 与 WPTA(L2) 强调动态调整。

**需人工裁定**：教学组件中"手腕水平"这一条的**表述措辞与可视化方式**——是作为静态姿态规则展示，还是作为"中立位 + 动态调整"展示。建议倾向后者（证据更强），但须由教学方拍板。

### 3.4 手腕 / 前臂 / 手掌关系（综合）

```
   肩
    │   上臂自然下垂（Taubman 主张上臂自然悬挂，避免抬肩）
    │
   肘 ──┐  肘部高度：与键面齐平或略高（Baylor L1）
        │
   前臂 ─┤  约与地面平行 / 略向键面倾斜（Baylor L1、Better World L3）
        │
   腕 ──┤  中立位：不塌陷、不过高、不尺偏/桡偏
        │  柔顺可动，作为减震器与重量通道
        │  与手背形成一条柔和直线（WPTA L2："a straight line from the wrist to the knuckles"）
        │
   掌 ──┤  掌指关节（MCP）构成拱顶（"powerhouse"）
        │  掌心形成横弓与纵弓，不压平、不贴键
        │
   指 ──┘  从掌指关节**自然下垂**，形成柔和曲线
           指尖触键；拇指以侧面 / 指甲侧边缘触键
           手指自然分开，一指一键
```

WPTA（L2）还给出一条重要的**对齐原则**："The finger that plays should be in a straight line with its flexor and extensor muscles." → 弹不同手指时，手—腕—前臂单元会做**轻微水平位移**以对齐。Baylor（L1）图示了弹 1–5 指时手的位置如何逐个向琴内/琴外移动（弹拇指时手向琴内移，弹长指时手向琴外移）。

> `CONSTRAINT→3D` **C-SH-07**：`FINGER_n_PRESS` 动画中，弹奏拇指（1）与弹奏小指（5）时，掌部的水平位置应有可见差异。这是区分"专业可信动画"与"假动画"的关键细节。

---

## 4. C. 常见错误手型（只研究记录，本阶段不制作）

### 4.1 错误清单与 3D 对比示范适配度

| ID | 错误项 | 中/英 | 表现 | 机制 / 后果 | 来源 | 3D 对比适配度 |
| --- | --- | --- | --- | --- | --- | --- |
| E-01 | **手指过直 / 平指** | Flat fingers / 手指伸得过直 | 手指接近伸直，以指腹平面压键 | 限制速度与力度控制，增加张力 | Music Academy(L3)、Musoca(L5)、Baylor(L1) 隐含 | ★★★★☆ **高**。静态可辨，与标准手型差异明显 |
| E-02 | **过度蜷曲 / 爪形** | Over-curled / claw | 手指蜷曲过度，指尖几乎指向掌心 | 张力、音色紧、无法放松 | 由 B-01"不能过于弯曲"(L5) 反推 + Taubman 反对 unnatural curling(L2) | ★★★★☆ **高**。但需人工界定"过度"的阈值 |
| E-03 | **掌指关节塌陷** | Collapsed MCP / Sunken knuckle bridge / 掌关节塌陷 | 手背拱顶塌平，第三关节凹入 | 手指只能"拍"键而非"奏"键；力量无法传递 | WPTA(L2)、Baylor(L1)、中文(L5) | ★★★★★ **最高**。这是最具教学价值的对比项，几乎是所有权威来源共同强调的头号问题 |
| E-04 | **第一关节塌陷 / 折指** | Collapsed DIP / 折指 | 靠近指甲的关节反折，指肚触键 | 力量无法流畅传输到琴键，严重影响音色 | Baylor(L1)、WPTA(L2)、中文(L5 列为第 1 号错误) | ★★★★★ **最高**。但**尺度小**，需支持缩放观察或局部特写 |
| E-05 | **手腕过高** | Wrist too high | 手腕明显高于手背平面 | 影响手腕运动与掌关节发力，动作别扭，手臂手腕疲劳 | 中文(L5)、Musoca/Better World 反推 | ★★★★☆ **高**。整体姿态差异，远距离即可辨识 |
| E-06 | **手腕过低 / 塌腕** | Dropped / low wrist | 手腕低于键面，甚至靠在键盘边缘 | 手指无法自然发力，音色生硬，增加腕部负担，可能引发尺神经痛 | 中文(L5)、Better World(L3)、Musoca(L5) | ★★★★☆ **高**。与 E-05 配对展示效果最好 |
| E-07 | **手腕僵硬** | Locked / rigid wrist | 手腕锁死，不随乐句调整 | 长期导致张力、疲劳、疼痛 | Music Academy(L3)、Better World(L3)、WPTA(L2) 引 Sándor | ★★☆☆☆ **低（静态）**。**本质是动态特征**，静态模型几乎无法表达。建议**仅在动画中**表现（如 AUTO_DEMO 中标准 vs 僵硬的对比），或配合标注文字 |
| E-08 | **手掌贴键 / 掌心塌陷** | Palm on keys / 手掌塌陷 | 掌心压在琴键/键面上，掌弓消失 | 掌指关节无法凸起，手指失去支撑 | 中文(L5)、由 B-02 + B-01 反推 | ★★★★☆ **高**。掌心视角下辨识度最好 → **这是"掌心视角"必须存在的重要理由之一** |
| E-09 | **拇指平躺 / 拇指锁死** | Thumb lying flat / Locked hitchhiker thumb | 拇指平摊在键上，或用关节而非侧缘触键 | 手指站不住，触键过用力，手腕抬高，影响稳定性与速度 | 中文(L5)、Better World(L3)、Musoca(L5) | ★★★★★ **最高**。拇指是结构差异最大的手指，错误形态极易辨识 |
| E-10 | **小指翘起** | Flying pinky | 弹其他指时小指向上翘起 | 前臂伸肌张力，手指独立性不足 | Music Academy(L3)、Better World(L3) | ★★★★☆ **高**。但**只在"某指弹奏"的上下文中才有意义** → 需与单指触键动画配合 |
| E-11 | **虎口夹紧** | 虎口夹紧 | 拇指与食指间开口闭合 | 虎口变形，影响灵活度与舒适度 | 中文(L5) | ★★★☆☆ **中**。尺度较小，需近距离观察 |
| E-12 | **颠手腕 / 抖腕** | Wrist bobbing | 手腕上下抖动代偿发力 | 发力方式错误，手指力量不足 | 中文(L5) | ★☆☆☆☆ **极低（静态）**。纯动态特征，只能做动画 |
| E-13 | **拇指悬于键外** | Thumb off keys | 拇指掉到琴键外，无法支撑 | 影响稳定性与音色 | 中文(L5) | ★★★☆☆ **中**。需键盘参照物才能判断 |

### 4.2 3D 对比示范推荐优先级（建议，需人工确认）

**第一梯队（强烈建议首批制作）** — 静态即可清晰表达、教学价值最高：
1. **E-03 掌指关节塌陷**
2. **E-04 第一关节塌陷（折指）**
3. **E-09 拇指平躺**
4. **E-01 手指过直**
5. **E-05 手腕过高 / E-06 手腕过低**（配对）

**第二梯队** — 有效但需要缩放、特写或特定视角：
6. **E-08 手掌贴键**（需掌心视角）
7. **E-02 过度蜷曲**（需人工界定阈值）
8. **E-11 虎口夹紧**
9. **E-10 小指翘起**（需配合单指触键上下文）

**第三梯队** — 静态不宜表达，仅在动画中考虑：
10. **E-07 手腕僵硬**
11. **E-12 颠手腕**

> ⚠ **HUMAN_REVIEW_REQUIRED · HR-05**：以上优先级由 WorkBuddy 依据"静态可辨识度 + 权威来源强调程度"推导，**需钢琴教学方确认**。特别是 **E-02「过度蜷曲」的阈值**——"过度"与"正确的自然弯曲"之间需要教学方给出明确分界，否则 3D 对比可能误导学生。

### 4.3 `CONSTRAINT→3D`

- **C-ERR-01**：错误手型对比**不得**与标准手型使用不同的 mesh。所有错误姿态必须是**同一 Rig 驱动出的不同 Pose**，以保证对比的公平性与可解释性。
- **C-ERR-02**：E-04（DIP 塌陷）与 E-03（MCP 塌陷）要求 **DIP 与 MCP 关节能够分别独立反折 / 塌陷**，且塌陷时几何不得穿模。这是 Rig 与 Skin Weight 的硬性验收项。
- **C-ERR-03**：E-08（手掌贴键）与 E-05/E-06（腕高低）要求模型**包含手腕与前臂段**，否则无法表达腕部相对键面的高度。见 `CANONICAL_HAND_POSE_SPEC_R1.md` §5 的 `HR-06`。
- **C-ERR-04**：错误对比项的**命名与元数据**应在资产阶段预留（如 `ERR_COLLAPSED_MCP`），但**本阶段不制作**。

---

## 5. 教学结论 → 3D 资产约束汇总

| 约束 ID | 内容 | 来源 |
| --- | --- | --- |
| C-ID-01 | 左右手 Finger ID 语义一致（1 拇指 … 5 小指） | §2.1 |
| C-ID-02 | Finger ID 为语义 ID，不得用几何索引隐式表达 | §2.3 |
| C-ID-03 | UI 指号 ↔ 骨骼命名双向可查 | §2.3 |
| C-ID-04 | 双手自然置于键盘时两拇指相对、朝向中央 C（镜像校验首要项） | §2.3 |
| C-SH-01 | 必须存在可复现的 RELAXED 姿态，定义取自"自然下垂手形" | §3.2 |
| C-SH-02 | 掌指关节在标准手型下必须保持凸起轮廓，且俯视/斜前可辨识 | §3.2 |
| C-SH-03 | 拇指朝向与旋前角度必须与四指明显不同（防"猿手"） | §3.2 |
| C-SH-04 | 拇指两节指骨；四指三节指骨 | §3.2 |
| C-SH-05 | DIP 须独立可控，且禁止负向过伸 | §3.2 |
| C-SH-06 | 单指触键动画须含手腕/掌部轻微伴随调整 | §3.2 |
| C-SH-07 | 弹 1 指 vs 弹 5 指时掌部水平位置应有可见差异 | §3.4 |
| C-ERR-01 | 错误姿态与标准姿态共用同一 mesh 与 Rig | §4.3 |
| C-ERR-02 | DIP 与 MCP 须能独立塌陷且不穿模 | §4.3 |
| C-ERR-03 | 模型须含手腕与前臂段，以表达腕部高度 | §4.3 |
| C-ERR-04 | 错误对比项命名预留，本阶段不制作 | §4.3 |

---

## 6. 权威度分级与来源

### 6.1 分级定义

| 等级 | 定义 |
| --- | --- |
| **L1** | 音乐院校 / 大学正式教材、同行评审学术文献 |
| **L2** | 权威教学机构 / 专业协会期刊、正规教材类资料 |
| **L3** | 专业钢琴教师 / 专业教育机构 |
| **L4** | 钢琴厂商 / 厂商教育资料 |
| **L5** | 其他（SEO 站点、自媒体聚合、转载站）— **仅作辅助与交叉验证，不作主要科学依据** |
| **L1‑T / L2‑T** | 技术类来源（3D / 图形学 / API 文档），用于 3D 资产规范，不用于钢琴教学判断 |

### 6.2 主要来源（钢琴教学）

| 来源 | 机构 / 作者 | 等级 | 用途 |
| --- | --- | --- | --- |
| Baylor Piano Basics, Ch.1 Fundamentals of Piano Technique（Open Books） | Baylor University · Michael Clark | **L1** | 手指编号、自然手型、掌指关节塌陷、前臂—腕—手单元、对齐原则 |
| *An analysis of musculoskeletal disorder risk factors… Lhevinne and Taubman piano schools*（SAGE, 2023） | 同行评审文献综述 | **L1** | 流派差异的核心证据：指骨弯曲度、腕背伸、抬指观 |
| *Looking Inside the Art of Piano Performance*（e-journal） | World Piano Teachers Association (WPTA) | **L2** | 掌指关节拱顶 "powerhouse"、"box"、拇指自然位、C 形开口、反对固定手腕 |
| Piano Finger Numbers | piano.org | **L2** | 手指编号（左右手一致） |
| The Different Schools of Piano Playing | Kawai Australia | **L4** | 学派谱系背景（辅助） |
| Taubman Festival 报道（David Witten, Montclair State University, Cali School of Music） | Montclair State University | **L2** | Taubman 反对刻意卷指与僵坐姿（教师观点，载体为地方媒体） |
| Piano Technique Fundamentals | The Music Academy | **L3** | 手腕中立、拇指侧触键、错误清单 |
| Piano Hand Position Lessons Online That Work | Better World Music School | **L3** | 生物力学链条、四种常见手型错误、前臂倾角 |
| Correcting Piano Hand Position Errors | Noble Academy | **L3** | 塌陷、手腕高度、张力 |
| 钢琴学习 9 种常见错误手型 | 网易号（自媒体） | **L5** | 中文教学口径交叉验证：折指、拇指平躺、腕过高/过低、掌关节塌陷、虎口夹紧、翘指、颠腕、拇指在键外 |
| 基础钢琴练习法——手型（译介） | 广州爱乐（译介） | **L5** | 中文口径交叉验证，含"指尖与指腹之间"的精细触键描述 |
| 中央音乐学院 钢琴基础教学视频（转载） | 转载站 | **L5** | 中文口径交叉验证：半圆手型、指尖触键、拇指外侧触键、手背不得向小指侧倾斜 |

### 6.3 来源缺口（`REFERENCE_GAP`）

- **`REFERENCE_GAP-03`（教学）**：未能直接获取**中央音乐学院 / 上海音乐学院 / 中国音乐学院等国内音乐院校官方教材或官方教学资料**，也未能获取 Royal Conservatory of Music、ABRSM、Juilliard、Curtis、Eastman 等院校的一手教材。现有中文内容均为转载或聚合（L5），**不足以支撑面向数字教材的正式教学依据**。
  → **需人工提供**：国内院校官方钢琴基础教材（或指定教学大纲），用于复核 §3 各条结论，尤其是 B-14（手背不得向小指侧倾斜）等中文口径特有条目。

- **`REFERENCE_GAP-04`（教学）**：未能获取关于"**初学者手型的量化角度数值**"（各关节目标屈曲角度、腕部相对高度的具体毫米/角度值）的权威资料。现有来源均为定性描述（"natural curve"、"gently curved"、"level"）。
  → **需人工提供**或人工裁定数值，否则 3D 标准手型只能凭推测设定。

---

## 7. `HUMAN_REVIEW_REQUIRED` 汇总

| ID | 事项 | 阻塞的下游工作 | 严重度 |
| --- | --- | --- | --- |
| **HR-01** | 手指弯曲程度与触键部位（Lhevinne vs Taubman） | STANDARD_HAND 姿态、指尖触键点、各关节目标角度 | **阻塞** |
| **HR-02** | 手腕具体高度 | STANDARD_HAND 姿态、E-05/E-06 对比 | **阻塞** |
| **HR-03** | 是否主动抬指、抬多高 | FINGER_n_PRESS 动画 | **阻塞**（仅阻塞动画阶段，不阻塞几何/Rig） |
| **HR-04** | "手腕水平"的表述与可视化方式 | 教学文案、UI 标注 | 中 |
| **HR-05** | 错误手型对比优先级；E-02「过度蜷曲」阈值 | 错误对比资产制作 | 中（不阻塞第一阶段） |
| **`REFERENCE_GAP-03`** | 国内院校官方教材未获取 | 全部教学结论的最终背书 | **阻塞（背书层面）** |
| **`REFERENCE_GAP-04`** | 手型量化角度数值缺失 | STANDARD_HAND 的精确数值 | **阻塞** |

> **说明**：HR-01 / HR-02 / `REFERENCE_GAP-04` 主要阻塞**动画与标准手型姿态的精确数值**，**不阻塞** 母版几何生成、拓扑、Rig 骨架结构等与"具体教学角度数值"无关的工作。因此本阶段后续规范（母版姿态、资产规范、流水线）仍可进入人工审核——它们刻意避开了对这些数值的依赖。详见 `CANONICAL_HAND_POSE_SPEC_R1.md` §6。

---

## 8. 本阶段禁止事项（重申）

本阶段**未**进行且**不得**进行：创建最终 hand mesh、Blender 从零雕刻手、腾讯混元 3D 生成、Rig、Skin Weight、动画、Three.js、HTML UI、钢琴键盘开发、自动进入下一阶段。

---

**文档状态：READY_FOR_HUMAN_REVIEW**
