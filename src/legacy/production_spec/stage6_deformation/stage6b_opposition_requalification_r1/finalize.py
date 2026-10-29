import sys
sys.dont_write_bytecode=True
import json,hashlib,html
from pathlib import Path
from datetime import datetime,timezone,timedelta
from html.parser import HTMLParser
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
PHASE='STAGE6B_OPPOSITION_REQUALIFICATION_R1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
stamp=datetime.now(timezone(timedelta(hours=8))).isoformat()
auto=read(OUT/'STAGE6B_MINIMUM_MACHINE_AUTOMATIC_R1.json');matrix=read(OUT/'STAGE6B_CURRENT_9_CASE_MATRIX_R1.json');proof=read(OUT/'SOURCE_PROTECTION_R1.json')
assert len(auto['rows'])==9 and auto['automatic_status']=='PASS' and read(OUT/'STAGE6B_ZERO_RESET_R1.json')['status']=='PASS'
assert read(OUT/'PREREQUISITE_VERIFICATION_R1.json')['status']=='PASS' and proof['native_payload_unchanged']
assert sha(proof['source']['path'])==proof['source_sha256_before']==proof['source_sha256_after']
l3=['CMC_OPP_30','CMC_MCP_L3','FULL_OPP_L3'];cases=[c['case_id'] for c in matrix['cases']]
screen_rows=[]
for cid in cases:
 screen_rows.append({'case_id':cid,'classification':'NO_VISIBLE_ISSUE_OBSERVED','visible_status':'ACCEPTABLE_PENDING_HUMAN',
  'ordinary_full_hand':f'renders/{cid}__FULL_HAND_SOLID.png','thumb_palmar_oblique':f'renders/{cid}__THUMB_PALMAR_OBLIQUE_SOLID.png',
  'close_views':[f'renders/{cid}__{v}.png' for v in ['THUMB_CLOSE','FIRST_WEB_CLOSE','PALMAR_CLOSE']] if cid in l3 else [],
  'observation':'未观察到 gross tearing、thumb flap、尖刺、表面破裂、明显穿入 palm/index/middle、first-web collapse 或 gross 邻指误带动。可见 opposition 压缩、接触投影、局部 crease、低模 faceting / shading，按产品可见原则保留。',
  'thumb_distal_torn_flap':'ABSENT','first_web_visible_collapse':False,'obvious_gross_penetration':False,'gross_non_target_contamination':False,
  'nail_observation':'普通实体图中未观察到明显指甲崩坏。','dorsal54_visible_regression':'NO','palmar16_visible_regression':'NO',
  'human_approval':'PENDING','extra_forensic_required':False})
screen={'phase':PHASE,'ACCEPTANCE_POLICY':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','reviewer':'Codex ordinary-solid preliminary inspection; final Human authority retained',
 'case_count':9,'NO_VISIBLE_ISSUE_OBSERVED':9,'POSSIBLE_VISIBLE_ISSUE':0,'CLEAR_VISIBLE_ISSUE':0,'VISIBLE_ISSUE_CASES':[],
 'STAGE6B_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN','rows':screen_rows,'all_main_and_required_close_renders_inspected':True,
 'normal_opposition_contact_or_compression_is_not_automatic_failure':True,'human_approval':'PENDING','hidden_crossing_census':False}
dump('STAGE6B_VISIBLE_SCREEN_R1.json',screen)
visual_keys={'gross_tearing_count':0,'visible_thumb_flap_count':0,'gross_surface_break_count':0,'obvious_gross_penetration_count':0,'first_web_visible_collapse_count':0,'gross_non_target_contamination_count':0}
machine={'phase':PHASE,'STAGE6B_MACHINE_SAFETY':'PASS','MACHINE_SAFETY_PASS_COUNT':9,'automatic_minimum_pass_count':9,
 'thresholds':auto['thresholds'],'threshold_rule_reused_without_optimization':True,'visual_gate_method':'Direct ordinary-solid screening of full-hand, thumb/palmar oblique, and required L3 closes. Counts describe observed gross defects, not absence of all mathematical crossings.',
 'NaN_Inf_count':0,'collapsed_face_count':0,'degenerate_edge_count':0,'obvious_severe_stretch_count':0,**visual_keys,'ZERO_restore':'PASS',
 'rows':[dict(x,ordinary_solid_gross_surface_screen='PASS_NO_GROSS_VISIBLE_FAILURE_OBSERVED',**visual_keys,minimum_safety_status='PASS') for x in auto['rows']],
 'hidden_crossing_census':False,'proxy_penetration_ranking':False,'normal_dot_audit':False,'minimum_safety_requires_final_Human_visual_approval':False,'product_naturalness_Human_approval':'PENDING'}
