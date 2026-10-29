import sys
sys.dont_write_bytecode=True
import json,hashlib,html,re
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone,timedelta
OUT=Path(__file__).resolve().parent
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
stamp=datetime.now(timezone(timedelta(hours=8))).isoformat()
phase='WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1'
auth=read('AUTHORIZED_POSE45_AND_INPUT_R1.json');auto=read('MINIMUM_MACHINE_AUTOMATIC_R1.json')
protection=read('SOURCE_PROTECTION_R1.json');manifest=read('RENDER_MANIFEST_R1.json')
assert len(auto['rows'])==14 and auto['automatic_status']=='PASS' and read('ZERO_RESET_R1.json')['status']=='PASS'
assert protection['native_payload_unchanged'] and sha(auth['source_asset'])==auth['source_sha256']
assert len(manifest['renders'])==26
binding=read('PALMAR_THREE_POSE_HUMAN_APPROVAL_BIND_R1.json')
binding.setdefault('recorded_at_Asia_Shanghai',stamp)
binding['original_task_source_sha256']=sha(binding['original_task_source_path'])
dump('PALMAR_THREE_POSE_HUMAN_APPROVAL_BIND_R1.json',binding)
static_names=[('DORSAL_FULL','掌背 · 整手'),('PALMAR_FULL','掌侧 · 整手'),('RADIAL_SIDE','桡侧 · 拇指侧'),('ULNAR_SIDE','尺侧 · 小指侧'),('THUMB_WEB_OBLIQUE','拇指根 / first web · 斜视'),('FINGERTIP_DISTAL_OBLIQUE','指尖 / 指甲 · 斜视')]
static={'phase':phase,'state':'RSSF / ZERO','reviewer':'Codex ordinary-solid preliminary visual screening; final Human authority retained',
        'view_count':6,'visible_issue_count':0,'status':'ACCEPTABLE_PENDING_HUMAN','human_approval':'PENDING',
        'checks':['overall proportions','dorsal/palmar silhouette','five finger roots','interdigital webs','thumb root/first web','wrist transition','nail areas'],
        'views':[{'view_id':n,'label':label,'image':f'renders/ZERO__{n}.png','classification':'NO_VISIBLE_ISSUE_OBSERVED','observation':'未观察到明显凹坑、鼓包、尖刺、塌陷、穿模或异常腕部过渡；可见轻微低模 faceting / shading。'} for n,label in static_names]}
dump('WHOLE_HAND_STATIC_VISUAL_REVIEW_R1.json',static)
issue={'case_id':'INDEX_MCP_45','location':'食指 MCP 根部靠拇指的 first-web 边缘','classification':'POSSIBLE_VISIBLE_ISSUE',
       'description':'普通斜侧整手图可见 first-web 边缘的尖角状折边；近景中呈 V 形硬折。待 Human 判断是否超出正常 crease / 轻微 faceting 的可接受范围。',
       'full_hand_screenshot':'renders/INDEX_MCP_45__ALTERNATE_FULL_HAND_SOLID.png',
       'main_screenshot':'renders/INDEX_MCP_45__FULL_HAND_SOLID.png',
       'supplements':['renders/INDEX_MCP_45__LOCAL_CLOSE.png','renders/INDEX_MCP_45__ALTERNATE.png','renders/INDEX_MCP_45__GRAZING.png'],
       'confirmed_human_visible_blocker':False,'human_decision':'PENDING','automatic_repair':False,'numerical_root_cause_research':False}
poses={'phase':phase,'case_count':14,'cases_completed':14,'no_visible_issue_observed_count':13,'possible_visible_issue_count':1,
       'clear_visible_issue_count':0,'visible_issue_count':1,'visible_issue_count_semantics':'One POSSIBLE candidate pending Human; zero confirmed CLEAR blockers.',
       'status':'POSSIBLE_VISIBLE_ISSUE_PENDING_HUMAN','human_approval':'PENDING','VISIBLE_ISSUE_CASES':[issue],
       'cases':[{'case_id':c['case_id'],'stage6a_source_case_id':c['stage6a_source_case_id'],'bone':c['bone'],'applied_rotation_deg':-45,
                 'classification':'POSSIBLE_VISIBLE_ISSUE' if c['case_id']==issue['case_id'] else 'NO_VISIBLE_ISSUE_OBSERVED',
                 'full_hand_solid':f"renders/{c['case_id']}__FULL_HAND_SOLID.png",
                 'supplemental_review':issue if c['case_id']==issue['case_id'] else None,
                 'ordinary_solid_observation':issue['description'] if c['case_id']==issue['case_id'] else '未观察到明显异常；弯曲压缩、轻微低模 faceting / shading 不作为 blocker。',
                 'obvious_new_penetration_observed':False,'gross_non_target_contamination_observed':False} for c in auth['cases']]}
