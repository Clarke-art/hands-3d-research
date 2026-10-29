from pathlib import Path
import sys, json, hashlib
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(r'<HANDS_ROOT>')
OUT=ROOT/'production_spec/stage5_production_rig/stage5b_r1e_cap_boundary_e_five_vertex_adjudication_r1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before=read('FROZEN_HASHES_BEFORE.json')
workspace_records=[];external_records=[]
for rel,s in before['workspace'].items():
    p=ROOT/rel;t=sha(p) if p.is_file() else None
    workspace_records.append({'path':rel,'before_sha256':s,'after_sha256':t,'equal':s==t})
for path,s in before['external'].items():
    p=Path(path);t=sha(p) if p.is_file() else None
    external_records.append({'path':path,'before_sha256':s,'after_sha256':t,'equal':s==t})
new_outside=[]
for p in ROOT.rglob('*'):
    if p.is_file() and '.git' not in p.relative_to(ROOT).parts and not p.is_relative_to(OUT):
        if str(p.relative_to(ROOT)) not in before['workspace'] and p.relative_to(ROOT).as_posix() not in before['workspace']:
            new_outside.append(str(p.relative_to(ROOT)))
assert all(x['equal'] for x in workspace_records+external_records)
assert not new_outside
assert not list(OUT.rglob('*.blend')) and not list(OUT.rglob('*.blend1'))
hashes={'status':'PASS','all_preexisting_workspace_files_before_equal_after':True,
 'workspace_file_count':len(workspace_records),'external_original_response_file_count':len(external_records),
 'new_files_outside_authorized_review_directory':new_outside,'workspace':workspace_records,'external':external_records,
 'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,
 'scope':'All existing files, including production, prior review evidence, R3 authority/evidence and Human responses; only new review output excluded'}
dump('FROZEN_HASH_VERIFICATION.json',hashes)
C=read('E_BASELINE_FIVE_VERTEX_CONTEXT.json');A=read('E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json')
D=read('FIVE_VERTEX_INDIVIDUAL_FORENSIC.json');V=read('E_FIVE_VERTEX_VARIANT_ANALYSIS.json')
E=read('NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json');B=C['baseline'];F=A['final']
sys.path.insert(0,str(OUT/'scripts'))
from e_geometry import F as NATIVE_FACES, ED, NF
face_union=sorted({v for fi in E['face_ids'] for v in NATIVE_FACES[fi]})
counts=Counter(tuple(sorted((a,b))) for fi in E['face_ids'] for a,b in zip(NATIVE_FACES[fi],NATIVE_FACES[fi][1:]+NATIVE_FACES[fi][:1]))
boundary=sorted(e for e,n in counts.items() if n==1)
assert face_union==E['vertex_ids']
assert boundary==sorted(tuple(sorted(e)) for e in E['boundary_edges'])
assert [list(sorted(ED[i])) for i in E['boundary_edge_ids']]==E['boundary_edges']
assert E['vertex_ids']==B['vertex_ids'] and E['face_ids']==B['face_ids']
assert not A['added_or_removed_non_disputed_vertices']
assert F['manifold_disk'] and F['closed_loop_count']==1 and F['connected_component_count']==1
assert not F['nonmanifold_edges'] and not F['nonmanifold_vertex_links'] and not F['boundary_bad_degree_ids']
assert A['local_spike_notch_clear'] and F['nail_margin_edge_preserved']
assert V['five_independent_requested_test_records']==5 and len(V['necessary_combination_consistency_checks'])==1
assert not V['five_bit_subset_enumeration_performed'] and not V['boundary_family_redesign']
assert E['human_final_approval'] is None and not E['authority_freeze_performed'] and not E['production_authority_applied']
assert sha(Path(C['human_boundary_response_path']))==sha(OUT/'HUMAN_BOUNDARY_RESPONSE_SOURCE_COPY.json')
assert read('UI_VERIFICATION.json')['status']=='PASS'
status={'execution':'CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1','mode':'READ_ONLY_FIVE_VERTEX_ONLY',
 'E_FINAL':'READY_FOR_HUMAN_CAP_AUTHORITY_FREEZE','NEXT':'HUMAN_CAP_AUTHORITY_FREEZE',
 'next_condition':'Human answers Q1–Q7 of this five-vertex review; no automatic freeze or application',
 'region_identity':'ACCEPTED_UNCHANGED','old_cap9':'INVALID_INHERITED_FINDING_NOT_REOPENED',
 'E_baseline_vertices':37,'E_baseline_faces':25,'E_FINAL_vertices':37,'E_FINAL_faces':25,
 'five_vertex_decisions':E['five_vertex_decisions'],'baseline_final_membership_identical':True,
 'human_final_approval':None,'Human_five_vertex_response_generated':False,'authority_freeze_performed':False,
 'production_authority_applied':False,'boundary_authority_applied':False,
 'R1F_CREATED':False,'Stage6_runs':0,'R3_runs':0,'strict_bound_recalculations':0,'retopology_performed':False,
 'BLEND_FILES_WRITTEN':0,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,
 'frozen_hashes_status':'PASS','preexisting_workspace_files_frozen':len(workspace_records),
 'external_original_Human_responses_frozen':len(external_records),'STOP':'WAIT_FOR_HUMAN_FIVE_VERTEX_REVIEW'}
