import json,hashlib,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
PHASE='OFFICIAL_L1_FIRST_WEB_TARGETED_DEFORMATION_FIX_R1'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
proof=read('PRESERVATION_AND_MINIMUM_SAFETY_R1.json');key=read('CORRECTIVE_KEY_R1.json');weight=read('WEIGHT_ITERATION_2.json');manifest=read('MATCHED_RENDER_MANIFEST_R1.json')
cases=manifest['case_ids'];candidate=ROOT/proof['candidate']['path'];candidate_sha=sha(candidate)
assert candidate_sha==proof['candidate']['sha256']==key['candidate']['sha256']
assert proof['basis_exact'] and proof['basis_vertex_writes']==0 and proof['bone_count']==21
assert all(r['automatic_status']=='PASS' and r['ZERO_RESTORE']=='PASS' and r['gross_tearing_severe_stretch_count']==0 for r in proof['checks']['AFTER'])
assert key['case_values']['ZERO']==key['case_values']['INDEX_MCP_45']==key['case_values']['FULL_OPP_L1']==0
previous=json.loads((ROOT/'audits/official_l1_product_rebase_feasibility_r1/STATIC_BIND_AND_REBASE_R1.json').read_text())
protected=[]
for name in ['source','rig_source','weight_donor','candidate']:
    row=previous[name];actual=sha(ROOT/row['path']);assert actual==row['sha256']
    protected.append({'role':name,'path':row['path'],'expected_sha256':row['sha256'],'actual_sha256':actual,'unchanged':True})
dump('INPUT_AND_PRODUCTION_PROTECTION_R1.json',{'protected':protected,'production_writes':0})
comments={
 'ZERO':'静态外形视觉一致；Basis 顶点坐标逐项相同，corrective = 0。',
 'INDEX_MCP_45':'原上缘片状台阶消失，保留自然根部 crease；corrective = 0。',
 'CMC_OPP_30':'原尖角 flap / 硬台阶消退，保留窄的软组织 crease 与轻微 L1 分面；未见虎口封闭。',
 'FULL_OPP_L1':'no-regression sentinel：未见回退，虎口自然，corrective = 0。',
 'FULL_OPP_L2':'原硬折消退，局部过渡圆滑，虎口开口仍保留。',
 'FULL_OPP_L3':'原片状尖折消退，保留正常压缩 crease，未见新 flap / collapse。'}
visual={'reviewer':'Codex preliminary visual screen, not human approval','case_ids':cases,'case_count':6,'views_per_case':['PALMAR_FULL','DORSAL_FULL','FIRST_WEB_CLOSE','WEB_GRAZING'],'cases':[{'case_id':c,'status':'PASS_CODEX_PRELIMINARY','hard_fold_blocker':False,'new_visible_defect_count':0,'gross_tearing_visible_count':0,'gross_penetration_visible_count':0,'opening_natural':True,'comment':comments[c]} for c in cases],'normal_crease_and_mild_faceting_retained':True,'human_approval':'PENDING','candidate_sha256':candidate_sha}
dump('PRELIMINARY_VISIBLE_SCREEN_R1.json',visual)
status={'PHASE':PHASE,'BASIS_GEOMETRY_CHANGED':'NO','BASIS_VERTEX_POSITION_WRITES':0,'LOCAL_WEIGHT_TUNING_VERTEX_COUNT':proof['changed_vertex_count'],'WEIGHT_ITERATION_COUNT':2,'CORRECTIVE_KEY_COUNT':1,
 **{c+'_STATUS':('PASS_VISUALLY_UNCHANGED_CODEX_PRELIMINARY' if c=='ZERO' else 'PASS_NO_REGRESSION_CODEX_PRELIMINARY' if c=='FULL_OPP_L1' else 'PASS_CODEX_PRELIMINARY') for c in cases},
 'FIRST_WEB_HARD_FOLD_REMAINING_CASE_COUNT':0,'NEW_VISIBLE_DEFECT_COUNT':0,'VISIBLE_PRODUCT_BLOCKER_COUNT':0,'ZERO_RESTORE':'PASS','MACHINE_SAFETY':'PASS_MINIMUM_NUMERICAL_AND_GROSS_VISIBLE_SCREEN','PRODUCTION_PROMOTION':'NO','VERDICT':'READY_FOR_HUMAN_VISUAL_APPROVAL','HUMAN_APPROVAL':'PENDING','STOP':'STOP — HUMAN REVIEW','candidate':proof['candidate'],'corrective_vertex_count':key['changed_vertex_count'],'zero_before_after_max_error_mm':proof['zero_before_after_max_error_mm'],'minimum_safety':{'NaN_Inf':0,'collapsed_face':0,'degenerate':0,'gross_tearing':0,'gross_penetration':0,'gross_penetration_evidence':'Ordinary matched solid render visual screen only; no hidden intersection census.'},'authorized_case_ids':cases}
