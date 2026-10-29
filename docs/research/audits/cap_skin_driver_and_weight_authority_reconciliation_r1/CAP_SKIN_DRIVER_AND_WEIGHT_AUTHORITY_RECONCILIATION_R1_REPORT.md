# CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1

本轮形成可供 Human 审批的 deterministic skin authority/rebuild plan。主要 authority 全部 RESOLVED，状态仍为 PENDING_HUMAN_APPROVAL。没有生成新权重向量，没有重建 skin、保存 blend、修改 geometry/rig、重跑 R3 或运行 Stage6。

## 正式输入与范围

R3 authority canonical SHA256 `361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0`、membership SHA256 `f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d`均精确匹配。冻结 graph 962/1881、THUMB/INDEX 498/464、boundary20、ambiguity21、CLASS_A6/6、FIRST_WEB7/14且hardpins0、old9 INDEX9且hardrole0、cap37与INDEX145 hard sources均保留。读取旧 field/validator 仅为绑定证据，未运行相关求解或 validator。

corrected rig SHA256 `5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe` 与实际保存文件一致；直接读取21 bones，与批准后的 saved/reloaded 全量 snapshot逐 slot比较 local head/tail/frame/parent/deform标记。THUMB_IP.head完全不变；IP tail/roll、TIP head/tail/roll保持 corrected authority。实际16 deform bones、5 nondeform TIP helpers。MAX_INF=4沿用正式 production rule。R1/R1A/R1B/C/D/E、R2A、corrected、RSSF均只读，未设置 pose 或调用 evaluated mesh。native geometry采用既有 hash绑定的Stage4A保存坐标；没有新 anatomy研究。RSSF与R1B保存坐标最大差3.81469727e-06 mm，为序列化浮点误差。

## cap37 driver

37/37点都投影在corrected IP段，clamped mu范围[0.6943277663100877, 1.0]，IP head之后纵向距离15.2725–21.9961 mm，radial distance 0–7.9127 mm，低于历史tube诊断尺度。terminal v284与corrected IP.tail吻合；thumb nail独立冻结支持未更改。历史cap37中21点带有foreign driver，不能自动继承。

提案：IP主导 + MCP residual。沿corrected CMC→MCP→IP→terminal累计arc s，q(t)=6t^5−15t^4+10t^3，t=clamp(0.5+(s−s_IP)/(2h),0,1)，h=5×MED=19.441025 mm，s_IP=74.642959 mm。IP share语义q、MCP residual语义1−q。参数来自已批准R1B centered quintic family，仅重绑定正确chain，不继承old cap selector。这里只保存公式，没有逐点计算/生成candidate vectors。只有公式饱和处可IP=1，不能因cap名字37点一起one-hot。TIP禁止驱动。

同一profile延续到相容thumb proximal support，不在cap边界开关。cap2-ring最大arc相邻跳跃4.445563 mm，解析profile jump上界0.214377。这说明profile可以连续，不能替代尚未存在的candidate-to-retained seam/static/deformation检查。既有cap1/2-ring跳跃完整作为baseline登记，投影segment tie seams也需检查。cap proposal validation = DEFORMATION_VALIDATION_REQUIRED。

## old cap9 correction

9/9为冻结native INDEX_SURFACE、fresh INDEX、hardrole0。逐点保存R1/R1A/R1B历史vectors、native/RSSF positions、INDEX MCP/PIP/DIP segment distances与longitudinal projection；每点2-ring都有干净native+fresh INDEX-exclusive/source-backed witness。witness保留实际WRIST/MCP/PIP/DIP组合和vector hashes；不能把全部点设INDEX_MCP=1。

未来candidate采用4组INDEX+WRIST simplex约束harmonic reconstruction；edge系数MED/length，geometry inverse-square bone-distance prior系数0.01，fixed valid local vectors为Dirichlet pins，按sorted IDs实现唯一convex问题。0.01为本轮明确提交Human审核的deterministic prior strength，不冒称历史批准参数。此优化未运行；所有cap9旧THUMB保护/override退休。需通过native INDEX continuity、outer seams、crater/spike以及targeted deformation检查。

## first-web wrapper

FIRST_WEB21 exact IDs保持不变。保留WRIST/THUMB_CMC/THUMB_MCP/INDEX_MCP四组shared semantics；THUMB_IP=0，TIP=0。旧cap/ownership依赖selector和wrapper exclusions退休。R3 7/14只作context，不能转换bone ratios。R1B四组静态support全部符合wrapper，但新周边candidate仍需三向continuity。2-ring共98点，仅工程检查范围，不扩展解剖membership。thumb/index context和既有WRIST carrier context共同约束全16维向量的同一个positive-edge convex patch；每点采用自己的allowed support，21web点采用shared四组。禁止只优化某一侧。

