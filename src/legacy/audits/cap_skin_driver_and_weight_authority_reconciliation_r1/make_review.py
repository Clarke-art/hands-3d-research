import json,hashlib,html
from pathlib import Path
from snapshot import OUT,ROOT,sha
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
files=['CAP_SKIN_DRIVER_AUTHORITY_R1.json','CAP37_SKIN_DRIVER_AUTHORITY_R1.json','OLD_CAP9_SKIN_CORRECTION_AUTHORITY_R1.json',
 'FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json','SKIN_WEIGHT_CONTINUITY_CONTRACT_R1.json','CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1.json',
 'R1B_SAFE_WEIGHT_REUSE_SET_R1.json','SKIN_REBUILD_ENVELOPE_R1.json','EDGE5879_REBUILD_SCOPE_R1.json','CMC_GEOMETRY_PROTECTION_CONTEXT_R1.json',
 'INPUT_AUTHORITY_VERIFICATION_R1.json','R1B_FROZEN_SIDE_GUARD_AUDIT_R1.json']
packet={'review_id':'SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW_R1','phase':'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1',
 'proposal_status':'PENDING_HUMAN_APPROVAL','scope':'DETERMINISTIC_SKIN_DRIVER_AND_WEIGHT_REBUILD_PLAN_ONLY',
 'R3_authority_hash':'361f4f25201f5810830dc1bfc4bd2cf19db908aef8945801a63bfd2829197ff0',
 'R3_membership_hash':'f57483723e90cc34e0551bf70fac00c7c8cb789dbad5d0e248018fdaddd3741d',
 'corrected_rig_sha256':'5d5f86bb59135715a77515468c2b76fe81e2a44e2e8c5d6c17fcc3d56d2147fe',
 'proposal_files':{n:sha(OUT/n) for n in files},'no_new_skin_vectors':True,
 'candidate_static_and_deformation_validation':'NOT_RUN; DEFORMATION_VALIDATION_REQUIRED',
 'after_approval':'TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1','Stage6_authorized':False,'automatic_apply':False}
