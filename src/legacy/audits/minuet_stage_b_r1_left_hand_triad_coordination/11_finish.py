from stage_common import *
import urllib.request
diag=read(P/'ENGINEERING_DIAGNOSTICS.json');fit=read(P/'COORDINATED_TRAJECTORY_FIT.json');man=read(P/'SCENE_MANIFEST.json');videos=read(P/'VIDEO_VERIFICATION.json')
protect=read(P/'FROZEN_AND_APPROVED_BASELINE_VERIFICATION.json');assert protect['all_protected_hashes_unchanged']
contacts=diag['triad_contacts'];major=diag['major_contact_mismatch_notes'];timing=diag['same_key_pressure_max_difference']<1e-6
status=dict(phase='MINUET_STAGE_B_R1_LEFT_HAND_TRIAD_COORDINATION',client_date='2026-10-10',
    LEFT_TRIAD_TARGET_MAPPING='PASS',THREE_FINGER_CONTACT='PASS' if not major else 'PARTIAL',
    SHARED_ROOT_FINGER_COORDINATION='PASS' if not major else 'PARTIAL',CHORD_TIMING_CORRECTNESS='PASS' if timing else 'FAIL',
    LEFT_HAND_NATURALNESS='HUMAN_PENDING',MUSIC_FUNCTIONAL_CORRECTNESS='PASS' if not major and timing else 'FAIL',
    ENGINEERING_DIAGNOSTICS='WARN' if not major else 'FAIL',GENERALIZABLE_CHORD_MECHANISM='IMPLEMENTED',
    STAGE_A_R2_APPROVED_BASELINE_PRESERVED='YES',FROZEN_ASSETS_UNCHANGED='YES',
    FINAL_STATUS='READY_FOR_HUMAN_REVIEW' if not major and timing else 'FAIL_CLOSED',
    technical_PASS_not_Human_naturalness_approval=True,new_dynamic_candidates=1,new_left_chord_occurrences=1,
    source_midis=[55,59,62],provisional_fingers=[5,3,1],source_on_tick=0,source_off_tick=768,
    source_duration_sec=.857142,presentation_lead_sec=.35,video_frames=100,video_fps=60,video_duration_sec=100/60,
    original_MIDI_unmodified=True,right_hand_motion_or_audio=False,full_measure_claimed=False,
    mirrored_right_trajectory=False,manual_finger_pose_patches=False,post_render_refits=0,restarts=0,
    solver_converged=fit['success'],solver_nfev=fit['nfev'],
    retained_WARN=['Finite32-point skin probe enters target B3 by up to about2.72mm; no full soft-contact/collision proof',
        'Root acceleration peak about16002mm/s² and planned C1 knot acceleration changes; not strict C2 physics',
        'Linear120Hz bake approximates the planned C1 curve',
        'Small/middle finger curve, thumb opening and idle-finger relaxation require complete1x Human review'],
    Agent_complete_realtime_audiovisual_review='NOT_PERFORMED_BROWSER_TOOL_INITIALIZATION_FAILURE',
    browser_error='windows sandbox failed: helper_unknown_error: setup refresh had errors',
    isolated_chord_pass_not_complete_Stage_B_pass=True,next_left_accompaniment_or_dual_hand_started=False,
    next_stage_ready='WAIT_FOR_HUMAN_DECISION',stop='STOP — HUMAN REVIEW')