first-web允许bones的slots全部不变且IP禁止，因此IP距离变化本身不要求改21点的vectors；其中1点需要重建、其余20点定向复验。CMC cage geometry FROZEN/PASS；exact skin mask未在本轮新冻结，仅geometry locality/protection context，不从R3创建mask。

## corrected field影响与exact reuse

静态逐vertex比较old R2A与corrected deform-chain nearest segment、raw/clamped mu、arc、normalized longitudinal、distance/radius-normalized location。共同radius尺度沿用历史R1B诊断值。material阈值：distance或arc≥0.5MED，mu/normalized longitudinal≥0.05，radius-normalized≥0.1，或nearest segment改变；必须同时有active thumb distal field支持。全mesh numerical changes与active skin影响分开记录，不能因远处投影变化判全mesh失效。normalized longitudinal分母变化单独作为诊断，不是本规则使用的毫米arc，不能单独触发重建。active affected 163点。IP roll carriers即使距离变化小仍需定向复验，距离审计不证明旋转deformation合格。

每vertex唯一分类：SAFE_REUSE 2401；TARGETED_REVALIDATION 771；REBUILD_REQUIRED 244；UNRESOLVED 0，总计3416。safe每条vector有hash证明：未经过legacy R1A/B selector写入、没有corrected IP frame carrier、outside新cap/web/boundary/repair scopes、实际driver slots不变、support及normalization合格。包括21个fresh THUMB-label点及475个CMC/MCP历史carrier；没有THUMB label→全部rebuild规则。旧1931独立候选中1920个仍安全、11个因新continuity scope进入复验/重建。R1B仍是历史master，不宣告为新production truth。

R1C/D/E实际保存delta及其cap-derived repair scope作为复验原因保留，不导入失败candidate向量。safe vectors也必须在获批后的新corrected bind上完成zero-pose/regression确认；SAFE_REUSE是exact vector eligibility，不是新资产已通过deformation。

## envelope与edge5879

总envelope 1015点=244必须写candidate点+771可通过gates保留原vector的复验点。包含cap37/old9、fresh20-edge endpoints及2-ring 126点、FIRST_WEB21及2-ring、corrected active field、历史确有依赖repair范围、edge5879两端及18点2-ring。各component互相重叠，不能把component counts相加当total。2-ring用作continuity pins/regression boundary，不升级anatomy。outer seam失败只扩展必要local candidate范围，禁止全mesh兜底。

edge5879历史 PARTLY_CAP_DERIVED，R1E CMC_MCP_L3 ratio 11.041286717387363及weight partition mismatch保留为真实证据；本轮没有重算deformation。fresh v1551/v3125均INDEX（不同于历史THUMB上下文），v3125属于FIRST_WEB21故shared wrapper优先；v1551按corrected geometry/INDEX side guard决定正常chain drive。两端都在REBUILD_REQUIRED并带2-ring，动作TARGETED_REBUILD_REQUIRED。R1B近连续的旧pair仅作retention prior，不能复用R1E wrist-heavy错误partition。

## continuity与Human gate

sum=1±1e−5、nonnegative/finite、16deform groups、max4、TIP=0、first-web IP=0、old9无THUMB override、side guard不定义比例。新提案筛查gates：one-ring max per-group jump≤0.5，L1≤1；均明确是待Human审批的新static screening contract，不冒称历史生产规则。所有内部与跨envelope edges检查，不允许不相干one-hot driver swap；历史坏baseline不豁免绝对gate。profile平滑不替代projection seam和实际skin continuity。

每项authority状态RESOLVED指规则可执行；candidate static/deformation仍NOT_RUN，DEFORMATION_VALIDATION_REQUIRED可以进入获批后的候选重建，不再增加解剖逐点研究。Review七问仅审批driver/INDEX修正/shared wrapper/reuse-envelope/edge/ownership guard/下一候选重建。全部YES才批准TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1；不会自动执行、不批准Stage6/production promotion。

proposal bundle SHA256 `a0a3811f00984edce73db6ff4171d72aeaec07e27dbe17936266dec6d9da1340`。

NEXT = HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL。STOP = YES。

## 输出核验

3416点分类覆盖与互斥、safe vector hashes/实际driver slots、5类bounded skin neighbourhood、old9 INDEX witnesses、cap37 projection、proposal bundle及24个response logic guard cases通过。8个浏览器静态视图通过，QA全YES无法导出或成为Human审批，正式页面恢复空白。2035个preexisting workspace/external formal response files before==after。BLEND_FILES_WRITTEN=0；weights written=0；R3 reruns=0；Stage6 runs=0。