dump('STAGE6B_MINIMUM_MACHINE_SAFETY_R1.json',machine)
old_files={'CMC_OPP_30':'STAGE6B_CMC_OPP_30_BEFORE_AFTER.png','CMC_MCP_L3':'STAGE6B_CMC_MCP_L3_BEFORE_AFTER.png','FULL_OPP_L3':'STAGE6B_FULL_OPP_L3.png'}
old={'phase':PHASE,'OLD_VISIBLE_TORN_FLAP_REAPPEARS':'NO','OLD_STAGE6B_TORN_FLAP_REAPPEAR_COUNT':0,
 'historical_scope':'HISTORICAL_PRE_R2_COMPARATOR','old_failure_not_used_as_current_verdict':True,'historical_numeric_forensic_not_reanalyzed':True,
 'comparators':[{'case_id':cid,'historical_ordinary_render':ref(ROOT/'production_spec/stage6_deformation/stage6b/renders'/name),'role':'HISTORICAL_PRE_R2_COMPARATOR','CURRENT':'ABSENT','current_ordinary_render':f'renders/{cid}__THUMB_PALMAR_OBLIQUE_SOLID.png','observation':'旧 gross 破面 / 远端撕裂 flap 在当前 fresh 普通实体图中未复现。光照、shade 和 camera 不匹配，仅做 gross 可见缺陷对照，不据此量化差异。'} for cid,name in old_files.items()],
 'all9_current_screen':[{'case_id':cid,'CURRENT':'ABSENT','old_visible_torn_flap_reappears':'NO'} for cid in cases],'human_confirmation':'PENDING'}
dump('STAGE6B_OLD_TORN_FLAP_REGRESSION_R1.json',old)
sentinel={'phase':PHASE,'DORSAL54_VISIBLE_REGRESSION':'NO','PALMAR16_VISIBLE_REGRESSION':'NO','method':'ZERO ordinary-close sentinel images + all9 ordinary posed views; no region numerical reanalysis.',
 'rows':[{'repair':'dorsal54','visible_regression':'NO','image':'renders/ZERO__DORSAL54_SENTINEL.png'},{'repair':'palmar16','visible_regression':'NO','image':'renders/ZERO__PALMAR16_SENTINEL.png'}],'Human_confirmation':'PENDING'}