dump('FINAL_STATUS.json',status)
attempt=read(P/'CANDIDATE_ATTEMPT.json');attempt.update(status='COMPLETED_SINGLE_CANDIDATE',performance_blends=1,views=3,post_render_refits=0);dump('CANDIDATE_ATTEMPT.json',attempt)
def write(n,t):(P/n).write_text(t,encoding='utf8')
write('TRIAD_CONTACT_AND_NATURALNESS_REVIEW.md',f'''# TRIAD_CONTACT_AND_NATURALNESS_REVIEW · Stage B R1

**{status['FINAL_STATUS']}；LEFT_HAND_NATURALNESS = HUMAN_PENDING。** 指腹数值通过不等于自然度批准；本单个和弦也不等于整个Stage B通过。

## 主审核材料

同一唯一DESIGN_ONLY候选的教学、俯视、侧斜完整原速带声视频，均100帧/60fps，约1.666667秒。原和弦持键0.857142秒，仅一次G3/B3/D4及必要准备/释放/自然回位；没有右手、后继A3、人工重奏或完整小节宣称。0.5×只在审核页作辅助，主按钮固定1×。

所有233个实际评估采样的全部左手顶点在三种预先声明的正常相机画面内，包括手掌、五指和腕端；正交比例0.56m，不是只截三指尖。原速MP4完整解码检查通过；音频只由原三个左手voice及冻结Grand样本构成。

Agent查看了生成前正常静态回读图、候选正常教学原帧以及完整阶段表，有限可见检查没有发现三个主动指仍明显悬空、琴键却发声的情况。但这些图不能代替完整1×自然度审核。浏览器工具初始化返回 `windows sandbox failed: helper_unknown_error: setup refresh had errors`，未进入页面，故Agent没有声称实时观看/听取完整1×带声播放。审核页HTTP/Range及可播放媒体另行验证，最终由Human实际观看。

## 三指接触与同步

|目标/指号|实际skin持键间隙范围mm|水平出界max mm|结果边界|
|---|---|---|---|
|G3 / 小指5|{contacts[0]['skin_gap_min_mm']:.3f} .. {contacts[0]['skin_gap_max_mm']:.3f}|{contacts[0]['horizontal_max_mm']:.3f}|本实例有限触键数据支持；小指弯曲自然性待审。|
|B3 / 中指3|{contacts[1]['skin_gap_min_mm']:.3f} .. {contacts[1]['skin_gap_max_mm']:.3f}|{contacts[1]['horizontal_max_mm']:.3f}|本实例有限触键数据支持；中指曲度与目标键接触邻域待审。|
|D4 / 拇指1|{contacts[2]['skin_gap_min_mm']:.3f} .. {contacts[2]['skin_gap_max_mm']:.3f}|{contacts[2]['horizontal_max_mm']:.3f}|本实例有限触键数据支持；拇指展开及腕部姿态待审。|

三指各有独立非零按压关节变化：小指MCP约1.55°，中指PIP约1.40°，拇指CMC约2.71°，同时共享腕的少量位移/旋转。各指随键下降约8.32/6.72/9.18mm；深度不同来自各自接触纵深和真实枢轴，不是琶音。三键归一化压力差为0，均在原同一NOTE_ON起始35ms下沉，同一NOTE_OFF释放、70ms回弹。持键时三者同在各自可奏区。

音频3个原voice同时起止，映射/有限谱峰校验通过，约−1.0至−1.2cents；无漏音或额外音。AAC容器最后静音尾部显示1.666s、视频1.666667s，差约0.667ms；原音乐事件/PCM调度不受影响。

## 自然度与有限WARN

正常画面可见小指/中指较明显的曲度和闲置食指的伸展形态。是否是合理曲指或不自然钩爪、两闲指是否放松，必须以整段1×原速判断，不能由工程范围内自动填写PASS。若Human认为明显手型崩坏或不协调，应按产品FAIL，而非以接触数值掩盖。

有限32个代表性skin点在目标B3键体内最大进入约{diag['maximum_sampled_key_penetration_mm']:.2f}mm，恢复后为0；这是目标接触邻域的proxy记录，不应谎称严重邻键错误已证明，也不宣称零碰撞。未进行逐顶点forensic或按点修补。

root全段X/Y/Z变化约2.15/5.10/6.38mm，峰值速度约{diag['root_max_speed_mm_sec']:.1f}mm/s、加速度约{diag['root_max_accel_mm_sec2']:.0f}mm/s²；关节峰值约{diag['joint_max_speed_deg_sec']:.1f}°/s。计划C1但非严格C2，烘焙120Hz LINEAR近似需保留边界WARN。没有工程关节越界。求解19次评估成功终止，明确区别于Stage A R2的未收敛历史WARN；不能据此批准人体自然度。

没有生成第二动作、改指、单指补丁或根据视频重新调参。后续左手连续伴奏/双手验证须待Human决定。
''')
write('IMPLEMENTATION_REPORT.md',f'''# IMPLEMENTATION_REPORT · MINUET_STAGE_B_R1_LEFT_HAND_TRIAD_COORDINATION

**{status['FINAL_STATUS']} · STOP — HUMAN REVIEW。** 真正新增同手多目标同时接触任务，原三音、原时值及DESIGN_PROVISIONAL指法不变；自然度Human待审。

## 实际非冻结改动

所有新增文件在本独立目录。`left_chord_motion.py` 是Stage A R2联合规划模块的受控适配：使用左手自身rest/轴/marker/root及L1/L2自然关节参考；显式并发目标集合和同指重叠冲突校验；三指静态与动态目标均在共同root问题中成立；两闲指使用既有左手idle域；释放覆盖70ms并增加渐进恢复及首尾准备约束。没有镜像右手轨迹、固定原D2/D3目标或修改任何Rig结构。

`03_generate.py` 复用Stage A带状状态/接触/速度/加速度求解，将全部同时任务一起初始化和求解。31个支撑、812未知量、233输出采样；一次联合动态轨迹求解在19次评估后成功终止。8个通用阶段初值均联合所有当时手指，不是三段单指动画。3个静态预检及未保存Blender静态回读发生在动态候选前，0个静态Action/0保存blend。

`04_scene.py` 从批准L1静态场景副本建立左手独立动作场景，烘焙一份L关节Action、一份L共同rootAction和3根键Action；保留原四静态core、正式手结构和88键网格。保存重开后pad与FK最大差约{man['actual_pad_vs_FK_max_mm']:.5f}mm，实际键世界几何差约{man['actual_key_world_parity_max_mm']:.6f}mm。没有右手表演场景。相机在生成前固定正常全手视角，原音名只作显示标签，不伪造触键。

`07_audio.py` 使用既有冻结Grand映射、音量/velocity、pitchRatio、NOTE_OFF release与PCM方法，仅绑定本三音输入。3voices，没有改MIDI或声音事件。三原速媒体全解码通过；三根键使用相同原事件压力，非目标键不动。完整左手所有实际顶点跨233采样均在正常三视角内。

本轮通用接口可以接收其他三音目标且拒绝重叠同指，另组57/61/64只运行规划接口，0动态候选/0音频。它验证数据/目标机制可复用，未宣称其他和弦或长段伴奏已合格。

## 限制与一次候选

唯一动态候选 `STAGE_B_LEFT_TRIAD_DESIGN_ONLY_R1.blend`。没有后渲染重求解、单指手工pose、逐帧补丁、换指或重复演奏。工程WARN为有限target-B3接触邻域约2.72mm进入、root加速度/插值边界以及未验证的自然度；不按历史3mm单点门槛作Human可见否决，也不掩盖任何明显失败。

生成前修正过CLI3.12 SciPy与Blender3.13FK读取的导入边界，未改求解参数。后续修正过新审核服务继承的旧端口，使用8872；这是交付服务，不改变候选/音频。Stage A R2任何文件都未改。

## 最终Q1–Q12

|问题|回答|
|---|---|
|Q1 原MIDI关系|3音均tick0起音、tick768释放；PPQ384，tempo428571μs/q，共同持键0.857142s；原channel1/velocity90。期间无其他左手持键，原右手重叠3音不进入本演示。|
|Q2 左手指法|G3=小指5、B3=中指3、D4=拇指1，DESIGN_PROVISIONAL；原乐谱无可靠指法，未教师认证，生成前锁定。|
|Q3 冻结左Rig可达性|本实例已获得原左FK、正式Rig和真实skin的静态/动态三指共同触键证据；9个主动链骨独立。不是对全部三音和弦的泛化证明。|
|Q4 是否复用联合框架|是。复用Stage A R2的共同root+全部关节/键内接触/时序导数求解与烘焙回读，通过实际L矩阵和轴适配；不是独立动画重拼或镜像右轨迹。|
|Q5 三指都达键吗|技术检查支持：三主动skin marker均在目标可奏区域，最大间隙约1.51/0.87/1.47mm，且各有独立关节按压与真实下沉位移；自然视觉结论仍待Human。|
|Q6 三键同时吗|是，原同一NOTE_ON/OFF下归一化压力差0，35ms共同下沉、原0.857142s持键、70ms共同回弹；无琶音时序改写。|
|Q7 掌腕/手型自然吗|HUMAN_PENDING。有限静态和动态工程可达不能替代完整1×审核。|
|Q8 可见异常吗|所查正常帧未发现明显悬浮假和弦；小指/中指曲度、拇指展开、闲置食指伸展及整体释放节奏仍须Human判断，有限B3接触域进入与高加速度记录WARN。不声称全部异常已排除。|
|Q9 手工pose/专属补丁|没有。音乐范围/指法明确写入输入审计；运动核无G3/B3/D4专属姿态或世界坐标，生成后无单指补丁。|
|Q10 可复用机制|IMPLEMENTED：任意给定左手目标集合/不同指号可产生并发接触约束并联合求root；另一组三音只读规划接口通过，未生成第二候选。|
|Q11 原批准成果保护|YES，{protect['protected_files']}个保护文件哈希一致；冻结右R2/左R1、Grand88、四静态及Stage A R2批准代码/候选/视频/报告均保持。最新Human批准另存于本轮权威绑定，不重写旧报告。|
|Q12 进入下一阶段吗|本实例技术结果支持后续讨论，但当前等待Human实际观看后决定；本轮没有启动左手连续伴奏、双手或完整Stage B。|

严格状态见 `FINAL_STATUS.json`。所有PASS只表示本实例有限工程/音乐功能条件，不表示Human已批准左手自然度。审核入口 `HUMAN_REVIEW.html`；该隔离和弦不是完整小节。
''')
checks={}
for name in ['HUMAN_REVIEW.html','normal_speed_teaching.mp4','normal_speed_overhead.mp4','normal_speed_side_oblique.mp4']:
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8872/'+name,method='HEAD')) as r:
        assert r.status==200;checks[name]=dict(status=r.status,bytes=int(r.headers['Content-Length']),content_type=r.headers.get('Content-Type'))
