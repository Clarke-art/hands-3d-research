from articulation_common import *
import mido
E=np.load(PRE/'evaluated.npz');A=np.load(PRE/'motion.npz');times=E['times'];fit=read(PRE/'RIGHT_SEQUENCE_FIT.json');coef=np.radians(fit['coefficients_deg']);man=read(PRE/'SCENE_MANIFEST.json')
assert sha(PRE/'SHORT_PHRASE_DESIGN_ONLY_R1.blend')==man['sha256']
midi=c.P/'source/anna-magdalena-22.mid';m=mido.MidiFile(midi);rows=[];meta=[]
for tr,track in enumerate(m.tracks):
 held={};tick=0
 for msg in track:
  tick+=msg.time
  if msg.is_meta:meta.append({'track':tr,'tick':tick,**msg.dict()})
  elif msg.type=='note_on' and msg.velocity:held[msg.channel,msg.note]=(tick,msg.velocity)
  elif msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0):
   on,v=held.pop((msg.channel,msg.note));rows.append({'track':tr,'channel':msg.channel,'midi_note':msg.note,'on_tick':on,'off_tick':tick,'velocity':v})
 assert not held
rows=sorted([r for r in rows if r['on_tick']<1536],key=lambda n:(n['on_tick'],n['track']))
assert rows==[{k:n[k] for k in ['track','channel','midi_note','on_tick','off_tick','velocity']} for n in TL['notes']]
assert sha(midi)==TL['source_midi_sha256']
notes=[];limited=[]
for n in TL['notes']:
 if n['hand']!='R':continue
 j=n['finger']-1;k=n['key_index'];samples=[];on=n['note_on'];off=n['note_off']
 for phase,t in [('PREPARATION_START',on-.12),('MID_PREPARATION',on-.06),('NOTE_ON',on),('PRESS_MIDDLE',on+.0175),('FULL_DOWN',on+.035),('HOLD_MIDDLE',(on+.035+off)/2),('NOTE_OFF',off),('RELEASE_MIDDLE',off+.035),('KEY_RETURN_END',off+.07),('RECOVERY_END',off+.22)]:
  i=int(np.argmin(abs(times-t)));q=A['R_q'][i];fixed=o.measure(E['R_pads'][i,j],n['midi_note'],E['key_angles'][i,k]);skin=o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,k]);pad=E['R_skin_pads'][i,j];kp=o.keytransform(n['midi_note'],fit['targets'][str(j)],E['key_angles'][i,k]);samples.append({'phase':phase,'requested_source_sec':t,'sample_source_sec':float(times[i]),'pad_xyz_mm':pad*1000,'skin_gap_mm':skin['gap_mm'],'fixed_gap_mm':fixed['gap_mm'],'horizontal_mm':skin['horizontal_mm'],'joint_deg':np.degrees(q[j]),'key_angle_rad':float(E['key_angles'][i,k]),'moving_target_xyz_mm':kp*1000})
 # Compare actual unpressed -> full-down pad and target displacement, without changing timing.
 at=lambda t:int(np.argmin(abs(times-t)))
 a=at(on);b=at(on+.035);start=at(on-.12)
 press=(E['R_skin_pads'][b,j]-E['R_skin_pads'][a,j])*1000;key0=o.keytransform(n['midi_note'],fit['targets'][str(j)],E['key_angles'][a,k]);key1=o.keytransform(n['midi_note'],fit['targets'][str(j)],E['key_angles'][b,k]);keydelta=(key1-key0)*1000
 note={'note_id':n['note_id'],'midi':n['midi_note'],'finger':n['finger'],'original_on_off':[on,off],'prepare_duration_sec':.12,'pressure_duration_sec':.035,'key_release_duration_sec':.07,'return_total_after_off_sec':.22,'pressure_pad_delta_mm':press,'pressure_key_target_delta_mm':keydelta,'preparation_pad_delta_mm':(E['R_skin_pads'][a,j]-E['R_skin_pads'][start,j])*1000,'pressure_following_z_deficit_mm':float(press[2]-keydelta[2]),'samples':samples};notes.append(note)
 if n['midi_note'] in [81,78]:
  rest=np.array(read(o.FORMAL/'FORMAL_INPUT_EXTRACTION_R1.json')['R']['rest_vertices_canonical']);vid=c.MARKERS['R'][j]['mesh_vertex'];patchids=np.flatnonzero(np.linalg.norm(rest-rest[vid],axis=1)<=.008)
  for phase,t in [('NOTE_ON',on),('FULL_DOWN',on+.035),('HOLD_MIDDLE',(on+.035+off)/2)]:
   i=at(t);actual=E['R_verts'][i,patchids];local=o.keytransform(n['midi_note'],actual,E['key_angles'][i,k],True);valid=[]
   for surf in c.KEYS[k]['key_top_playable_surface']:
    inside=(local[:,0]>=surf['xmin'])&(local[:,0]<=surf['xmax'])&(local[:,1]>=surf['ymin'])&(local[:,1]<=surf['ymax']);valid.extend((local[inside,2]-surf['z'])*1000)
   limited.append({'note_id':n['note_id'],'midi':n['midi_note'],'phase':phase,'source_sec':t,'palmar_patch_radius_mm':8,'patch_vertices':len(patchids),'vertices_over_actual_playable_face':len(valid),'closest_patch_surface_gap_mm':float(min(valid,key=abs)) if valid else None,'marker_skin_gap_mm':o.measure(E['R_skin_pads'][i,j],n['midi_note'],E['key_angles'][i,k])['gap_mm']})