dump('STAGE6B_DORSAL_PALMAR_REPAIR_SENTINEL_R1.json',sentinel)
status={'phase':PHASE,'recorded_at_Asia_Shanghai':stamp,'ACCEPTANCE_POLICY':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST','PREREQUISITES':'PASS',
 'FORMAL_CASE_COUNT':9,'FORMAL_CASES_COMPLETED':9,'OPPOSITION_VECTOR_AUTHORITY_REUSED':True,'POSE_DEFINITION_REUSED':True,
 'MACHINE_SAFETY_PASS_COUNT':9,'NAN_INF_COUNT':0,'COLLAPSE_COUNT':0,'DEGENERATE_COUNT':0,'OBVIOUS_SEVERE_STRETCH_COUNT':0,
 'GROSS_TEARING_COUNT':0,'VISIBLE_THUMB_FLAP_COUNT':0,'GROSS_SURFACE_BREAK_COUNT':0,'OBVIOUS_GROSS_PENETRATION_COUNT':0,
 'FIRST_WEB_VISIBLE_COLLAPSE_COUNT':0,'GROSS_NON_TARGET_CONTAMINATION':0,'ZERO_RESTORE':'PASS','OLD_STAGE6B_TORN_FLAP_REAPPEAR_COUNT':0,
 'CMC_OPP_30_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN','CMC_MCP_L3_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN','FULL_OPP_L3_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN',
 'OTHER6_VISIBLE_ISSUE_COUNT':0,'CLEAR_VISIBLE_ISSUE_COUNT':0,'POSSIBLE_VISIBLE_ISSUE_COUNT':0,'VISIBLE_ISSUE_CASES':[],
 'DORSAL54_VISIBLE_REGRESSION':'NO','PALMAR16_VISIBLE_REGRESSION':'NO','GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'RIG_WRITES':0,'JOINT_WRITES':0,'MODIFIER_WRITES':0,'BLEND_PRODUCTION_SAVES':0,
 'PRODUCTION_PROMOTION':'NO','STAGE6B_MACHINE_SAFETY':'PASS','STAGE6B_VISIBLE_STATUS':'ACCEPTABLE_PENDING_HUMAN','STAGE6B_HUMAN_PRODUCT_QUALIFICATION':'PENDING_HUMAN',
 'CMC_DEFORMATION_FINAL':'NOT_SET_PENDING_HUMAN','COMBINED_THUMB_OPPOSITION':'NOT_SET_PENDING_HUMAN','HUMAN_PASS_AUTOMATICALLY_RECORDED':False,
 'FULL_OPP_L3_PURPOSE':'DIAGNOSTIC_FULL_CHAIN_OPPOSITION_STRESS_CASE','STANDARD_TEACHING_POSE_OR_ROM_DEFINED':False,
 'FRESH_POSE_CASE_APPLICATIONS':9,'ORDINARY_SOLID_RENDER_COUNT':29,'EXTRA_FORENSIC_RENDER_COUNT':0,'PROTECTED_HISTORY_DRIFT':'PENDING_FINAL_FILE_HASH_VERIFICATION',
 'VERDICT':'READY_FOR_HUMAN_STAGE6B_VISUAL_APPROVAL','NEXT_EXECUTED':False,'STOP':'HUMAN REVIEW',
 'FUTURE_TEACHING_MOTION_ROUTE_IF_HUMAN_PASS':'Prefer existing piano motion / dataset -> retarget to current 21-bone hand -> Human-visible validation; no manual full piano-motion suite started.',
 'prohibited_audits_executed':[]}
dump('STAGE6B_OPPOSITION_REQUALIFICATION_R1_STATUS.json',status)

def button(path,label,cls='image'):
 return f'<button type="button" class="{cls}" data-image="{path}" data-title="{html.escape(label)}" aria-label="放大：{html.escape(label)}"><img src="{path}" alt="{html.escape(label)}" loading="lazy"></button>'
top=''
for cid in l3:
 top+=f'<article class="case"><h3>{cid}</h3>'+button(f'renders/{cid}__FULL_HAND_SOLID.png',cid+' · 整手')+'<div class="mini">'+button(f'renders/{cid}__THUMB_CLOSE.png',cid+' · 拇指 / 掌侧近景')+button(f'renders/{cid}__FIRST_WEB_CLOSE.png',cid+' · first web 近景')+'</div><p class="legend">整手 ↑　拇指 / 掌侧近景 · first web ↑</p><details><summary>其它普通实体视角</summary>'+''.join(f'<button class="link" type="button" data-image="renders/{cid}__{v}.png" data-title="{cid} · {label}">{label}</button>' for v,label in [('THUMB_PALMAR_OBLIQUE_SOLID','掌侧斜视'),('PALMAR_CLOSE','掌侧近景')])+'</details></article>'
compact=''
for cid in cases:
 if cid in l3:continue
 compact+=f'<article class="case small"><h3>{cid}</h3>'+button(f'renders/{cid}__THUMB_PALMAR_OBLIQUE_SOLID.png',cid+' · 掌侧斜视')+f'<button class="link" type="button" data-image="renders/{cid}__FULL_HAND_SOLID.png" data-title="{cid} · 整手">查看整手</button></article>'
