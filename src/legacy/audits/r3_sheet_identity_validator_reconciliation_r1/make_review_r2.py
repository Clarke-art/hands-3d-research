import sys
sys.dont_write_bytecode=True
import json,re
from reconcile import OUT,FRESH,read,dump,sha,METHOD,RUN
D=read(FRESH/'R3_FRESH_REVIEW_VIEW_DATA_R1.json');R=read(OUT/'R3_SHEET_IDENTITY_REVALIDATION_R2.json');S=read(OUT/(RUN+'_STATUS.json'));assert R['verdict']=='FRESH_R3_SHEET_IDENTITY_PASS'
oldlabels=D['labels'].copy();oldcut=D['fresh_boundary'].copy();D['sheet_valid']=True;D['index_sheet']=[int(v) for v,l in D['labels'].items() if l=='INDEX'];D['thumb_body']=[int(v) for v,l in D['labels'].items() if l=='THUMB'];D['mixed_face_ids']=read(OUT/'R3_MIXED_BOUNDARY_FACE_BAND_AUDIT.json')['face_ids'];D['sheet_validator_method']=METHOD;D['validator_revalidation_hash']=sha(OUT/'R3_SHEET_IDENTITY_REVALIDATION_R2.json')
D['status'].update({'technical_validation_verdict':'PASS_READY_FOR_HUMAN_REVIEW','review_reasons':[],'INDEX_sheet_vertex_count':464,'THUMB_ownership_region_vertex_count':498,'body_THUMB_side_count':None,'canonical_sheet_validator_method':METHOD,'sheet_validation_scope':'bounded solved vertex-label field; no global physical mesh split','validator_revalidation_hash':D['validator_revalidation_hash'],'original_R1_face_dual_failure_preserved':True,'Human_Review_page_generated':'YES','R3_rerun_count_this_reconciliation':0,'fresh_labels_changed_this_reconciliation':0})
assert D['labels']==oldlabels and D['fresh_boundary']==oldcut
page=(FRESH/'R3_FRESH_RESULT_HUMAN_REVIEW.html').read_text(encoding='utf8')
start=page.index('const DATA=')+len('const DATA=');end=page.index(';\n',start);page=page[:start]+json.dumps(D,separators=(',',':'),ensure_ascii=False).replace('</',r'<\/')+page[end:]
alert='''<div class="alert"><strong>PASS_READY_FOR_HUMAN_REVIEW · SHEET IDENTITY PASS (R2)</strong><br>仅更正 derived validator semantics：fresh labels、graph、sources、cut、energy、ambiguity 全部冻结。R3 rerun=0。<br><strong>Canonical：</strong>bounded vertex-label region identity + pure-face support + mixed boundary band。THUMB 498 / INDEX 464，各 1 个 source-backed component；pure THUMB 463 faces / pure INDEX 438 faces，各 1 component；mixed 21 faces，1 个连续 band。v233 + INDEX nail 与 v284 + cap37 + THUMB nail 独立识别两侧。<br>原 full face-dual 1 component / identity collision 是 VALIDATOR_METHOD_MISMATCH，原失败输出保持 immutable。即使 barrier 化 mixed faces，完整 mesh 仍可通过 graph 外未赋值区域连通；本次不声明物理切割或 global body ownership。Skin / Stage6 / 自动 APPLY 全部未运行，仍需 Human result approval。</div>'''
page=re.sub(r'<div class="alert">.*?</div>',lambda _:alert,page,count=1,flags=re.S)
page=page.replace('TECHNICALLY_VALID_BUT_HUMAN_REVIEW_REQUIRED','PASS_READY_FOR_HUMAN_REVIEW')
page=page.replace('Fresh R3 · Human result review','Fresh R3 · Human result review R2')
page=page.replace('新的 R3 ownership 结果','Fresh R3 · validator reconciliation R2')
page=page.replace('本页展示新的 Dijkstra、min-cut、closure 与 derived authority revalidation。','本页复用冻结的 R1 Dijkstra、min-cut、closure 结果，展示本轮 read-only sheet validator reconciliation。')
page=page.replace('15 个视图','16 个视图').replace('05 · INDEX sheet revalidation','05 · INDEX ownership sheet identity').replace('06 · THUMB / body side','06 · THUMB counterpart region')
page=page.replace('<option value="SOURCES">','<option value="MIXED_BAND">16 · Mixed boundary face band</option><option value="SOURCES">')
page=page.replace('不可确认；full face-dual 只有一个 component','域内 INDEX 464 / THUMB 498；global body 不赋值')
page=page.replace('INDEX sheet / body','INDEX ownership / THUMB counterpart')
page=page.replace('INDEX sheet 是否合理？（当前 full face-dual 未分离，identity collision）','INDEX ownership sheet 是否合理？（R2：域内独立 anchor-resolved region）')
page=page.replace('接受 candidate 不会自动冻结 labels 或运行 skin reconciliation；sheet identity collision 仍单独记录。','接受 candidate 不会自动冻结 labels 或运行 skin reconciliation；原 R1 full face-dual failure 与 R2 methodology correction 均保留。')
page=page.replace("const REVIEW_ID='R3_FRESH_RESULT_HUMAN_REVIEW_R1'","const REVIEW_ID='R3_FRESH_RESULT_HUMAN_REVIEW_R2'")
page=page.replace("fresh_result_label_hash:meta.result_hash,","fresh_result_label_hash:meta.result_hash,validator_revalidation_hash:meta.validator_revalidation_hash,canonical_sheet_validator_method:meta.sheet_validator_method,")
page=page.replace("INDEX_SHEET:'FAIL_REVALIDATION：full frozen face dual 只有 1 component，3414 faces / 3416 vertices。v233 与 v284 identity collision；没有独立 INDEX sheet 可显示。视图显示未分离 mesh、fresh graph labels 与两个独立 markers。'","INDEX_SHEET:'R2 PASS：域内 INDEX ownership region 464 vertices，1 个 source-backed component；pure INDEX 438 faces，1 component。v233 + 全部 INDEX nail 独立定位；不要求整个物理 mesh 被分离。'")
page=page.replace("BODY:'Body / THUMB counterpart 无法独立确认：与 INDEX marker 同一 face component。只显示 current binary THUMB labels，不能把它称为独立解剖 sheet。'","BODY:'R2 PASS：THUMB counterpart 498 vertices，pure THUMB 463 faces，各 1 component；v284 + cap37 + THUMB nail 定位。graph 外 2454 点仍未求解，不能据此称为完整 body/wrist ownership map。'")
page=page.replace("ENERGY:'Fresh energy", "MIXED_BAND:'21 个 mixed polygons 形成 1 个连续 shared-edge boundary band，邻接两侧 pure faces；19 个全在 graph，2 个含未赋值 corners。band 只用于 validation，不引入第三个 ownership label。',ENERGY:'Fresh energy")
page=page.replace("const hide=scene.mode==='BODY'&&lab(v)!=='THUMB';","const hide=(scene.mode==='BODY'&&lab(v)!=='THUMB')||(scene.mode==='INDEX_SHEET'&&lab(v)!=='INDEX');")
page=page.replace("function point(v,col,size,ring=false)","if(scene.mode==='MIXED_BAND')for(const f of DATA.mixed_face_ids)polygon(DATA.faces[f],'#efaf3970','#b37d15');\nfunction point(v,col,size,ring=false)")
page=page.replace('Sheet revalidation 状态保留在 response。','R2 sheet method 和 revalidation hash 保留在 response。')
page=page.replace('当前 labels 未冻结。','当前 labels 未经 Human result freeze。')
assert 'FAIL_REVALIDATION：full frozen' not in page and 'const DATA=' in page
(OUT/'R3_FRESH_RESULT_HUMAN_REVIEW_R2.html').write_text(page,encoding='utf8');dump('R3_FRESH_REVIEW_VIEW_DATA_R2.json',D)
S['Human_Review_R2_generated']=True;dump(RUN+'_STATUS.json',S)
dump('R3_HUMAN_REVIEW_R2_GENERATION_AUDIT.json',{'pass':True,'original_R1_HTML_sha256':sha(FRESH/'R3_FRESH_RESULT_HUMAN_REVIEW.html'),'new_R2_HTML_sha256':sha(OUT/'R3_FRESH_RESULT_HUMAN_REVIEW_R2.html'),'labels_unchanged':D['labels']==oldlabels,'boundary_unchanged':D['fresh_boundary']==oldcut,'result_hash':D['result_hash'],'validator_hash':D['validator_revalidation_hash'],'review_id':'R3_FRESH_RESULT_HUMAN_REVIEW_R2','high_level_questions':7,'automatic_apply':False,'solver_executed':False})
print('R2 Human Review generated; original R1 files untouched.')
