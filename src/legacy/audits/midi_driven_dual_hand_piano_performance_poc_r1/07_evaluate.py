from performance_core import *
import ast,math
# Reuse only geometric distance functions, never previous source motion or fitting.
tree=ast.parse((PRE/'05_solve.py').read_text(encoding='utf-8-sig'))
keys=KEYS
policy=read(P/'CONTACT_TOLERANCE_POLICY_R1.json')
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['rot','measurement']],type_ignores=[]),'frozen_key_geometry_queries','exec'))
A=np.load(P/'evaluated_candidate.npz');M=np.load(P/'procedural_motion.npz');onsets=[];held=[];summary={};collision={}
for s in ['R','L']:
 pad=A[s+'_pads'];v=A[s+'_verts'];rest=np.array(RIG[s]['rest_verts']);palm=(rest[:,1]>=.045)&(rest[:,1]<.105);wrist=rest[:,1]<.045;hitrows=[]
 for n in TL['notes']:
  if n['hand']!=s:continue
  i=round(n['note_on']*HZ);m=measurement(pad[i,n['finger']-1],KEYS[n['key_index']],A['key_angles'][i,n['key_index']]);onsets.append({'note_id':n['note_id'],'hand':s,'finger':n['finger'],'midi_note':n['midi_note'],'time':n['note_on'],**m})
  for i in np.flatnonzero((A['times']>=n['note_on'])&(A['times']<n['note_off'])):
   m=measurement(pad[i,n['finger']-1],KEYS[n['key_index']],A['key_angles'][i,n['key_index']]);held.append({'note_id':n['note_id'],'hand':s,'observation':int(i),'time':float(A['times'][i]),**m})
 for i in range(len(A['times'])):
  hit=np.zeros(len(rest),bool)
  for k in KEYS:
   q=rot(v[i],np.array(k['press_pivot']),-A['key_angles'][i,k['key_index']])
   for g in k['geometry']:
    gv=np.array(g['vertices']);lo=gv.min(0);hi=gv.max(0);hit|=np.all(q>=lo,axis=1)&np.all(q<=hi,axis=1)&(q[:,2]<hi[2]-.003)
  if hit.any():hitrows.append({'observation':i,'time':float(A['times'][i]),'mesh_vertices':int(hit.sum()),'palm_vertices':int(hit[palm].sum()),'wrist_vertices':int(hit[wrist].sum())})
 collision[s]=hitrows;on=[r for r in onsets if r['hand']==s];hh=[r for r in held if r['hand']==s]
 summary[s]={'onset_count':len(on),'onset_contact_pass':sum(r['contact_within_fixed_tolerances'] for r in on),'held_observations':len(hh),'held_contact_pass':sum(r['contact_within_fixed_tolerances'] for r in hh),'max_abs_vertical_gap_mm':max(abs(r['vertical_gap_mm']) for r in hh),'max_horizontal_error_mm':max(r['horizontal_in_key_error_mm'] for r in hh),'floating_held_observations':sum(r['vertical_gap_mm']>3 for r in hh),'penetrating_held_observations':sum(r['penetration'] for r in hh),'palm_collision_observations':sum(r['palm_vertices']>0 for r in hitrows),'wrist_collision_observations':sum(r['wrist_vertices']>0 for r in hitrows),'max_joint_step_deg_at120Hz':float(np.degrees(np.max(np.abs(np.diff(M[s+'_q'],axis=0))))),'finite_vertices':bool(np.isfinite(v).all())}
dump('CONTACT_VALIDATION_R1.json',{'summary':summary,'marker_authority':'Canonical pad surface marker, inherited; evaluated skin drift under0.25mm','tolerances':'Inherited vertical3mm horizontal2mm and correct playable polygon','fingering_authority':'DESIGNED_PROVISIONAL','onsets':onsets,'held':held,'collisions':collision,'scope':'Vertex/key-piece volume screen only, not hidden anatomy audit; no other candidate tested'})
print(json.dumps(summary),flush=True)