dump('PREVIOUS_PHASE_CONTACT_EVIDENCE.json',{'original_midi_reparsed':True,'18_notes_unchanged':True,'midi_sha256':sha(midi),'previous_candidate_sha256':man['sha256'],'notes':notes,'limited_A5_Fsharp_patch_check':limited,'actual_saved_reopened_geometry':True,'no_new_motion_generated':True,'classification':{'MIDI_keys_audio_timing':'CONFIRMED_CORRECT','right_phase_time_lag':'NOT_SUPPORTED: old phases are on MIDI clock, no scheduling delay','visual_slowness':'SUPPORTED:120ms gradual approach,70ms return+150ms recovery, tiny held-key following for white keys and fixed right root; not a tempo error','A5':'CONFIRMED:initial contact deficit and insufficient following of white-key travel; no early return during HOLD','Fsharp5':'Actual active pad is over raised moving black playable face with sub-mm gap; no measured major hovering. Human visual perception remains distinct.'}})
before=read(PRE/'PROTECTED_INPUTS_BEFORE.json')
for f in PRE.rglob('*'):
 if f.is_file():before[str(f)]=sha(f)
assert all(sha(f)==h for f,h in before.items())
dump('PROTECTED_INPUTS_BEFORE.json',before)
lines=['# RIGHT_HAND_MOTION_CAUSE_ANALYSIS','','2026-10-09 · 有限读取上一轮唯一候选 · 未重查整个历史 · 新候选尚未生成','', '## Q1 为什么看起来动作慢？','','**SUPPORTED：阶段分配与触键幅度造成视觉迟缓；没有证据支持MIDI、键、声音错时。** 上一轮右手每音从起音前120ms以quintic缓慢靠近，120 BPM下十六分音符只有125ms，所以准备横跨几乎整个前音。35ms下压与MIDI同步，但一些白键手指的下降小于键面下降。NOTE_OFF后70ms回弹，随后150ms回位，多个不同手指的长尾叠加，看起来像持续缓慢改变手型。持键系数恒定，右root固定；不是发声音符都应不停上下摆动。','', '真实时钟错位：NOT_SUPPORTED。有效触键追随不足：CONFIRMED（A5）。过长靠近/回位、幅度不足造成感知慢：SUPPORTED；需要Human原速最终评价。','', '## Q2 A5为什么悬空？','','**CONFIRMED：初始接触未到达，35ms压力下降不足，且持续HOLD维持失败姿态。** x/y在目标白键可奏区；不是按错键或目标身份错。小指MCP接触/下压系数停在“准备角+12°”界限；该边界是上一轮适配的工程限制，不是冻结Rig证明的生理极限。固定掌根与受限曲线不能补足白键键程。HOLD并未过早回升：真正回升只在原NOTE_OFF后。','', '## Q3 F#5中指是否真实悬空？','','**CONFIRMED：虚拟皮肤pad水平位于实际抬高黑键可奏面内；SUPPORTED：该局部指腹已贴近并追随运动黑键。** 上轮 required gap约0.464–0.748mm，未测到A5那样的持续分离。有限8mm指腹邻域/实际运动黑键面证据见JSON；不会预认Human错看，也不会把虚拟pad等同有受力面积的真实接触。摄像机/指尖与pad不同位置能解释悬空观感，但其为唯一原因仍UNKNOWN；需匹配俯视与侧斜Human复核。','', '## Q4 为什么双手不协调？','','**SUPPORTED：可见起音动作可信度不一致，而非两手必须完全同相。** 左手D2/D3在原四分/八分节拍交替，有明显共同腕/指运动；右手前音准备和长尾回位不断叠加，白键音（尤其A5）缺少随键下压。两手事件时钟一致，左手奏不同节奏本来合理。必须让每个右手发声音符都有及时的有效下降与持键接触。左手保持上一轨迹作对照，不重拟合29参数。','', '|音符|起音pad gap mm|full-down gap mm|35ms pad Z变化 mm|35ms key目标Z变化 mm|','|---|---|---|---|---|']
for n in notes:
 if n['note_id'] in ['n00','n03','n05','n06','n08']:
  on=next(r for r in n['samples'] if r['phase']=='NOTE_ON');down=next(r for r in n['samples'] if r['phase']=='FULL_DOWN');lines.append(f"|{c.KEYS[n['midi']-21]['note_name']}|{on['skin_gap_mm']:.3f}|{down['skin_gap_mm']:.3f}|{n['pressure_pad_delta_mm'][2]:.3f}|{n['pressure_key_target_delta_mm'][2]:.3f}|")
lines+=['','诊断基于上轮代码、保存重开数组、三视角原视频对应帧和有限局部接触数据。浏览器实时观看若不可用将单独记录，不声称已完成代理1×带声体验评审。','', '本轮最小机制方向：缩短并明确准备/触键/释放阶段；以实际运动键面拟合接触和下压；允许同一右手低幅度公共掌根配合和有界闲置指补偿，参数按digit共享而非按音符手调。维持原MIDI、35/70ms键律与原音频；不改冻结Rig，不另造姿态，单次整段拟合。']
(P/'RIGHT_HAND_MOTION_CAUSE_ANALYSIS.md').write_text('\n'.join(lines),encoding='utf8')
print('LIMITED_DIAGNOSIS_SOURCE_VERIFIED',len(before),flush=True)
for x in limited:print(x,flush=True)