bundle=hashlib.sha256(canon(packet)).hexdigest();dump('SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json',packet)
(OUT/'SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1_CANONICAL.json').write_bytes(canon(packet))
dump('SKIN_AUTHORITY_PROPOSAL_HASH_R1.json',{'algorithm':'SHA-256','canonicalization':'UTF-8 sorted keys compact separators arrays retained no newline; full proposal bundle including exact component file hashes','proposal_bundle_hash':bundle})
data=read('REVIEW_VISUAL_DATA_R1.json');evidence=read('SAVED_RIG_AND_SKIN_EVIDENCE_R1.json')['sources']
data['weights_R1B']=evidence['R1B']['weights'];data['weights_R1E']=evidence['R1E']['weights']
data['impact']=read('CORRECTED_RIG_SKIN_FIELD_IMPACT_AUDIT_R1.json')['per_vertex'];data['packet']=packet;data['bundle_hash']=bundle
summary=read('CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_STATUS.json')
cap=read('CAP37_SKIN_DRIVER_AUTHORITY_R1.json');reuse=read('R1B_SAFE_WEIGHT_REUSE_SET_R1.json');web=read('FIRST_WEB_SKIN_WEIGHT_WRAPPER_R2.json')
report=f'''# CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1

本轮形成可供 Human 审批的 deterministic skin authority/rebuild plan。主要 authority 全部 RESOLVED，状态仍为 PENDING_HUMAN_APPROVAL。没有生成新权重向量，没有重建 skin、保存 blend、修改 geometry/rig、重跑 R3 或运行 Stage6。

## 正式输入与范围

R3 authority canonical SHA256 `{packet['R3_authority_hash']}`、membership SHA256 `{packet['R3_membership_hash']}`均精确匹配。冻结 graph 962/1881、THUMB/INDEX 498/464、boundary20、ambiguity21、CLASS_A6/6、FIRST_WEB7/14且hardpins0、old9 INDEX9且hardrole0、cap37与INDEX145 hard sources均保留。读取旧 field/validator 仅为绑定证据，未运行相关求解或 validator。

corrected rig SHA256 `{packet['corrected_rig_sha256']}` 与实际保存文件一致；直接读取21 bones，与批准后的 saved/reloaded 全量 snapshot逐 slot比较 local head/tail/frame/parent/deform标记。THUMB_IP.head完全不变；IP tail/roll、TIP head/tail/roll保持 corrected authority。实际16 deform bones、5 nondeform TIP helpers。MAX_INF=4沿用正式 production rule。R1/R1A/R1B/C/D/E、R2A、corrected、RSSF均只读，未设置 pose 或调用 evaluated mesh。native geometry采用既有 hash绑定的Stage4A保存坐标；没有新 anatomy研究。RSSF与R1B保存坐标最大差{read('INPUT_AUTHORITY_VERIFICATION_R1.json')['RSSF_max_geometry_storage_delta_mm']:.9g} mm，为序列化浮点误差。

## cap37 driver

37/37点都投影在corrected IP段，clamped mu范围{cap['geometry_evidence']['IP_segment_mu_range']}，IP head之后纵向距离15.2725–21.9961 mm，radial distance 0–7.9127 mm，低于历史tube诊断尺度。terminal v284与corrected IP.tail吻合；thumb nail独立冻结支持未更改。历史cap37中{cap['geometry_evidence']['historical_FOREIGN_driver_cap_count']}点带有foreign driver，不能自动继承。

提案：IP主导 + MCP residual。沿corrected CMC→MCP→IP→terminal累计arc s，q(t)=6t^5−15t^4+10t^3，t=clamp(0.5+(s−s_IP)/(2h),0,1)，h=5×MED={cap['rule']['h_mm']:.6f} mm，s_IP={cap['rule']['s_IP_mm']:.6f} mm。IP share语义q、MCP residual语义1−q。参数来自已批准R1B centered quintic family，仅重绑定正确chain，不继承old cap selector。这里只保存公式，没有逐点计算/生成candidate vectors。只有公式饱和处可IP=1，不能因cap名字37点一起one-hot。TIP禁止驱动。

同一profile延续到相容thumb proximal support，不在cap边界开关。cap2-ring最大arc相邻跳跃{cap['continuity_gate']['max_cap_2ring_arc_jump_mm']:.6f} mm，解析profile jump上界{cap['continuity_gate']['upper_bound_at_largest_jump']:.6f}。这说明profile可以连续，不能替代尚未存在的candidate-to-retained seam/static/deformation检查。既有cap1/2-ring跳跃完整作为baseline登记，投影segment tie seams也需检查。cap proposal validation = DEFORMATION_VALIDATION_REQUIRED。

## old cap9 correction

9/9为冻结native INDEX_SURFACE、fresh INDEX、hardrole0。逐点保存R1/R1A/R1B历史vectors、native/RSSF positions、INDEX MCP/PIP/DIP segment distances与longitudinal projection；每点2-ring都有干净native+fresh INDEX-exclusive/source-backed witness。witness保留实际WRIST/MCP/PIP/DIP组合和vector hashes；不能把全部点设INDEX_MCP=1。

未来candidate采用4组INDEX+WRIST simplex约束harmonic reconstruction；edge系数MED/length，geometry inverse-square bone-distance prior系数0.01，fixed valid local vectors为Dirichlet pins，按sorted IDs实现唯一convex问题。0.01为本轮明确提交Human审核的deterministic prior strength，不冒称历史批准参数。此优化未运行；所有cap9旧THUMB保护/override退休。需通过native INDEX continuity、outer seams、crater/spike以及targeted deformation检查。

## first-web wrapper

FIRST_WEB21 exact IDs保持不变。保留WRIST/THUMB_CMC/THUMB_MCP/INDEX_MCP四组shared semantics；THUMB_IP=0，TIP=0。旧cap/ownership依赖selector和wrapper exclusions退休。R3 7/14只作context，不能转换bone ratios。R1B四组静态support全部符合wrapper，但新周边candidate仍需三向continuity。2-ring共98点，仅工程检查范围，不扩展解剖membership。thumb/index context和既有WRIST carrier context共同约束全16维向量的同一个positive-edge convex patch；每点采用自己的allowed support，21web点采用shared四组。禁止只优化某一侧。

first-web允许bones的slots全部不变且IP禁止，因此IP距离变化本身不要求改21点的vectors；其中{web['FIRST_WEB21_classification_counts'].get('REBUILD_REQUIRED',0)}点需要重建、其余{web['FIRST_WEB21_classification_counts'].get('TARGETED_REVALIDATION',0)}点定向复验。CMC cage geometry FROZEN/PASS；exact skin mask未在本轮新冻结，仅geometry locality/protection context，不从R3创建mask。

## corrected field影响与exact reuse

静态逐vertex比较old R2A与corrected deform-chain nearest segment、raw/clamped mu、arc、normalized longitudinal、distance/radius-normalized location。共同radius尺度沿用历史R1B诊断值。material阈值：distance或arc≥0.5MED，mu/normalized longitudinal≥0.05，radius-normalized≥0.1，或nearest segment改变；必须同时有active thumb distal field支持。全mesh numerical changes与active skin影响分开记录，不能因远处投影变化判全mesh失效。normalized longitudinal分母变化单独作为诊断，不是本规则使用的毫米arc，不能单独触发重建。active affected {summary['corrected_rig_affected_vertex_count']}点。IP roll carriers即使距离变化小仍需定向复验，距离审计不证明旋转deformation合格。

每vertex唯一分类：SAFE_REUSE {summary['R1B_safe_reuse_count']}；TARGETED_REVALIDATION {summary['targeted_revalidation_count']}；REBUILD_REQUIRED {summary['rebuild_required_count']}；UNRESOLVED 0，总计3416。safe每条vector有hash证明：未经过legacy R1A/B selector写入、没有corrected IP frame carrier、outside新cap/web/boundary/repair scopes、实际driver slots不变、support及normalization合格。包括{reuse['safe_THUMB_label_count']}个fresh THUMB-label点及{reuse['safe_thumb_CMC_MCP_carrier_count']}个CMC/MCP历史carrier；没有THUMB label→全部rebuild规则。旧1931独立候选中{reuse['previous_1931_independent_set_rechecked']['still_safe']}个仍安全、{reuse['previous_1931_independent_set_rechecked']['now_targeted_or_rebuild']}个因新continuity scope进入复验/重建。R1B仍是历史master，不宣告为新production truth。

R1C/D/E实际保存delta及其cap-derived repair scope作为复验原因保留，不导入失败candidate向量。safe vectors也必须在获批后的新corrected bind上完成zero-pose/regression确认；SAFE_REUSE是exact vector eligibility，不是新资产已通过deformation。

## envelope与edge5879

总envelope {summary['rebuild_envelope_total_count']}点={summary['rebuild_required_count']}必须写candidate点+{summary['targeted_revalidation_count']}可通过gates保留原vector的复验点。包含cap37/old9、fresh20-edge endpoints及2-ring {summary['fresh_R3_boundary_transition_count']}点、FIRST_WEB21及2-ring、corrected active field、历史确有依赖repair范围、edge5879两端及18点2-ring。各component互相重叠，不能把component counts相加当total。2-ring用作continuity pins/regression boundary，不升级anatomy。outer seam失败只扩展必要local candidate范围，禁止全mesh兜底。

edge5879历史 PARTLY_CAP_DERIVED，R1E CMC_MCP_L3 ratio 11.041286717387363及weight partition mismatch保留为真实证据；本轮没有重算deformation。fresh v1551/v3125均INDEX（不同于历史THUMB上下文），v3125属于FIRST_WEB21故shared wrapper优先；v1551按corrected geometry/INDEX side guard决定正常chain drive。两端都在REBUILD_REQUIRED并带2-ring，动作TARGETED_REBUILD_REQUIRED。R1B近连续的旧pair仅作retention prior，不能复用R1E wrist-heavy错误partition。

## continuity与Human gate

sum=1±1e−5、nonnegative/finite、16deform groups、max4、TIP=0、first-web IP=0、old9无THUMB override、side guard不定义比例。新提案筛查gates：one-ring max per-group jump≤0.5，L1≤1；均明确是待Human审批的新static screening contract，不冒称历史生产规则。所有内部与跨envelope edges检查，不允许不相干one-hot driver swap；历史坏baseline不豁免绝对gate。profile平滑不替代projection seam和实际skin continuity。

每项authority状态RESOLVED指规则可执行；candidate static/deformation仍NOT_RUN，DEFORMATION_VALIDATION_REQUIRED可以进入获批后的候选重建，不再增加解剖逐点研究。Review七问仅审批driver/INDEX修正/shared wrapper/reuse-envelope/edge/ownership guard/下一候选重建。全部YES才批准TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1；不会自动执行、不批准Stage6/production promotion。

proposal bundle SHA256 `{bundle}`。

NEXT = HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL。STOP = YES。
'''
(OUT/'CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md').write_text(report,encoding='utf-8')
template=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Skin Authority · Human Review R1</title>
<style>
:root{font-family:Segoe UI,Microsoft YaHei,sans-serif;color:#182d36;background:#eef3f3}*{box-sizing:border-box}body{margin:0}header{background:#122e3a;color:#edf7f7;padding:28px 36px}header h1{font-size:28px;margin:8px 0}header p{max-width:1080px;line-height:1.7;color:#bfd3da}small{font-size:12px}.wrap{max-width:1440px;margin:auto;padding:24px}.banner{background:#fff2cd;border-left:4px solid #b88013;padding:16px;line-height:1.7}.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:20px 0}.stat{background:#fff;border:1px solid #dce5e8;border-radius:10px;padding:18px}.stat strong{display:block;font-size:28px}.stat span{font-size:12px;color:#526c77}.grid{display:grid;grid-template-columns:minmax(0,1fr) 345px;gap:18px}.card{background:#fff;border:1px solid #d8e2e5;border-radius:12px;padding:20px;margin-bottom:18px}.tabs{display:flex;flex-wrap:wrap;gap:7px}.tabs button{background:#eaf1f4;border:1px solid #cad8dd;padding:8px 12px;border-radius:6px;cursor:pointer}.tabs button.active{background:#1a5366;color:white}.viewtitle{font-size:18px;margin:18px 0 6px}.description{min-height:52px;color:#546b75;font-size:13px;line-height:1.6}canvas{width:100%;height:510px;background:#f6f9fa;border-radius:8px;cursor:crosshair}.controls{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;margin:14px 0}.controls label{display:flex;align-items:center;gap:6px}.legend{font-size:12px;display:flex;gap:13px;flex-wrap:wrap}.dot{width:10px;height:10px;display:inline-block;border-radius:50%;margin-right:4px}pre{font-size:11px;line-height:1.5;overflow:auto;max-height:460px;white-space:pre-wrap;word-break:break-all;background:#f4f7f8;padding:12px}h2{font-size:20px;margin:0 0 12px}h3{font-size:16px;margin-bottom:8px}.rule{font-size:13px;line-height:1.7}.rule b{color:#164f65}code{font-size:12px;background:#eef3f5;padding:2px 4px}details{margin:10px 0}summary{cursor:pointer;font-weight:600}.question{border-bottom:1px solid #e1e8eb;padding:18px 0}.question p{margin:0 0 10px;font-size:14px;line-height:1.6}.question label{display:inline-flex;gap:5px;margin-right:20px;font-size:14px}.question small{color:#616382;display:block;margin-top:9px;line-height:1.6}textarea{width:100%;min-height:120px;border:1px solid #b5cbd4;border-radius:6px;padding:12px;font:inherit}button.primary{background:#1b586d;color:white;border:0;border-radius:7px;padding:13px 20px;font-weight:600;cursor:pointer}button:disabled{opacity:.4;cursor:not-allowed}.actionrow{display:flex;gap:16px;align-items:center;margin:20px 0}.message{font-size:13px;color:#49646f}.hash{word-break:break-all;font:11px Consolas,monospace;color:#59747e}a{color:#17607d}.notice{color:#ae3e32;font-size:13px}.readonly{font-size:12px;color:#617780}.proofs{display:grid;grid-template-columns:1fr 1fr;gap:16px}footer{padding:12px 0;color:#5f747e;font-size:12px}@media(max-width:950px){.grid,.proofs{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}canvas{height:440px}header{padding:24px}.wrap{padding:16px}}
</style>
<header><small>PIANO HAND · SKIN AUTHORITY RECONCILIATION R1</small><h1>冻结 ownership → 连续 skin authority 提案</h1><p>审批 corrected rig、cap37、old cap9、first-web 的 driver 规则与局部 rebuild plan。所有图均来自保存的静态坐标；未生成新权重、未执行 deformation。本页提交决定，不会自动重建或启动 Stage6。</p></header>
<main class="wrap"><div class="banner"><b>规则已解决；候选验证待执行。</b> RESOLVED = deterministic proposal，PENDING_HUMAN_APPROVAL。未来 candidate 必须通过 static continuity 与 targeted deformation；本轮未宣告任何新 skin field 合格。</div>
<div class="stats"><div class="stat"><strong>2401</strong><span>SAFE_REUSE · exact vector candidates</span></div><div class="stat"><strong>771</strong><span>TARGETED_REVALIDATION</span></div><div class="stat"><strong>244</strong><span>REBUILD_REQUIRED</span></div><div class="stat"><strong>1015</strong><span>envelope / mesh 3416</span></div><div class="stat"><strong>0</strong><span>new weights · blend writes · Stage6</span></div></div>
<div class="grid"><section class="card"><div class="tabs" id="tabs"></div><h2 class="viewtitle" id="viewtitle"></h2><p class="description" id="description"></p><canvas id="mesh" width="1100" height="650" aria-label="Saved static mesh evidence, rotate using sliders and click vertices to inspect"></canvas>
<div class="controls"><label>Yaw <input id="yaw" type="range" min="-180" max="180" value="0"></label><label>Pitch <input id="pitch" type="range" min="-85" max="85" value="0"></label><label><input id="wire" type="checkbox" checked> topology</label><label><input id="chains" type="checkbox" checked> saved chains</label><button id="reset">Reset view</button></div>
<div class="legend"><span><i class="dot" style="background:#29846c"></i>safe / context</span><span><i class="dot" style="background:#d2a036"></i>targeted revalidation</span><span><i class="dot" style="background:#c94d4d"></i>rebuild required</span><span><i class="dot" style="background:#245ba9"></i>corrected thumb</span><span><i class="dot" style="background:#956abc"></i>old R2A thumb</span><span><i class="dot" style="background:#138b9a"></i>INDEX chain</span></div><p class="readonly">静态工程投影；拓扑遮挡未做表面裁切。点击点读取 vertex ID、frozen side、历史 vectors 与 old/corrected projection。</p></section>
<aside><section class="card"><h2>Evidence inspector</h2><p class="readonly">历史 R1B/R1E vectors 是只读证据，不是新权重。</p><pre id="inspector">选择一个点。</pre></section><section class="card"><h3>Binding hashes</h3><div id="bindings" class="hash"></div><p><a href="CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_REPORT.md">完整报告</a> · <a href="SKIN_AUTHORITY_PROPOSAL_BUNDLE_R1.json">proposal bundle</a></p></section></aside></div>
<div class="proofs"><section class="card rule"><h2>Driver decisions</h2><p><b>cap37：</b>IP 主导 + MCP residual。corrected arc centered quintic：<code>t=clamp(0.5+(s−sIP)/(2h))</code>，<code>q=6t⁵−15t⁴+10t³</code>，<code>h=19.441025 mm</code>。公式延续到相容 proximal thumb support。全部37点位于IP段；只有公式饱和处可one-hot。</p><p><b>old cap9：</b>9/9 INDEX。退休所有THUMB cap覆盖；每点都有2-ring干净INDEX历史witness，未来以INDEX+WRIST四组连续约束重建，不设手工MCP比例。</p><p><b>first-web：</b>exact21 IDs；WRIST / THUMB_CMC / THUMB_MCP / INDEX_MCP四组shared；IP=0。R3 7/14只作context。</p><p><b>TIP helpers：</b>5个全部non-deform，禁止进入skin vector。</p></section>
<section class="card rule"><h2>Validation & scope</h2><p>corrected active distal-field影响163点；fresh boundary2-ring126点；first-web2-ring98点；edge5879两端及2-ring18点。范围互相重叠，total1015。</p><p>cap2-ring最大arc邻接跳跃4.445563 mm，quintic profile jump解析上界0.214378；仍需检查实际candidate与retained seam，不能拿公式平滑代替skin验证。</p><p>old R1E edge5879 combined ratio <b>11.0412867</b>保留。fresh v1551/v3125均INDEX；v3125属于shared21。两端需targeted rebuild。</p><p>continuity contract：sum1、nonnegative、max4、TIP0、IP-on-web0、无illegal leakage。新增Human proposal screening：单组jump≤0.5，L1≤1，no abrupt one-ring swap；失败需局部平滑或明确deformation证明。</p><p>SAFE_REUSE包括21个THUMB label点及475个CMC/MCP carrier；不是THUMB⇒全rebuild。candidate尚未创建，<b>DEFORMATION_VALIDATION_REQUIRED</b>。</p></section></div>
<section class="card"><h2>Human decision · Q1–Q7</h2><p class="readonly">全部问题默认未选择。YES/NO均可导出；全部YES才记录candidate rebuild审批。请填写Notes说明限制。</p><form id="reviewform"><div id="questions"></div><h3>Notes</h3><textarea id="notes" placeholder="审批理由、限制与需关注的deformation条件"></textarea><div class="actionrow"><button id="export" type="button" class="primary" disabled>EXPORT RESPONSE JSON</button><span id="message" class="message">请完成Q1–Q7。</span></div></form><details><summary>Response preview</summary><pre id="responsepreview">尚未形成response。</pre></details><p class="notice" id="qa"></p></section>
<footer>R3 ownership、cap37、FIRST_WEB21、CMC cage geometry 与历史master保持冻结。Human全YES只批准下一 targeted candidate rebuild；automatic_apply=false，Stage6=false，production promotion=false。</footer></main>
<script id="evidence" type="application/json">__DATA__</script><script>
'use strict';
const D=JSON.parse(document.getElementById('evidence').textContent), $=id=>document.getElementById(id);
const views=[
 ['scope','完整 scope','SAFE_REUSE / TARGETED_REVALIDATION / REBUILD_REQUIRED 的逐vertex分区。绿色仍需未来corrected bind/zero-pose确认。',null,false],
 ['cap','cap37 driver','37点均在corrected IP段。蓝=corrected chain，紫=旧R2A；历史foreign vectors不可自动继承。','CAP37_CONTINUITY_2RING',false],
 ['oldnative','old cap9 · native','保存native geometry与2-ring证据。native INDEX身份已冻结，本轮不重新判断anatomy。','OLD_CAP9_INDEX_CONTINUITY_2RING',true],
 ['oldrssf','old cap9 · RSSF','当前静态positions；每点2-ring有INDEX-compatible历史vector作为未来continuous reconstruction pins。','OLD_CAP9_INDEX_CONTINUITY_2RING',false],
 ['web','first-web','shared21与工程2-ring；三个方向共同检查，IP绝对为0，7/14侧信息不决定骨比例。','FIRST_WEB_CONTINUITY_2RING',false],
 ['boundary','boundary transition','fresh20 ownership edges的38 endpoints + 2-ring126点。只是skin transition测试范围，不是新anatomy。','FRESH_R3_BOUNDARY_TRANSITION_2RING',false],
 ['impact','corrected field','active material变化163点；未把全mesh投影数值变化当作全mesh skin invalidation。','CORRECTED_DISTAL_FIELD_AFFECTED',false],
 ['edge','edge5879','两端fresh均INDEX，v3125为shared21；R1E ratio11.0412867与局部partition mismatch依然有效。','EDGE5879_CONTINUITY_2RING',false]
];let view=0,selected=null,screen=[];
const colors={SAFE_REUSE:'#29846c',TARGETED_REVALIDATION:'#d2a036',REBUILD_REQUIRED:'#c94d4d'};
views.forEach((v,i)=>{const b=document.createElement('button');b.textContent=v[1];b.id='view-'+v[0];b.onclick=()=>{view=i;selected=null;draw()};$('tabs').append(b)});
function draw(){
 const v=views[view],canvas=$('mesh'),ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 document.querySelectorAll('.tabs button').forEach((b,i)=>b.classList.toggle('active',i===view));$('viewtitle').textContent=v[1];$('description').textContent=v[2];
 const set=new Set(v[3]?D.sets[v[3]]:D.positions_mm.map((_,i)=>i));const P=v[4]?D.native_positions_mm:D.positions_mm;
 const a=+$('yaw').value*Math.PI/180,b=+$('pitch').value*Math.PI/180;
 function rotate(p){const x=p[0]*Math.cos(a)-p[1]*Math.sin(a),z=p[2];const y=p[0]*Math.sin(a)+p[1]*Math.cos(a);return[x,z*Math.cos(b)-y*Math.sin(b),y*Math.cos(b)+z*Math.sin(b)]}
 const R=P.map(rotate),xs=[...set].map(i=>R[i][0]),ys=[...set].map(i=>R[i][1]);
 const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),scale=Math.min((canvas.width-150)/Math.max(1,maxX-minX),(canvas.height-110)/Math.max(1,maxY-minY));
 function point(p){const r=rotate(p);return[canvas.width/2+(r[0]-(minX+maxX)/2)*scale,canvas.height/2-(r[1]-(minY+maxY)/2)*scale]}
 const pix=P.map(point);screen=[];
 if($('wire').checked){ctx.lineWidth=0.7;ctx.strokeStyle='#c6d3d9';ctx.beginPath();for(const[i,j]of D.edges){if(!set.has(i)||!set.has(j))continue;ctx.moveTo(...pix[i]);ctx.lineTo(...pix[j])}ctx.stroke()}
 if(!v[4]&&$('chains').checked){for(const[ch,c,dash]of[[D.old_THUMB_chain_mm,'#956abc',[7,4]],[D.THUMB_chain_mm,'#245ba9',[]],[D.INDEX_chain_mm,'#138b9a',[]]]){ctx.strokeStyle=c;ctx.lineWidth=3;ctx.setLineDash(dash);ctx.beginPath();ch.forEach((p,i)=>i?ctx.lineTo(...point(p)):ctx.moveTo(...point(p)));ctx.stroke();ctx.setLineDash([])}}
 for(const i of [...set].sort((i,j)=>R[i][2]-R[j][2])){const p=pix[i];ctx.fillStyle=colors[D.classifications[i]];ctx.beginPath();ctx.arc(...p,v[3]?3.8:1.8,0,Math.PI*2);ctx.fill();screen.push({i,x:p[0],y:p[1]})}
 const mark=view===1?D.sets.CAP37:view===2||view===3?D.sets.OLD_CAP9:view===4?D.sets.FIRST_WEB21:view===7?[1551,3125]:[];
 for(const i of mark){if(!set.has(i))continue;ctx.strokeStyle='#152c36';ctx.lineWidth=1.3;ctx.beginPath();ctx.arc(...pix[i],6,0,Math.PI*2);ctx.stroke();if(mark.length<12||i===284){ctx.fillStyle='#172f39';ctx.font='bold 13px Segoe UI';ctx.fillText('v'+i,pix[i][0]+8,pix[i][1]-6)}}
 if(view===7){const[i,j]=[1551,3125];ctx.strokeStyle='#cb344c';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(...pix[i]);ctx.lineTo(...pix[j]);ctx.stroke()}
 if(selected!==null){const p=pix[selected];ctx.strokeStyle='#091d27';ctx.lineWidth=2;ctx.beginPath();ctx.arc(...p,9,0,Math.PI*2);ctx.stroke()}
}
$('mesh').onclick=e=>{const r=$('mesh').getBoundingClientRect(),x=(e.clientX-r.left)*$('mesh').width/r.width,y=(e.clientY-r.top)*$('mesh').height/r.height;const best=screen.map(p=>({...p,d:Math.hypot(p.x-x,p.y-y)})).sort((a,b)=>a.d-b.d)[0];if(best&&best.d<25){selected=best.i;inspect(selected);draw()}};
function inspect(i){$('inspector').textContent=JSON.stringify({vertex_id:i,classification:D.classifications[i],frozen_R3_side:D.frozen_labels[i]||'OUTSIDE_BOUNDED_DOMAIN',membership:Object.keys(D.sets).filter(k=>D.sets[k].includes(i)),historical_R1B_vector:D.weights_R1B[i],historical_R1E_vector:D.weights_R1E[i],projection_comparison:D.impact[i]},null,2)}
for(const id of['yaw','pitch','wire','chains'])$(id).oninput=draw;
$('reset').onclick=()=>{$('yaw').value=0;$('pitch').value=0;draw()};
$('bindings').textContent='Proposal '+D.bundle_hash+'\nR3 '+D.packet.R3_authority_hash+'\nMembership '+D.packet.R3_membership_hash+'\nCorrected rig '+D.packet.corrected_rig_sha256;
const questions=[
 ['Q1_cap37_driver_semantics','cap37：接受corrected-arc IP主导 + MCP residual的连续quintic driver规则？','37点不按cap名字one-hot；未来验证proximal1/2-ring seams与IP/MCP deformation。'],
 ['Q2_old_cap9_INDEX_reconstruction','old cap9：接受退休THUMB覆盖，按local INDEX-compatible field重建？','9点历史vectors与干净2-ring INDEX witnesses已保存；不手工设置INDEX_MCP=1。'],
 ['Q3_FIRST_WEB_shared_wrapper','FIRST_WEB21：接受shared CMC/MCP/WRIST/INDEX-MCP wrapper，THUMB_IP=0？','exact21 membership不变；7THUMB/14INDEX只是side context，邻域必须三向连续。'],
 ['Q4_safe_reuse_and_rebuild_envelope','接受R1B safe-reuse / rebuild envelope？','2401 safe、771 targeted、244 rebuild；total1015；2-ring工程continuity范围。新gates单组jump≤0.5、L1≤1，candidate/deformation尚待验证。'],
 ['Q5_edge5879_targeted_scope','接受edge5879进入targeted rebuild/revalidation？','v1551/v3125及18点2-ring已覆盖；历史R1E ratio11.0412867有效，fresh两端INDEX，v3125 shared21优先。'],
 ['Q6_ownership_as_side_guard','接受ownership label仅作side/guard，不直接变成one-hot weights？','正常bone chain、joint/surface位置、approved shared semantics与continuity共同决定weights；所有TIP helpers禁止deform。'],
 ['Q7_approve_targeted_candidate_rebuild','是否批准进入TARGETED_RIG_AND_SKIN_DATA_REBUILD_AFTER_APPROVAL_R1？','仅批准下一targeted candidate重建与其必要验证；不自动执行、不批准Stage6或production promotion。']
];
questions.forEach(([id,q,n],i)=>{const el=document.createElement('div');el.className='question';const p=document.createElement('p');p.textContent='Q'+(i+1)+'. '+q;el.append(p);for(const val of['YES','NO']){const l=document.createElement('label'),r=document.createElement('input');r.type='radio';r.name=id;r.value=val;r.id=id+'_'+val;r.onchange=update;l.append(r,document.createTextNode(val));el.append(l)}const s=document.createElement('small');s.textContent=n;el.append(s);$('questions').append(el)});
const validationMode=new URLSearchParams(location.search).get('validation')==='1';
function collect(answers,notes,validation,timestamp){
 const complete=questions.every(([id])=>['YES','NO'].includes(answers[id])),accepted=complete&&questions.every(([id])=>answers[id]==='YES')&&!validation;
 return {review_id:D.packet.review_id,phase:'HUMAN_SKIN_AUTHORITY_RECONCILIATION_APPROVAL',proposal_bundle_hash:D.bundle_hash,
  R3_authority_hash:D.packet.R3_authority_hash,R3_membership_hash:D.packet.R3_membership_hash,corrected_rig_sha256:D.packet.corrected_rig_sha256,
  technical_verdict:'DETERMINISTIC_PROPOSAL_READY_FOR_HUMAN_REVIEW',...answers,notes,timestamp,
  validation_mode:validation,response_kind:validation?'QA_PREVIEW_NOT_HUMAN_APPROVAL':'HUMAN_SKIN_AUTHORITY_RECONCILIATION_RESPONSE',
  all_questions_answered:complete,accepted_as_skin_authority_rebuild_plan:accepted,skin_rebuild_candidate_approved:accepted,
  authorized_next_phase:accepted?D.packet.after_approval:null,authority_scope:D.packet.scope,
  candidate_static_pass:false,candidate_deformation_pass:false,Stage6_approved:false,production_promotion_approved:false,
  automatic_apply:false,automatic_solver_execution:false,applies_production_changes:false};
}
function update(){const ans={};questions.forEach(([id])=>ans[id]=document.querySelector('input[name="'+id+'"]:checked')?.value||null);const r=collect(ans,$('notes').value,validationMode,new Date().toISOString());$('responsepreview').textContent=JSON.stringify(r,null,2);$('export').disabled=!r.all_questions_answered||validationMode;$('message').textContent=validationMode?'QA preview：不能导出Human approval。':!r.all_questions_answered?'请完成Q1–Q7。':r.accepted_as_skin_authority_rebuild_plan?'全部YES：可导出候选重建审批；不会自动执行。':'包含NO：可导出反馈；不批准下一阶段。';return r}
$('notes').oninput=update;
$('export').onclick=()=>{const r=update();if(validationMode||!r.all_questions_answered)return;const url=URL.createObjectURL(new Blob([JSON.stringify(r,null,2)+'\n'],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=D.packet.review_id+'_RESPONSE_'+r.timestamp.replace(/[:.]/g,'-')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
if(validationMode)$('qa').textContent='VALIDATION MODE · QA only. No Human approval/export available.';
window.skinReviewAPI={collect,questionIds:questions.map(q=>q[0]),validationMode,data:D,selectView:id=>{view=views.findIndex(v=>v[0]===id);if(view>=0)draw()},inspect};
draw();update();
</script></html>'''
template=template.replace('__DATA__',json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/'))
(OUT/'SKIN_AUTHORITY_RECONCILIATION_HUMAN_REVIEW.html').write_text(template,encoding='utf-8')
summary['Human_Review_generated']=True;dump('CAP_SKIN_DRIVER_AND_WEIGHT_AUTHORITY_RECONCILIATION_R1_STATUS.json',summary)
print('Human Review generated. Proposal bundle hash:',bundle)
