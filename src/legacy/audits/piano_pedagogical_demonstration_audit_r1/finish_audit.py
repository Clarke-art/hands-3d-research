import json,hashlib,collections,urllib.request
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent/'minuet_stage_c_lightweight_animation_poc_r1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
before=read(P/'PROTECTED_INPUTS_BEFORE.json');changed=[]
for p,h in before.items():
 path=Path(p)
 if not path.exists():changed.append(p);continue
 with path.open('rb') as f:new=hashlib.file_digest(f,'sha256').hexdigest()
 if new!=h:changed.append(p)
assert not changed,changed
save('ASSET_PRESERVATION.json',dict(files_compared=len(before),changed=changed,historical_baseline_count=6727,lightweight_candidate_and_media_included=True,method='Pre/post SHA256 plus matching existing 6727-file historical freeze manifest. Read-only evaluation preceded snapshot but made no writes; all historical files match recorded pre-existing hashes. No claims for files outside this manifest.',new_motion_solves=0,new_dynamic_candidates=0))
notes=read(P/'NOTE_INDEX.json');counts=dict(collections.Counter(n['teaching'] for n in notes));unknown=[n['note_id'] for n in notes if n['spatial']=='UNKNOWN']
for view in ['TEACHING','OVERHEAD','SIDE_OBLIQUE']:
 assert len(list((S/'_frames'/view).glob('*.png')))==357
 for n in notes:
  for f in n['evidence_frames'].values():assert (S/f'_frames/{view}/{f:04d}.png').exists()
url='http://127.0.0.1:8769/audits/minuet_stage_c_lightweight_animation_poc_r1/normal_speed_teaching_NOT_APPROVED.mp4'
with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':'bytes=0-99'})) as r:
 assert r.status==206 and len(r.read())==100
