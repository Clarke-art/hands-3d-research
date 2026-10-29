from performance_core import *
import ast,math
keys=KEYS;policy=read(P/'CONTACT_TOLERANCE_POLICY_R1.json')
tree=ast.parse((PRE/'05_solve.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rot','measurement']],type_ignores=[]),'inherited_key_measurement','exec'))
A=np.load(P/'evaluated_candidate.npz');M=np.load(P/'procedural_motion.npz');OLD=P.parent/'midi_driven_dual_hand_piano_performance_poc_r1';old=np.load(OLD/'procedural_motion.npz')
coord=read(P/'HAND_POSTURE_COORDINATION_R1.json');onsets=[];held=[];releases=[];summary={};collisions={};wrong={};continuity={}
boxes={k['key_index']:[(np.min(g['vertices'],axis=0),np.max(g['vertices'],axis=0)) for g in k['geometry']] for k in KEYS}
for s in ['R','L']:
 pad=A[s+'_pads'];V=A[s+'_verts'];rest=np.array(RIG[s]['rest_verts']);palm=(rest[:,1]>=.045)&(rest[:,1]<.105);wrist=rest[:,1]<.045
 for n in TL['notes']:
  if n['hand']!=s:continue
  def row(i):return {'note_id':n['note_id'],'hand':s,'finger':n['finger'],'midi_note':n['midi_note'],'observation':int(i),'time':float(A['times'][i]),**measurement(pad[i,n['finger']-1],KEYS[n['key_index']],A['key_angles'][i,n['key_index']])}
  onsets.append(row(round(n['note_on']*HZ)))
  held.extend(row(i) for i in np.flatnonzero((A['times']>=n['note_on'])&(A['times']<n['note_off'])))
  releases.extend(row(i) for i in np.flatnonzero((A['times']>=n['note_off'])&(A['times']<=n['note_off']+.14)))
 hitrows=[];wrongrows=[]
 for i,t in enumerate(A['times']):
  v=V[i];hit=np.zeros(len(rest),bool)
  relevant=[k for k in KEYS if any(lo[0]<=v[:,0].max() and hi[0]>=v[:,0].min() for lo,hi in boxes[k['key_index']])]
  for k in relevant:
   q=rot(v,np.array(k['press_pivot']),-A['key_angles'][i,k['key_index']])
   for lo,hi in boxes[k['key_index']]:hit|=np.all(q>=lo,axis=1)&np.all(q<=hi,axis=1)&(q[:,2]<hi[2]-.003)
  if hit.any():hitrows.append({'observation':i,'time':float(t),'mesh_vertices':int(hit.sum()),'palm_vertices':int(hit[palm].sum()),'wrist_vertices':int(hit[wrist].sum())})
  for j in range(5):
   expected={n['midi_note'] for n in TL['notes'] if n['hand']==s and n['finger']==j+1 and n['note_on']-.16<=t<n['note_off']+.14}
   for k in relevant:
    if k['midi_note'] in expected:continue
    mm=measurement(pad[i,j],k,A['key_angles'][i,k['key_index']])
    if mm['inside_correct_playable_region'] and abs(mm['vertical_gap_mm'])<=3:
     wrongrows.append({'observation':i,'time':float(t),'finger':j+1,'unexpected_midi':k['midi_note'],'state':coord['states_by_finger_THUMB_INDEX_MIDDLE_RING_LITTLE'][s][i][j],**mm})
 on=[r for r in onsets if r['hand']==s];hh=[r for r in held if r['hand']==s];rr=[r for r in releases if r['hand']==s]
 summary[s]={'onset_count':len(on),'onset_contact_pass':sum(r['contact_within_fixed_tolerances'] for r in on),'held_observations':len(hh),'held_contact_pass':sum(r['contact_within_fixed_tolerances'] for r in hh),'held_floating':sum(r['vertical_gap_mm']>3 for r in hh),'held_penetrating':sum(r['penetration'] for r in hh),'max_abs_held_vertical_mm':max(abs(r['vertical_gap_mm']) for r in hh),'max_held_horizontal_mm':max(r['horizontal_in_key_error_mm'] for r in hh),'release_observations':len(rr),'release_penetrating':sum(r['penetration'] for r in rr),'release_end_gaps_mm':[r['vertical_gap_mm'] for r in rr if abs(r['time']-(next(n['note_off'] for n in TL['notes'] if n['note_id']==r['note_id'])+.14))<1/HZ],'unexpected_key_pad_contacts':len(wrongrows),'palm_collision_observations':sum(r['palm_vertices']>0 for r in hitrows),'wrist_collision_observations':sum(r['wrist_vertices']>0 for r in hitrows),'mesh_collision_observations':len(hitrows)}
 collisions[s]=hitrows;wrong[s]=wrongrows
 q=np.degrees(M[s+'_q']);steps=np.diff(q,axis=0);acc=np.diff(steps,axis=0)*HZ*HZ;root=M[s+'_root'];droot=np.diff(root,axis=0);R=M[s+'_rotation'];rstep=np.degrees(np.arccos(np.clip((np.trace(np.transpose(R[:-1],(0,2,1))@R[1:],axis1=1,axis2=2)-1)/2,-1,1)))
 continuity[s]={'max_joint_step_deg_per8_33ms':float(np.max(abs(steps))),'max_joint_velocity_deg_s':float(np.max(abs(steps))*HZ),'max_joint_acceleration_deg_s2':float(np.max(abs(acc))),'max_palm_translation_step_mm':float(np.linalg.norm(droot,axis=1).max()*1000),'max_palm_rotation_step_deg':float(rstep.max()),'root_xyz_range_mm':(np.ptp(root,axis=0)*1000).tolist(),'joint_min_deg':q.min(0).tolist(),'joint_max_deg':q.max(0).tolist(),'joint_excursion_deg':np.ptp(q,axis=0).tolist(),'nonfinite':int(np.count_nonzero(~np.isfinite(V))),'old_max_joint_step_deg':float(np.max(abs(np.degrees(np.diff(old[s+'_q'],axis=0)))))}
 if s=='R':continuity[s]['at_old_jump_time_2_608333_index_PIP_step_deg']=float(steps[312,1,1])
 print(s,summary[s],continuity[s]['max_joint_step_deg_per8_33ms'],flush=True)
dump('KEY_CONTACT_R1.json',{'summary':summary,'tolerances':'UNCHANGED vertical3mm horizontal2mm; strict actual playable polygon; no marker changes','onsets':onsets,'held':held,'releases':releases,'unexpected_key_pad_contacts':wrong,'collision_screen':collisions,'scope':'Same evaluated marker queries and key-piece vertex-volume screen as prior; not full triangle/hidden anatomy audit. Unexpected idle pad contact flags visible risk, not MIDI-generated wrong sound.'})
dump('MOTION_CONTINUITY_R1.json',{'sample_Hz':HZ,'hands':continuity,'method':'Measured on saved/reopened candidate at409 observations. In-solver temporal constraints; no filtering after solve.','key_angles_exactly_unchanged':bool(np.array_equal(M['key_angles'],old['key_angles']))})
