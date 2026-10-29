from performance_core import *
import subprocess
before=read(P/'PROTECTED_INPUTS_BEFORE_R1.json');unchanged={f:sha(f)==v for f,v in before.items()};assert all(unchanged.values())
for n,h in read(P/'INHERITED_INPUTS_R1.json').items():assert sha(P/n)==h,('INHERITED_CHANGED',n)
lock=read(P/'PRE_GENERATION_LOCK_R1.json');assert sha(P/'01_coordinate.py')==lock['script_sha256'];assert sha(P/'GENERATION_POLICY_R1.json')==lock['policy_sha256']
A=np.load(P/'procedural_motion.npz');OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';old=np.load(OLD/'procedural_motion.npz');assert np.array_equal(A['times'],old['times']);assert np.array_equal(A['key_angles'],old['key_angles'])
temporal={}
for s in ['R','L']:
 q=np.degrees(A[s+'_q']);root=A[s+'_root'];v=np.diff(q,axis=0)*HZ;a=np.diff(q,n=2,axis=0)*HZ*HZ;rv=np.diff(root,axis=0)*HZ;ra=np.diff(root,n=2,axis=0)*HZ*HZ
 assert np.max(abs(v))<=360.00001;assert np.max(abs(a))<=14400.001;assert np.max(abs(rv))<=.320001;assert np.max(abs(ra))<=14.00001
 temporal[s]={'joint_velocity_deg_s':float(np.max(abs(v))),'joint_acceleration_deg_s2':float(np.max(abs(a))),'root_axis_velocity_m_s':float(np.max(abs(rv))),'root_axis_acceleration_m_s2':float(np.max(abs(ra)))}
assert len(list((P/'_frames').glob('*.png')))==204
identity=read(P/'CANDIDATE_IDENTITY_R1.json');assert sha(P/'HAND_POSTURE_CONTACT_REFINED_DESIGN_ONLY_R1.blend')==identity['candidate_sha256'];assert all(v['intrinsic_static_identity']=='MATCHED' and v['vertex_count']==3300 and v['bone_count']==21 for v in identity['hands'].values())
for video in ['product_midi_dual_hand_motion_refined.mp4','product_motion_before_after.mp4']:
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(P/video)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');assert int(v['nb_read_frames'])==204;assert a['codec_name']=='aac'
assert read(P/'VIDEO_VERIFICATION_R1.json')['status']=='PASS_MEDIA_STRUCTURE_AND_AUDIO_IDENTITY'
dump('REPRODUCTION_VERIFICATION_R1.json',{'status':'PASS','protected_files':len(unchanged),'temporal_bounds':temporal,'source_timeline_fingering_keyboard_markers_tolerances_audio':'EXACT','saved_candidate_identity':'MATCHED','videos':'204 frames each,60fps,AAC retained','scope':'Technical reproduction and identity only; never overrides human-visible quality verdict'})
print('VERIFY PASS:',len(unchanged),'protected files; exact event/key/audio inputs; temporal constraints; candidate and both videos')