save('DELIVERY_VERIFICATION.json',dict(midi_events_verified=46,notes=23,phase_samples=138,source_frames_per_view=357,view_count=3,all_phase_images_exist=True,http_byte_ranges='PASS 206 / 100 bytes',browser_23_note_links='PASS: all selected correct nearest original PNG and 1280px width',browser_rates='PASS: observed actual playbackRate 1, 0.5, 0.25 and paused=false',browser_seek='PASS: R11 starts at 3.783333s; side view B02 starts at 3.833333s',browser_frame_step='PASS: R11 frame227 -> 228',browser_view_switch='PASS: same frame retained; three views load',continuous_slow_motion_subjective_review='HUMAN_PENDING; agent inspected original stills/sequences, not a continuous perceptual study',source_preservation='PASS'))
save('FINAL_STATUS.json',dict(ALL_23_NOTE_MAPPING='PASS',ACTIVE_KEY_CONTACT='PASS',KEY_PRESS_HOLD_RELEASE='PARTIAL',SLOW_MOTION_SPATIAL_CORRECTNESS='FAIL',PEDAGOGICAL_DEFECTS=dict(BLOCKING=3,WARN=2,counting='issue groups, not frames or affected notes'),NOTE_TEACHING_RESULTS=counts,FINGERING_PROFESSIONAL_APPROVAL='DESIGN_PROVISIONAL',NORMAL_SPEED_VISUAL_ACCEPTANCE='HUMAN_PREVIOUSLY_ACCEPTED',PEDAGOGICAL_DEMONSTRATION_QUALITY='HUMAN_PENDING',NEW_MOTION_SOLVES=0,NEW_DYNAMIC_CANDIDATES=0,FROZEN_ASSETS_UNCHANGED='YES',PROTECTED_FILES_CHECKED=len(before),FINAL_STATUS='READY_FOR_HUMAN_PEDAGOGICAL_REVIEW',AUDIT_MODE='PEDAGOGICAL_AUDIT_ONLY',STOP='HUMAN REVIEW',candidate_sha256=read(S/'SCENE_MANIFEST.json')['sha256'],completion=dict(note_index=True,all_23_notes_assessed=True,skin_key_phase_samples=138,three_original_media=True,review_page_browser_verified=True,standards_and_defects=True),evidence_limits=dict(spatial_unknown_notes=unknown,continuous_slow_motion_perception='HUMAN_PENDING',professional_fingering='UNKNOWN / DESIGN_PROVISIONAL',real_piano_repetition_mechanics='UNKNOWN: no hammer/action model',contact='Finite actual skin vertices + original normal-view images; no continuous whole-surface proof',geometry='Reused current candidate new-branch diagnostics; no old source depths substituted'),next_stage='Human reviews B01/B02/B03, W01/W02 and UNKNOWN notes; only after separate authorization consider the three bounded corrections. No repair performed.',historical_engineering_status='FAIL_CLOSED / NOT_APPROVED unchanged'))
answers='''# 最终十二问

当前已具备独立 Human 教学审核条件；尚不具备直接向初学者发布、反复模仿的通过结论。

1. **Q1 — 正确候选手指/琴键？** PASS。23 音及 46 个事件与实际 MIDI 对齐；对应 skin 顶点在触键/持键样本中落于目标可奏键面范围。包含 F♯5 黑键；不是只验证音名映射。
2. **Q2 — 哪些触键可信？** 全部 23 音的有限六阶段检查支持主动触键；左手和弦三指共同下沉，右手黑键高度得到体现。触键 PASS 不覆盖旁边闲置指穿模，也不是全时连续接触证明。
3. **Q3 — 明显悬空？** 已查 NOTE_ON、+40ms、持键、NOTE_OFF 的实际 skin 样本与关键图未发现主动指明显悬空。准备/释放升高是正常阶段，不能拿它当悬空持键。
4. **Q4 — 误导性邻指重叠？** 有。约 1.1–1.2s 与 3.73–3.87s，当前原帧可见中指/无名指融合或交叉，当前 skin 相交佐证。列 B01/B02 BLOCKING。0.5×/0.25× 的连续主观显著性待 Human 确认；暂停错误本身不能用原速接受豁免。
5. **Q5 — 黑键穿模？** 当前候选有。2.600s 食指/A♯4、4.050s 中指/D♯5、4.916667s 无名指/C♯5 的原视角画面与实际 skin 内部命中支持 B03 BLOCKING。G♯4 可见影响不够明确，W01，不凭深度单独升级。
6. **Q6 — 左手教学价值？** 有条件支持。7 音自身触键/持键/释放检查通过，开头 G3+B3+D4 为 5/3/1 指，后续 A3/B3/C4/B3 落点保持；原片同时包含右手阻断问题。左手闲置指伸展和专业手型仍待教师确认。
7. **Q7 — 无害工程瑕疵？** 已查主动键附近亚毫米级 skin 正间隙或浅接触未破坏触键理解，不要求逐顶点零间隙；只有投影覆盖而无相交证据也不能直接定穿模。其余黑键命中不可一概称无害，8 个右手音空间结论 UNKNOWN。
8. **Q8 — 必须修复什么？** 审核建议必须修复 B01/B02 的独立手指位置/交替表达，以及 B03 中可见嵌入黑键的闲置指路径。它们可能让学生模仿物理上不可行的动作。
9. **Q9 — 专业指法仍不确定？** 是。候选指法、E5 进入的跨指方式、同指重复 G4、闲置指伸展及左手手型是否适合初学者，仍为 DESIGN_PROVISIONAL；本轮不代替钢琴教师认可。
10. **Q10 — 可提交真正 Human 验收？** 可以。审核页面可独立查看原三视角、1×/0.5×/0.25×、原帧和 23 音六阶段，并定位缺陷。READY_FOR_HUMAN_PEDAGOGICAL_REVIEW 表示交付准备完成，教学质量仍 HUMAN_PENDING，不能等同通过。
11. **Q11 — 最小下一步？** 先审 B01/B02 的两个交接窗，再审 B03 的三个黑键片段；只有另行授权后才考虑局部修复。W01/W02 和 8 个 UNKNOWN 音先补 Human 判断，不直接展开全键盘优化。本轮零修复。
12. **Q12 — 冻结资产与历史是否保护？** 是。7,911 个受保护文件前后 SHA256 一致，其中 6,727 个亦匹配既有历史冻结记录；含唯一候选、MIDI、原媒体、历史资产。无新运动求解、无新动态候选、无 Blend 保存、无 Rig/权重/琴键修改。结论范围以清单为准，历史 FAIL_CLOSED / NOT_APPROVED 保留。

## 明确保留的不足

右手 R01、R04、R05、R06、R08、R09、R13、R15 的其他空间命中教学可见性不足，综合 UNKNOWN；它们的主动触键检查仍 PASS。全部慢速连续观看的主观显著性由 Human 决定，不伪装成已经完成的视觉实验。原帧近邻定位与事件子帧的误差在页面中分开显示。

STOP — HUMAN REVIEW
'''
(P/'FINAL_ANSWERS.md').write_text(answers,encoding='utf8')
(P/'OPEN_REVIEW.txt').write_text('当前入口：http://127.0.0.1:8769/audits/piano_pedagogical_demonstration_audit_r1/HUMAN_REVIEW.html\n若服务已停止：在本目录运行 python serve_review.py，再打开上述地址。\nHUMAN_REVIEW.html 可直接双击，若浏览器对本地 MP4 定位有限制，请使用此支持 Range 的本地服务。\n只绑定 127.0.0.1，无外网发布。\n',encoding='utf8')
print('FINAL',counts,'PROTECTED',len(before),'UNCHANGED')
