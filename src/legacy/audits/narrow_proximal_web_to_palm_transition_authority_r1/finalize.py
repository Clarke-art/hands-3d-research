import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
NAME='NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf8'))
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
P=read('PROXIMAL_TRANSITION_LOCAL_PATCH_R1.json');S=read(NAME+'_STATUS.json');M=read('PROXIMAL_TRANSITION_ROW_EVIDENCE_MATRIX.json');C=read('PROXIMAL_STOP_NEIGHBOR_NEGATIVE_CONTROL_AUDIT.json')
checks=[]
def ck(n,v):
    assert v,n
    checks.append({'name':n,'passed':True})
ck('fixed five-row scope',P['row_ids']==['P02','P03','P04','P05','P06'])
ck('exact ten surface faces and eighteen vertices',len(P['focus_face_ids'])==10 and len(P['focus_vertex_ids'])==18)
ck('direct incident context has twenty-eight faces',len(P['direct_incident_face_ids'])==28)
for v,info in P['topology']['vertices'].items():
    fan=info['local_ordered_face_fan'];ck('v'+v+' regular closed local fan',info['valence']==4 and fan['closed_fan'] and set(fan['cyclic_face_ids'])==set(info['incident_face_ids']))
for state,d in P['states'].items():
    rr=d['rows']
    for r in rr:
        n=state+' '+r['row_id'];fr=r['frame']
        for key in ['longitudinal','transverse','surface_normal','orthonormal_longitudinal','orthonormal_transverse']:
            ck(n+' finite unit '+key,np.isfinite(fr[key]).all() and np.isclose(np.linalg.norm(fr[key]),1))
        ck(n+' orthonormal local frame',abs(np.dot(fr['orthonormal_longitudinal'],fr['surface_normal']))<1e-9 and abs(np.dot(fr['orthonormal_transverse'],fr['surface_normal']))<1e-9 and abs(np.dot(fr['orthonormal_transverse'],fr['orthonormal_longitudinal']))<1e-9)
        for sec in ['incoming','outgoing']:
            t=r['frontiers'][sec];pos=np.array([d['vertex_positions_world_m'][str(v)] for v in t['ordered_vertex_ids']]); ck(n+' '+sec+' exact chord',np.isclose(np.linalg.norm(pos[-1]-pos[0])*1000,t['chord_width_mm']));ck(n+' '+sec+' exact two-edge arc',np.isclose(np.linalg.norm(np.diff(pos,axis=0),axis=1).sum()*1000,t['partial_arc_width_mm']))
        for lane in r['lanes']:
            fi=lane['face_id'];info=P['topology']['faces'][str(fi)];ck(n+' original quad '+str(fi),len(info['vertex_ids'])==4)
            a=set(P['topology']['edges'][str(lane['incoming_edge_id'])]['vertex_ids']);b=set(P['topology']['edges'][str(lane['outgoing_edge_id'])]['vertex_ids']);ck(n+' opposite original edges '+str(fi),not a&b and a|b==set(info['vertex_ids']))
            coords=np.array([d['vertex_positions_world_m'][str(v)] for v in info['vertex_ids']]);normal=np.cross(coords,np.roll(coords,-1,axis=0)).sum(0);normal/=np.linalg.norm(normal);ck(n+' polygon normal independently recomputed '+str(fi),np.allclose(normal,lane['face_normal']))
        ck(n+' geometry references CMC-MCP only',r['thumb_chain_relation']['nearest_segment_index']==0)
        ck(n+' no invented palmar/thenar normal authority',r['surface_cues']['semantic_palmar_basis']=='UNAVAILABLE' and r['surface_cues']['semantic_thenar_basis']=='UNAVAILABLE')
    for a,b in zip(rr[:-1],rr[1:]):ck(state+' adjacent rows share exact edge pair '+a['row_id'],a['outgoing_edge_ids']==b['incoming_edge_ids'])
    signs=[r['frame']['longitudinal_dot_thumb_axis'] for r in rr];ck(state+' longitudinal reversal stable neighbourhood',signs[0]<0 and signs[-1]>0 and np.flatnonzero(np.array(signs)>0)[0]==(2 if state=='NATIVE' else 3))
    ck(state+' row-mean radial sign differs across P04/P05',rr[2]['frame']['normal_dot_chain_radial']>0>rr[3]['frame']['normal_dot_chain_radial'])
    facesigns=[a['normal_dot_own_face_centroid_radial'] for a in rr[3]['lanes']];ck(state+' P05 own-centroid face signs are mixed',min(facesigns)<0<max(facesigns))