dump('WHOLE_HAND_POSE45_VISUAL_REVIEW_R1.json',poses)
sentinel={'phase':phase,'method':'Ordinary solid ZERO close views plus whole-hand pose inspection; visual regression only, no region quantification.',
          'DORSAL_REPAIR_VISIBLE_REGRESSION':'NO','PALMAR_REPAIR_VISIBLE_REGRESSION':'NO','human_repair_confirmation':'PENDING',
          'sentinels':[{'repair':'dorsal54','image':'renders/ZERO__DORSAL54_SENTINEL.png','visible_regression':'NO','observation':'未见此前已修复的局部凹陷重新出现。'},
                       {'repair':'palmar16','image':'renders/ZERO__PALMAR16_SENTINEL.png','visible_regression':'NO','observation':'未见此前已修复的掌侧根部 shelf 异常重新出现；保持既有三姿 Human approval。'}],
          'INDEX_MCP45_first_web_candidate_is_repair_regression_claim':False}
dump('DORSAL_PALMAR_REPAIR_SENTINEL_R1.json',sentinel)
machine={'phase':phase,'policy':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','MACHINE_SAFETY':'PASS','case_count':14,
         'thresholds':auto['thresholds'],'NaN_Inf':0,'collapsed_faces':0,'degenerate_edges':0,'obvious_severe_stretch':0,
         'obvious_new_self_intersection_or_penetration_observed':0,'ZERO_restore':'PASS','gross_non_target_contamination':0,
         'visual_component_method':'Codex ordinary-solid inspection of complete main images; final Human authority retained. No exhaustive hidden-crossing census.',
         'possible_hard_fold_is_separate_product_visual_candidate':issue['case_id'],'hidden_crossing_census':False,
         'rows':[dict(r,obvious_penetration_and_gross_non_target_screen='NO_OBVIOUS_NEW_PENETRATION_OR_GROSS_CONTAMINATION_OBSERVED',
                      obvious_new_penetration_observed_count=0,gross_non_target_contamination_observed_count=0) for r in auto['rows']]}
dump('MINIMUM_MACHINE_SAFETY_R1.json',machine)
status={'phase':phase,'recorded_at_Asia_Shanghai':stamp,'ACCEPTANCE_POLICY':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST',
        'PALMAR_THREE_POSE_HUMAN_APPROVAL_BOUND':True,'PALMAR_ROOT_TARGETED_VISUAL_DEFORMATION_R1':'HUMAN_APPROVED',
        'STATIC_VIEW_COUNT':6,'POSE45_CASE_COUNT':14,'POSE45_CASES_COMPLETED':14,'MACHINE_SAFETY':'PASS',
        'STATIC_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN','POSE45_VISIBLE_STATUS':'POSSIBLE_VISIBLE_ISSUE_PENDING_HUMAN',
        'STATIC_VISIBLE_ISSUE_COUNT':0,'POSE45_VISIBLE_ISSUE_COUNT':1,'POSE45_POSSIBLE_VISIBLE_ISSUE_COUNT':1,'POSE45_CLEAR_VISIBLE_ISSUE_COUNT':0,
        'VISIBLE_ISSUE_CASES':[issue],'DORSAL_REPAIR_VISIBLE_REGRESSION':'NO','PALMAR_REPAIR_VISIBLE_REGRESSION':'NO',
        'DORSAL_REPAIR_REGRESSION':'NO','PALMAR_REPAIR_REGRESSION':'NO','ZERO_RESTORE':'PASS','GROSS_NON_TARGET_CONTAMINATION':0,
        'GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'RIG_WRITES':0,'JOINT_WRITES':0,'BLEND_PRODUCTION_SAVES':0,
        'SOURCE_SHA256_UNCHANGED':True,'CURRENT9_HUMAN_RESPONSE':'HOLD_NOT_CLOSED','PRODUCTION_PROMOTION':'NO',
        'WHOLE_HAND_HUMAN_APPROVAL':'PENDING','ORDINARY_SOLID_IMAGE_COUNT':26,'POSE_APPLICATION_COUNT':14,
        'VERDICT':'HUMAN_REVIEW_REQUIRED_POSSIBLE_VISIBLE_ISSUE','READY_FOR_HUMAN_WHOLE_HAND_APPROVAL':False,
        'VERDICT_REASON':'One ordinary-solid first-web hard-fold candidate awaits Human classification; no automatic repair.',
        'NEXT_IF_WHOLE_HAND_HUMAN_PASS':'CURRENT_FULL_STAGE6A_CROSSING_HUMAN_CLOSURE_R1','NEXT_EXECUTED':False,'STOP':'HUMAN REVIEW',
        'PROHIBITED_AUDITS_EXECUTED':[]}
