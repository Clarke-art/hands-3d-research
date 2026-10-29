"""Verify output consistency and frozen files; never apply Human authority."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from html.parser import HTMLParser
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
NAME='PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append({'name':n,'passed':True})
V=read(OUT/'REVIEW_VIEW_DATA.json');F=V['faces'];E=V['edges']
expected={'P02':[1372,1375],'P03':[1373,1374],'P04':[1368,1371],'P05':[1369,1370],'P06':[1378,1377]}
ck('exact five rows',V['row_faces']==expected)
vf={};ef={}
for f,vs in enumerate(F):
 for v in vs:vf.setdefault(v,set()).add(f)
 for x,y in zip(vs,vs[1:]+vs[:1]):ef.setdefault(tuple(sorted([x,y])),set()).add(f)
patch=read(OUT/'LOCAL_FACE_PATCHES_R1.json')
ck('scope union 28 direct faces',len(patch['analysis_scope_face_ids'])==28 and set(patch['analysis_scope_face_ids'])==set(V['local_context_faces']))
ck('guard rows no new stop',set(V['guard_rows'])=={'P01','P07'} and patch['guards_are_context_only_not_stop_candidates'])
for p in patch['patches']:
 ids=p['focus_face_ids'];vids={v for f in ids for v in F[f]}
 ck(p['row']+' exact quad focus',ids==expected[p['row']] and all(len(F[f])==4 for f in ids))
 ck(p['row']+' direct fan independently rebuilt',set(p['direct_incident_face_ids'])==set.union(*(vf[v] for v in vids)) and len(p['direct_incident_face_ids'])==12)
 ck(p['row']+' no recursive growth',p['no_recursive_growth'])
ck('all analysis fan faces are quads',all(len(F[f])==4 for f in patch['analysis_scope_face_ids']))
roles=read(OUT/'PROXIMAL_EXACT_FACE_ROLE_MAP_R1.json')
ck('ten exact faces only',len(roles['faces'])==10 and {q['face_id'] for q in roles['faces']}=={f for fs in expected.values() for f in fs})
for q in roles['faces']:
 ck('face '+str(q['face_id'])+' role and exact questions',q['surface_role']=='AMBIGUOUS' and len(q['exact_face_questions'])==5 and q['face_id'] in expected[q['row']])
flow=read(OUT/'LOCAL_SURFACE_FLOW_R1.json')
ck('no scalar extrema or normal-sign semantic assignment',flow['new_scalar_extrema_computed'] is False and flow['no_anatomical_role_from_normal_sign'])
for s,rows in flow['states'].items():
 Q=np.array(V['vertices'][s])
 ck(s+' five flow rows',len(rows)==5)
 for row in rows:
  ck(s+row['row']+' exact two lanes',row['faces']==expected[row['row']] and len(row['lane_flows'])==2)
  for lane in row['lane_flows']:
   n=np.array(lane['normal']);t=np.array(lane['longitudinal_surface_tangent'])
   ck(s+str(lane['face_id'])+' unit tangent in surface plane',np.isclose(np.linalg.norm(n),1) and np.isclose(np.linalg.norm(t),1) and abs(n@t)<1e-9)
   for tr in lane['transports']:
    R=np.array(tr['minimal_rotation_matrix']);a=tr['from_face_id'];b=tr['to_face_id'];edge=tr['shared_edge_id']
    ck(s+str(a)+'→'+str(b)+' real shared edge',{a,b}<=ef[tuple(sorted(E[edge]))] and set(E[edge])==set(tr['shared_edge_vertex_ids']) and a in patch['analysis_scope_face_ids'] and b in patch['analysis_scope_face_ids'])
    ck(s+str(a)+'→'+str(b)+' proper rotation',np.allclose(R.T@R,np.eye(3),atol=1e-9) and np.isclose(np.linalg.det(R),1))
    ck(s+str(a)+'→'+str(b)+' transport normals and tangent',np.allclose(<REDACTED_EMAIL>(tr['source_normal']),tr['target_normal'],atol=1e-9) and np.allclose(<REDACTED_EMAIL>(tr['source_longitudinal_tangent']),tr['transported_tangent'],atol=1e-9))
comparison=read(OUT/'THREE_BOUNDARY_ROLE_CHANGE_COMPARISON.json')
fixed={'A':([1375,1374],[[1518,293],[386,1518]],[[1373,1368],[1374,1371]]),'B':([4666,4668],[[1444,2822],[1520,2822]],[[1368,1369],[1371,1370]]),'C':([1376,1377],[[294,1519],[1519,385]],[[1369,1378],[1370,1377]])}
ck('only ABC and D unresolved',len(comparison['candidates'])==3 and comparison['fourth_boundary_not_added'] and comparison['machine_unique_candidate']=='NONE')
for c in comparison['candidates']:
 ids,verts,trans=fixed[c['option']];bs=c['boundary_edges']
 ck(c['option']+' exact original boundary',([x['edge_id'] for x in bs],[x['vertex_ids'] for x in bs],[[x['before_face_id'],x['after_face_id']] for x in bs])==(ids,verts,trans))
 ck(c['option']+' no role proof or premature exclusion',not c['ROLE_CHANGE_PROVEN'] and c['TOO_EARLY']=='UNRESOLVED' and c['TOO_LATE']=='UNRESOLVED')
for n in ['P02_EARLY_SIDE_CONTROL_AUDIT','P06_LATE_SIDE_CONTROL_AUDIT']:
 ck(n+' remains unproven',read(OUT/(n+'.json'))['result']=='FAIL')
ck('new P02 rule allows broader influence','NOT required' in read(OUT/'P02_EARLY_SIDE_CONTROL_AUDIT.json')['new_rule_applied'])
refs=read(OUT/'ANATOMICAL_REFERENCE_EVIDENCE.json')
for r in refs['sources']:
 if 'local_path' in r:ck(r['id']+' licensed frozen local reference hash',sha(ROOT/r['local_path'])==r['sha256'] and r['license']=='CC BY-SA 4.0')
frame=read(OUT/'LOCAL_ANATOMICAL_REFERENCE_FRAME_R1.json')
ck('native corrected joint position not invented',frame['native_MCP_CMC_positions_not_inferred'] and frame['states']['NATIVE']['corrected_chain_world_m'] is None)
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.radios=[];self.scripts=[];self.external=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if tag=='input' and a.get('name')=='selected_option':self.radios.append(a)
  if tag in ['script','img'] and a.get('src','').startswith(('http:','https:')):self.external.append(a['src'])
html=(OUT/'PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW.html').read_text(encoding='utf8');parser=Parser();parser.feed(html)
ck('four selectable choices none checked',[a['value'] for a in parser.radios]==['A','B','C','D'] and all('checked' not in a and 'disabled' not in a for a in parser.radios))
ck('all required answer and view controls',{'native-canvas','rssf-canvas','display-boundary','zoom-scope','show-flow','Q1_P02_digit_web_acceptable','Q2_P06_broader_interface_acceptable','boundary-readout','Q4_native_RSSF_context_acceptable','Q5_approve_for_boundary_authority','notes','export-response','clear-response','response-preview'}<=parser.ids)
ck('self-contained assets and no answer persistence',not parser.external and 'localStorage' not in html and 'sessionStorage' not in html)
for p in sorted((OUT/'renders').glob('*.png')):
 with Image.open(p) as im:im.verify()
 ck(p.name+' valid PNG',True)
ck('nine scientific reference views',len(list((OUT/'renders').glob('*.png')))==9)
qa=read(OUT/'BROWSER_UI_VERIFICATION_R1.json');logic=read(OUT/'RESPONSE_LOGIC_VERIFICATION_R1.json')
ck('browser no preselection images loaded and clean reset',qa['initial_state']['selected']==0 and all(q['loaded'] for q in qa['initial_state']['images']) and qa['clear_and_view_change_state']['selected']==0 and qa['clear_and_view_change_state']['answers']==['']*4)
ck('four view switches acknowledged',len(qa['view_checks'])==4 and all(v['pressed']=='true' for v in qa['view_checks']))
ck('response logic meaningful negative checks passed',logic['passed'] and logic['check_count']>=21)
download=Path(r'<USER_HOME>\Downloads\AUTOMATED_UI_VALIDATION_NOT_HUMAN_2026-10-03T08-17-19-740Z.json')
downloaded=read(download)
ck('actual browser-downloaded QA JSON equals preview',downloaded==qa['export_preview'] and downloaded['response_kind']=='AUTOMATED_UI_VALIDATION_NOT_HUMAN' and downloaded['approved_for_boundary_authority'] is False)
dump('QA_DOWNLOAD_VERIFICATION_R1.json',{'qa_only':True,'is_human_response':False,'download_path':str(download),'sha256':sha(download),'preview_exact_match':True,'required_fields_present':True,'production_changes':False})
before=read(OUT/'FROZEN_HASHES_BEFORE.json')
after={'workspace':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts},'external':{p:sha(p) for p in before['external']}}
ck('all previously existing workspace and external files unchanged',before==after)
dump('FROZEN_HASHES_AFTER.json',after)
freeze={'before_equals_after':True,'workspace_files':len(before['workspace']),'external_files':len(before['external']),'changed_files':[],'added_workspace_files_outside_new_audit_directory':[],'protected':'All previously existing Stage4/Stage5/corrected rig/cap37/FIRST_WEB21/nail/CMC cage/distal stop/R2/R3/Stage6/Human response files are byte-identical.'}
dump('FROZEN_HASH_VERIFICATION_R1.json',freeze)
status=read(OUT/(NAME+'_STATUS.json'))
ck('final authorized Human gate',status['status']=='MACHINE_EVIDENCE_EXHAUSTED_HUMAN_ADJUDICATION_REQUIRED' and status['NEXT']=='HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION' and status['STOP'])
ck('all production deltas and run counts zero',all(status[k]==0 for k in ['WEIGHT_DELTA','GEOMETRY_DELTA','TOPOLOGY_DELTA','BONE_DELTA','JOINT_DELTA','R2_runs','R3_runs','skin_runs','Stage6_runs','BLEND_FILES_WRITTEN','Human_response_count']))
status.update(frozen_before_equals_after=True,static_verification_check_count=len(checks),response_logic_verification_check_count=logic['check_count'],browser_ui_verified=True,actual_JSON_download_verified=True,QA_download_is_not_Human_response=True)
dump(NAME+'_STATUS.json',status)
dump('STATIC_VERIFICATION_R1.json',{'passed':True,'check_count':len(checks),'checks':checks,'production_or_solver_executed':False,'Human_decision_recorded':False})
report=f'''# PROXIMAL_PARTIAL_CIRCUMFERENCE_SEMANTIC_BOUNDARY_AUTHORITY_R1

最终状态：**MACHINE_EVIDENCE_EXHAUSTED_HUMAN_ADJUDICATION_REQUIRED**。机器唯一候选为 NONE；在指定局部、真实拓扑与批准参考范围内，十张 exact face 的 anatomical role 仍为 AMBIGUOUS。NEXT = HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION；等待 Human 导出的 JSON，STOP。

## 范围与判定

只分析 P02–P06 的十张指定 face、直接 incident fans，以及每行一个 distal/proximal guard。P01/P07 仅为 guard context。五行直接 fan 的并集为 28 张原始 quad；每行直接 fan 为 12 张。全手坐标仅供视图定位，不计算全掌 role map，不沿链延伸，不加入第四条边界。

| 行 | Exact face IDs | 最终 exact role | 已有描述性支持与剩余缺口 |
|---|---|---|---|
| P02 | 1372 / 1375 | AMBIGUOUS | 成对 lanes、横向条带和 frozen web 方向提供 digit-web compatibility；两状态的主导 thumb wrapping 身份没有解剖注册。 |
| P03 | 1373 / 1374 | AMBIGUOUS | digit-web 支持与 morphology transition 并存；不能将转向自动升格为 broader-interface onset。 |
| P04 | 1368 / 1371 | AMBIGUOUS | 两 lane 连续存在，邻接 fan 没有独立批准的 broader sheet 身份。 |
| P05 | 1369 / 1370 | AMBIGUOUS | 既有 per-face 描述性场混合；normal sign 或极值不能裁定 anatomical role。 |
| P06 | 1378 / 1377 | AMBIGUOUS | post-reversal 只作已有描述，缺少正向 broader-interface 证明。 |

此表的 AMBIGUOUS 是逐面 anatomy authority 结论，不否认前轮的几何描述或 digit-web compatibility。JSON 逐面回答 thumb-local digit、web-facing flank、partial-circumference sector、broader palm/metacarpal/thenar interface 及其证据来源，并保留每面顶点、边、incident fan 和 immediate row。

P02 early control = FAIL，含义是主导 digit-web organization **未获机器认证**，不是已证实其属于 broader interface。本轮采用放宽后的新规则：允许 broader influence；没有将“无法排除 broader influence”本身当作失败原因。P06 late control = FAIL，因为正向 broader-interface 证据未建立，不能用“不像 digit”或 post-reversal 替代。

## Surface flow 与正向 broader 证据

LOCAL_SURFACE_FLOW_R1.json 保存 native/RSSF 每张 focus face 的原始面法向、incoming/outgoing transverse vector、面内 longitudinal tangent、沿真实 shared edge 的最小旋转搬运及 ordered vertex fans。搬运只连接原始相邻面；验证旋转正交、det=+1、法向与切向搬运一致。法向和切向用于表面组织描述，不产生 ownership 或阈值排名。

原始两 lanes 到所有固定 rows 仍成对连通。直接 fans 均为规则 quad continuation，没有独立批准的 thenar/palm sheet role 标签。每行检查五项正向 broader 条件：停止 thumb wrapping、跨越更宽掌/掌骨表面、两 lane 不再成对 digit-sector、fan 转入共享 sheet、独立 anatomical reference 证明该关系。没有一行同时取得所需正向证明。几何 pairing 的存在也不反向证明必然属于 digit。

部分 circumference 不要求闭合 ring；本轮明确审查 transverse wrapping、longitudinal branch、normal-field organization、frozen-web sector 关系和 broader-sheet 排除/主导组织。没有用完美圆柱或完整闭环作为必要条件。既有 widening 和 reversal 只保留出处，不计算任何新 scalar extrema，不用它们推荐 A/B/C。

## 三个固定候选

| Option | 固定边界 | 顶点对 | Exact face transitions | Role change proven | Too early / too late |
|---|---|---|---|---|---|
| A STOP_AFTER_P03 | e1375 / e1374 | [1518,293] / [386,1518] | 1373→1368 / 1374→1371 | NO | UNRESOLVED / UNRESOLVED |
| B STOP_AFTER_P04 | e4666 / e4668 | [1444,2822] / [1520,2822] | 1368→1369 / 1371→1370 | NO | UNRESOLVED / UNRESOLVED |
| C STOP_AFTER_P05 | e1376 / e1377 | [294,1519] / [1519,385] | 1369→1378 / 1370→1377 | NO | UNRESOLVED / UNRESOLVED |

三条均未被排除，均未证明 distal digit-web → proximal broader interface 的精确角色变化。D = KEEP_UNRESOLVED 不建立新的边界。机器证据在用户指定的局部 authority 问题上已用尽；一般 anatomical context 足够开展有范围的 Human review，因此不选择 INSUFFICIENT_ANATOMICAL_REFERENCE。

## Anatomy reference 的来源与限制

采用批准 corrected kinematic distal direction、批准 thumb nail dorsal、frozen FIRST_WEB21 四 seeds 与既有真实 strip、批准 RSSF MCP/CMC，以及独立 Stage4C wrist reference。旧 Stage4B cut-plane wrist 不作为此参考。方向轴均不等于 palm normal。既有 strip 是几何上下文，不是新增角色批准；CMC cage 不作为 hard ownership 来源。

Native 没有独立批准的 corrected MCP/CMC 位置注册。本页通过相同 frozen nail 顶点 IDs 的刚性方向拟合搬运 approved corrected distal orientation，拟合 RMS = {frame['states']['NATIVE']['native_nail_transport_fit_rms_mm']:.6f} mm；只搬运方向，不声称 native MCP/CMC 位置。精确 approved joint markers 出现在 RSSF companion。该限制在页面与 JSON 均可见。侧名是 thumb-local nail/web reference side，不是全掌表面标签。

先检查本地参考：AI canonical 图片和未注册模型缩略图不能作为真实 anatomy。采用已有 Sciencia58 真实手外观照片：背侧使用 male_both_sides 的右手 dorsal panel，掌侧使用 Hand female 5；CC BY-SA 4.0 授权和来源链接保留。照片为其他手，landmark registration 仍待 Human，不将其位置转换为本模型 face ID。来源：[Hand male both sides](https://commons.wikimedia.org/wiki/File:Hand_male_both_sides.jpg)、[Hand female 5](https://commons.wikimedia.org/wiki/File:Hand_female_5.jpg)。

仅补做一次针对 first-web/MCP/thenar 的来源查阅。Kapandji 的 indexed English abstract 支持 first-web 功能涉及 trapeziometacarpal、肌筋膜、web integument 与 thenar aponeurotic system，不能给出本 asset 的离散边界。[Functional anatomy of the first web space, 1986](https://pubmed.ncbi.nlm.nih.gov/3767503/)。2024 cadaver study 的 indexed abstract excerpt 支持外观形态不对称和 palmar-abduction 参考姿态相关；不能把 chain 当作完美圆柱或确定 A/B/C。[Measurement and observation of the first web space based on morphology and clinical applications](https://pubmed.ncbi.nlm.nih.gov/39084025/)。查阅日 2026-10-03；PubMed 直接访问遇 CAPTCHA，未绕过，未查 full text。术后 WashU 图片未作为正常 anatomy authority，也未嵌入重分发。

## Human Review 与验证

交付 PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_HUMAN_REVIEW.html：自包含、无 CDN，支持本地离线打开。native/RSSF 两个 viewer 可拖动、缩放、切换 palmar/dorsal/radial/ulnar、局部/冻结 context、IDs 和 flow。附九张科学图：三边界总览、A/B/C closeups、P02/P06 controls、两状态四视角和 frozen landmarks。

A/B/C/D 为真实可选 radio，均未预选；Q1/Q2/Q4/Q5 均为空，Notes 可填写，Q3 自动绑定原始 edges 和 face transitions。导出 JSON 具有 review_id、selected_option、Q1–Q5、notes、timestamp。D 导出 null 边界并保持未决。批准 A/B/C 需要 Q1/Q2/Q4 全为 YES。导出不应用 authority、不修改 production，不延伸角色或自动启动 solver。批准范围仅为 proximal semantic stop。

使用 computer-use 浏览器流程验证。空答复被阻止，A/B/C 的 Q3 IDs 与固定边对一致，D/UNRESOLVED 实际生成 JSON。浏览器 download-event 捕获 API 超时，但实际下载文件在本机 Downloads 中找到，并逐字段与浏览器预览完全相同；QA_DOWNLOAD_VERIFICATION_R1.json 记录其哈希。测试文件名及 response_kind 均明确为 AUTOMATED_UI_VALIDATION_NOT_HUMAN，approved_for_boundary_authority=false，不能作为 Human decision。正式页面已恢复无测试参数和空白答案，Human response count = 0。

页面第一次运行的 newline-escape JS 语法错误已通过 raw HTML template 修复，重新加载后双 viewer、表单与导出均运行。{logic['check_count']} 项 response logic 检查覆盖三边对、D/null、空答复、无效第四候选、矛盾批准、timestamp、Unicode 和生成 HTML 的 JS 解析；另有 {len(checks)} 项静态/拓扑/搬运/冻结一致性验证通过。浏览器截图记录空白选项与导出控件。

## 冻结与停止

既有 {len(before['workspace'])} 个 workspace 文件与 {len(before['external'])} 个外部输入文件全部 before == after；新增 workspace 文件仅位于本轮 audit 目录。所有既有 Stage4、Stage5、corrected rig、cap37、FIRST_WEB21、nail、CMC cage、distal stop evidence、R2/R3、Stage6、Human responses 均字节相同。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT_DELTA 全为 0；R2/R3/skin/Stage6 runs = 0；BLEND_FILES_WRITTEN = 0。

NEXT = HUMAN_PROXIMAL_PARTIAL_CIRCUMFERENCE_BOUNDARY_ADJUDICATION。等待 Human 导出 JSON；不再进入 scalar audit。STOP = YES。
'''
(OUT/(NAME+'_REPORT.md')).write_text(report,encoding='utf8')
manifest={'authority':NAME,'scope':'New audit evidence only; manifest excludes itself.','files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}}
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',manifest)
print(json.dumps({'passed':True,'checks':len(checks),'frozen_workspace_files':len(before['workspace']),'frozen_external_files':len(before['external']),'output_files':len(manifest['files']),'status':status['status'],'NEXT':status['NEXT'],'STOP':True},indent=2))