with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8872/normal_speed_teaching.mp4',headers={'Range':'bytes=0-127'})) as r:
    assert r.status==206 and len(r.read())==128
dump('REVIEW_DELIVERY_VERIFICATION.json',dict(url='http://127.0.0.1:8872/HUMAN_REVIEW.html',HEAD_checks=checks,range_response=206,
    original_speed_media_decode_pass=True,Agent_realtime_playback_review='NOT_PERFORMED_TOOL_INITIALIZATION_FAILED',
    browser_error=status['browser_error'],Codex_open_result='queued',Human_naturalness='PENDING'))
files={str(f.relative_to(P)):dict(sha256=sha(f),bytes=f.stat().st_size) for f in P.rglob('*') if f.is_file() and '_frames' not in f.parts and f.name!='DELIVERY_MANIFEST.json'}
dump('DELIVERY_MANIFEST.json',dict(candidate_count=1,new_blend=man['path'],files=files,
    primary_review='HUMAN_REVIEW.html',video_views=3,frames_each=100,fps=60,source_chord_duration_sec=.857142,
    isolated_chord_not_full_measure=True,Stage_A_R2_preserved=True,status=status['FINAL_STATUS'],stop='STOP — HUMAN REVIEW'))
print('FINAL_STAGE_B',json.dumps({k:v for k,v in status.items() if k.isupper()},ensure_ascii=False),flush=True)
