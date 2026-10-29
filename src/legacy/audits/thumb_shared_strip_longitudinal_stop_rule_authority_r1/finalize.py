import sys
sys.dont_write_bytecode=True
from data import *
from PIL import Image
NAME='THUMB_SHARED_STRIP_LONGITUDINAL_STOP_RULE_AUTHORITY_R1'
T=read(OUT/'RAW_LOCAL_COLUMN_TRACES.json');D=read(OUT/'DISTAL_NON_NAIL_LONGITUDINAL_PROFILE.json');P=read(OUT/'PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json');A=read(OUT/'LONGITUDINAL_STOP_EVENT_CANDIDATE_AUDIT.json');C=read(OUT/'LONGITUDINAL_STOP_NEGATIVE_CONTROL_AUDIT.json');S=read(OUT/'LOCAL_DIAGNOSTIC_SUPPORT_SETS.json');SIDE=read(OUT/'DISTAL_FRONTIER_SIDE_IDENTITY_R1.json')
checks=[]
def ck(name,v):
    assert v,name
    checks.append({'name':name,'PASS':True})
ck('Frozen seeds and cap counts retained',len(CAP)==37 and len(WEB)==21 and SEEDS<=WEB)
ck('Identical original native/RSSF topology',J['NATIVE']['edges']==E and J['NATIVE']['faces']==F)
ck('Side identity from exact faces',SIDE['sides'][0]['first_continuation_face']==1177 and SIDE['sides'][0]['nail_overlap']==[304] and SIDE['sides'][1]['first_continuation_face']==1176 and not SIDE['sides'][1]['nail_overlap'])
for key,trace in T.items():
    for r in trace['rows']:
        for rec in r['records']:
            ck(key+' '+r['row_id']+' face '+str(rec['face_id'])+' original opposite-edge continuation',rec['face_id'] in EFS[rec['incoming_edge']] and rec['outgoing_edge'] in fedges(rec['face_id']) and not set(E[rec['incoming_edge']])&set(E[rec['outgoing_edge']]))
ck('Distal exact D01-D05 sequence',[r['face_ids'][0] for r in T['distal_non_nail']['rows']]==[1176,1213,1214,1226,1227])
ck('First cap conflict D05 after safe D04',all(not r['cap_overlap'] and not r['nail_overlap'] for r in T['distal_non_nail']['rows'][:4]) and T['distal_non_nail']['rows'][4]['cap_overlap']==[298,1454])
ck('Distal event-adjacent edge4524',A['distal']['non_nail_side']['stop_boundary_edge_ids']==[4524])
ck('Local geodesic stays local',all(v['vertex_count']<50 for v in D['local_metric_scope'].values()))
ck('Complete stop negative-control gate fails explicitly',C['overall_non_arbitrary_stop_gate']=='FAIL' and C['proximal_gate']=='FAIL')
ck('Earlier and later distal controls',len(C['distal_non_nail_controls'])==5 and all(r['cap_conflict'] for r in C['distal_non_nail_controls'] if r['offset_from_D04']>0))
ck('Five proximal controls surface supported',all(r['surface']['surface_supported'] and not r['cap_conflict'] and not r['nail_conflict'] for r in C['proximal_neighbor_controls']))
ck('F3+D04 diagnostic complete faces no wires',S['F3_plus_D04_diagnostic_only']['surface']['surface_supported'] and not S['F3_plus_D04_diagnostic_only']['surface']['wire_only_edge_ids'] and not S['F3_plus_D04_diagnostic_only']['surface']['dangling_vertex_ids'])
ck('Proximal exact row stop not fabricated',A['proximal']['final_row'] is None and A['proximal']['final_face_ids'] is None)
for state in ['NATIVE','RSSF']:
    ck(state+' cap-distance actual zero on conflicting row',D['states'][state][-1]['distance_to_cap37_min_vertex_mm']==0)
    ck(state+' finite normals and distances',all(np.isfinite(r['mean_normal']).all() and np.isfinite(r['mean_arc_mm']) for r in P['states'][state]+D['states'][state]))
