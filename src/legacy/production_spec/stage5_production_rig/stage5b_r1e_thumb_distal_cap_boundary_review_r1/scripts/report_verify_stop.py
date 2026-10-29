"""Final evidence verification, report and integrity audit; never applies cap authority."""
import sys
sys.dont_write_bytecode=True
import json, hashlib, math
from pathlib import Path
from PIL import Image
from boundary_geometry import *
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def dump(n,o): (OUT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
CMP=load(OUT/'CAP_BOUNDARY_CANDIDATE_COMPARISON.json'); CL=load(OUT/'CAP_EXPANSION_VERTEX_CLASSIFICATION.json')
FORE=load(OUT/'CURRENT_CAP_BOUNDARY_FORENSIC.json'); V882=load(OUT/'V882_BOUNDARY_FORENSIC.json')
CN={k:load(OUT/f'CAP_BOUNDARY_CANDIDATE_{k}.json') for k in 'ABCDE'}
H=FORE['Human_authority_verbatim']; before=load(OUT/'FROZEN_HASHES_BEFORE.json')
assert len(FORE['vertices'])==48 and len(FORE['faces'])==33 and len(CL['vertices'])==28
assert CN['A']['face_ids']==sorted(CF) and CN['A']['vertex_ids']==sorted(CV)
assert all(max(G[F[fi]])<=9 for fi in CN['B']['face_ids'])
assert CN['C']['minimum_additions_proven'] and CN['C']['minimum_additions_coverage_lower_bound']==len(CN['C']['added_face_ids'])==3
assert CORE<=set(CN['C']['vertex_ids']) and not(set(CN['C']['vertex_ids'])&set(CMP['distal_shaft_proxy_ids_in_A']))
assert CORE<=set(CN['E']['vertex_ids']) and abs(abs(CN['E']['metrics']['boundary_angular_winding_numbers'][0])-1)<1e-8
assert CN['D']['sector_transition_knee_range_mm']==[7.5,14.0] and 'NON_VIABLE' in CN['D']['status']
for k,c in CN.items():
    fs=set(c['face_ids']); p=patch(fs); m=c['metrics']
    assert set(c['vertex_ids'])=={v for fi in fs for v in F[fi]}
    assert p['single_disk'] and m['seed_included'] and p['euler_characteristic']==1
    assert p['component_count']==1 and p['closed_loop_count']==1
    assert not p['nonmanifold_edges'] and not p['nonmanifold_vertex_links']
    assert abs(m['max_geodesic_mm']-max(G[m['vertices']]))<1e-8
    assert c['production_authority_applied'] is False and c['membership_authority_applied'] is False
assert math.isclose(V882['vertex']['geodesic_from_v284_mm'],15.894139268401133,abs_tol=1e-8)
assert [r['face_id'] for r in V882['vertex']['why_included_by_A']]==[67]
required_png=[f'CAP_BOUNDARY_CANDIDATES_{v}.png' for v in ['DORSAL','PALMAR','RADIAL','ULNAR','SIDE','TIP']]+['CAP_28_EXPANSION_VERTICES_FORENSIC.png']
for name in required_png: Image.open(OUT/'renders'/name).verify()
ui=load(OUT/'UI_VERIFICATION.json'); assert ui['status']=='PASS' and ui['all_human_answers_remain_blank']
ZERO={k:0 for k in ['BLEND_FILES_WRITTEN','WEIGHT_DELTA','GEOMETRY_DELTA','TOPOLOGY_DELTA','BONE_DELTA','JOINT_DELTA']}
after={'workspace':{p:sha(ROOT/p) for p in before['workspace']},'external':{p:sha(Path(p)) for p in before['external']}}
changed=[p for p,h in before['workspace'].items() if after['workspace'][p]!=h]+[p for p,h in before['external'].items() if after['external'][p]!=h]
added=[p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts and p.relative_to(ROOT).as_posix() not in before['workspace']]
assert not changed and not added
dump('FROZEN_HASH_VERIFICATION.json',{'all_before_equals_after':True,'before':before,'after':after,
    'protected_workspace_files':len(before['workspace']),'protected_external_human_responses':len(before['external']),
    'changed_files':changed,'new_files_outside_review_directory':added,'new_blend_files':[],
    'scope':'Every existing workspace file except .git plus the original Downloads Human cap response. All Stage4/5/6, R3 evidence, previous Human responses/reviews and references are included.',
    **ZERO,'R1F_CREATED':False,'Stage6_runs':0,'R3_runs':0,'strict_bound_recomputations':0,
    'cap_membership_authority_applied':False,'nail_modified':False,'retopo':False})
rec=CMP['ENGINEERING_RECOMMENDATION']
status={'execution':'THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1','date_local':'2026-10-02','timezone':'Asia/Shanghai',
    'scope':'READ_ONLY / BOUNDARY_ONLY / ANATOMICAL_TOPOLOGICAL_CANDIDATE_REVIEW',
    'Human_authority_verbatim':H,'human_response_path':FORE['human_response_path'],'human_response_sha256':FORE['human_response_sha256'],
    'CURRENT_48_VERTEX_REGION_IDENTITY':'ACCEPTED_UNCHANGED','native_branch_identity_reopened':False,
    'OLD_CURRENT_CAP_9':'CONFIRMED_CONTAMINATED_NATIVE_INDEX_SURFACE','old_cap9_restored':False,
    'BOUNDARY':'UNRESOLVED','NEXT':'MANUAL_CAP_BOUNDARY_REVIEW','ENGINEERING_RECOMMENDATION':rec,
    'candidate_summary':{k:{'vertex_count':c['metrics']['vertex_count'],'face_count':c['metrics']['face_count'],
        'max_geodesic_mm':c['metrics']['max_geodesic_mm'],'status':c['status']} for k,c in CN.items()},
    'expansion_classification_counts':CL['classification_counts'],'v882_classification':V882['vertex']['classification'],
    'classification_authority':'PROVISIONAL_ENGINEERING_ONLY_PENDING_HUMAN_BOUNDARY_REVIEW',
    'production_authority_applied':False,'cap_authority_frozen':False,'human_boundary_answers':[],
    'nail_authority_frozen_unchanged':True,'old_strict_bounds':'INVALIDATED_AS_ANATOMICAL_CAP_ENDPOINT_EVIDENCE',
    'replacement_bound_produced':False,**ZERO,'R1F_CREATED':False,'Stage6_runs':0,'R3_runs':0,'retopo':False,
    'frozen_hashes_all_before_equals_after':True,'review_page':'THUMB_DISTAL_CAP_BOUNDARY_REVIEW.html',
    'STOP':'WAITING_FOR_HUMAN_BOUNDARY_REVIEW'}
dump('THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_STATUS.json',status)
table='\n'.join(f'| {k} | {m["vertex_count"]} | {m["face_count"]} | {m["max_geodesic_mm"]:.6f} | {m["median_geodesic_mm"]:.6f} | {m["boundary_edge_count"]} | {m["surface_area_mm2"]:.3f} | {m["boundary_perimeter_mm"]:.3f} | {m["boundary_axial_spread_mm"]:.3f} | {m["bulb_coverage"]["rounded_tip_proxy_area_coverage_fraction"]*100:.2f}% |' for k,c in CN.items() for m in [c['metrics']])
anatomy='\n\n'.join(f'**{k} — {c["name"]}**：{c["human_readable_anatomical_interpretation"]}\n\nRule：{c["rule"]}\n\nStatus：`{c["status"]}`。' for k,c in CN.items())
classlist='\n'.join(f'- {code} / {label}：'+', '.join('v'+str(r['vertex_id']) for r in CL['vertices'] if r['classification_code']==code) for code,label in CL['classification_labels'].items())
over13='\n'.join(f'| {r["vertex_id"]} | {r["geodesic_from_v284_mm"]:.6f} | {r["axial_depth_from_tip_mm"]:.6f} | {r["normal_tip_axis_component"]:.4f} | {r["curvature_proxy"]["normal_variation_rad_per_mm"]:.4f} | {r["classification_code"]} |' for r in CL['vertices'] if r['geodesic_from_v284_mm']>13)
report=f'''# THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_REPORT

**BOUNDARY=UNRESOLVED；NEXT=MANUAL_CAP_BOUNDARY_REVIEW；STOP。** 工程推荐 E 进入 Human comparison，未批准最终 boundary、未冻结 cap、未应用 production authority。全部计算只来自冻结的 native/pre-RSSF 静态 geometry/topology，未运行动态 deformation。

## Human input 与权威范围

首先读取原始文件 `{FORE['human_response_path']}`，SHA256 `{FORE['human_response_sha256']}`；本目录 source copy 逐字节相同。原样接受 Q1=YES、Q2=YES、Q3=NO、Q4=NO、Q5=UNRESOLVED、Q6=APPROVE_WITH_BOUNDARY_REVIEW。

> {H['answers']['notes']}

CURRENT_48_VERTEX_REGION_IDENTITY=ACCEPTED_UNCHANGED。没有重新提问 thumb identity、重开 native branch identity，或将局部 shaft-edge 观察升级为 region identity contradiction。OLD_CURRENT_CAP_9=CONFIRMED_CONTAMINATED，旧九点 {D['current_cap9']} 全部 native INDEX_SURFACE，不得恢复，也未恢复。

## 候选结果

| candidate | vertices | faces | max g mm | median g mm | boundary edges/vertices | area mm² | perimeter mm | boundary axial spread mm | bulb proxy area coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{table}

所有 A–E patch：component_count=1、closed_loop_count=1、Euler=1、seed v284 included=YES、edge nonmanifold=0、vertex-link nonmanifold=0。边界顶点数与边界边数相同。所有周向环 absolute winding=1（方向随 loop traversal ±1）；E 的12个30° sectors 均有点，是展示指标，不是选择条件。A/B/C/D 的11/10/11/11 sectors 不表示有 surface hole。

{anatomy}

## C 的最小 closure 证明

B 是17点/9面的单闭环 disk，但缺核心 v880/v1755/v285。C 在保留 B 全部 faces 的前提下，允许从 A 添加 face，排除含多信号 shaft-extension corners 的 faces，要求全部20核心点、单 disk / 单闭环。每个允许 added face 最多覆盖一个缺失核心，故至少需3个 added faces。穷举3-face combinations 1540个，其中32个覆盖核心，8个形成有效disk。按 boundary axial spread→geodesic RMS→area→face IDs 排序得到 added faces {CN['C']['added_face_ids']}。这证明限定域内最低补面数，不声称全球最小 anatomical cap。没有自由手选顶点或补造新面。

## D 的 curvature transition 与限制

从 native area-weighted normals 计算 normal dot(IP→tip)，并计算一环 median normal-angle/edge-length curvature proxy。另对两环点拟合 quadratic surface，输出 principal curvature proxies、RMS、rank 与样本数。以 native edge median {MESHRES:.6f} mm 的0.5/0.7/1.0倍为平滑带宽，对1–23 mm轴深 profile 联合拟合连续双线性 hinge，搜索3–14.5 mm knot。

全局最佳 knees 为9.5/10.0/11.5 mm；median10mm生成诊断 D（64 faces /75 vertices）。十二周向窗口35° Gaussian 下，带宽/方向的最佳 knees 为7.5–14.0mm，跨度6.5mm 大于一个 local median edge。没有唯一稳定的全周 curvature crease。因此 D 标记 **NON_VIABLE_AS_UNIQUE_STABLE_CURVATURE_AUTHORITY_DIAGNOSTIC_PATCH_ONLY**，保留未经修补的诊断 patch 供 Human 看清失败范围。D 的连通闭环只是拓扑事实，不能反证这一限制。

## E 的 deterministic axial circumferential rule

使用既有 native IP→tip engineering axis，以tip为轴深0；扫描 native THUMB faces 的1–15mm唯一 centroid-depth thresholds。每阈值取 distal sublevel 的 seed-connected component；必须保持20个核心点、一个 manifold disk / closed loop、absolute angular winding=1、最大角间隙≤60°。最小化 boundary geodesic 对9mm的RMS偏差，随后以area→cut depth→IDs破同分。最终 centroid-depth cut={CN['E']['centroid_depth_cut_mm']:.6f} mm，37点/25面。并非逐点手选，也不是新增切面/retopo；face角点可跨越这一 centroid plane，最大 corner轴深6.690820mm。

E 加入 A 之外 v297/v298，通过 faces1942/1944：两点 g=13.284340/13.367420mm，轴深5.447803/5.344341mm，normal轴分量约0.473/0.469，符合 tip-facing rounded surface proxy。它们只属于新审阅候选，不登记新的 authority。

**E 未包含暂列 rounded-bulb corner 类的 v1453/v2785/v2790。** E80.95%与A81.25%的 bulb proxy 面积近似，不代表逐面或逐点相同。Human 需判断上述新增与遗漏是否合理或需 narrow fix；本轮不会为保留 E 而改写分类。这是推荐的明确未解决限制。

## 28 个 expansion vertices 分类

全部48点/33面的 CURRENT_CAP_BOUNDARY_FORENSIC.json 包含 vertex/face IDs、g、Euclidean tip距离、world XYZ mm、area-weighted native normal、curvature proxies、nail/边界 membership、IP距离、轴投影/深度、周向角、1-ring、exact2-ring、selected/native face incidence。face rows另含几何面积、最大边长、native normal与各候选归属。

分类仅为 **PROVISIONAL_ENGINEERING_FOR_HUMAN_BOUNDARY_REVIEW**。“A/D REQUIRED”是暂定保留解释，不能自行注册为 Human anatomical necessity。E 保留未决情形；没有 >9mm→DELETE 规则，也没有 connected→15.89mm acceptable 规则。

统计：A=15、B=5、C=3、D=1、E=4。

{classlist}

分类依据同时包含轴深、native法线朝向、normal-variation curvature、nail关系、mesh resolution、face admission、各候选归属、core retention与boundary topology。C类要求轴深超过最低profile knee9.5mm、normal轴分量<0.15、normal variation<0.08rad/mm三项共同成立；这些工程阈值须 Human 验证，不能把它们当人体固定常数。A类要求短轴深、tip-facing法线与曲率代理共同支持 rounded envelope；沿周向较长的geodesic并不把其自动判为shaft。

## v882 与其余 >13mm 顶点

v882仅通过 **face67=[882,2496,880,39]** 的 corner union 纳入：其中 core v880 g=8.826592mm，故 face满足min-corner9mm；v882自身g=15.894139mm。face67不是 approved nail face，虽v882也是邻接approved nail的顶点。

v882 tip Euclidean=11.951136mm，IP Euclidean=11.722515mm；轴深11.154648mm，IP→tip投影10.909349mm，仍在IP distal侧。normal dotaxis=0.039780，median normal variation=0.042974rad/mm；两环quadratic RMS=0.097030mm。它对应 distal nail margin / near-transverse distal-shaft continuation，不是靠一个长距离就作出的分类。暂定 **C/PROXIMAL_OVERREACH** 指 terminal cap边界的局部shaft尾角，不指middle/proximal thumb identity，也不撤回Human Q3=NO。

| vertex | g mm | axial depth mm | normal axial | normal variation rad/mm | provisional class |
| --- | ---: | ---: | ---: | ---: | --- |
{over13}

v1453/v2785/v2790虽g>13mm，仍有tip-facing curved-bulb证据，因此暂列A；这直接展示分类不是距离截断。其余逐点判据及face-admission证据全部在classification JSON。

## Approved nail relation

12-face approved nail冻结，native轴深3.737248–19.631122mm。不能要求 entire nail 必须在terminal cap内。distal margin proxy为v37/v879：A/D/E均包含；B/C只含v879。E的闭环边界沿 approved nail distal margin **edge v37–v879** 相接，未选入approved nail整面，也没有给nail创建内部孔或拆开nail权威。A选入distal nail face65；D选入64/65/1040，连成一个nail intersection component，但其shaft延伸问题独立存在。B/C虽未修改nail，对完整distal-margin关系偏小，需Human判断。

Nail-compatible工程关系：A/D/E；其中D仍不成立为稳定curvature authority。B/C属于distal nail-margin proxy partly omitted。这些关系不等同于 final anatomical boundary approval；v882 nail membership不能强制cap保留。

## ENGINEERING_RECOMMENDATION（E，仅供 Human）

- GEOMETRIC_REASON：{rec['GEOMETRIC_REASON']}
- ANATOMICAL_REASON：{rec['ANATOMICAL_REASON']}
- TOPOLOGICAL_REASON：{rec['TOPOLOGICAL_REASON']}
- LIMITATIONS：{rec['LIMITATIONS']}

没有使用 Stage6 stretch、历史deformation Gate、权重或strict bound来选边界。旧13.1646mm /5.9643 /6.5160继续保持 INVALIDATED AS ANATOMICAL CAP-ENDPOINT EVIDENCE，没有replacement bound。

## 审阅页与核验

THUMB_DISTAL_CAP_BOUNDARY_REVIEW.html：六方向切换；A/B/C/D/E/nail/core/expansion/vertexID/faceID开关；boundary-only；local tip closeup。灰色表面深度测试，彩色面/点/边为明确标示X-ray。方向为DORSAL(-Y)、PALMAR(+Y)、RADIAL(+X)、ULNAR(-X)、thumb side、tip axial。所有required7张PNG已验证并检查六视角和forensic图；浏览器真实运行测试全部开关、viewBox缩放、空答案拦截、脚本无错误，截图另存。Human Q1–Q7初始为空，测试没有生成Human verdict；无网络提交或自动freeze。

页面只问用户指定boundary Q1–Q7，不重新问region身份。Q6=A/B/C/D/E/UNRESOLVED；Q7=APPROVE_FOR_FREEZE/APPROVE_WITH_MINOR_BOUNDARY_FIX/REJECT/UNRESOLVED。

## 冻结保护与 STOP

{len(before['workspace'])}个既有workspace文件（包括所有Stage4A R2、Stage4B RSSF、Stage4C、Stage5A R2A、Stage5B R1B/R1E、R3 evidence/authority、旧Human registration response及全部审阅材料）与1个原始外部Human cap response，逐文件hash before==after。新增文件全部在本轮review目录。source copy bytes与原始response一致。完整记录见FROZEN_HASH_VERIFICATION.json。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R1F_CREATED=false；Stage6_runs=0；R3_runs=0；retopo=false；production_authority_applied=false。

**STOP — WAITING FOR HUMAN BOUNDARY REVIEW。BOUNDARY=UNRESOLVED；NEXT=MANUAL_CAP_BOUNDARY_REVIEW。**
'''
(OUT/'THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_REPORT.md').write_text(report,encoding='utf8')
req=['THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_REPORT.md','THUMB_DISTAL_CAP_BOUNDARY_REVIEW_R1_STATUS.json','CURRENT_CAP_BOUNDARY_FORENSIC.json','CAP_EXPANSION_VERTEX_CLASSIFICATION.json']+[f'CAP_BOUNDARY_CANDIDATE_{k}.json' for k in 'ABCDE']+['CAP_BOUNDARY_CANDIDATE_COMPARISON.json','V882_BOUNDARY_FORENSIC.json','THUMB_DISTAL_CAP_BOUNDARY_REVIEW.html']
assert all((OUT/n).exists() for n in req)
assert sha(OUT/'HUMAN_CAP_AUTHORITY_RESPONSE_R1_SOURCE_COPY.json')==FORE['human_response_sha256']
dump('OUTPUT_VERIFICATION.json',{'required_files':{n:sha(OUT/n) for n in req},'required_pngs':{n:sha(OUT/'renders'/n) for n in required_png},
    'candidate_topology_and_membership_checks':'PASS','source_native_hash_check':'PASS','Human_response_original_and_copy_match':True,
    'interactive_UI_verification':ui,'six_native_views_and_forensic_visually_checked':True,
    'region_identity_unchanged':True,'old_cap9_remains_invalid':True,'authority_applied':False,'all_frozen_hashes_before_equals_after':True,
    'STOP':'WAITING_FOR_HUMAN_BOUNDARY_REVIEW'})
print(json.dumps({'protected_workspace_files':len(before['workspace']),'protected_external_response_count':len(before['external']),
    'hashes_unchanged':True,'recommendation':'E_FOR_HUMAN_ONLY','BOUNDARY':'UNRESOLVED','NEXT':'MANUAL_CAP_BOUNDARY_REVIEW',**ZERO,'STOP':True}),flush=True)