dump('CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1_STATUS.json',status)
notes=C['Human_authority_verbatim']['answers']['notes']
rows=D['vertices']
table='\n'.join(f"| v{r['vertex_id']} | {r['decision']} | {r['geodesic_from_v284_mm']:.6f} | {r['euclidean_tip_distance_mm']:.6f} | {r['axial_depth_from_tip_mm']:.6f} | {r['circumferential_angle_deg']:.3f} | {r['nail_relation']} |" for r in rows)
reasons='\n\n'.join(f"**v{r['vertex_id']} — {r['decision']}**. {r['reason']}" for r in rows)
metrics='\n'.join(f"| {name} | {B[key]:.6f} | {F[key]:.6f} |" for name,key in [('Max geodesic (mm)','max_geodesic_mm'),('Boundary axial spread (mm)','boundary_axial_spread_mm'),('Area (mm²)','surface_area_mm2'),('Perimeter (mm)','boundary_perimeter_mm')])
variants=[]
for t in V['individual_tests']:
    m=t.get('metrics') or (t.get('conditional_minimum_face_closure') or {}).get('metrics')
    if m:
        variants.append(f"- v{t['vertex_id']}: {m['vertex_count']} vertices / {m['face_count']} faces; perimeter {m['boundary_perimeter_mm']:.6f} mm; axial spread {m['boundary_axial_spread_mm']:.6f} mm; component/loop {m['connected_component_count']}/{m['closed_loop_count']}; new concave-notch proxies {m['new_notch_proxy_vertex_ids']}." )
    else:variants.append(f"- v{t['vertex_id']}: KEEP is non-viable within the authorized five-vertex scope; no unsupported vertex-only membership or out-of-scope face patch constructed.")