dump('WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1_STATUS.json',status)

def card(path,title,note='',extra='',suspect=False):
    return f'<article class="card {"candidate" if suspect else ""}"><button type="button" class="image" data-image="{html.escape(path)}" data-title="{html.escape(title)}" aria-label="放大：{html.escape(title)}"><img src="{path}" alt="{html.escape(title)}" loading="lazy"></button><div class="caption"><h3>{html.escape(title)}</h3>{"<p>"+html.escape(note)+"</p>" if note else ""}{extra}</div></article>'
static_cards=''.join(card(v['image'],v['label']) for v in static['views'])
sentinel_cards=''.join(card(s['image'],s['repair']+' 修复区',s['observation']) for s in sentinel['sentinels'])
pose_cards=''
for c in poses['cases']:
    suspect=c['case_id']==issue['case_id'];extra=''
    if suspect:
        links=[(issue['full_hand_screenshot'],'普通整手 · 斜侧'),(issue['supplements'][0],'局部近景'),(issue['supplements'][1],'替代视角'),(issue['supplements'][2],'掠光')]
        extra='<details><summary>查看这一个 case 的补充视角</summary>'+''.join(f'<button type="button" class="supplement" data-image="{p}" data-title="INDEX_MCP_45 · {t}">{t}</button>' for p,t in links)+'</details>'
    pose_cards+=card(c['full_hand_solid'],c['case_id'],'first web 折边 · 待判断' if suspect else '',extra,suspect)
template=(OUT/'review_template.html').read_text(encoding='utf-8')
review=template.replace('@@STATIC@@',static_cards).replace('@@SENTINELS@@',sentinel_cards).replace('@@POSES@@',pose_cards)
(OUT/'review.html').write_text(review,encoding='utf-8')
report=f'''# {phase}

已完成静态整手六视图、dorsal54 / palmar16 sentinel、14 个正式 45° case。最低机器安全门 PASS，源资产保持不变。普通实体初筛保留 **INDEX_MCP_45 的一个 POSSIBLE_VISIBLE_ISSUE**；其余 13 case 未观察到明显产品问题。尚未获得本轮整手 Human approval，停止于 Human review。

## Human approval 绑定

以当前聊天中 Human 明确答复作为正式来源：MID_MCP_15 / 30 / 45 = ACCEPT；all_three_visually_approved = true。PALMAR_ROOT_TARGETED_VISUAL_DEFORMATION_R1 = HUMAN_APPROVED。Human 明确说明原 JSON 不在本地并授权以消息绑定。只创建本轮绑定记录，未改写历史 response 或历史报告。current9_closure_approved = false；production_promotion_approved = false。

## 唯一视觉候选

- 位置：食指 MCP 根部靠拇指的 first-web 边缘。
- pose：INDEX_MCP_45（已有正式 IDX_MCP_45，骨骼 INDEX_MCP_R，local X -45°）。
- 分类：POSSIBLE_VISIBLE_ISSUE，尚非 Human 确认 blocker。
- 描述：普通斜侧整手图可见尖角状折边，近景呈 V 形硬折；由 Human 判断是否超出正常 crease / 轻微 faceting 的可接受范围。
- 普通整手截图：[斜侧实体图]({issue['full_hand_screenshot']})；[主实体图]({issue['main_screenshot']})。
- 只为此 case 追加近景、替代、掠光和普通整手斜侧证据。未展开数值根因研究，未自动修复。

## 视觉与最低安全门

静态六视图初筛：未观察到明显异常，ACCEPTABLE_PENDING_HUMAN。指甲、指缝、拇指根、掌背轮廓、腕部过渡纳入普通实体检查。轻微低模 faceting / shading 保留，未据此自动升级。dorsal54 / palmar16 回退初筛 = NO / NO。

14 个 45° case 各自执行 RESET ZERO → 单骨 local X -45° → evaluate → render → RESET ZERO。有限值、面塌陷、边退化、明显严重拉伸均为 0；ZERO restore 14/14 PASS；WRIST_R 与 THUMB_CMC_R 保持锁定 ZERO。普通实体中未观察到明显新增穿模或严重邻指误带动，gross non-target contamination = 0。检查沿用已有最低阈值，不运行 hidden triangle crossing census。

初始斜侧相机遮住部分无名指 / 小指动作。展示阶段使用已评估的坐标替换 12 个四指主图为 distal/dorsal oblique，相机与灯光改变不施加新 pose，不打开源 blend。两个拇指主图保留可见拇指的斜侧视角。全手视图统一 scale / 中性材质 / studio lighting，sentinel 使用正常局部近景 scale。最终共 26 张普通实体图。

## 保护

源资产：`{auth['source_asset']}`

SHA256 前后均为 `{auth['source_sha256']}`。原始 mesh 坐标、拓扑、权重、rig rest bones、modifiers、groups 等 native payload 前后完全一致，最终 ZERO。GEOMETRY_WRITES = WEIGHT_WRITES = RIG_WRITES = JOINT_WRITES = BLEND_PRODUCTION_SAVES = 0。

未执行 R3、true-cap、2127-edge continuity、normal-dot、weight solver、joint fitting、anatomy / retopo research、Full42 或 Stage6B；未重做 dorsal54 / palmar16 因果研究；未检查 current9 forensic pairs。

## 最终字段

| 字段 | 结果 |
|---|---|
| PALMAR_THREE_POSE_HUMAN_APPROVAL_BOUND | true |
| STATIC_VIEW_COUNT | 6 |
| POSE45_CASE_COUNT / COMPLETED | 14 / 14 |
| MACHINE_SAFETY | PASS |
| STATIC_VISIBLE_ISSUE_COUNT | 0 |
| POSE45_VISIBLE_ISSUE_COUNT | 1 POSSIBLE，0 CLEAR |
| VISIBLE_ISSUE_CASES | INDEX_MCP_45 |
| DORSAL / PALMAR_REPAIR_VISIBLE_REGRESSION | NO / NO |
| ZERO_RESTORE | PASS |
| GROSS_NON_TARGET_CONTAMINATION | 0 |
| GEOMETRY / WEIGHT / RIG / JOINT_WRITES | 0 / 0 / 0 / 0 |
| BLEND_PRODUCTION_SAVES | 0 |
| CURRENT9_HUMAN_RESPONSE | HOLD_NOT_CLOSED |
| PRODUCTION_PROMOTION | NO |
| VERDICT | HUMAN_REVIEW_REQUIRED_POSSIBLE_VISIBLE_ISSUE |

## Human 回答

打开 [review.html](review.html)，只回答：

1. Q1：静态整手 ACCEPT / VISIBLE_ISSUE。
2. Q2：14 动作 ACCEPT_ALL / ISSUE_IN_CASES（如有问题，case ID + 简短描述）。尤其判断 INDEX_MCP_45 折边是否可接受。
3. Q3：dorsal54 / palmar16 修复保持 YES / NO。

若 Human 接受该候选并确认整手通过，才可将本轮记录为 whole-hand Human PASS。NEXT 条件为 CURRENT_FULL_STAGE6A_CROSSING_HUMAN_CLOSURE_R1，本轮未执行 NEXT。STOP — HUMAN REVIEW。
'''
(OUT/'WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1_REPORT.md').write_text(report,encoding='utf-8')
class References(HTMLParser):
    def __init__(self):super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ['src','href','data-image'] and v and not v.startswith('#'):self.paths.append(v)