dump(PHASE+'_STATUS.json',status)
rows='\n'.join(f'| {k} | {v} |' for k,v in status.items() if k in ['BASIS_GEOMETRY_CHANGED','BASIS_VERTEX_POSITION_WRITES','LOCAL_WEIGHT_TUNING_VERTEX_COUNT','WEIGHT_ITERATION_COUNT','CORRECTIVE_KEY_COUNT',*[c+'_STATUS' for c in cases],'FIRST_WEB_HARD_FOLD_REMAINING_CASE_COUNT','NEW_VISIBLE_DEFECT_COUNT','VISIBLE_PRODUCT_BLOCKER_COUNT','ZERO_RESTORE','MACHINE_SAFETY','PRODUCTION_PROMOTION','VERDICT'])
report=f'''# {PHASE}

**READY_FOR_HUMAN_VISUAL_APPROVAL — STOP — HUMAN REVIEW**

四个原失败动作中的上缘片状尖折已在普通实体图中消退到自然可接受程度。Codex 初步可见 blocker = 0；CMC30 / L3 仍保留窄的软组织 crease 与轻微低模分面，不能理解为无折痕。最终接受与否由 Human review 决定。

| 最终字段 | 结果 |
| --- | --- |
{rows}

## 局部修复

从指定输入 SHA256 `9e8b29875fc6c215ef1e0fce4f582774f10b21596835d03763edb771443b11ec` 开始。两次针对性 weight iteration 都限定同一 149 顶点支持区，只重新分配 WRIST_R / THUMB_CMC_R / THUMB_MCP_R / INDEX_MCP_R 四个已有骨骼组，保留所有其它 influence 和四组总量。通过四个失败姿态实际位移的局部曲率残差做受约束最小二乘，原权重作为软约束，边界淡出；没有重复上一轮的 generic neighbor-weight smoothing。第二次降低原权重约束系数，支持区没有扩大。两次均直接检查六状态普通实体图。

INDEX_MCP_45 的硬台阶已由权重修正消除。opposition 仍有偏锐的 crease，故停止权重调整，添加且只添加一个 `FIRST_WEB_OPPOSITION_CREASE_R1` corrective，作用于上述支持区内 {key['changed_vertex_count']} 个顶点。以 CMC30 的局部 posed surface 作小幅圆滑，再通过已有线性蒙皮逆变换写入该 shape key 的 delta；最大 posed rounding 位移 {key['max_posed_brush_delta_mm']:.6f} mm。没有写 Basis，没有添加骨骼、solver 或整手修改。

仅一个 driver、两个变量：已有 THUMB_CMC_R opposition 的 bone-local Euler X 与 THUMB_MCP_R flexion。低等级 opposition 与纯 INDEX flexion 不激活。表达式：

`{key['driver_expression']}`

本轮六个状态的 key value：ZERO = 0；INDEX_MCP_45 = 0；CMC_OPP_30 = 1；FULL_OPP_L1 = 0；FULL_OPP_L2 = {key['case_values']['FULL_OPP_L2']:.6f}；FULL_OPP_L3 = 1。阈值采用弧度，复用原骨骼局部轴；没有增加控制骨或自定义属性网络。retarget 时需保留原骨骼动作语义，本轮不执行 retarget。

## 保留与最低检查

Basis / topology / UV / 材质 / 21 骨骼层级、joint head-tail 与 rest matrix / transforms / Armature modifier 全部逐项不变；区域外所有权重逐项不变，区域内其它 influence 不变。Basis shape key 与输入坐标逐项相同。ZERO 的 before/after 求值最大差 {proof['zero_before_after_max_error_mm']:.12f} mm，为权重重分配引入的浮点误差，实体图视觉一致；各姿态恢复本 candidate ZERO 的误差均为 0 mm。这两个比较的基准不同。

只复测 ZERO、INDEX_MCP_45、CMC_OPP_30、FULL_OPP_L1/L2/L3 共六状态。NaN/Inf、collapsed face、degenerate edge、gross severe stretch 均为 0；gross tearing / gross penetration 的普通实体图可见筛查为 0。没有进行 hidden crossing census、normal-dot、true-cap、R3 或完整 Stage6 矩阵。最低机器检查不替代人眼审查。

输入 candidate、Official donor、corrected rig 与 production weight donor 的 SHA256 均保持原记录。不覆盖 production asset。

## 交付

[review.html](./review.html)：仅六个状态，每组 BEFORE / AFTER 普通掌侧 full view 与 first-web close；可展开背侧 full / grazing 辅助视图。48 张同机位原始实体图，所有原生面保留，无 cavity、无 cast shadow。评审选项均为空，不替人类选择。Human 结果可下载本地 JSON，绑定本 candidate SHA256。

DESIGN_ONLY candidate：[RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend](./RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend)，保存姿态 ZERO，SHA256 `{candidate_sha}`。

[保存重开与最低检查](./PRESERVATION_AND_MINIMUM_SAFETY_R1.json)、[权重第1轮](./WEIGHT_ITERATION_1.json)、[权重第2轮](./WEIGHT_ITERATION_2.json)、[一个 corrective 与 driver](./CORRECTIVE_KEY_R1.json)、[同机位渲染清单](./MATCHED_RENDER_MANIFEST_R1.json)、[Codex 初步可见筛查](./PRELIMINARY_VISIBLE_SCREEN_R1.json)、[输入与 production 保留](./INPUT_AND_PRODUCTION_PROTECTION_R1.json)。

浏览器核对：48/48 原始实体图载入成功，六个 Human 选项均未预填，下载按钮在未完成评审时禁用。[页面核对记录](./BROWSER_REVIEW_VERIFICATION_R1.json)。

![CMC30 同机位 before / after 与空白 Human review](./REVIEW_CMC_OPP_30_SCREENSHOT_R1.jpg)

**PRODUCTION_PROMOTION = NO. STOP — HUMAN REVIEW.**
'''
(OUT/(PHASE+'_REPORT.md')).write_text(report,encoding='utf-8')
views=[('PALMAR_FULL','普通实体 · 掌侧全景'),('FIRST_WEB_CLOSE','普通实体 · 虎口近景'),('DORSAL_FULL','普通实体 · 背侧全景'),('WEB_GRAZING','普通实体 · 斜视近景')]
def pair(c,v,title):
    return '<div class="view"><h3>'+title+'</h3><div class="pair">'+''.join(f'<figure><figcaption>{a}</figcaption><a href="renders/{a}__{c}__{v}.png" target="_blank"><img src="renders/{a}__{c}__{v}.png" alt="{a} {c} {v}" loading="eager"></a></figure>' for a in ['BEFORE','AFTER'])+'</div></div>'