report=f'''# CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1

E_FINAL = **READY_FOR_HUMAN_CAP_AUTHORITY_FREEZE**，仅表示五点审阅材料与工程自检完成。Human 本轮 Q1–Q7 未答；未执行 freeze，未应用 production authority。建议 v1453/v2785/v2790 REMOVE，v297/v298 KEEP；E_FINAL 与 Human-selected E baseline 完全一致：37 vertices / 25 faces。

## Binding Human input

先读取原始 `{C['human_boundary_response_path']}`，SHA-256 `{C['human_boundary_response_sha256']}`。本目录 SOURCE_COPY 为逐字节副本。Q1=YES，Q2=YES，Q3=NO，Q4=NO，Q5=YES，Q6=E，Q7=APPROVE_WITH_MINOR_BOUNDARY_FIX。以下 Human notes 原文保留为 binding input；其中既有比较没有在本轮重新计算：

> {notes}

region identity = ACCEPTED_UNCHANGED；E = SELECTED_HUMAN_BASELINE；old cap9 = INVALID（既有结论未重审）。仅五点进入本轮裁决；其它 E membership 冻结。未读取 A/B/C/D 候选文件，未设计新 boundary family，未重开 seed/branch/48-point identity、R3、first web、CMC cage、RSSF。

## Native evidence and method

NATIVE_PRE_RSSF_STAGE4A_R2，原始 blend SHA-256 `{E['native_mesh_sha256']}`；仅使用已保存 native 世界坐标、原始面/边及冻结 native independent THUMB partition。未运行 Blender。approved nail mask 不变；IP 是沿用的 native engineering estimate，IP→v284 axis 不变。

逐点记录 native XYZ、THUMB、seed edge-graph surface geodesic 及最短路径、Euclidean tip distance、IP 距离/轴投影、周向角/轴半径、area-weighted normal、1-ring/2-ring、incident faces、nail membership/proximity、normal curvature proxy 和带拟合残差的 2-ring quadratic curvature。详细记录见 FIVE_VERTEX_INDIVIDUAL_FORENSIC.json。

所有五点均 >9 mm；没有使用 >9 REMOVE 或 <9 KEEP 规则。geodesic 是 native THUMB induced edge graph 路径约定，不是连续曲面最短路径。圆润且朝向 tip 的 bulb-side 表面证据不会自动成为 cap membership；本轮判断 cap 的周向边界及合法 selected-face 支持。曲率、转角和内角阈值都是工程代理，不能独立充当解剖 authority。

| Vertex | Proposal | Geodesic mm | Euclidean tip mm | Axial depth mm | Circumferential angle deg | Nail relation |
|---|---|---:|---:|---:|---:|---|
{table}

全部五点沿用 THUMB identity；正的 tip-axis normal 分量及曲面证据未显示明确 shaft 信号。v1453/v2785 是 NAIL_ADJACENT；其它三点 NOT_NAIL_RELATED；五点均不在 approved distal nail-margin edge v37–v879，接近 nail 不构成 KEEP 理由。

## Individual adjudication

REMOVE 仅表示不进入 cap membership，原始模型顶点保持存在。

{reasons}

v1453：E 原边界在 v1382/v341 的 turn 为 22.887°/12.272°，没有清楚的 terminal-corner notch。最小合法加入 face1220 虽恢复一些 rounded skin，却形成面尺度外凸 tab 和两个凹角；不能据此认定 E 有缺口。

v2785/v2790：不把这些点重新归类为 shaft 或否定已接受的 distal region identity。v2785 的合法加入与 v1453 耦合；v2790 无法获得五点范围内的 selected-face 支持。因此它们的排除基于 boundary/face consistency，而非仅凭距离或“expansion tail”名称。

v297/v298：E 的 axial-face selection 纳入 face1942/1944，角点虽都超过 9 mm，仍提供圆润周向边界补全。删除后闭环依然存在，故它们不是维持拓扑闭环的必要点；KEEP 的依据是避免局部凹口。未为“为何仅 E 有”重开其它 family。

## Five independent tests and one necessary coupling check

5 个 requested independent test records，3 个 unique feasible hypothetical patches，只有一次必要 face1220 coupling check；未搜索 2^5 组合。所有假设仅存在于新审计数据。

v1453/v2785 的严格单点 add-one 都不能形成合法面。face1220=[341,1382,2785,1453] 是仅有五点范围内合法支持，需两点同时进入；分别的单点报告标注这一约束，并共用最小 coupling patch。该 patch 是 39v/26f，仍为单 disk/loop，却新增 v1382/v341 凹角（intrinsic interior 281.477°/260.463°），perimeter 增加 8.693155 mm，axial spread 增加 0.222507 mm。

v2790 四个 incident faces 全部要求未获授权的额外顶点；最近 face1243=[1450,2790,1342,285] 也需要 v1342。本轮禁止新增其它点，故报告 NON_VIABLE_KEEP_WITHIN_FIVE_VERTEX_SCOPE，不能伪造 unsupported KEEP vertex，也没有构造越界 patch。

v297 leave-one-out 仅移除 selected face1942；v298 仅移除 face1944。均保留其余已接受 E 顶点，仍连通闭环/manifold disk，但分别产生 v2965/v2966 凹口（intrinsic interior 279.457°/266.588°）。

{chr(10).join(variants)}

## E baseline versus E_FINAL and face-level consistency

| Metric | Baseline | E_FINAL |
|---|---:|---:|
| Vertices | 37 | 37 |
| Faces | 25 | 25 |
{metrics}
| Boundary edges / vertices | 22 / 22 | 22 / 22 |
| Connected components / closed loops | 1 / 1 | 1 / 1 |
| Euler characteristic | 1 | 1 |
| Nonmanifold edges / vertex links | 0 / 0 | 0 / 0 |

face union = final vertex membership；native edge IDs 与端点逐项一致；boundary = selected face incidence 1 的边；boundary 顶点 degree 全部 2。KEEP297/298 均有 selected-face 支持，三个 REMOVE 点均无 selected membership。其它 E 顶点零改动，faces/vertices/boundary 均与 baseline 相同。

每个 boundary 点记录 3D tangent turn、selected-face intrinsic angle sum、normal-angle/edge-length curvature discontinuity、turn curvature、入/出边长及 degree。局部角 sum >240° 为 concave notch proxy，<60° 为 narrow spike proxy。五点及其 1-ring 中 E_FINAL 无该类 spike/notch；所有 baseline smoothness 数值原样保留，无其它区域重审。边界是 native polygon edge 近似，不宣称光滑解析曲线。

Self-check：单 connected patch YES；单 closed boundary YES；non-manifold incidence 0；region identity unchanged YES；没有新增 proximal overreach（本轮五点范围，并沿用 Human E baseline）；nail coherent YES（edge37–879 保留）；五点邻域无 local spike/notch。上述检查使审阅包 READY；Human 仍需判断 boundary 的视觉合理性。

## Human review and outputs

打开 [CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html](CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html)。六个 native closeups：DORSAL/PALMAR/RADIAL/ULNAR/THUMB_SIDE/TIP，及统一 contact sheet，所有图都标出五个 ID。仅显示 E baseline、E_FINAL 和五点裁决，保留 approved nail/IP/v284 context。蓝虚线与绿相位线区分完全重合的 baseline/final；红 REMOVE / 绿 KEEP 点仍位于原 native mesh。彩色 evidence 为 X-ray 投影，灰色 mesh 深度显示；隐藏表面不会被冒充前表面。TIP 中 IP/seed 沿轴投影重合，页面明确标注。

Q1–Q5 各点 KEEP/REMOVE；Q6 YES/NO/UNRESOLVED；Q7 APPROVE_FOR_FREEZE/REJECT/UNRESOLVED。答案初始全空，不预填 Human 判断。网页只下载本地 response；与展示 proposal 不同的回答明确记录 mismatch，不自动修改 membership 或 authority。UI 检查 PASS：六 view、每 view 五标记、四 layer 开关、七题/选项、空提交阻止、无 script error；未生成 Human response。

主要 evidence：E_BASELINE_FIVE_VERTEX_CONTEXT.json；FIVE_VERTEX_INDIVIDUAL_FORENSIC.json；E_FIVE_VERTEX_VARIANT_ANALYSIS.json；NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json；E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json；NATIVE_FIVE_VERTEX_VIEW_METADATA.json；UI_VERIFICATION.json；OUTPUT_VERIFICATION.json；FROZEN_HASH_VERIFICATION.json；STATUS.json 及 renders/ 六张图/contact sheet。脚本位于本轮 scripts/，均未触及既有文件。

## Freeze preservation and STOP

{len(workspace_records)} 个既有 workspace 文件和 {len(external_records)} 个外部原始 Human response SHA-256 before == after。包含 Stage4A R2 / Stage4B RSSF / Stage4C / Stage5A R2A / Stage5B R1B / Stage5B R1E / R3 authority/evidence / Human registration、cap authority、boundary response；完整逐文件记录在 FROZEN_HASH_VERIFICATION.json。新文件仅在本审阅目录。

BLEND_FILES_WRITTEN=0；WEIGHT_DELTA=0；GEOMETRY_DELTA=0；TOPOLOGY_DELTA=0；BONE_DELTA=0；JOINT_DELTA=0；R1F_CREATED=false；Stage6_runs=0；R3_runs=0；strict_bound_recalculations=0；retopology=false。

NEXT=HUMAN_CAP_AUTHORITY_FREEZE，须先收到并核对本页 Human 五点/边界回答。本轮到此 STOP，等待 Human。production authority applied=NO，freeze performed=NO。
'''
(OUT/'CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1_REPORT.md').write_text(report,encoding='utf-8')
required=['CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1_REPORT.md','CAP_BOUNDARY_E_FIVE_VERTEX_ADJUDICATION_R1_STATUS.json',
 'E_BASELINE_FIVE_VERTEX_CONTEXT.json','FIVE_VERTEX_INDIVIDUAL_FORENSIC.json','E_FIVE_VERTEX_VARIANT_ANALYSIS.json',
 'NATIVE_THUMB_DISTAL_CAP_CANDIDATE_E_FINAL.json','E_FINAL_BOUNDARY_TOPOLOGY_AUDIT.json','CAP_BOUNDARY_E_FIVE_VERTEX_REVIEW.html',
 'FROZEN_HASH_VERIFICATION.json','UI_VERIFICATION.json']
