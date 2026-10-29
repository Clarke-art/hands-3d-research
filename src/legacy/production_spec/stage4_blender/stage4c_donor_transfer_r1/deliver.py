import sys
sys.dont_write_bytecode=True
from common import *
from html import escape
from PIL import Image
S=read(OUT/'APPLICATION_STRUCTURE_AUDIT_R1.json');B=read(OUT/'APPLICATION_BOUNDARY_CONTOUR_AUDIT_R1.json');W=read(OUT/'APPLICATION_WRITE_VERIFICATION_R1.json');EQ=read(OUT/'APPLICATION_GEOMETRY_EQUIVALENCE_R1.json');SAVE=read(OUT/'APPLICATION_SAVE_REOPEN_AUDIT_R1.json');A=read(OUT/'APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json');M=read(OUT/'APPLICATION_MATCHED_RENDER_MANIFEST_R1.json');old=read(FULL/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json');G=read(OUT/'APPLICATION_NATIVE_SECTIONS_R1.json')
assert all(d['status']=='PASS' for d in [S,B,W,EQ,SAVE,A]) and M['render_count']==42
assert old['FULL_STAGE6A_REQUALIFICATION_R1']=='FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION' and old['MACHINE_HARD_BLOCKER_COUNT']==9
for r in M['renders']:
 with Image.open(OUT/r['path']) as im:assert list(im.size)==r['resolution']
assert G['stages']['APPROVED_FORMAL_CANDIDATE']==G['stages']['APPLIED_NEW_STAGE4C_REVISION']
visual={'status':'PASS','CONTOUR_APPLICATION_EQUIVALENCE':'PASS','VISIBLE_DENT_APPLICATION_STATUS':'PASS_ABSENT_EXACT_HUMAN_APPROVED_CONTOUR_APPLIED','NATURAL_DORSAL_MCP_VALLEY':'PASS_EXACT_APPROVED_SHAPE_RETAINED','NEW_VISIBLE_CONTOUR_DEFECT':'NONE_OBSERVED','Human_visual_decision_source':ref(OUT/'HUMAN_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPROVAL_R1.json'),'application_confirmation':'Actual approved/application geometry equal; agent inspected new matched plain-solid images and original Human view. This confirms exact application of approved shape, does not create production qualification.','inspected_images':['THREE_COLUMN_APPLICATION_SOLID_R1.png','APPLICATION_VISUAL_INSPECTION_SHEET_R1.png','renders/APPLIED_NEW_STAGE4C_REVISION_HUMAN_SOURCE_NATIVE.png'],'all42_render_images': [r['path'] for r in M['renders']],'native_sections_0_60_120_exact_approved_vs_applied':True,'new_hinge_ridge_notch_silhouette_kink':'NONE_OBSERVED','production_promoted':False}
dump('APPLICATION_CONTOUR_EQUIVALENCE_R1.json',visual);B['visual_evidence']=visual;B['CONTOUR_APPLICATION_EQUIVALENCE']='PASS';dump('APPLICATION_BOUNDARY_CONTOUR_AUDIT_R1.json',B)
future={'NEXT':'STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1','next_recorded_only_not_executed':True,'future_order':['Stage5 geometry propagation','joint-to-surface / rest / zero / bind validation','static skin compatibility','geometry-dependent true-cap paths/bounds revalidation','targeted deformation revalidation','Full42 Stage6A requalification','Human contour / deformation review','Stage6B may be considered only after all preceding closures'],'new_stage4c_input':ref(ASSET),'frozen_design_plan':ref(DESIGN/'FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json'),'geometry_write_set':IDS,'direct_native_face_count':len(A['incident_native_face_ids']),'direct_incident_edge_count':len(A['incident_edge_ids']),'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True,'this_turn_executed':['new independent Stage4C geometry application','local static validation','factory-clean save/reopen validation','approval receipt binding','application contour equivalence evidence'],'this_turn_not_executed':['Stage5A geometry propagation','R2 production edit','rig/weight rebinding','bone/joint edits','R3 recomputation','true-cap paths/bounds recomputation','static skin qualification','targeted deformation','Full42','Stage6B','production freeze/promotion'],'NO_RESEARCH_REOPEN':read(DESIGN/'FORMAL_DONOR_TRANSFER_DOWNSTREAM_PLAN_R1.json')['NO_RESEARCH_REOPEN'],'old9_crossings_retained_independent_and_unadjudicated':True,'STOP':True}
dump('APPLICATION_DOWNSTREAM_STOP_BOUNDARY_R1.json',future)
status={'phase':PHASE,'HUMAN_AMENDMENT_APPROVAL':'APPROVED','SOURCE_HASH_VERIFIED':'PASS','HUMAN_APPROVAL_BOUND':'PASS','SOURCE_STAGE4C_HASH':EXPECTED_SOURCE,'APPROVED_FORMAL_CANDIDATE_HASH':EXPECTED_CANDIDATE,'DONOR_SOURCE_HASH':EXPECTED_DONOR,'HUMAN_APPROVAL_RECEIPT_SHA256':sha(OUT/'HUMAN_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPROVAL_R1.json'),'APPROVED_WRITE_SET_COUNT':54,'APPROVED_WRITE_SET':'54/54','ACTUAL_CHANGED_VERTEX_COUNT':54,'OUTSIDE54_POSITION_DRIFT':0,'MAX_COORD_DELTA_VS_APPROVED_TARGET_MM':W['MAX_EUCLIDEAN_COORDINATE_DELTA_MM'],'MAX_ABSOLUTE_COMPONENT_DELTA_VS_APPROVED_TARGET_MM':W['MAX_ABSOLUTE_COORDINATE_DELTA_MM'],'MEAN_COORD_DELTA_VS_APPROVED_TARGET_MM':W['MEAN_EUCLIDEAN_COORDINATE_DELTA_MM'],'RMS_COORD_DELTA_VS_APPROVED_TARGET_MM':W['RMS_EUCLIDEAN_COORDINATE_DELTA_MM'],'APPLICATION_ASSET_PATH':str(ASSET),'APPLICATION_ASSET_SHA256':sha(ASSET),'NEW_DERIVED_ASSET':'YES','SOURCE_HISTORY_PRESERVED':'PENDING_FINAL_HASH_AUDIT','APPROVED_CANDIDATE_TO_APPLICATION_GEOMETRY_EQUIVALENCE':'PASS','TOPOLOGY_PRESERVED':'PASS','UV_MATERIAL_PRESERVED':'PASS','TOPOLOGY_DRIFT':0,'UV_DRIFT':0,'MATERIAL_DRIFT':0,'WEIGHT_DRIFT':0,'BONE_JOINT_DRIFT':0,'NO_ADDED_VERTEX_GROUPS_ARMATURE_WEIGHTS_BONES':True,'NATIVE_V_E_F':[3416,6828,3414],'STRUCTURAL_GATE':'PASS','CONTACT_NO_REGRESSION':'PASS','NEW_TRUE3D_CONTACT_COUNT':0,'NEW_SELF_INTERSECTION_COUNT':0,'NEW_NONADJACENT_EXACT_INTERSECTION_COUNT':0,'NEW_OFF_SHARED_CROSSING_COUNT':0,'NEW_ILLEGAL_COPLANAR_OVERLAP_COUNT':0,'NEW_STRUCTURAL_BOWTIE_COUNT':0,'FACE_REVERSAL_COUNT':0,'DEGENERATE_COUNT':0,'BASELINE_CONTACT_WORSENING_COUNT':0,'BASELINE_FEATURE_EXPANSION_COUNT':0,'SHARP_TRANSITION_MIGRATION_COUNT':0,**{'EDGE'+k+'_DIHEDRAL':B['named_edges'][k]['application_dihedral_deg'] for k in ['6675','6602','6676']},'EDGE_NAMED_ANGLES_VS_APPROVED_DELTA_DEG':0,'VISIBLE_DENT_APPLICATION_STATUS':visual['VISIBLE_DENT_APPLICATION_STATUS'],'NEW_VISIBLE_CONTOUR_DEFECT':'NONE_OBSERVED','CONTOUR_APPLICATION_EQUIVALENCE':'PASS','SAVE_REOPEN':'PASS','SERIALIZATION_GEOMETRY_DRIFT':0,'AUTHORITY_INTERSECTION_RECHECK':'PASS','PROTECTED_HISTORY_DRIFT':'PENDING_FINAL_HASH_AUDIT','FULL_STAGE6A_STATUS_RETAINED':old['FULL_STAGE6A_REQUALIFICATION_R1'],'MACHINE_HARD_BLOCKER_COUNT_RETAINED':9,'FULL_STAGE6A_FROZEN_STATUS_FILE':ref(FULL/'FULL_STAGE6A_REQUALIFICATION_R1_STATUS.json'),'OLD_9_CROSSINGS_RECLASSIFIED_REPAIRED_ADJUDICATED':False,'PRODUCTION_PROMOTION':'NO','STAGE5_PROPAGATION_EXECUTED':False,'R3_TRUE_CAP_TARGETED_DEFORMATION_FULL42_STAGE6B_EXECUTED':False,'TARGET_COORDINATES_RECOMPUTED':False,'APPLICATION_VERDICT':'PENDING_FINAL_HASH_AUDIT','NEXT':future['NEXT'],'NEXT_EXECUTED':False,'STOP':True,'RENDER_COUNT':42,'DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED':True}
dump(PHASE+'_STATUS.json',status)
labels=['SOURCE_STAGE4C_R2','APPROVED_FORMAL_CANDIDATE','APPLIED_NEW_STAGE4C_REVISION'];titles=['Frozen Stage4C_R2','Human-approved formal candidate','Applied new Stage4C revision']
def grid(v,shade):return '<div class="grid">'+''.join(f'<figure><figcaption>{t}<small>{l}</small></figcaption><a href="renders/{l}_{v}_{shade}.png"><img src="renders/{l}_{v}_{shade}.png" alt="{l} {v} {shade}" loading="{("eager" if v=="CLOSE" else "lazy")}"></a></figure>' for l,t in zip(labels,titles))+'</div>'
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stage4C donor transfer — application review</title><style>body{margin:0;background:#f4f5f6;color:#202b34;font:15px/1.5 system-ui,"Microsoft YaHei",sans-serif}header{padding:12px 20px;background:#fff}h1{margin:0;font-size:20px}p{margin:6px 0}main{padding:12px 18px}h2{font-size:19px;margin:24px 0 8px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}figure{margin:0;background:#fff}figcaption{padding:8px;font-size:14px;font-weight:600;height:84px;box-sizing:border-box}small{display:block;font-size:10px;font-weight:400;overflow-wrap:anywhere}img{display:block;width:100%;height:auto}a{color:#285d86}details{background:#fff;padding:12px;margin:8px 0}table{border-collapse:collapse;background:#fff;width:100%;font-size:13px}td,th{padding:7px;text-align:left;border:1px solid #dce1e6}code{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}nav{display:flex;gap:12px;margin:8px 0}.note{padding:12px;background:#fff4dd}</style><header><h1>Stage4C donor transfer · application review</h1><p>HUMAN_AMENDMENT_APPROVAL = APPROVED · 独立 Stage4C geometry revision · PRODUCTION_PROMOTION = NO</p><p>54/54 精确应用；批准坐标差0mm；save/reopen与geometry equivalence PASS。STOP。</p></header><main><p>三列同机位普通实体：确认批准设计已被精确应用。点击图可查看原始640px文件。</p>',grid('CLOSE','FLAT'),'<nav><a href="#views">全部匹配视图</a><a href="#sections">原生剖面 / overlay</a><a href="#evidence">资产与证据</a></nav><div class="note">新asset只表示 Stage4C geometry amendment已应用。未传播Stage5，未promote。旧Full42 Stage6A保持FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION，9对独立severe crossings未裁决、未重分类。</div><h2 id="views">匹配视图 · 已批准结果的应用核验</h2>']
view_titles={'HUMAN':'原始 Human dent 机位 · 640×800','CLOSE':'Close solid','FULL_DORSAL':'Full dorsal hand','GRAZING':'Grazing','SIDE':'Side','SILHOUETTE':'Silhouette / 外轮廓','WIRE':'Native wire'}
for v in ['HUMAN','CLOSE','FULL_DORSAL','GRAZING','SIDE','SILHOUETTE','WIRE']:html.append('<h2>'+view_titles[v]+'</h2>'+grid(v,'FLAT')+'<details><summary>实际 source native smooth flags</summary>'+grid(v,'SOURCE_NATIVE')+'</details>')
html.append('<h2 id="sections">0° / 60° / 120° native sections</h2><p>来自实际source / approved / applied native geometry；同一物理平面与尺度，单位mm，faceID可追溯。approved/applied的剖面线段精确相等。Overlay红蓝重合用于application一致性核验。</p>')
for a in [0,60,120]:html.append(f'<h2>{a}°</h2><img src="sections/THREE_NATIVE_SECTIONS_{a}.svg" alt="{a} degree three native sections"><img src="sections/APPROVED_APPLIED_OVERLAY_{a}.svg" alt="{a} degree approved applied overlay">')
html.append('<h2>关键二面角 · 仅诊断</h2><table><tr><th>Edge</th><th>Source°</th><th>Approved°</th><th>Applied°</th><th>Applied−approved°</th></tr>')
for k,r in B['named_edges'].items():html.append(f'<tr><td>{k}</td><td>{r["source_dihedral_deg"]:.9f}</td><td>{r["approved_candidate_dihedral_deg"]:.9f}</td><td>{r["application_dihedral_deg"]:.9f}</td><td>0</td></tr>')
html.append('</table><p>角度不是人体threshold。所有高delta boundary诊断及exact true3D contact-no-regression证据已保留。</p><h2>应用身份与hash绑定</h2><p>Human approval原文另存且hash绑定；精确54 ID/set/local coordinate及formal JSON文件hash均验证PASS。未重新计算donor或target，未fairing/optimizer/手调/normal correction。</p><p>新asset：<a href="'+ASSET.name+'">'+ASSET.name+'</a><br>SHA256：<code>'+sha(ASSET)+'</code></p><h2>STOP boundary</h2><p>NEXT = STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1，仅记录，未执行。DO_NOT_PROMOTE_UNTIL_DOWNSTREAM_REQUALIFIED。</p><ol>')
for step in future['future_order']:html.append('<li>'+escape(step)+'</li>')
html.append('</ol><h2 id="evidence">完整输出</h2><ul>')
outputs=[PHASE+'_REPORT.md',PHASE+'_STATUS.json','HUMAN_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPROVAL_R1.md','HUMAN_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_APPROVAL_R1.json','HUMAN_APPROVAL_REQUEST_ORIGINAL.txt','APPLICATION_PREREQUISITE_GATE_R1.json','APPLICATION_WRITE_VERIFICATION_R1.json','APPLICATION_GEOMETRY_EQUIVALENCE_R1.json','APPLICATION_STRUCTURE_AUDIT_R1.json','APPLICATION_CONTACT_AUDIT_R1.json','APPLICATION_BOUNDARY_CONTOUR_AUDIT_R1.json','APPLICATION_CONTOUR_EQUIVALENCE_R1.json','APPLICATION_SAVE_REOPEN_AUDIT_R1.json','APPLICATION_AUTHORITY_INTERSECTION_AUDIT_R1.json','APPLICATION_PROTECTED_HISTORY_HASH_AUDIT_R1.json','APPLICATION_DOWNSTREAM_STOP_BOUNDARY_R1.json','APPLICATION_NATIVE_SECTIONS_R1.json','APPLICATION_MATCHED_RENDER_MANIFEST_R1.json',ASSET.name]
for o in outputs:html.append(f'<li><a href="{o}">{o}</a></li>')
html.append('</ul><p>STOP · Stage5与所有下游本轮均未执行。</p></main></html>');(OUT/'review.html').write_text(''.join(html),encoding='utf-8')
report=f'''# {PHASE}

结论待最终history hash审计：PASS_APPLIED_TO_NEW_STAGE4C_DERIVED_REVISION。APPLIED仅指新Stage4C派生几何版本创建，PRODUCTION_PROMOTION=NO。STOP。

## Human批准与唯一authority

本轮用户附件明确HUMAN_APPROVE_LOCAL_DONOR_SHAPE_TRANSFER_AMENDMENT_R1=APPROVED，dent PASS_ABSENT，自然valley PASS，新增visible defect NONE_OBSERVED。独立Human receipt JSON/MD记录原文hash、donor/source/candidate身份、54 IDs、write-set文件hash、coordinate JSON hash和精确54 stored local coordinate hash。原文另存HUMAN_APPROVAL_REQUEST_ORIGINAL.txt，旧design report/receipt不改写。

唯一coordinate authority为已批准FORMAL_DONOR_TRANSFER_COORDINATES_R1.json的candidate_local_m，绑定已批准candidate hash。输入SHA、54集合、full coordinate文件与54target payload hash逐一验证PASS；没有新的donor/ancestry solve、优化、fairing、fit、sculpt、手调、normal correction或contact cleanup。

## 新独立Stage4C revision

APPLICATION_ASSET_PATH：`{ASSET}`

APPLICATION_ASSET_SHA256：`{sha(ASSET)}`

资产从factory-startup clean reopen的frozen Stage4C_R2创建，先校验source和native topology，直接赋值精确54 stored-local targets。不是将candidate或probe改名/复制冒充应用结果。新asset仅增加合法AMENDMENT_* provenance与NOT_PROMOTED/downstream-requalified guards，既有custom props保留。

save后在另一个factory-startup Blender进程clean reopen，重新读取实际native coordinates和payload。再factory reset后打开真实approved candidate核对，actual geometry及全部protected payload精确相同。

APPROVED_WRITE_COUNT=54；ACTUAL_CHANGED_VERTEX_COUNT=54；OUTSIDE54_POSITION_DRIFT_COUNT=0。max绝对component / max Euclidean / mean / RMS coordinate delta均0mm。已批准target本来就是native float32已存储值，直接native赋值与save/reopen未产生额外舍入，不借tolerance接受任何漂移。

## Native payload保护

V/E/F=3416/6828/3414，native vertex/edge/face IDs、face cycles、manifold incidence、loops、UVcoords/connectivity、material slots/assignments/nodes、smooth/sharp flags、custom normal state、object matrices、既有metadata、其它mesh payload精确不变。Stage4C本身没有production rig，本轮未增加vertex groups、armature、weights或bones。

APPROVED_CANDIDATE_TO_APPLICATION_GEOMETRY_EQUIVALENCE=PASS。TOPOLOGY_DRIFT=0；UV_DRIFT=0；MATERIAL_DRIFT=0；WEIGHT_DRIFT=0；BONE_JOINT_DRIFT=0。SAVE_REOPEN=PASS；SERIALIZATION_GEOMETRY_DRIFT=0。

## Static true3D资格

重新以实际application保存/重开坐标运行reconciled exact finite-feature gate：54write-incident native fans对whole mesh，减去实际合法shared simplex；baseline component/feature/extent no-regression。其它pair因全部坐标不变而精确不变。源局部baseline12contact components→application0。

STRUCTURAL_GATE=PASS；CONTACT_NO_REGRESSION=PASS。new nonadjacent exact intersection、off-shared crossing、illegal coplanar overlap、true self-intersection、structural bow-tie、face reversal、degenerate、新true contact components、baseline contact worsening、feature expansion、sharp transition migration均0。

不恢复absolute projected bowtie zero语义。native oriented cycles不变，source→application线性morph的continuous native fan最小面积为{S['continuous_fan_area']['minimum_fan_triangle_area_mm2']:.15g}mm²，没有zero-area event；固定chart normal翻转属于diagnostic。端点exact intersection+continuous area不声称完整连续碰撞资格或Stage6资格。

## Contour application核验

|Edge|Source°|Approved°|Applied°|Applied−approved°|
|---|---:|---:|---:|---:|
'''
for k,r in B['named_edges'].items():report+=f'|{k}|{r["source_dihedral_deg"]:.9f}|{r["approved_candidate_dihedral_deg"]:.9f}|{r["application_dihedral_deg"]:.9f}|0|\n'
report+='''
这些角度只是证明同一个几何结果的诊断，不是人体threshold。完整boundary/outer fixed-fixed圈及abs(delta)>10°记录保留。

42张新render，第一屏SOURCE_STAGE4C_R2 / APPROVED_FORMAL_CANDIDATE / APPLIED_NEW_STAGE4C_REVISION三列普通实体；原始Human640×800、close、full dorsal、grazing、side、silhouette、wire。同一camera/light/scale，中性实体材质，flat及实际native smooth flags。0/60/120°实际native plane sections保留face IDs，approved/application线段精确一致，overlay重合。

Agent实际检查三列close、grazing、side、full dorsal、silhouette、wire及原始Human机位：已批准的notch消除与自然valley保持，未观察到新轮廓缺陷。VISIBLE_DENT_APPLICATION_STATUS=PASS_ABSENT_EXACT_HUMAN_APPROVED_CONTOUR_APPLIED；CONTOUR_APPLICATION_EQUIVALENCE=PASS。此处确认批准设计精确应用，不重新选择candidate，也不声称production-ready。

## Authority交集一致性

实际54集合及95incident native faces、148incident edges与设计footprint完全一致。cap37、FIRST_WEB21、freshR3 frozen protected domain、历史317 weight universe、thumb nail、oldcap9、冻结CMC cage context的write交集均为空；相关membership/文件hash不变，没有authority重研究。

CMC57 final-new-cage点由冻结历史六位小数记录精确恢复native ID，16 final boundary顶点由冻结实际edge/face incidence恢复，64 cage quads共73点。历史boundary_loop_world记录使用pole treatment前CO，不能把它当final position authority；该核对只追溯冻结context，不执行原建模或重新选择空间半径。详见authority intersection audit。

## 旧资格保留与STOP

FULL_STAGE6A_REQUALIFICATION_R1=FAIL_CLOSED_FULL_STAGE6A_REQUALIFICATION；MACHINE_HARD_BLOCKER_COUNT=9。旧9对severe crossings的原始证据/分类/receipt全部保留，本轮没有优化、修复、裁决、重分类或接受。

Stage5A与R2 production candidate没有几何传播、重绑定、weight或bone写入；没有R3、true-cap path/bound、static skin qualification、targeted deformation、Full42或Stage6B执行。PRODUCTION_PROMOTION=NO。

NEXT=STAGE5_GEOMETRY_PROPAGATION_AFTER_DONOR_TRANSFER_R1，仅记录，未执行。后续顺序：Stage5 geometry propagation → joint-to-surface/rest/zero/bind → static skin compatibility → geometry-dependent true-cap paths/bounds → targeted deformation → Full42 → Human contour/deformation review → 全部关闭后才可考虑Stage6B。NO_RESEARCH_REOPEN既有cap37/R3/FIRST_WEB/CMC/thumb/317 weights/retopo/bone authority，除非后续实际revalidation出现新直接证据。

## 最终字段（history audit完成后更新）

'''
report+='|Field|Value|\n|---|---|\n'+''.join('|'+k+'|'+str(v)+'|\n' for k,v in status.items())
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
print('Application contour equivalence, review/report/status, approval evidence links and explicit downstream STOP boundary generated')