sentinels=''.join(f'<article class="sentinel"><strong>{s["repair"]} · 未见回退</strong><button class="link" type="button" data-image="{s["image"]}" data-title="{s["repair"]} sentinel">查看实体图</button></article>' for s in sentinel['rows'])
template=(OUT/'review_template.html').read_text(encoding='utf-8');review=template.replace('@@L3@@',top).replace('@@OTHER@@',compact).replace('@@SENTINELS@@',sentinels)
(OUT/'review.html').write_text(review,encoding='utf-8')
angle_table='\n'.join(f"| {c['case_id']} | {c['cmc_deg']:g} | {c['mcp_deg']:g} | {c['ip_deg']:g} | PASS | NO_VISIBLE_ISSUE_OBSERVED |" for c in matrix['cases'])
field_table='\n'.join(f'| {k} | {v} |' for k,v in status.items() if k in ['FORMAL_CASE_COUNT','FORMAL_CASES_COMPLETED','OPPOSITION_VECTOR_AUTHORITY_REUSED','POSE_DEFINITION_REUSED','MACHINE_SAFETY_PASS_COUNT','NAN_INF_COUNT','COLLAPSE_COUNT','DEGENERATE_COUNT','GROSS_TEARING_COUNT','VISIBLE_THUMB_FLAP_COUNT','OBVIOUS_GROSS_PENETRATION_COUNT','FIRST_WEB_VISIBLE_COLLAPSE_COUNT','GROSS_NON_TARGET_CONTAMINATION','ZERO_RESTORE','OLD_STAGE6B_TORN_FLAP_REAPPEAR_COUNT','CMC_OPP_30_VISIBLE_STATUS','CMC_MCP_L3_VISIBLE_STATUS','FULL_OPP_L3_VISIBLE_STATUS','OTHER6_VISIBLE_ISSUE_COUNT','DORSAL54_VISIBLE_REGRESSION','PALMAR16_VISIBLE_REGRESSION','GEOMETRY_WRITES','WEIGHT_WRITES','RIG_WRITES','PRODUCTION_PROMOTION','STAGE6B_MACHINE_SAFETY','STAGE6B_VISIBLE_STATUS','VERDICT'])
report=f'''# {PHASE}

9/9 fresh historical Stage6B diagnostic cases completed on the actual repaired R2 asset. Minimum machine safety **PASS**; Codex ordinary-solid screen **ACCEPTABLE_PENDING_HUMAN**. Old gross torn flap not observed in any current case; no CLEAR visible issue observed. Final verdict: **READY_FOR_HUMAN_STAGE6B_VISUAL_APPROVAL**. STOP — HUMAN REVIEW.

## Prerequisites and unchanged authority

Stage6A Human PASS receipts verified, including stored receipt hashes. Actual asset SHA256 `{proof['source_sha256_after']}` and actual read-back weight hash `{proof['weight_hash_before']}` match the authorized frozen inputs before any nonzero pose.

Original stored vector from STAGE6B_OPPOSITION_VECTOR_AUDIT.json = `{matrix['stored_authority_raw']}`. Historical normalization reused = `{matrix['normalized_authority_as_historical_execution']}`; twist sign = -1. The stored float values were retained, not replaced by prompt digits. Single local XYZ exponential-map quaternion for CMC; MCP/IP use negative local-X flexion. The twist sign is already encoded in the vector and is not multiplied a second time. No axis probe, Jacobian solve, vector search or anatomy work performed.

Original pose definitions are reused without angle changes:

| Case | CMC degrees | MCP degrees | IP degrees | Minimum safety | Ordinary-solid screen |
|---|---:|---:|---:|---|---|
{angle_table}

All nine are DIAGNOSTIC / STRESS TEST POSES, not teaching-pose values, piano ROM or actual piano motion. FULL_OPP_L3 remains DIAGNOSTIC_FULL_CHAIN_OPPOSITION_STRESS_CASE.

## Fresh execution and minimum safety

Each case: RESET ZERO → apply the stored current case → evaluate → ordinary render → minimum safety check → RESET ZERO. Nine cases applied once each; no historical verdict imported. All NaN/Inf, collapse, degenerate and obvious severe-stretch counts = 0. Topology unchanged and only authorized thumb channels active; all 21 pose channels ZERO at each reset. ZERO restore 9/9 PASS.

Gross tearing / thumb flap / surface break / gross penetration / first-web collapse / gross non-target contamination are ordinary-solid observed counts, all 0. These counts do not claim all mathematical crossings are absent. Normal contact, first-web compression, thenar compression and minor faceting / shading were not treated as automatic failure. No hidden crossing census, proxy penetration ranking, normal-dot, 2127 static edges, true-cap or R3 runs.

## Ordinary visual screen

All 29 current ordinary-solid renders inspected: 18 main views (full hand + thumb/palmar oblique for every case), 9 required L3 close views (thumb / first web / palm), and 2 ZERO repair sentinels. Camera directions and scale fixed within each camera family, with framing center following the evaluated region; neutral material and stable studio lighting reused. Display copies preserve all native faces and evaluated coordinates; smooth shading is display-only. No extra grazing or forensic images were necessary.

No obvious distal torn flap, spike, first-web tearing or collapse, palm surface break, gross penetration through another finger, nail breakdown or gross neighbor-digit contamination observed. CMC30 root compression and crease remain visible in the evidence and are for final Human product-naturalness judgment. dorsal54 / palmar16 visible regression = NO / NO; both ZERO sentinels and ordinary posed context inspected without region quantification.

Three old same-case ordinary render sheets were read solely as HISTORICAL_PRE_R2_COMPARATOR. The old gross distal torn flap / break is CURRENT ABSENT. Cameras and shade differ, so the comparison supports only gross visible regression screening. No old forensic metric analysis copied, no old FAIL inherited as the current verdict, and no Stage6B PASS inferred from Stage6A.

## Production protection

Original native mesh geometry/topology, weights, rest rig, groups, modifiers and transforms match before/after in memory. Actual production asset SHA256 unchanged, final pose ZERO / RSSF. GEOMETRY_WRITES = WEIGHT_WRITES = RIG_WRITES = JOINT_WRITES = MODIFIER_WRITES = BLEND_PRODUCTION_SAVES = 0. Protected preexisting file comparison is recorded in PRODUCTION_READONLY_NO_DRIFT_VERIFICATION.json after final verification. Historical Stage6A closures and old Stage6B reports are retained unchanged.

## Final fields

| Field | Result |
|---|---|
{field_table}

## Human review

Open [review.html](review.html). The first section shows CMC_OPP_30, CMC_MCP_L3 and FULL_OPP_L3 (ordinary full / thumb-palm close / first-web close); the second shows the other six cases compactly; the third shows repaired-region sentinels. No forensic tables in the main page.

1. Q1: CMC family acceptable? ACCEPT / VISIBLE_ISSUE.
2. Q2: CMC+MCP / FULL family acceptable? ACCEPT / VISIBLE_ISSUE; case ID + brief description if needed.
3. Q3: dorsal54 / palmar16 maintained, with no obvious thumb flap / penetration / collapse? YES / NO.

Human product qualification is PENDING. CMC_DEFORMATION_FINAL and COMBINED_THUMB_OPPOSITION remain NOT_SET_PENDING_HUMAN. No teaching-pose definition, motion creation, left hand, web export or production promotion. Future actual teaching motion route remains existing piano motion / dataset → retarget current 21-bone hand → Human-visible validation. No NEXT executed.
'''
(OUT/'STAGE6B_OPPOSITION_REQUALIFICATION_R1_REPORT.md').write_text(report,encoding='utf-8')
class References(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href','data-image'] and v and not v.startswith('#'):self.paths.append(v)
refs=References();refs.feed(review);assert all((OUT/p).is_file() for p in refs.paths)
assert len(read(OUT/'RENDER_MANIFEST_R1.json')['renders'])==29 and len(list((OUT/'renders').glob('*.png')))==29
print('OUTPUTS_READY:9/9 PASS;29 ordinary renders;Human approval pending;source unchanged')