ck('Native/RSSF first tangent event differs by adjacent row',A['proximal']['event_descriptors']['NATIVE']['first_outward_tangent_nonnegative_row']=='P04' and A['proximal']['event_descriptors']['RSSF']['first_outward_tangent_nonnegative_row']=='P05')
for name in ['THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json','THUMB_SHARED_STRIP_LONGITUDINAL_STOP_HUMAN_REVIEW.html','renders/FINAL_LONGITUDINAL_STOP_CANDIDATE.png']:
    ck('Conditional complete-candidate artifact correctly withheld: '+name,not (OUT/name).exists())
pngs=sorted((OUT/'renders').glob('*.png'));ck('8 required unconditional visualizations',len(pngs)==8)
for p in pngs:
    with Image.open(p) as im:
        im.load();ck(p.name+' nonblank full-resolution evidence',im.width>=2000 and im.height>=1200 and np.asarray(im).std()>10)
dump('STATIC_VERIFICATION_R1.json',{'status':'PASS','check_count':len(checks),'checks':checks,'forbidden_solver_executed':False,'diagnostic_metric_note':'Local edge-geodesic requested by user computed only on fixed distal evidence faces, not any R3 domain/field. Proximal tracing has no shortest-path search.'})
before=read(OUT/'FROZEN_HASHES_BEFORE.json');after={'workspace':{p:sha(ROOT/p) for p in before['workspace']},'external':{p:sha(p) for p in before['external']}}
allnow={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents and '.git' not in p.parts}
added=sorted(allnow-set(before['workspace']));removed=sorted(set(before['workspace'])-allnow);changed={g:[p for p,h in before[g].items() if after[g][p]!=h] for g in before}
assert before==after and not added and not removed
dump('FROZEN_HASHES_AFTER.json',after)
freeze={'status':'PASS','before_equals_after':True,'workspace_file_count':len(before['workspace']),'external_file_count':len(before['external']),'changed_files':changed,'added_outside_audit':added,'removed_outside_audit':removed,'WEIGHT_DELTA':0,'GEOMETRY_DELTA':0,'TOPOLOGY_DELTA':0,'BONE_DELTA':0,'JOINT_DELTA':0}
dump('FROZEN_HASH_VERIFICATION_R1.json',freeze)
status={'authority':NAME,'status':'FAIL_CLOSED','distal_nail_side_stop':'RESOLVED','distal_nail_side_mechanism':'AUTHORITY_CONFLICT_TERMINATION_BEFORE_FACE1177_NAIL_V304','distal_non_nail_stop':'RESOLVED_STOP_RULE_CANDIDATE_PENDING_HUMAN','distal_non_nail_final_row':'D04','distal_non_nail_last_safe_faces':[1226],'distal_non_nail_safe_taper_faces':[1176,1213,1214,1226],'distal_non_nail_first_forbidden_face':1227,'distal_non_nail_cap_conflict_ids':[298,1454],'distal_safe_rule_is_not_positive_shared_anatomy_approval':True,'proximal_stop':'UNRESOLVED','proximal_stop_mechanism':None,'proximal_final_row':None,'proximal_final_faces':None,'proximal_event_band':['P03','P04','P05'],'asymmetric_distal_taper':'YES_STOP_RULE_PROPOSAL_ONLY','neighbor_stop_negative_controls':'FAIL_OVERALL_DISTAL_CONDITIONAL_PASS_PROXIMAL_FAIL','native_RSSF_stop_topology_stable':False,'distal_stop_topology_stable':True,'original_mesh_topology_stable':True,'surface_supported':True,'surface_support_scope':'F3+D04 diagnostic (not final role extension)','wire_only_edges':0,'lateral_frontier_after_stop':'UNRESOLVED','final_shared_role_extension_vertex_count':None,'final_shared_role_extension_face_count':None,'THUMB_EXCLUSIVE_local_complement_count':None,'diagnostic_F3_plus_D04_counts':{'vertices':35,'faces':20,'role_approved':False},'FIRST_WEB21_changed':False,'cap37_changed':False,'nail_changed':False,'first_web_hard_pin_count':0,'Human_Review_required':True,'Human_review_page_generated':False,'role_extension_generated':False,'R2_runs':0,'R3_runs':0,'Stage6_runs':0,'skin_rebuild_runs':0,'strict_bound_runs':0,'retopo_runs':0,'BLEND_FILES_WRITTEN':0,'production_modified':False,'frozen_verification':freeze,'NEXT':'NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY','next_exact_scope':A['next_scope'],'STOP':True}
dump(NAME+'_STATUS.json',status)
dtable='\n'.join(f"| {r['row_id']} | {r['face_ids'][0]} | {r['distance_to_cap37_min_vertex_mm']:.6f} | {D['states']['RSSF'][i]['distance_to_cap37_min_vertex_mm']:.6f} | {r['normal_dot_web_context']:.6f} / {D['states']['RSSF'][i]['normal_dot_web_context']:.6f} |" for i,r in enumerate(D['states']['NATIVE']))
ptable='\n'.join(f"| {n} | {','.join(map(str,T['proximal']['rows'][int(n[1:])-1]['face_ids']))} | {next(r['mean_arc_mm'] for r in P['states']['NATIVE'] if r['row_id']==n):.6f} | {next(r['mean_arc_mm'] for r in P['states']['RSSF'] if r['row_id']==n):.6f} |" for n in ['P02','P03','P04','P05','P06'])
images='\n\n'.join(f'![{p.stem}](renders/{p.name})' for p in pngs)
report=f'''# {NAME}

**FAIL_CLOSED。Distal 已形成侧别明确、由 frozen authority conflict 定位的停止规则候选；proximal semantic stop 仍不唯一。没有 role extension、complement 或完整候选审批页面。**

## 审查范围与保护

仅从已有 R00–R08 / F3 columns4–6 出发，沿原始 quad 的 opposite edge 追踪局部 face columns。没有横向扩大到全掌，没有重建四角色地图、tube radius、R3 graph/unary/solve，没有 skin、Stage6、strict bound、retopo 或 production 写入。

9条环、8个完整 annulus、4个 frozen shared seeds、FIRST_WEB21、cap37、nail、corrected rig 与 CMC geometry-protected/non-hard-source 角色保持原样。F3 仍是诊断。first-web hard pins=0。旧 R2/R3 labels、skin weights、nearest winner 都未作为输入 truth。单位候选不复审。

输入使用前轮已校验的原始 native/RSSF 坐标、stable vertex/edge/face IDs 和 corrected chain。`INPUT_VERIFICATION.json` 校验前轮输出 manifest 及冻结 source hashes。代码只运行本新目录内的纯 Python 静态审查；既有 Blender/R2/R3/skin 脚本没有执行。

## Distal 侧别及可支持的停止规则

LEFT=column4，从 R00 v1399 出发；其第一 extension face1177 包含 frozen nail v304。停止边为 e4475=[1399,2774]，必须在进入1177之前停止。RIGHT=column6，从 v1396 出发，经 face1176，属于不立即碰到 nail 的一侧。两者由真实 incident faces / edges 判定，不凭截图。完整 frontier edges、首次 continuation edge、两种状态的 nail/cap 距离、normal 与 tangent 见 `DISTAL_FRONTIER_SIDE_IDENTITY_R1.json`。

RIGHT 的确定性 opposite-edge 延续为：1176→1213→1214→1226→1227。D01–D04 无 frozen cap/nail 冲突；D05 face1227 首次含 cap37 的 v298/v1454，同时出现非4-valence 顶点。native/RSSF 使用同样 IDs。这个事件不是任意角度或曲率阈值。

| Row | Face | native 最近 cap 顶点距离 mm | RSSF 同指标 mm | web-context normal dot native / RSSF |
|---|---:|---:|---:|---|
{dtable}

Distal 停止规则候选：**沿既有 non-nail 面列继续，在首次 frozen nail/cap 冲突前停止**。最后安全 row=D04 / face1226，末端边 e4524；下一面1227禁止进入 shared extension。左侧在1177前停，右侧在1227前停，允许 asymmetric taper。

这里的 RESOLVED 指该固定 face-column 上的停止规则候选已可确定，仍 pending Human；并不是宣称所有安全面已经获得 anatomical shared ownership。硬冲突建立禁止继续的上界；逐面连续性、仍朝 web context 的辅助法向与逐渐接近 frozen distal cap 提供候选的上下文。D01–D04 的正 normal dot 不是 membership 阈值，也不自动证明 shared anatomy。后续 lateral/role authority 仍须独立满足。

D0 CROP_AT_R00、D1 单面、D2 两面都没有在其截断处发现独立事件。D3 追至首个冻结冲突产生 D04 规则候选。不能因为它们更短或新增点更少选择 D0–D2。

## Proximal：首次形态转向窗口已定位，唯一 stop 未确定

沿 R08 两个真实面列，P01=3032/3033，P02=1372/1375，之后 P03=1373/1374，P04=1368/1371，P05=1369/1370，P06=1378/1377。所有这些行仍有完整原始 quad 支撑。

| Row | Face IDs | native outgoing mean chain arc mm | RSSF outgoing mean chain arc mm |
|---|---|---:|---:|
{ptable}

native 的纵向方向在 P03→P04 首次反转；RSSF 在 P04→P05 首次反转。同一批顶点逐步远离各自 thumb centerline，表面方向转向更广的 interface。这个变化支持 **P03–P05 是待裁决的 morphology transition window**，不足以唯一选择某行作为 DIGIT_WEB_TO_PALM_SEMANTIC_TRANSITION。

两种状态的差异来自 repose 与各自轴估计，不把它伪装成精确不变的 stop。native axis 取独立 native joint evidence，RSSF axis 取 corrected live chain；两者 arc 原点不同，绝对 arc 不作为跨状态 anatomical equality。MCP 仅作参照，没有“过 MCP 自动停止”。profile 中 R06–R08 的 arc 是 columns4–6 采样值，不是16点整环平均值。

为检验 S3，只沿同两个面列继续到第一个 lane valence event：P35 的 v247 valence3，且 successor faces1923/1922仍为 quads。这个纯拓扑 negative control 证明 regular quad continuation 可远远越过早期形态转折；P35 不能作为 web-strip semantic stop。没有搜索任意 shortest path，也没有把这35行纳入 shared region。不存在全掌 membership 或 ownership 重建。

`PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json` 包含 R06/R07/R08 与全部实际 trace rows 的 arc、距离轴 proxy、frontier separation、partial-section arc/chord、角宽、normal progression、tangent、valence、CMC v794 空间距离及 proximal/thenar-facing 方向 proxy。这些方向只表示结构位置，不能制造 thenar ownership。CMC cage 原 geometry 完全保留，没有使用先前不精确的73点重构作为精确 cage mask。

**证据限制明确保留：** 已知 R06–R08 的 circumferential completeness 可沿用；R08 后仅两列的完整 faces 不足以证明全圆周是否完整。该字段记为未证，而非把两列连续当作完整 thumb ring。没有为补足它而横向扩展整个 palm。距离为 mm；nail/cap 距离明确为最近冻结顶点距离，非连续面距离。local tube radius proxy 只是距离轴描述，不是被禁止的 tube-radius authority 重算。

## Negative controls 与候选 family

Distal 对 D04 检查提前2行D02、提前1行D03、延后1行D05、延后2行D06。早停没有对应 frozen conflict；晚停跨过 cap37，不能接受。该 gate 对“沿此固定列走到首个冲突前”的停止规则候选通过，但不代替 role-membership approval。nail侧也检查早一行、1177前及晚一行；进入1177造成 nail v304 冲突。

Proximal 对 P02–P06 各停止方案检查：全部有真实 surface support，零 cap/nail 冲突，均无对应的独立拓扑切断。native 与 RSSF 的几何转折落在相邻行；没有现有冻结 anatomical boundary 能从中选一个。因此 **neighbor-stop 完整 gate=FAIL**，不是选择最短/最连通方案。

| Family | 结论 |
|---|---|
| S1 SYMMETRIC_CROP | 拒绝作为 authority；R00/R08 是旧分析范围 |
| S2 ASYMMETRIC_TAPER + PROXIMAL_SEMANTIC_STOP | Distal 可形成停止规则候选；proximal 未解 |
| S3 FULL_FACE_STRIP_UNTIL_TOPOLOGY_STOP | 拒绝作为语义 authority；lane pole 不能说明 web/palm role transition |
| S4 HYBRID_AUTHORITY_CONFLICT_AND_MORPHOLOGY_STOP | 未形成完整候选；仅 distal conflict 已确定 |

`LONGITUDINAL_STOP_NEGATIVE_CONTROL_AUDIT.json` 保留全部面/点/冲突/支撑证据；不把邻近安全裁切隐瞒成唯一解。

## Lateral 与 role extension gate

columns4–6 维持原 topology candidate，不扩大横向范围。Distal frozen conflicts 不能反证其余圆周为 exclusive；proximal stop 又未解，故 `LATERAL_FRONTIER_POST_STOP_REVALIDATION.json`=UNRESOLVED。

F3+D04 仅诊断：35点/20面，完整 surface support，wire-only=0，dangling=0。这不是 final shared extension count。正式 extension 顶点/面数及 THUMB_EXCLUSIVE complement count 均为 null，不能写0来假装已批准空集合。

没有生成 `THUMB_WEB_SHARED_NEUTRAL_ROLE_EXTENSION_R1.json`、`FINAL_LONGITUDINAL_STOP_CANDIDATE.png` 或完整 Human Review HTML，符合仅成功时生成的条件。8张无条件证据图已生成，所有视图标注 FAIL CLOSED。

## 验证与冻结

{len(checks)} 项静态检查通过：原始 opposite-edge 邻接、侧别 frozen conflict、相邻行对照、局部 metric 范围、native/RSSF exact topology、surface support、输出条件与8张 PNG 完整性。验证通过不等于 authority 成功。

用户要求的 shared-seed edge-geodesic 仅在 F3 加 distal trace 的固定面图上计算，用于 profile 描述。未计算全场 R3 dT/dI，也未建 R3 graph；proximal 没有 shortest-path 搜索。curvature 使用 normal turn/edge dihedral 描述，没有 magic threshold。

冻结核验：{len(before['workspace'])} 个既有工作区文件 + {len(before['external'])} 个外部 authority/Human/本轮请求文件 before==after；新审查目录外新增、删除、修改均为0。WEIGHT_DELTA=GEOMETRY_DELTA=TOPOLOGY_DELTA=BONE_DELTA=JOINT_DELTA=0。R2=R3=Stage6=skin rebuild=strict bound=retopo=0，BLEND_FILES_WRITTEN=0。

## 唯一 NEXT

**NARROW_PROXIMAL_WEB_TO_PALM_TRANSITION_AUTHORITY**：仅在 P03–P05（1373/1374、1368/1371、1369/1370）及 P02/P06 邻接对照内，取得能确定 web strip→broader shared interface 的独立、同 IDs 可复核的边界证据。不要再次追踪整个 domain。lateral confirmation 保留为该上游问题解决后的 gate，不在本轮扩大研究。

**STOP。**

## 可视证据

{images}
'''
(OUT/(NAME+'_REPORT.md')).write_text(report,encoding='utf8')
dump('OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json',{'files':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='OUTPUT_EVIDENCE_HASH_MANIFEST_R1.json' and '__pycache__' not in p.parts},'scope':'This new audit directory only'})
print(json.dumps({'authority_status':'FAIL_CLOSED','distal_nail':'RESOLVED','distal_non_nail':'RESOLVED_STOP_RULE_CANDIDATE_PENDING_HUMAN','proximal':'UNRESOLVED','checks_passed':len(checks),'frozen_counts':[len(before['workspace']),len(before['external'])],'before_equals_after':True,'NEXT':status['NEXT'],'STOP':True},indent=2))