for a in C['alternatives']:
    for e in a['edges']:ck(a['stop']+' e'+str(e['edge_id'])+' exact face incidence',set(e['incident_face_ids'])=={e['before_face_id'],e['after_face_id']})
ck('scorecard uses only categorical evidence states',all(r[k]['state'] in ['PRESENT','ABSENT','AMBIGUOUS'] for r in M['row_states'] for k in ['DIGIT_WEB_EVIDENCE','TRANSITION_EVIDENCE','PALM_INTERFACE_EVIDENCE']))
ck('no weighted score',M['no_weighted_total'])
ck('unique stop not fabricated',S['status']=='FAIL_CLOSED' and S['proposed_boundary']=='UNRESOLVED' and S['last_defensible_digit_web_row'] is None and S['first_defensible_broader_interface_row'] is None)
ck('neighbor alternatives honestly retained',not C['neighbor_stop_alternatives_rejected'] and len(C['alternatives'])==3)
for n in ['PROXIMAL_WEB_TO_PALM_BOUNDARY_EDGE_AUTHORITY_CANDIDATE.json','PROXIMAL_WEB_TO_PALM_TRANSITION_HUMAN_REVIEW.html','THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json','renders/PROPOSED_WEB_TO_PALM_BOUNDARY.png']:ck('conditional artifact withheld '+n,not (OUT/n).exists())
required=['P02_P06_TRANSITION_OVERVIEW','P03_P05_TRANSITION_CLOSEUP','ROW_LOCAL_FRAMES_NATIVE','ROW_LOCAL_FRAMES_RSSF','FRONTIER_SEPARATION_PROFILE','NORMAL_FIELD_TRANSITION','PARTIAL_CIRCUMFERENCE_VALIDITY','MCP_CMC_LOCAL_CONTEXT','P02_NEGATIVE_CONTROL','P06_NEGATIVE_CONTROL']
ck('ten required unconditional PNGs',{p.stem for p in (OUT/'renders').glob('*.png')}==set(required))
for n in required:
    with Image.open(OUT/'renders'/ (n+'.png')) as im:
        im.load();ck(n+' full resolution nonblank PNG',im.width>=2000 and im.height>=1400 and np.asarray(im).std()>10)
for p in OUT.glob('*.py'):
    tree=ast.parse(p.read_text(encoding='utf8'));imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):imports.extend(x.name.split('.')[0] for x in node.names)
        if isinstance(node,ast.ImportFrom):imports.append(node.module.split('.')[0])
    ck(p.name+' no solver, Blender, historical-script or network imports',set(imports)<={'sys','json','hashlib','pathlib','numpy','matplotlib','PIL','ast'})