refs=References();refs.feed(review)
assert all((OUT/p).is_file() for p in refs.paths), 'Missing review page asset'
assert all('@@' not in s for s in [review]), 'Unfilled review template'
required=['WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1_REPORT.md','WHOLE_HAND_SURFACE_INTEGRITY_BASELINE_R1_STATUS.json',
          'WHOLE_HAND_STATIC_VISUAL_REVIEW_R1.json','WHOLE_HAND_POSE45_VISUAL_REVIEW_R1.json','DORSAL_PALMAR_REPAIR_SENTINEL_R1.json',
          'MINIMUM_MACHINE_SAFETY_R1.json','PALMAR_THREE_POSE_HUMAN_APPROVAL_BIND_R1.json','review.html']
assert all((OUT/p).is_file() for p in required)
for p in OUT.glob('*.json'):json.loads(p.read_text(encoding='utf-8-sig'))
dump('DELIVERY_VERIFICATION_R1.json',{'status':'PASS','required_outputs_present':True,'review_local_references_all_resolve':True,
     'ordinary_solid_render_count':len(list((OUT/'renders').glob('*.png'))),'all_output_json_parse':True,
     'source_sha256_matches':sha(auth['source_asset'])==auth['source_sha256'],'browser_preview':'http://127.0.0.1:8847/review.html',
     'human_response_fields_unselected':True,'source_protection_result':'PASS'})
dump('FINAL_EVIDENCE_MANIFEST_R1.json',{'phase':phase,'recorded_at_Asia_Shanghai':stamp,
     'files':[{'path':p.relative_to(OUT).as_posix(),'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='FINAL_EVIDENCE_MANIFEST_R1.json']})
print(json.dumps({k:status[k] for k in ['VERDICT','MACHINE_SAFETY','STATIC_VIEW_COUNT','POSE45_CASES_COMPLETED','VISIBLE_ISSUE_CASES','ZERO_RESTORE']},ensure_ascii=False,indent=2))
