# PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBILITY_R1

**VERDICT = PASS_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBLE**。临时position-only donor restoration可行：上方小框hard shelf明显减弱、自然指根crease保留；下方正常区域几何精确不变。本轮是feasibility，不是Human最终接受、正式design或APPLY。

## Human target lock

HUMAN_TARGET_LOCKED=YES。根据本次Human明示的“上方小橙框defect / 下方大橙框正常”，确定性绑定此前已交付的CANDIDATE_PIXEL_SELECTION图：上框[520,260,720,350]、下框[330,380,720,640]，case/view=IDX_MCP_30__LOCAL_ALTERNATE，1600×1100。复用已保存pixel ray hit，不以文字猜ID。

上框原始visible hits涉及33 vertices/16faces；下框69 vertices/49faces。3个native faces与10个顶点跨界，全部作为normal/boundary参考并position锁定。独立defect core为23 vertices/13faces；core/normal membership无交集。没有为了image rectangle切faces、重建ownership或改topology。下框不是defect，未整体平滑或重塑。

## Donor与真实ancestry

DONOR_SOURCE=OFFICIAL_HAND_REALISTIC_MULTIRES_L1；Stage2 evaluated L1在local/world coordinates和native faces精确等价。没有用coarse base作target，没有nearest projection。

当前顶点→Stage4A_R2_BASE ID由唯一exact local coordinate identity恢复；source parentage使用已有historical split-edge ancestry和Multires subdivision graph。三个实际core write顶点：

- 3353：source L1 parents125/2078，weights约0.500001691/0.499998309。
- 3354：source L1 parents126/2079，weights约0.500001767/0.499998233。
- 3359：source L1 parents1025/3174，weights约0.500001712/0.499998288。

每个target由parent weights确定性导出，再通过已有frozen RSSF per-vertex linear J传递。公式：`target = old_Stage4C + J * (donor_ancestry_rest - Stage4A_engineered_rest)`。当前anchor已包含此前dorsal54 donor restoration，因此new delta扣除该已有transfer，避免double restoration。顶点3306/3314仅有float32 roundtrip量级差异，不重新移动。0.0001mm仅用于排除该既有保存数值噪声，不是人体阈值或structure exemption。

## Scope

Human defect membership23；实际core写入3；shared ancestry closure13；transition context0；TOTAL_TRANSFER_PROBE_WRITE_COUNT=16。完整write set为3348–3363，正好对应已有`CON1_MIDDLE_MCP@-1mm`16顶点construction event。Scope来自nonzero source deviation的native adjacency component及shared L1 parentage closure，不是固定1/2ring或whole-palm expansion。

正常区69顶点全部锁定，必需closure与normal交集0。未经许可的normal context移动0。闭包之外positions精确不变。16 vertices的max move约4.762357mm。

## Source / current / earliest stage

SOURCE_NATURAL_CREASE_PRESENT=YES；CURRENT_HARD_FACETING_PRESENT=YES；ENGINEERING_AMPLIFICATION_CONFIRMED=YES。最早确认hard shelf为Stage4A_R2_BASE / saved CON1_MIDDLE_MCP@-1mm snapshot。既有saved event直接记录3348–3363的来源，因此无需新的producer-operation replay。

Source本身有自然root crease，目标不是smooth flat surface。Matched静态图中probe去掉current的异常局部shelf，保留attachment、掌面体积与source-like transition。write-incident native dihedral平均值约57.29°→16.68°、最大178.18°→49.60°；source native对应patch均值约15.70°、最大39.82°。这些是不同topology的描述量，不是产品或人体阈值。原生截面显示current折返/shelf消失，probe向donor progression恢复。

## 静态structure gate

临时probe从current R2同几何资产建立，仅修改16个vertex positions，保存新文件并clean-reopen；完整protected native payload逐字段精确相同，21 bones与weights保留。V/E/F=3416/6828/3414；native cycles、manifold、UV、materials、smooth/sharp/custom normals、weights、bone/joint data均不变。

复用此前reconciled true3D contact registry / finite shared-simplex semantics。全部changed incident native fans对whole mesh，未受影响pair坐标恒等。new nonadjacent exact intersection=0；new off-shared crossing=0；new illegal coplanar overlap=0；new self-intersection=0；new structural bow-tie=0；new degenerate=0；new face reversal=0；new contact component=0；existing contact worsening=0；feature expansion=0；new boundary transition folds=0。10个旧local contact components消失，不是将它们重新归为legal。没有absolute projected bowtie zero要求。

连续linear transfer path最小fan triangle area0.02931984mm²，无zero-area event；这不是完整连续collision qualification。endpoint static PASS，不替代任何Stage6 deformation qualification。

## 正常区保护与current9独立

正常区69vertices/49faces所有坐标精确不变，max displacement0。同camera/scale/light/static pose的SOLID、FLAT、GRAZING lower normal crop最大RGB差异1/255、mean约0.0013/255；无新contour/ridge/dent/bulge/flattening观测。NORMAL_CONTEXT_VISIBLE_CHANGE=NEGLIGIBLE_PENDING_HUMAN；专门before/after供Human核对。

CURRENT9_WRITESET_DIRECT_OVERLAP_COUNT=0；1/2ring overlap=0；CURRENT9_CAUSAL_INDEPENDENCE=CONFIRMED_FOR_THIS_PROBE（static write incidence scope）。Current9仍HOLD_NOT_CLOSED；未改答案、未创建approval receipt/closure或写active Human authority。

原先Downloads的response源文件在本轮开始时已不存在，本轮不能再次检查其外部字节；上一轮hold receipt及所有工作区Human资料完整冻结，未重建response。

## Review与边界

`review.html`第一屏提供CURRENT / OFFICIAL_L1 / TRANSFER_PROBE / DIFFERENCE四列，匹配确认图camera/scale/light，全部静态RAW/RSSF frame。原Human确认图保存的IDX30 pose只作locator参考，不宣称本轮重跑。Donor列保留official native3300vertices/3298faces，以existing frozen RSSF coordinate map作display-only静态对齐；未将donor topology替换进current。

close solid、alternate、grazing、flat、wire、三条native mesh cross-section、source/lineage与normal-area before/after均已提供。Formal APPLY=NO；Stage5 propagation=0；skin/true-cap/targeted deformation qualification=0；Full42=0；Stage6=0；pose smoke=0；Stage6B=0；production promotion=NO。

TOPOLOGY_CHANGE_REQUIRED=NO；WEIGHT_CHANGE_REQUIRED=NO；RIG_CHANGE_REQUIRED=NO；RET0PO_REQUIRED=NO（此静态feasibility范围，不代表未来deformation已通过）。Production assets没有写入。NEXT=PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_DESIGN_R1，仅记录，未执行。

**STOP — HUMAN REVIEW**。临时文件`TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend`明确DESIGN_ONLY / NOT_PRODUCTION / NOT_APPROVED。