required += ['renders/E_FIVE_VERTEX_'+n+'_CLOSEUP.png' for n in ['DORSAL','PALMAR','RADIAL','ULNAR','THUMB_SIDE','TIP']]
required += ['renders/E_FIVE_VERTEX_NATIVE_MULTIVIEW_CONTACT_SHEET.png']
assert all((OUT/n).is_file() and (OUT/n).stat().st_size for n in required)
dump('OUTPUT_VERIFICATION.json',{'status':'PASS','required_outputs':[{'path':n,'sha256':sha(OUT/n)} for n in required],
 'face_vertex_boundary_consistency':True,'five_vertex_scope_only':True,'unchanged_E_final':True,
 'five_individual_test_records':5,'necessary_combination_checks':1,'unique_hypothetical_patches':3,
 'v2790_KEEP_face_support':'NON_VIABLE_WITHIN_AUTHORIZED_SCOPE','human_original_copy_byte_identical':True,
 'no_prior_candidate_family_reopened':True,'native_only':True,'approved_nail_unchanged':True,
 'six_views_plus_contact_sheet':True,'UI':'PASS','human_answers_blank':True,'freeze_or_production_application':False,
 'production_and_prior_evidence_hashes':'PASS','STOP':True})
print(json.dumps({'status':'PASS','decisions':E['five_vertex_decisions'],'frozen_workspace':len(workspace_records),
 'frozen_external':len(external_records),'READY':True,'production_applied':False,'STOP':True}))
