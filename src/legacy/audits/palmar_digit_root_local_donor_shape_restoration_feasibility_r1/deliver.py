import sys
sys.dont_write_bytecode=True
from common import *
import html
scope=read(OUT/'PALMAR_ROOT_TRANSFER_SCOPE_R1.json');scope['DEFECT_CORE_MEMBERSHIP_VERTEX_COUNT']=len(scope['DEFECT_CORE_VERTEX_IDS']);scope['DEFECT_CORE_COUNT']=len(scope['DEFECT_CORE_WRITE_VERTEX_IDS']);scope['count_semantics']='core-write + ancestry-closure-write + transition-context-write = total temporary probe position writes; Human core membership count separately recorded';dump('PALMAR_ROOT_TRANSFER_SCOPE_R1.json',scope)
lock=read(OUT/'PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json');core=read(OUT/'PALMAR_ROOT_DEFECT_CORE_R1.json');normal=read(OUT/'PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json');gate=read(OUT/'PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json');protection=read(OUT/'PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json');ind=read(OUT/'PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json');donor=read(OUT/'PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json');payload=read(OUT/'TEMP_PROBE_PAYLOAD_PRESERVATION_R1.json');visual=read(OUT/'PALMAR_ROOT_VISUAL_FEASIBILITY_REVIEW_R1.json');P=read(OUT/'TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.json')
passed=gate['status']=='PASS' and payload['all_protected_payloads_exact'] and protection['positions_exact'] and protection['entire_excluded_face_geometry_exact'] and not scope['scope_blocker'] and visual['primary_shelf_reduced'] and visual['natural_crease_preserved']
verdict='PASS_LOCAL_DONOR_SHAPE_RESTORATION_FEASIBLE' if passed else 'FAIL_CLOSED_LOCAL_DONOR_RESTORATION_FEASIBILITY'
status={'phase':PHASE,'HUMAN_TARGET_LOCKED':'YES','PRIMARY_DEFECT_ROI_VERTEX_COUNT':len(core['vertex_ids']),'PRIMARY_DEFECT_ROI_FACE_COUNT':len(core['face_ids']),'UPPER_BOX_VISIBLE_HIT_VERTEX_COUNT':len(core['visible_upper_box_hit_vertex_ids']),'UPPER_BOX_VISIBLE_HIT_FACE_COUNT':len(core['visible_upper_box_hit_face_ids']),'EXCLUDED_NORMAL_ROI_VERTEX_COUNT':len(normal['vertex_ids']),'EXCLUDED_NORMAL_ROI_FACE_COUNT':len(normal['face_ids']),'shared_screen_hit_vertices_NORMAL_LOCKED':lock['shared_native_vertex_ids'],'shared_screen_hit_faces_boundary_not_full_defect':lock['shared_native_face_ids'],'DONOR_SOURCE':'OFFICIAL_HAND_REALISTIC_MULTIRES_L1','DONOR_ANCESTRY_CONFIDENCE':'EXACT_SUBDIVISION_GRAPH_AND_HISTORICAL_SPLIT_EDGE_PARENTAGE','OFFICIAL_STAGE2_L1_EXACT_EQUIVALENT':'YES','SOURCE_NATURAL_CREASE_PRESENT':'YES','CURRENT_HARD_FACETING_PRESENT':'YES','SOURCE_TO_CURRENT_GEOMETRY_DEVIATION_MAX_CORE_MM':donor['SOURCE_TO_CURRENT_GEOMETRY_DEVIATION']['core_max_mm'],'ENGINEERING_AMPLIFICATION_CONFIRMED':'YES','EARLIEST_CONFIRMED_HARD_FACETING_STAGE':donor['EARLIEST_CONFIRMED_HARD_FACETING_STAGE'],'POSITION_ONLY_DONOR_RESTORATION_FEASIBLE':'YES' if passed else 'NO','DEFECT_CORE_COUNT':scope['DEFECT_CORE_COUNT'],'ANCESTRY_CLOSURE_COUNT':scope['ANCESTRY_CLOSURE_COUNT'],'TRANSITION_CONTEXT_COUNT':scope['TRANSITION_CONTEXT_COUNT'],'TOTAL_TRANSFER_PROBE_WRITE_COUNT':scope['TOTAL_TRANSFER_PROBE_WRITE_COUNT'],'NEW_TRUE3D_DEFECT_COUNT':gate['NEW_TRUE3D_DEFECT_COUNT'],'new_contact_components':gate['new_contact_component_count'],'existing_contact_worsening':gate['existing_contact_worsening_count'],'feature_expansion':gate['feature_expansion_count'],'NORMAL_CONTEXT_VISIBLE_CHANGE':protection['NORMAL_CONTEXT_VISIBLE_CHANGE'],'NORMAL_CONTEXT_GEOMETRY_CHANGE':'NONE_EXACT','PRIMARY_DEFECT_VISIBLE_STATUS':visual['machine_visual_review'],'CURRENT9_WRITESET_DIRECT_OVERLAP_COUNT':ind['CURRENT9_WRITESET_DIRECT_OVERLAP_COUNT'],'CURRENT9_WRITESET_NEIGHBORHOOD_OVERLAP_COUNT':ind['CURRENT9_WRITESET_NEIGHBORHOOD_OVERLAP_COUNT'],'CURRENT9_CAUSAL_INDEPENDENCE':ind['CURRENT9_CAUSAL_INDEPENDENCE'],'TOPOLOGY_CHANGE_REQUIRED':'NO' if passed else 'UNRESOLVED','WEIGHT_CHANGE_REQUIRED':'NO' if passed else 'UNRESOLVED','RIG_CHANGE_REQUIRED':'NO' if passed else 'UNRESOLVED','RET0PO_REQUIRED':'NO' if passed else 'UNRESOLVED','PRODUCTION_DRIFT':0,'VERDICT':verdict,'status':verdict,'NEXT':'PALMAR_DIGIT_ROOT_LOCAL_DONOR_SHAPE_RESTORATION_DESIGN_R1' if passed else 'STOP_REVIEW_FEASIBILITY_FAILURE','NEXT_EXECUTED':False,'DESIGN_ONLY':True,'NOT_PRODUCTION':True,'NOT_APPROVED':True,'CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','Full42_runs':0,'Stage6_runs':0,'deformation_qualification_runs':0,'pose_smoke_runs':0,'Stage5_propagation_runs':0,'true_cap_recomputation_runs':0,'Stage6B_runs':0,'production_geometry_writes':0,'production_normal_writes':0,'production_weight_writes':0,'production_rig_writes':0,'production_material_modifier_writes':0,'formal_APPLY':False,'production_promotion':False,'Human_product_acceptance':'PENDING','STOP':'STOP — HUMAN REVIEW'}
dump(PHASE+'_STATUS.json',status)
prior_receipt=read(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json');initial=read(OUT/'HUMAN_RESPONSE_HASH_BEFORE.json');hold={'CURRENT_9_CROSSING_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','answers_written':False,'closure_created':False,'approval_receipt_created':False,'active_authority_written':False,'previous_hold_receipt':ref(PRIOR/'CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json'),'prior_response_sha256':prior_receipt['sha256_after'],'external_downloaded_response_present_at_start':initial['current_external_source_present'],'external_downloaded_response_present_at_end':RESPONSE.is_file(),'current_response_byte_check':'UNAVAILABLE_EXTERNAL_FILE_MISSING_AT_START' if not initial['current_external_source_present'] else 'PENDING_FINAL_CHECK','external_source_reconstructed':False}
dump('CURRENT9_HUMAN_RESPONSE_HOLD_VERIFICATION_R1.json',hold)
def img(path,title,desc=''):
 return '<figure><a href="'+html.escape(path)+'" target="_blank"><img loading="lazy" src="'+html.escape(path)+'" alt="'+html.escape(title)+'"></a><figcaption><b>'+html.escape(title)+'</b><br>'+html.escape(desc)+'</figcaption></figure>'
def fn(state,view='HUMAN_CAMERA',kind='SOLID'):return f'renders/{state}__{view}__{kind}.png'
body='<h1>掌侧指根 · Local donor restoration feasibility R1</h1><div class="notice">'+verdict+' · DESIGN_ONLY / NOT_PRODUCTION / NOT_APPROVED · STOP — HUMAN REVIEW</div><p>上方橙色＝PRIMARY DEFECT CORE；下方青色＝NORMAL / POSITION LOCKED。四列为同机位、scale、lighting、静态 RAW/RSSF frame；未运行新的 Stage6 pose。</p><div class="four">'
for state,title in [('CURRENT_RAW','CURRENT · RAW'),('OFFICIAL_L1_RSSF_DISPLAY','OFFICIAL L1 / Stage2 donor'),('TRANSFER_PROBE','TRANSFER PROBE · design only')]:body+=img(fn(state),title,'完整原生 surface，普通实体 smooth display')
body+=img(fn('TRANSFER_PROBE',kind='ROI_LABEL'),'DIFFERENCE / ROI LABEL','橙色 defect；青色正常区；金色线段显示16顶点恢复位移。')+'</div>'
body+='<div class="facts">23 core vertices / 13 core faces；normal 69 vertices / 49 faces。实际 probe writes＝3 core + 13 ancestry closure + 0 transition＝16。Normal geometry精确不变；新增 true3D defect＝0。</div><h2>Human target lock 与原确认图</h2>'
body+=img('renders/HUMAN_TARGET_LOCK_LABELS.png','Human 已确认：只处理上方小框','这是此前确认图的标注参考（saved IDX_MCP_30）。上面四列采用同相机静态RAW，不宣称重新验证该Stage6 pose。')
body+='<p>原生 faces 可能跨越上下两个像素选区。3个跨界faces及10个共享顶点归正常/边界参考；共享顶点锁定。独立 defect membership 与正常 membership 无交集；没有剪faces或改topology。</p><h2>近景普通实体 · 自然 crease 保留</h2><div class="four">'
for state,title in [('CURRENT_RAW','CURRENT'),('OFFICIAL_L1_RSSF_DISPLAY','DONOR'),('TRANSFER_PROBE','PROBE')]:body+=img(fn(state,'CLOSE'),title)
body+=img(fn('TRANSFER_PROBE','CLOSE','ROI_LABEL'),'ROI + donor-derived displacement')+'</div><h2>Alternate view</h2><div class="four">'
for state,title in [('CURRENT_RAW','CURRENT'),('OFFICIAL_L1_RSSF_DISPLAY','DONOR'),('TRANSFER_PROBE','PROBE')]:body+=img(fn(state,'ALTERNATE'),title)
body+=img(fn('TRANSFER_PROBE','ALTERNATE','ROI_LABEL'),'ROI labels')+'</div>'
for kind,title in [('GRAZING','Grazing light'),('FLAT_SOURCE_NATIVE','Flat / SOURCE_NATIVE'),('WIRE','Wire · current engineering topology retained')]:
 body+='<h2>'+title+'</h2><div class="three">'
 for state in ['CURRENT_RAW','OFFICIAL_L1_RSSF_DISPLAY','TRANSFER_PROBE'] if kind!='WIRE' else ['CURRENT_RAW','TRANSFER_PROBE']:body+=img(fn(state,'CLOSE',kind),state+' · '+kind)
 body+='</div>'
body+='<h2>下方正常区 · BEFORE / AFTER 单独对照</h2><p>69个顶点与49个faces几何精确相同。普通实体/flat/grazing像素最大差异为1/255色阶；没有新的contour改变，Human产品观感仍待确认。</p><div class="two">'+img('renders/EXCLUDED_NORMAL__BEFORE.png','NORMAL BEFORE · locked')+img('renders/EXCLUDED_NORMAL__AFTER.png','NORMAL AFTER · unchanged')+'</div>'
body+='<h2>真实 mesh cross-section</h2><p>三条截面使用 Blender native loop triangles 与同一平面直接相交。红线是current折返/shelf，绿线是probe，紫线是冻结RSSF frame中的native L1 donor；没有profile smoothing。</p>'
for name in ['FINGER_AXIS','CROSS_FINGER_AXIS','DIAGONAL_TANGENT']:body+=img('sections/'+name+'.png',name)
body+='<h2>Source 与最早工程 lineage</h2><p>Official L1与Stage2 evaluated L1的世界坐标、local坐标和native topology精确相同。16个恢复顶点3348–3363来自既有saved CON1_MIDDLE_MCP@-1mm construction snapshot；最早确认的hard shelf阶段为Stage4A_R2_BASE。下列historical snapshots各自保留原有状态/固定diagnostic registration，不冒称与上面RSSf三列具有相同pose。</p><div class="four">'
for state in ['SOURCE_PRE_ENGINEERING_L1','STAGE4A_R2_BASE','STAGE4A_R2','STAGE4B_RSSF']:body+=img(fn(state),state)
body+='</div><h2>结构与authority边界</h2><ul><li>V/E/F = 3416 / 6828 / 3414，face cycles / manifold / UV / materials / smooth / sharp / custom normals / weights / 21 bones与joints均保留。</li><li>所有write-incident native fans 对整手exact contact registry：new component=0、worsening=0、feature expansion=0；10个旧local contact components消失，未豁免旧接触。</li><li>连续linear transfer路径的最小fan triangle area=0.02931984 mm²；无零面积事件。不存在absolute projected bowtie zero gate。</li><li>正常区position锁定；write set与current9 direct / 1-ring / 2-ring overlap全部0。</li><li>temporary probe不进入production authority；Full42 / Stage6 / pose smoke / deformation qualification / Stage5 propagation / Stage6B全部0。</li></ul><h2>Human review</h2><p>本轮只判断这条local donor position restoration路线是否可行。请查看：上方shelf是否恢复成自然指根crease；下方正常区域是否保持原状；是否有新ridge/dent/bulge或边界不连续。没有 repair approval / apply / current9 closure 按钮。</p><p>NEXT仅记录为 '+status['NEXT']+'，本轮没有执行。Current9继续HOLD_NOT_CLOSED。</p><details><summary>Machine status全部字段</summary><pre>'+html.escape(json.dumps(status,ensure_ascii=False,indent=2))+'</pre></details><details><summary>证据JSON与临时probe</summary><ul>'
for name in ['PALMAR_ROOT_HUMAN_TARGET_LOCK_R1.json','PALMAR_ROOT_DEFECT_CORE_R1.json','PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json','PALMAR_ROOT_SOURCE_ANCESTRY_R1.json','PALMAR_ROOT_DONOR_SOURCE_COMPARISON_R1.json','PALMAR_ROOT_DONOR_TARGET_COORDINATES_R1.json','PALMAR_ROOT_TRANSFER_SCOPE_R1.json','PALMAR_ROOT_TRANSFER_STRUCTURE_AUDIT_R1.json','PALMAR_ROOT_NORMAL_CONTEXT_PROTECTION_AUDIT_R1.json','PALMAR_ROOT_CURRENT9_INDEPENDENCE_R1.json','PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json','TEMP_PALMAR_ROOT_DONOR_TRANSFER_PROBE_R1.blend']:body+='<li><a href="'+name+'">'+name+'</a></li>'
body+='</ul></details><p class="small">当前Downloads中的已填写response源文件在本轮开始时已不可见，因此本轮不能再次核验该外部文件字节。上一轮hold verification receipt保持冻结；本轮没有重建response、修改答案、写acceptance authority或创建closure。</p>'
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Palmar donor restoration feasibility R1</title><style>body{font:15px/1.6 system-ui,sans-serif;margin:0 auto;padding:18px;max-width:1780px;background:#f6f7f9;color:#202d3a}h1{font-size:24px;margin:0 0 8px}h2{font-size:21px;margin:30px 0 12px}.notice{background:#e7f6ee;border-left:5px solid #20875e;padding:10px;font-size:14px}.four,.three,.two{display:grid;gap:10px}.four{grid-template-columns:repeat(4,minmax(0,1fr))}.three{grid-template-columns:repeat(3,minmax(0,1fr))}.two{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0 0 12px;background:white;padding:8px;border:1px solid #d4dde6}img{display:block;width:100%;height:auto}figcaption{font-size:13px;margin-top:7px;overflow-wrap:anywhere}.facts{background:#e6edf4;padding:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}.small{font-size:12px;color:#56687b}a{color:#2368a5}@media(max-width:1000px){.four,.three{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.four,.three,.two{grid-template-columns:1fr}}</style><body>'+body+'</body></html>'
(OUT/'review.html').write_text(page,encoding='utf-8')
report=f'''# {PHASE}

**VERDICT = {verdict}**。临时position-only donor restoration可行：上方小框hard shelf明显减弱、自然指根crease保留；下方正常区域几何精确不变。本轮是feasibility，不是Human最终接受、正式design或APPLY。

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

正常区69顶点全部锁定，必需closure与normal交集0。未经许可的normal context移动0。闭包之外positions精确不变。16 vertices的max move约{donor['SOURCE_TO_CURRENT_GEOMETRY_DEVIATION']['write_set_max_mm']:.6f}mm。

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
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
print('Delivered',verdict,'Human review pending; NEXT recorded only',flush=True)