ck('no blend or bytecode generated',not list(OUT.rglob('*.blend')) and not list(OUT.rglob('*.pyc')))
dump('STATIC_VERIFICATION_R1.json',{'status':'PASS','check_count':len(checks),'checks':checks,'semantic_authority_status':'FAIL_CLOSED','verification_pass_is_not_semantic_approval':True})
before=read('FROZEN_HASHES_BEFORE.json')
now={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
after={'workspace':now,'external':{p:sha(p) for p in before['external']}}
added=sorted(set(now)-set(before['workspace']));removed=sorted(set(before['workspace'])-set(now));changed={g:[p for p,h in before[g].items() if after[g].get(p)!=h] for g in before}
assert before==after and not added and not removed,'Frozen sources changed; cannot assert zero production delta'
dump('FROZEN_HASHES_AFTER.json',after)
freeze={'status':'PASS','before_equals_after':True,'workspace_file_count':len(now),'external_file_count':len(after['external']),'changed_files':changed,'added_outside_audit':added,'removed_outside_audit':removed,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0,'scope':'Every pre-existing workspace file including all production, previous audits, Human responses and external frozen/request files.'}
dump('FROZEN_HASH_VERIFICATION_R1.json',freeze);S['frozen_verification']=freeze;S['static_check_count']=len(checks);S['required_visual_count']=10;dump(NAME+'_STATUS.json',S)

table=[]
for i,n in enumerate(P['row_ids']):
    a=P['states']['NATIVE']['rows'][i];b=P['states']['RSSF']['rows'][i]
    def pair(fun):return f'{fun(a):.6f} / {fun(b):.6f}'
    table.append(f"| {n} | {' / '.join(map(str,a['face_ids']))} | {pair(lambda r:r['frontiers']['outgoing']['chord_width_mm'])} | {pair(lambda r:r['frontiers']['outgoing']['arc_chord_ratio'])} | {pair(lambda r:r['frame']['longitudinal_dot_thumb_axis'])} | {pair(lambda r:r['frame']['transverse_dot_circumferential'])} | {pair(lambda r:r['frame']['normal_dot_chain_radial'])} |")
facep05={s:[a['normal_dot_own_face_centroid_radial'] for a in d['rows'][3]['lanes']] for s,d in P['states'].items()}
rssfcirc=[r['frame']['transverse_dot_circumferential'] for r in P['states']['RSSF']['rows'][3:]]
matrix='\n'.join(f"| {r['row_id']} | {r['DIGIT_WEB_EVIDENCE']['state']} | {r['TRANSITION_EVIDENCE']['state']} | {r['PALM_INTERFACE_EVIDENCE']['state']} |" for r in M['row_states'])
edgetable='\n'.join(f"| {a['stop']} | e{a['edges'][0]['edge_id']} = {a['edges'][0]['vertex_ids']} | e{a['edges'][1]['edge_id']} = {a['edges'][1]['vertex_ids']} | {' / '.join(str(e['before_face_id'])+'→'+str(e['after_face_id']) for e in a['edges'])} | UNPROVEN |" for a in C['alternatives'])
summary=[(1,'P02 semantic state','DIGIT_WEB supported；negative-control certification unresolved'),(2,'P03 semantic state','DIGIT_WEB + morphology transition'),(3,'P04 semantic state','TRANSITION；role AMBIGUOUS'),(4,'P05 semantic state','TRANSITION；per-face own-centroid radial signs mixed；role AMBIGUOUS'),(5,'P06 semantic state','Post-reversal morphology；broader-interface role UNPROVEN'),(6,'last defensible digit-web row','UNRESOLVED'),(7,'first defensible broader-interface row','UNRESOLVED'),(8,'proposed boundary','UNRESOLVED'),(9,'left boundary edge ID','null；no authority candidate'),(10,'right boundary edge ID','null；no authority candidate'),(11,'partial-circumference validity stop','UNRESOLVED'),(12,'local-frame transition','UNRESOLVED'),(13,'normal-field evidence','AMBIGUOUS for semantic boundary'),(14,'frontier-separation evidence','AMBIGUOUS for semantic boundary'),(15,'P02 negative control','FAIL；required exclusion not proven'),(16,'P06 negative control','FAIL；required broader role not proven'),(17,'neighbor-stop alternatives rejected','NO'),(18,'native/RSSF same topological transition neighbourhood','YES；P03–P05 only'),(19,'surface-supported','YES；fixed ten original quads'),(20,'FIRST_WEB21 changed','NO'),(21,'cap37 changed','NO'),(22,'nail changed','NO'),(23,'authority status','FAIL_CLOSED'),(24,'Human Review page generated','NO'),(25,'R2 runs','0'),(26,'R3 runs','0'),(27,'Stage6 runs','0'),(28,'BLEND_FILES_WRITTEN','0'),(29,'NEXT',S['NEXT']),(30,'STOP','YES')]
dump('FINAL_SUMMARY_30_FIELDS.json',{'fields':[{'number':i,'field':k,'value':v} for i,k,v in summary]})
summ='\n'.join(f'| {i} | {k} | {v} |' for i,k,v in summary)
report=f'''# {NAME}

**FAIL_CLOSED；选择 D：仍无法唯一确定。** 固定 P02–P06 证据支持局部形态转向，但没有建立“最后 digit-web 行 / 第一 broader-interface 行”的唯一邻接对。最强几何提示为 P04/P05；它没有通过独立角色证据及 negative-control gates，不能升级为 authority candidate。

## 范围、输入和冻结约束

审查仅含 10 个指定原始 quad、18 个 incident vertices、28 个直接 vertex-incident faces。未递归追踪 neighbour，未建立 P07+ 搜索链；直接邻面中包含边界外的 incident faces，仅用于法向和局部 face fan。没有读取其更远 longitudinal profile。上一轮 trace/profile JSON 加载后立即筛选 P02–P06；旧脚本均未 import 或运行。

输入：经冻结 hash 校验的 READ_ONLY_LIVE_EXTRACTION.json，含 native/RSSF 原始坐标、相同 topology IDs 和 corrected RSSF chain。native 使用既有独立 native joint/axis evidence；它是 native 结构参照，不冒称有另一个已经应用的 corrected native rig。两状态用各自参照，绝对 chain arc 不被当成跨状态 anatomical equality。继承的 web/proximal-direction cue 只取上一轮对应五行；没有重新研究 distal/lateral/global domain。

FIRST_WEB21=FROZEN，hard pins=0；cap37=HUMAN_APPROVED_FROZEN；thumb nail=FROZEN；corrected rig=HUMAN_APPROVED/APPLIED_VERIFIED；CMC cage=GEOMETRY_PROTECTED/NOT OWNERSHIP HARD SOURCE。CORRECTED_COMMON_MM_SEMANTICS 保持 pending Human。没有 ownership labels、weights、nearest-digit winner、历史 thenar sphere 或 R3 输出作为 truth。

## Same-ID local patch 与可复算定义

每行记录 face/vertex/edge IDs、两侧 longitudinal frontier、incoming/outgoing 二段 section、world positions、polygon normals、直接 incident 面积加权 vertex normals、local L/T/N、orthonormal frame、chain/MCP/CMC 关系和 surface cues。normal 为 world-space Newell 面积向量，vertex normal 为直接 incident polygon 向量和的单位化；不是 Blender cached split normal。中心 radial direction 只用于方向投影，不输出或建立 tube radius/anchors。

L=outgoing 三顶点平均位置减 incoming 三顶点平均位置后单位化；T=两 section left→right 向量和后单位化；N=两面面积向量和后单位化。incoming/outgoing neighbour tangents 仅从本五行引用，窗口端外侧为 null。frame 同时保留原 L/T 和投影到 tangent plane 的 orthonormal L/T。

下表数值均为 **native / RSSF**；宽度为 mm，dots 为方向分量。

| Row | Faces | outgoing chord | arc/chord | L·axis | T·circ | mean N·radial |
|---|---|---|---|---|---|---|
{chr(10).join(table)}

## E1–E6 的独立核查与限制

**E1 longitudinal turn：** native 首次 sign reversal 为 P03/P04；RSSF 为 P04/P05。四段 tangent turns：native 17.842/23.740/26.446/22.678°，RSSF 17.172/22.664/28.346/24.446°。最大采样 turn 在 P04/P05，但没有 degree threshold，也不把 sampled maximum 视为 semantic authority。

**E2 frontier separation：** native chord 8.552→8.912→9.471→10.074→10.023 mm；RSSF 8.431→8.766→9.313→9.948→9.933 mm。P02→P05 分别增宽约 17.80% / 17.99%；随后小幅收缩。arc/chord 全程约 1.006–1.031。该带宽变化是真实 surface widening，却没有离散的两侧 fan-out/fusion 事件。局部近直的两条 edges 既可能属于 digit-sector，也可能属于 broader interface，不能单独选 P05 或 P04。

**E3 partial circumference：** 两条 face columns 不被解释为完整环。P04/P05 出现同状态 area-mean N·radial 正→负，属于共同几何提示。不过以每一 face 自己的 centroid radial 复核，P05 两种状态都混合：native face1369 {facep05['NATIVE'][0]:+.6f}、1370 {facep05['NATIVE'][1]:+.6f}；RSSF face1369 {facep05['RSSF'][0]:+.6f}、1370 {facep05['RSSF'][1]:+.6f}。RSSF P05/P06 的 T·circ 仍为 {rssfcirc[0]:.6f} / {rssfcirc[1]:.6f}。native P02 的 vertex317 径向 vertex-normal dot 已为负；以“所有法向都须朝 radial outward”作语义规则会使早端 control 先失效。kinematic chain 没有被批准为圆柱 surface axis；mean sign、per-face sign、vertex sign 不能互相替代。因此“columns4–6 在哪行之后不再是 thumb-local partial sector”仍 UNRESOLVED。

**E4 normal field：** normal turn 连续：native 22.112/22.433/19.549/12.476°；RSSF 21.720/24.125/21.866/13.030°。web cue native 从 0.843→−0.210，RSSF 从 0.956→0.534；不要求同一个 scalar 在同一行翻转。但局部 flank-normal agreement 在 P02 已为 0.993/0.992，全程约 0.971–0.998，无法作为只在 later rows onset 的 broader-interface discriminator。没有把 CMC direction/proximal proxy 命名成 anatomical palmar/thenar normal basis，也没有因负 palm-proxy dot 宣称“不是 palm”。

继承的 web/proximal cue 使用上一轮 equal-weight face-normal mean；本轮重新计算的 field 使用 area-weighted mean，JSON 和图表明确标为 inherited，不能当成同一新 N 的严格分量。继承 thenar-facing direction 是先前 v794 方向 proxy，不等同于本轮 corrected-chain CMC head direction。它们只保留描述性上下文，均没有成为本轮独立 role authority。

**E5 local frame：** 窗口内所有行均有非退化 surface frame，随 row 平滑旋转。P04/P05 的转动最大并不证明角色刚在该边转换；P05 的 lane 差异和 P02 的 state discrepancy 都阻止 frame scalar 自行获得 authority。local frame transition 的准确语义边界 UNRESOLVED。

**E6 MCP/CMC：** 所有 row centre 的最近 thumb reference segment 都是 CMC→MCP（segment0），不存在本窗口中的 chain-segment switch。MCP/CMC distance、offset、direction 均逐行记录；这些只表述位置，不以“越过 MCP”或 CMC cage 来决定 role。当前片带到 metacarpal/thenar/palm 的具体 anatomical fusion 没有独立局部表面证明。

## Row evidence matrix

PRESENT 表示有该方向的证据，不等于 membership 被批准。缺少排除证据记 AMBIGUOUS，不记 ABSENT；没有加权总分。

| Row | DIGIT_WEB_EVIDENCE | TRANSITION_EVIDENCE | PALM_INTERFACE_EVIDENCE |
|---|---|---|---|
{matrix}

P02 保留较强 web-facing 与 digit-side continuation 支持；P03 仍有 digit-web 支持并进入 morphology transition；P04 为双状态转向窗口；P05 已有径向 orientation 变化但逐面混合；P06 为 post-reversal morphology，仍缺少 positive broader-interface role certification。

## Negative controls 与真实 edge alternatives

**P02=FAIL（required exclusion 未证）**：它不像 P05/P06 的后续转向状态，但 proposed broader-context proxy——与 flank normal 对齐——从 P02 就已同样强。不能因此证明候选前一侧一定独立于 broader interface。FAIL 不把 P02 反向标成 palm。

**P06=FAIL（required broader role 未证）**：它已经 post-reversal，且两 face 的 own-centroid N·radial 都为负；仍没有积极表面角色证据证明它“已经太晚”。RSSF 中的 circumferential/web cue 仍存在。FAIL 不宣称它完整保持 digit-web，也不扩展到 P07。

所有 18 个 patch vertices valence4；每行 vertex-incident face union=12；28 个直接邻面均为 quads。每个 incident vertex 的 4 面 cyclic fan 和 shared-edge sequence 已记录，均无本窗口独有的 pole、branch 或 fan event。该结果只作辅助；没有用 graph connectivity 作 authority。

以下是三个 **未被排除的真实边对**，不是批准候选；cross-strip boundary edges 与 longitudinal frontier edges 分开记录。

| Stop alternative | Left boundary edge / vertices | Right boundary edge / vertices | Incident face transition | semantic authority |
|---|---|---|---|---|
{edgetable}

STOP_AFTER_P03：native turn 跨该 cut；RSSF P04 仍未 reversal，没有证明 P04 是首行 broader-interface。STOP_AFTER_P04：共同 mean radial sign 与最大 tangent turn 是最强提示；但 P05 两状态逐面仍混合，positive broader-interface onset 未证。STOP_AFTER_P05：P06 后续转动和 P05 最大 chord 无法证明 P05 是最后 web 行。这三者不是同样已批准的 boundaries；它们是三个仍不能排除的裁切位置。**neighbor alternatives rejected=NO**。

native/RSSF 确实共享 P03–P05 stable topology neighbourhood；这满足窗口稳定性，不满足唯一语义 stop。surface-supported=YES 仅针对原始十个 quads。

## 输出、核验和唯一 NEXT

10 张要求的无条件证据图已经生成。没有 boundary-candidate JSON、proposed-boundary PNG、Human Review HTML 或 role extension，因为唯一 candidate 未成立。没有把无候选的裁决问题发给 Human 当作批准页面。

{len(checks)} 项静态核验通过：原始 incidence/opposite-edge、same-ID rows、Newell normals 独立复算、normal/frame 有限性及正交性、真实 section arc/chord、逐面 sign mixture、semantic gate、10 PNG 解码与完整性及 conditional artifacts。静态 PASS 不等于 authority PASS。

冻结核验：{len(now)} 个既有工作区文件 + {len(after['external'])} 个 external frozen/Human/request 文件，before==after；新增审查目录外新增、删除、修改均 0。全部既有 Stage4/5、rig、cap37、FIRST_WEB21、nail、CMC cage、R2/R3、Stage6、Human responses、distal evidence byte hashes 不变。WEIGHT/GEOMETRY/TOPOLOGY/BONE/JOINT DELTA 全部 0；R2=R3=Stage6=BLEND_FILES_WRITTEN=0。

**唯一剩余 blocker / NEXT：{S['NEXT']}。** 只需对同三个真实 edge pairs 取得能独立区分“仍有 partial thumb-circumference 语义 / 已进入 broader-interface”的局部 surface-role discriminator，配合同样 P02/P06 controls；可以是局部可复核的 anatomical surface-frame reference 或 exact-face role evidence。不能再把另一 scalar extremum 替代角色证据，也不能扩展 proximal domain。lateral 仍保留 unresolved，等待本上游问题解决。

## 30 项最终汇总

| # | Field | Result |
|---|---|---|
{summ}

**STOP。**

## 可视证据

'''+ '\n\n'.join(f'![{n}](renders/{n}.png)' for n in required)+'\n'
(OUT/(NAME+'_REPORT.md')).write_text(report,encoding='utf8')
dump('VISUAL_EVIDENCE_MANIFEST.json',{'render_type':'Scientific plots of exact frozen coordinates and direction fields; diagnostic projections do not infer semantic role','unconditional_visual_count':10,'files':[{'path':'renders/'+n+'.png','sha256':sha(OUT/'renders'/(n+'.png'))} for n in required],'conditional_candidate_visual_generated':False,'Human_review_generated':False})
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json'}})
print(json.dumps({'status':S['status'],'static_checks':len(checks),'frozen_workspace_files':len(now),'frozen_external_files':len(after['external']),'before_equals_after':True,'NEXT':S['NEXT'],'STOP':True},indent=2))
