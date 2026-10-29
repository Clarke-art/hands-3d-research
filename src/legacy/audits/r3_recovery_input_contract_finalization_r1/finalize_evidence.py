"""Independent static verification and evidence publication. No solver or Blender."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, math
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
RUN = 'R3_RECOVERY_INPUT_CONTRACT_FINALIZATION_R1'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()
def canonical(d): return json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf8')
def dump(n, d): (OUT/n).write_text(json.dumps(d, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf8')
checks = []
def check(n, b):
    checks.append({'name': n, 'passed': bool(b)})
    if not b: raise AssertionError(n)
c = read(OUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json')
h = read(OUT/'R3_CONTRACT_HASH_R1.json')
check('Canonical serialization and hash reproduce', canonical(c) == (OUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1_CANONICAL.json').read_bytes() and hashlib.sha256(canonical(c)).hexdigest() == h['canonical_contract_hash'])
check('Pretty contract hash reproduces', sha(OUT/'CANONICAL_R3_RECOVERY_INPUT_CONTRACT_R1.json') == h['pretty_contract_file_hash'])
for name, ref in c['files'].items(): check('Bound constituent '+name, sha(ref['path']) == ref['sha256'])
for name, ref in c['frozen_authority_sources'].items(): check('Frozen authority '+name, sha(ROOT/ref['path']) == ref['sha256'])
def part(n): return read(OUT/n)
t = part('R3_AUTHORITY_BACKED_THUMB_HARD_SOURCES_R1.json')
i = part('R3_INDEX_HARD_SOURCES_R1.json')
n = part('R3_NEUTRAL_INTERFACE_CONTEXT_R1.json')
g = part('R3_ENGINEERING_GRAPH_DOMAIN_R1.json')
s = part('R3_GRAPH_SURFACE_SUPPORT_AUDIT_R1.json')
cost = part('R3_COST_UNIT_CONTRACT_R1.json')
inf = part('R3_INF_AUTHORITY_CANDIDATE_R1.json')
cl = part('R3_CLOSURE_CONTRACT_R1.json')
val = part('R3_VALIDATOR_CONTRACT_R1.json')
T, I, G = set(t['unique']['vertex_ids']), set(i['unique']['vertex_ids']), set(g['vertex_ids'])
N = set(n['all_neutral_workspace']['vertex_ids'])
W = set(n['FIRST_WEB21']['membership']['vertex_ids'])
def source(k): return read(ROOT/c['frozen_authority_sources'][k]['path'])
raw = source('READ_ONLY_LIVE_EXTRACTION.json')['RSSF']
F, E, V = raw['faces'], raw['edges'], raw['vertices_world_m']
cap = source('cap_authority')
nails = source('nail_authority')['per_digit_faces']
thumb_nail = {v for f in nails['thumb'] for v in F[f]}
index_nail = {v for f in nails['index'] for v in F[f]}
check('THUMB derived from approved cap and nail only', T == set(cap['vertex_ids']) | thumb_nail and len(T) == c['THUMB_hard_source_count'])
check('INDEX unique ingredient union', I == set(i['ingredients']['resolved_index_tube']['vertex_ids']) | index_nail and len(I) == c['INDEX_hard_source_count'])
check('Hard sets disjoint; neutral complete partition', not T&I and N == G-(T|I) and not N&(T|I))
check('Frozen FIRST_WEB21 contained and never pinned', W == set(source('first_web_membership')['selected_vertices']) and W <= N and not W&(T|I))
lookup = {tuple(sorted(e)): ix for ix, e in enumerate(E)}
face_ids = set(g['face_ids'])
fv = {v for f in face_ids for v in F[f]}
fe = {lookup[tuple(sorted((a,b)))] for f in face_ids for a,b in zip(F[f], F[f][1:]+F[f][:1])}
GE = set(g['edge_ids'])
check('Full original faces exactly support every vertex and edge', G == fv and GE == fe)
check('Face membership complete within baseline', face_ids == {f for f, vs in enumerate(F) if set(vs) <= (set(g['baseline_vertices']['vertex_ids'])-set.union(*(set(x['vertex_ids']) for x in g['construction']['excluded_explicit_landmarks'].values())))})
adj = {v:set() for v in G}
for e in GE:
    a,b = E[e]; adj[a].add(b); adj[b].add(a)
seen = {min(G)}; stack = list(seen)
while stack:
    for w in adj[stack.pop()]-seen: seen.add(w); stack.append(w)
check('One source-reachable component, no dangling points', seen == G and T|I <= G and all(len(x)>1 for x in adj.values()))
check('Surface-support evidence exact', all(set(fs) == {f for f in face_ids if e in {lookup[tuple(sorted((a,b)))] for a,b in zip(F[f],F[f][1:]+F[f][:1])}} for e,fs in ((int(e),fs) for e,fs in s['per_edge_full_face_support'].items())))
check('No explicit landmark leakage', all(not G & set(x['vertex_ids']) for x in g['construction']['excluded_explicit_landmarks'].values()))
check('Wire spur removed without preserving old count', g['removed_vertices'] == [3049] and s['wire_only_edges_count'] == 0 and G == set(g['baseline_vertices']['vertex_ids'])-{3049})
check('Actual metric converted once from frozen RSSF', all(math.isclose(g['edge_lengths_mm'][str(e)], math.dist(V[E[e][0]],V[E[e][1]])*1000, rel_tol=1e-12) and g['edge_lengths_mm'][str(e)]>0 for e in GE))
prox = source('proximal_boundary')
check('P04/P05 frozen authority preserved', prox['status'] == 'HUMAN_APPROVED_FROZEN' and prox['stop']=='STOP_AFTER_P04' and [prox['distal_row'],prox['proximal_row']]==['P04','P05'] and {4666,4668} <= GE and {1368,1369,1371,1370} <= face_ids and n['proximal_boundary']['incident_face_transitions']==[[1368,1369],[1371,1370]])
band = n['conservative_web_transition_band']
check('Conservative transition band never hard pins or crosses guards', set(band['vertex_ids']) <= N and not set(band['face_ids'])&{1177,1227} and not band['formal_anatomical_role_extension'] and band['hard_pin_count']==0)
check('Cost candidate requires Human approval', cost['R3_COST_UNIT']=='CORRECTED_COMMON_MM_SEMANTICS' and not cost['Human_cost_freeze_recorded'] and not cost['auto_run_permitted'])
check('Unit table consistent', all(x['corrected_unary_capacity']==round(x['distance_mm']*1000) and x['pairwise_capacity']==1296 for x in cost['example_table']))
check('INF safe actual final graph', inf['INF']==len(G)*400000+len(GE)*1296+1 and inf['B']==inf['INF']-1 and c['INF']==inf['INF'])
check('Single cut capacity exact', all(x['directed_arc_cut_cost']==x['expected']==(1296 if x['u_side']!=x['v_side'] else 0) for x in part('R3_PAIRWISE_COST_CONTRACT_R1.json')['encoding_truth_table']))
check('Full sweep OR and non-convergence fail closed defined', 'OR every target change' in cl['full_sweep_changed'] and 'FAIL_CLOSED' in cl['non_convergent'] and cl['iteration_cap_full_sweeps'] == 20 and not cl['executed_this_run'])
check('Independent identity validators and six CLASS_A edges', len(val['checks'])==10 and val['INDEX_identity']['tip']==233 and val['THUMB_identity']['tip']==284 and len(val['CLASS_A_edges'])==6 and all(set(E[x['edge_id']])==set(x['vertex_ids']) for x in val['CLASS_A_edges']))
check('No old label truth or automatic run', not c['old_labels_used_as_truth'] and not c['Human_approved'] and not c['ready_to_auto_run'] and not c['automatic_apply'] and c['status']=='READY_FOR_HUMAN_APPROVAL')
static = part('STATIC_GATES_R1.json'); logic = part('RESPONSE_LOGIC_VERIFICATION_R1.json')
check('Initial static gates and response tests pass', static['passed'] and all(x['passed'] for x in static['checks']) and logic['passed'] and all(x['passed'] for x in logic['checks']))
browser = part('BROWSER_UI_VERIFICATION_R1.json'); delivery = part('BROWSER_FINAL_DELIVERY_STATE_R1.json')
check('Browser map focus and view controls verified', all(x['mode']==x['selected'] for x in browser['map_checks']) and all(x['focus']==x['selected'] for x in browser['focus_checks']) and all(x['pressed']=='true' for x in browser['view_checks']))
check('Browser missing and contradictory responses blocked', 'Q8' in browser['empty_export_error'] and 'Q1–Q7' in browser['contradictory_approval_error'])
qa_path = Path(r'<USER_HOME>\Downloads\AUTOMATED_R3_CONTRACT_UI_VALIDATION_NOT_HUMAN_2026-10-03T09-48-05-102Z.json')
qa = read(qa_path)
check('Actual exported QA JSON matches observed preview', qa == browser['QA_preview'])
check('QA cannot authorize Human contract or execution', qa['validation_mode'] and not qa['approved_for_input_contract'] and not qa['cost_semantics_approved_with_contract'] and qa['authorized_next_phase'] is None and not qa['automatic_solver_execution'] and qa['canonical_contract_hash']==h['canonical_contract_hash'])
dump('QA_DOWNLOAD_VERIFICATION_R1.json', {'path':str(qa_path),'sha256':sha(qa_path),'matches_browser_preview':True,'qa_only':True,'is_Human_response':False,'grants_authority':False})
check('Delivered page blank and no validation parameters', delivery['delivered_without_validation_parameters'] and delivery['blank_state']['answers']==['']*8 and delivery['blank_state']['notes']=='' and delivery['blank_state']['preview']=='' and all(delivery['blank_state']['images']) and not delivery['runtime_errors'] and not browser['runtime_errors'])
class Controls(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='select' and d.get('id','') in ['Q'+str(j) for j in range(1,9)]: self.ids.append(d['id'])
html=(OUT/'R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW.html').read_text(encoding='utf8'); parser=Controls();parser.feed(html)
check('Eight genuine selectable questions and embedded bindings', sorted(parser.ids)==['Q'+str(j) for j in range(1,9)] and h['canonical_contract_hash'] in html and c['frozen_authority_sources']['proximal_boundary']['combined_authority_hash'] in html)
for p in sorted((OUT/'renders').glob('*.png')):
    with Image.open(p) as im: im.verify()
check('Six render artifacts verified', len(list((OUT/'renders').glob('*.png')))==6)
before=part('FROZEN_HASHES_BEFORE.json')
after={'workspace':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts},'external':{p:sha(p) for p in before['external']}}
check('Every historical workspace and external file unchanged', before==after)
dump('FROZEN_HASHES_AFTER.json',after)
frozen={'status':'PASS','all_before_equal_after':True,'workspace_file_count':len(before['workspace']),'external_file_count':len(before['external']),'workspace_blend_file_count':sum(p.lower().endswith('.blend') for p in before['workspace']),'changed_files':[],'historical_files_modified':False,'Human_responses_modified':False,'FIRST_WEB21_changed':False,'cap37_changed':False,'nail_changed':False}
dump('FROZEN_HASH_VERIFICATION_R1.json',frozen)
dump('FINAL_STATIC_VERIFICATION_R1.json',{'passed':True,'check_count':len(checks),'checks':checks,'initial_static_gate_count':static['check_count'],'response_logic_check_count':logic['check_count'],'Human_approval_received_this_run':False,'actual_R3_result_validated':False})
status=part(RUN+'_STATUS.json')
status.update({'static_gates':'PASS','initial_static_gate_count':static['check_count'],'final_static_check_count':len(checks),'response_logic_check_count':logic['check_count'],'Human_Review_page_generated':'YES','browser_UI_verified':True,'actual_QA_JSON_download_verified':True,'actual_Human_approval_received':False,'cost_authority_Human_frozen':False,'frozen_hashes_before_equal_after':True,'frozen_workspace_file_count':len(before['workspace']),'frozen_external_file_count':len(before['external']),'conservative_transition_band_vertex_count':len(band['vertex_ids']),'conservative_transition_band_face_count':len(band['face_ids']),'INDEX_resolved_tube_ingredient_used':True})
dump(RUN+'_STATUS.json',status)
report=f'''# R3_RECOVERY_INPUT_CONTRACT_FINALIZATION_R1

状态：READY_FOR_HUMAN_APPROVAL。工程 contract 已收束，尚未收到本轮 Human approval。CORRECTED_MM 仍是待审批 candidate；本轮没有计算 R3 distance fields、mincut、closure 或 Stage6。

## Sources 与 neutral workspace

THUMB = canonical cap37 ∪ approved thumb nail22，重叠2，unique {len(T)}。v284 已属于 cap37；没有额外 landmark pin。历史 THUMB_STRONG241、ambiguous THUMB tube、旧 corridor、FIRST_WEB21、CMC、thenar sphere、旧 cap9 proximity 和旧 R2 labels 均不增加 THUMB pins。THUMB_TUBE_HARD_ANCHOR_AUTHORITY = RETIRED_FROM_R3_VNEXT_HARD_SOURCE_CONTRACT；历史文件完整保留。THUMB tube radius 不再是 R3 前置条件。

INDEX = 已 RESOLVED 的独立 native-guarded INDEX tube143 ∪ approved INDEX nail43，重叠41，unique {len(I)}。按原 source predicate 从 corrected chain 重建并与 resolved ingredient IDs 核对，不复制历史 strong-set 报告数字。这里保留的是已 resolved 的 INDEX ingredient；“tube-derived hard sources = NO”仅指退休的 ambiguous THUMB tube 路线。

两 hard sets 交集0；重复 provenance 每 unique vertex 仅一个 INF terminal。FIRST_WEB21 frozen membership 保留、全部进入 neutral context、hard pins0。全部 unpinned graph vertices = {len(N)}；其中 columns4–6 conservative transition band = {len(band['vertex_ids'])} vertices / {len(band['face_ids'])} faces。该 band 是工程 context，不等于 anatomical FIRST_WEB membership，也不是正式 shared-role extension。

## Deterministic graph 与 cleanup

从原 G3_K2 construction 重建：native pre-RSSF structural thumb/index 的 closed two-ring branch cores → G1（去 WEB）→ G2（加 frozen WEB21）→ native thumb/index/wrist 限制下 two-ring dilation。Structural Voronoi partition 仅用于重建 bounded workspace 和独立 INDEX source guard，不构成 anatomy 或旧 R2/R3 truth。

排除 middle/ring/little nails 和各 terminal two rings、独立 wrist v2260 two rings。只保留完整原始 surface polygons，最终 vertex/edge IDs 是这些完整 faces 的 vertex / cyclic edge union。要求唯一 connected component 且包含全部 hard sources / WEB；不通过 component 大小判断 INDEX。

重建 baseline 963V / 1882E，清理后 {len(G)}V / {len(GE)}E / {len(face_ids)}F。删除唯一无完整 face support 的 v3049 与 wire (1891,3049)，没有为保持 count 留下错误结构。所有 graph edges 均有真实完整 surface face support；无 dangling point，source reachable，explicit other-digit/wrist landmark leakage0。

Graph 保留19个 native Voronoi wrist structural candidates，属于不确定 proximal optimization workspace；不把该结构分类视作生物学 wrist truth。独立 wrist landmark 及 two-ring exclusion 无泄漏。Graph 不是 anatomical ownership map，unresolved anatomy 不构成 blocker。

## Frozen proximal 与 distal guards

Human-approved STOP_AFTER_P04 / P04–P05 / e4666,e4668 原样保留；vertex pairs [1444,2822]、[1520,2822]，faces1368→1369、1371→1370。该 authority 限制旧 strip 的 semantic propagation；不推导 P04 全部 THUMB 或 P05 全部 SHARED，不裁掉 broader solver graph。

Distal nail guard：在 face1177 / nail v304 前停止。Non-nail：D04 / face1226 是已有 safe evidence；下一面1227 碰 cap37 v298/v1454。继续作为 PRIOR_EVIDENCE / ENGINEERING_GUARD，未升级为新的 Human anatomical membership。Transition band 不碰 hard-source faces，不跨1177/1227。

CMC geometry FROZEN / PASS，仅 frozen wrapper，hard-source role NONE；不把近似 cage coordinate mapping 当 membership authority。cap、nail、FIRST_WEB、corrected rig、历史 Human authority 均 hash protected。

## Cost、INF 与 closure candidate

R3_COST_UNIT = CORRECTED_COMMON_MM_SEMANTICS。Original RSSF world-m edge lengths只转换一次到 mm；dT/dI 使用最终 graph 到 unique sources 的 mm edge-geodesic。不可达 FAIL_CLOSED；域外不求解、不注入旧 labels。Finite capacity = min(400000, round(distance_mm×1000))，400mm cap。Python rounding 为 nearest / ties-to-even。

| mm | corrected unary | historical bug | pairwise |
|---:|---:|---:|---:|
|1|1000|1|1296|
|5|5000|5|1296|
|10|10000|10|1296|
|20|20000|20|1296|

TAU = {cost['TAU_mm']:.14f} mm；pairwise TAU/3 ×1000 round =1296。每无向 edge 两条 directed P arcs，cut 只计一次1296，四种 label pairing algebraic truth table通过。历史10mm unary=10造成 pairwise domination 已明确承认；本轮不重做 provenance research。

B = {len(G)}×400000 + {len(GE)}×1296 = {inf['B']}；INF = B+1 = {inf['INF']}。Pin-respecting cut finite bound ≤B；任何 violated pin cost≥INF>B。使用实际 final counts，没有复制旧 G3 INF。

Closure 只消费 fresh R3 labels；THUMB+INDEX完整 sweep，changed 在两 loop 前初始化、OR累计。声明 stable ID ordering、每更新验证 pins、20 full-sweep cap、repeated-state cycle FAIL_CLOSED、cap仍变化 FAIL_CLOSED。Ambiguity abs(dT_mm−dI_mm)<TAU_mm，不重复 mm conversion。本轮 closure执行0。

## Future validators 与 history

已定义10项 fresh recompute checks：hard pins、graph/connectivity/source reachability、label components/islands、sheet split、ambiguous band、CLASS_A六条 original-edge geometry、INDEX v233+nail identity、THUMB v284+cap37+nail identity、frozen wrappers/deformation followup、deterministic reproducibility。禁止“第二大 component = INDEX”。Face dual split 使用 fresh cut edges；identity冲突或无法一致识别应 fail revalidation。

历史 labels/boundary/flow/changed34/sheet217/3199 仅 HISTORICAL_COMPARISON_ONLY。未读取历史 label contents 作 truth；不以减少旧 label diff 为目标。历史 graph1008/1977与final962/1881的集合差仅展示。未来成功 R3 之后仍需要 skin weights、targeted deformation、full Stage6；本 contract 不批准这些工作。

ANATOMICAL_LATERAL_FRONTIER、FULL_FOUR_ROLE_MAP、exact palm/thenar/first-web biological boundary继续 UNRESOLVED，不阻塞工程 candidate。不启动 lateral、proximal或tube逐面 anatomy research。

## Human Review 与 verification

R3_RECOVERY_INPUT_CONTRACT_HUMAN_REVIEW.html 已生成：真实Q1–Q8可选 controls、Notes、EXPORT RESPONSE JSON，无预选、无自动APPLY。包含 Native/RSSF可旋转模型、8种 map layers、4个 focus、4个 view、6张 context renders、source/neutral/WEB/boundary/guards/graph/diff/cost table。

{static['check_count']} initial static gates、{len(checks)} independent final checks、{logic['check_count']} response-logic checks通过。Browser实际验证 missing/contradictory answers blocked、map/focus/view切换、JSON下载、clear/reset和最终空白页面。QA下载文件明确 validation_mode=true / AUTOMATED_UI_VALIDATION_NOT_HUMAN，approved=false / next=null，不构成 Human response。正式交付页面没有 validation query，Q1–Q8与Notes均空白，6张图片全部载入，runtime errors0。

Canonical candidate hash：`{h['canonical_contract_hash']}`。
Human frozen proximal authority hash：`{c['frozen_authority_sources']['proximal_boundary']['combined_authority_hash']}`。
Canonical JSON以UTF8、sorted keys、compact separators、无trailing newline hash；14个 constituent files和frozen source path/hash被绑定。Human JSON export绑定以上两个hash。本轮没有 Human approval。

## Frozen protection 与 STOP

全部 {len(before['workspace'])} 个 pre-existing workspace files、{len(before['external'])} 个 external frozen files before==after；包括 {frozen['workspace_blend_file_count']} 个 workspace .blend。无历史文件、Human responses、cap37、FIRST_WEB21、nail修改。详细 before/after和verification JSON已保存。

WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0；R2_runs=R3_runs=Stage6_runs=BLEND_FILES_WRITTEN=0。只新增本轮 audit 输出。

NEXT = HUMAN_R3_RECOVERY_INPUT_CONTRACT_APPROVAL。仅独立核验真实Human JSON批准后，才可进入 R3_FULL_RECOMPUTE_AND_AUTHORITY_REVALIDATION_R1。本轮 STOP。
'''
(OUT/(RUN+'_REPORT.md')).write_text(report,encoding='utf8')
manifest={'algorithm':'SHA-256','canonical_contract_hash':h['canonical_contract_hash'],'status':'READY_FOR_HUMAN_APPROVAL','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',manifest)
print(json.dumps({'passed':True,'final_checks':len(checks),'protected_workspace_files':len(before['workspace']),'protected_external_files':len(before['external']),'protected_blends':frozen['workspace_blend_file_count'],'output_files':len(manifest['files'])+1,'contract_hash':h['canonical_contract_hash'],'status':status['status']},indent=2))