sections=[]
for c in cases:
    sections.append(f'<section id="{c}" data-case="{c}"><h2>{c}</h2><p class="note">Codex 初步观察：{html.escape(comments[c])}</p>'+''.join(pair(c,v,t) for v,t in views[:2])+'<details><summary>背侧 / grazing 辅助实体图</summary>'+''.join(pair(c,v,t) for v,t in views[2:])+'</details>'+f'<label class="decision">Human review <select data-review="{c}" aria-label="{c} human review"><option value="">未评审 — 请选择</option><option value="ACCEPT">ACCEPT — 可接受</option><option value="REJECT">REJECT — 仍有可见问题</option></select></label><textarea data-notes="{c}" aria-label="{c} notes" placeholder="可选：指出可见问题的位置"></textarea></section>')
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Official L1 · First web · Human review</title><style>
*{box-sizing:border-box}body{margin:0;background:#11151b;color:#e9edf4;font:16px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1380px;margin:auto;padding:32px 24px 70px}h1{font-size:28px;line-height:1.35}h2{font-size:22px}h3{font-size:15px;color:#acb9cb;margin:24px 0 10px}a{color:#93c5fd}nav{display:flex;gap:10px;flex-wrap:wrap;margin:22px 0}nav a{padding:8px 12px;border:1px solid #394554;border-radius:6px;text-decoration:none}section{border-top:1px solid #394554;padding:24px 0 36px;scroll-margin-top:16px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0;background:#1e242c;border:1px solid #3b4655;border-radius:8px;overflow:hidden}figcaption{padding:8px 14px;font-weight:650}img{width:100%;height:auto;display:block}p{max-width:1000px}.note{color:#b1bfd0}code{overflow-wrap:anywhere;color:#b5c8dd}details{margin:22px 0}summary{cursor:pointer;color:#a6c9f0}select,textarea,button{font:inherit;background:#202936;color:#edf4ff;border:1px solid #4a5b70;border-radius:6px;padding:9px 12px}select{margin-left:16px}textarea{width:100%;margin-top:12px;min-height:70px}button{cursor:pointer;margin-top:18px;background:#284b6f}button:disabled{opacity:.4;cursor:default}.tag{color:#9fd0b2}footer{border-top:1px solid #394554;padding-top:24px}@media(max-width:700px){main{padding:20px 12px}.pair{gap:7px}h1{font-size:23px}select{display:block;margin:8px 0}}
</style></head><body><main><h1>Official L1 · 虎口上缘局部形变修复</h1><p class="tag">READY_FOR_HUMAN_VISUAL_APPROVAL · DESIGN_ONLY · STOP — HUMAN REVIEW</p><p>仅六状态同机位 BEFORE / AFTER。查看上缘是否仍有尖折、片状台阶或 flap，同时确认 ZERO 一致、L1 无回退、虎口开口自然。点击任意图片可打开原始分辨率。Codex 初步可见 blocker = 0，人类评审尚未完成。</p><p>2 次局部 weight iteration · 149 顶点 · 1 个 corrective · Basis 不变 · production promotion = NO</p><p>Candidate SHA256：<code>__SHA__</code></p><nav>__NAV__</nav>__SECTIONS__<footer><p>六项均作出选择后可下载本地评审 JSON。此结果不会自动修改候选或推广 production。</p><button id="download" disabled>下载 Human review JSON</button><p id="progress" aria-live="polite">已评审 0 / 6</p><p><a href="__REPORT__">报告</a> · <a href="__STATUS__">状态 JSON</a> · <a href="RIGHT_HAND_OFFICIAL_L1_FIRST_WEB_TUNED_DESIGN_ONLY_R1.blend">DESIGN_ONLY candidate blend</a></p></footer></main><script>
const selects=[...document.querySelectorAll('[data-review]')];const button=document.getElementById('download');function update(){const n=selects.filter(s=>s.value).length;document.getElementById('progress').textContent=`已评审 ${n} / 6`;button.disabled=n!==6;}selects.forEach(s=>s.addEventListener('change',update));button.addEventListener('click',()=>{const result={phase:'__PHASE__',candidate_sha256:'__SHA__',reviewed_at:new Date().toISOString(),production_promotion:'NO',cases:selects.map(s=>({case_id:s.dataset.review,verdict:s.value,notes:document.querySelector(`[data-notes="${s.dataset.review}"]`).value}))};const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='FIRST_WEB_HUMAN_VISUAL_REVIEW_R1.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
</script></body></html>'''
for a,b in {'__SHA__':candidate_sha,'__NAV__':''.join(f'<a href="#{c}">{c}</a>' for c in cases),'__SECTIONS__':''.join(sections),'__REPORT__':PHASE+'_REPORT.md','__STATUS__':PHASE+'_STATUS.json','__PHASE__':PHASE}.items():page=page.replace(a,b)
(OUT/'review.html').write_text(page,encoding='utf-8')
# A concise comparison for the report / chat; untouched originals remain linked.
canvas=Image.new('RGB',(1600,770),(20,24,30));draw=ImageDraw.Draw(canvas)
for k,a in enumerate(['BEFORE','AFTER']):
    canvas.paste(Image.open(OUT/'renders'/f'{a}__CMC_OPP_30__FIRST_WEB_CLOSE.png').resize((800,733)),(k*800,37));draw.text((k*800+16,12),a+' / CMC_OPP_30',fill='white')
canvas.save(OUT/'CMC_OPP_30_BEFORE_AFTER.png')
dump('FINAL_OUTPUT_MANIFEST_R1.json',{'candidate':proof['candidate'],'files':[{'path':p.relative_to(OUT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in [OUT/(PHASE+'_REPORT.md'),OUT/(PHASE+'_STATUS.json'),OUT/'review.html',OUT/'MATCHED_RENDER_MANIFEST_R1.json',OUT/'PRESERVATION_AND_MINIMUM_SAFETY_R1.json',*[OUT/r['path'] for r in manifest['renders']]]],'render_count':48,'case_count':6,'production_promotion':'NO'})
print('DELIVERED',status['VERDICT'],'149 VERTICES / 2 WEIGHT ITERATIONS / 1 KEY',candidate_sha)
