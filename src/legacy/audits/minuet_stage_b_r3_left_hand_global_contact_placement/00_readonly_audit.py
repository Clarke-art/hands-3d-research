from stage_common import *
from left_continuous_motion import *
import shutil
assert not (P/'CANDIDATE_ATTEMPT.json').exists()
protected = read(R2/'PROTECTED_INPUTS_BEFORE.json')
paths = set(protected) | {str(p) for p in R2.rglob('*') if p.is_file()}
if not (P/'PROTECTED_INPUTS_BEFORE.json').exists():
    before = {p:sha(p) for p in sorted(paths)}
    dump('PROTECTED_INPUTS_BEFORE.json',before)
dump('HUMAN_AUTHORITY_BIND.json',dict(latest_human_feedback='R2 overall motion accepted; all seven white-key placements in scope',old_R2_record_unchanged=True,scope='GLOBAL_CONTACT_PLACEMENT_REFINEMENT_ONLY',candidate_limit=1,old_idle_finger_WARN_out_of_scope=True))
shutil.copyfile(R2/'PERFORMANCE_TIMELINE.json',P/'PERFORMANCE_TIMELINE.json')
A=dict(np.load(R2/'motion.npz'));E=dict(np.load(R2/'evaluated.npz'));tl=read(P/'PERFORMANCE_TIMELINE.json');fit=read(R2/'COORDINATED_TRAJECTORY_FIT.json')
co=EventCoordinator(tl['notes'],read(R2/'GENERATION_POLICY.json'));T=E['times'];m=o.models('L')
patches=[]
for j in range(5):
    marker=c.MARKERS['L'][j];ix=marker['mesh_vertex'];v=m['V'];names=c.SETUPS['L',c.DIGITS[j]][0]
    distal=m['names'].index(names[-1]);owned=m['W'][:,distal]>.5
    # A finite anatomically anchored local pad cap: same distal ownership and
    # rest-space distance <= 55% of the 90%-quantile transverse distal width.
    dist=np.linalg.norm(v-v[ix],axis=1)
    candidates=np.flatnonzero(owned)
    width=float(np.quantile(v[candidates,0],.95)-np.quantile(v[candidates,0],.05))
    radius=.55*width
    patch=np.flatnonzero(owned & (dist<=radius))
    assert len(patch)>=4,(j,width,len(patch))
    patches.append(dict(finger=j+1,marker_vertex=int(ix),vertices=patch.tolist(),rest_distal_transverse_width_mm=width*1000,radius_mm=radius*1000,selection='distal weight > 0.5; rest distance to skin pad marker <= 0.55*distal transverse P90 width'))
dump('PAD_PATCHES.json',patches)
rows=[]
for ni,n in enumerate(tl['notes']):
    j=n['finger']-1;k=c.KEYS[n['key_index']];s=k['key_top_playable_surface'][0]
    ids=np.flatnonzero((T>=n['note_on']-1e-9)&(T<n['note_off']-1e-9));samples=[]
    for i in ids:
        angle=E['key_angles'][i,n['key_index']]
        center=o.keytransform(n['midi_note'],E['L_skin_pads'][i,j],angle,True)*1000
        cap=o.keytransform(n['midi_note'],E['L_verts'][i,patches[j]['vertices']],angle,True)*1000
        # P90 finite pad footprint; full selected cap extrema retained for review.
        left,right=np.quantile(cap[:,0],[.05,.95]);lo,hi=s['xmin']*1000,s['xmax']*1000
        samples.append(dict(time=float(T[i]),center_x_mm=float(center[0]),center_to_left_mm=float(center[0]-lo),center_to_right_mm=float(hi-center[0]),pad_left_mm=float(left),pad_right_mm=float(right),pad_width_mm=float(right-left),pad_left_margin_mm=float(left-lo),pad_right_margin_mm=float(hi-right),cap_full_left_margin_mm=float(cap[:,0].min()-lo),cap_full_right_margin_mm=float(hi-cap[:,0].max()),gap_mm=float(center[2]-s['z']*1000),left_extent_mm=float(center[0]-left),right_extent_mm=float(right-center[0])))
    rows.append(dict(note_id=n['note_id'],note=n['note_name'],finger=n['finger'],note_on=n['note_on'],note_off=n['note_off'],key_left_mm=s['xmin']*1000,key_right_mm=s['xmax']*1000,key_width_mm=(s['xmax']-s['xmin'])*1000,planned_xy_mm=fit['solved_contact_xy_mm'][ni],samples=samples,summary=dict(center_x_range_mm=[min(r['center_x_mm'] for r in samples),max(r['center_x_mm'] for r in samples)],center_min_edge_mm=min(min(r['center_to_left_mm'],r['center_to_right_mm']) for r in samples),pad_min_edge_mm=min(min(r['pad_left_margin_mm'],r['pad_right_margin_mm']) for r in samples),pad_max_width_mm=max(r['pad_width_mm'] for r in samples),left_extent_max_mm=max(r['left_extent_mm'] for r in samples),right_extent_max_mm=max(r['right_extent_mm'] for r in samples),lateral_drift_mm=np.ptp([r['center_x_mm'] for r in samples]))))
dump('R2_ALL_ACTIVE_PLACEMENT.json',dict(source_motion_sha256=sha(R2/'motion.npz'),source_candidate_sha256=sha(R2/'STAGE_B_R2_LEFT_CONTINUOUS_DESIGN_ONLY.blend'),notes=rows,patch_scope='finite distal skin cap, not full finger silhouette or pressure area; no exhaustive forensic'))
print('R2_READ_ONLY_ALL_SEVEN',flush=True)
for r in rows:print(r['note_id'],r['note'],r['finger'],r['planned_xy_mm'],r['summary'],flush=True)
print('NPZ',[(n,A[n].shape) for n in A],[(n,E[n].shape) for n in E],flush=True)
