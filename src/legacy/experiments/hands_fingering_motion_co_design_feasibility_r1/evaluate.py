"""Bounded fingering search and read-only frozen-Rig static assessment.

No solver, Blender, animation, or trajectory output. Native Hand.generate is used
unchanged. FK/LBS formulas reuse the existing native frozen-model representation.
"""
import os, sys, json, hashlib, time, itertools
from pathlib import Path
sys.dont_write_bytecode = True
os.environ['OPENBLAS_NUM_THREADS'] = '1'
O = Path(__file__).resolve().parent
ROOT = O.parents[1]
BEFORE = {}; IN_HASH = False

def digest(p):
    global IN_HASH
    IN_HASH = True
    try:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            for b in iter(lambda: f.read(1048576), b''): h.update(b)
        return h.hexdigest()
    finally: IN_HASH = False

def guard(event, args):
    if event not in ('open','os.listdir','os.scandir','os.mkdir','os.remove','os.rename'): return
    if not args or not isinstance(args[0], (str,bytes,os.PathLike)): return
    p = Path(os.fsdecode(args[0])).resolve()
    if '/3d interactive components/piano' in p.as_posix().lower():
        raise RuntimeError('EXCLUDED_PIANO_ACCESS')
    writing = event in ('os.mkdir','os.remove','os.rename')
    if event == 'open':
        mode = args[1]; flags = args[2]
        writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
    if writing and not p.is_relative_to(O): raise RuntimeError('WRITE_OUTSIDE_CURRENT_EXPERIMENT')
    if event == 'open' and not writing and not IN_HASH and p.is_relative_to(ROOT) and not p.is_relative_to(O) and '_deps' not in p.parts and p.is_file():
        if str(p) not in BEFORE: BEFORE[str(p)] = digest(p)

sys.addaudithook(guard)
OLD = ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'
SEQ = ROOT/'experiments/hands_sequence_fingering_planning_r1'
C1 = ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance'
MODEL = ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'
sys.path.insert(0,str(OLD/'_deps'))
sys.path.insert(0,str(SEQ/'evidence/pianoplayer'))
import numpy as np
import mido
from pianoplayer.hand import Hand
from pianoplayer.models import INote, keypos

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(name, obj):
    (O/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,
        default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item())+'\n',encoding='utf8')

START = time.perf_counter()
POL = read(O/'EVALUATION_POLICY.json')
dump('POLICY_LOCK_RECEIPT.json',dict(policy_sha256=digest(O/'EVALUATION_POLICY.json'),
     locked_before_new_results=True,unix_time=time.time()))
TL = read(C1/'PERFORMANCE_TIMELINE.json')
NOTES = TL['notes']; R = sorted([n for n in NOTES if n['hand']=='R'],key=lambda n:n['on_tick'])
L = sorted([n for n in NOTES if n['hand']=='L'],key=lambda n:(n['on_tick'],n['midi_note']))
assert len(R)==16 and len(L)==7
scene = read(C1/'SCENE_MANIFEST.json')
blend = C1/'STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend'
BEFORE[str(blend)] = digest(blend)
assert BEFORE[str(blend)]==scene['sha256']
midi_path = ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid'
mid = mido.MidiFile(str(midi_path))
tick=0; sec=0.; tempo=500000; active={}; events=[]; tempos=[]
for m in mido.merge_tracks(mid.tracks):
    sec += mido.tick2second(m.time,mid.ticks_per_beat,tempo); tick += m.time
    if m.type=='set_tempo': tempo=m.tempo; tempos.append([tick,tempo])
    if m.type=='note_on' and m.velocity>0:
        key=(m.channel,m.note); assert key not in active
        active[key]=dict(channel=m.channel,midi_note=m.note,on_tick=tick,source_on_sec=sec,velocity=m.velocity)
    elif m.type=='note_off' or (m.type=='note_on' and m.velocity==0):
        n=active.pop((m.channel,m.note)); n.update(off_tick=tick,source_off_sec=sec); events.append(n)
cut=max(n['off_tick'] for n in NOTES)
excerpt=[n for n in events if n['on_tick']<cut]
assert len(excerpt)==23
errors=[]
for n in NOTES:
    hit=[a for a in excerpt if all(a[k]==n[k] for k in ['channel','midi_note','on_tick','off_tick','velocity'])]
    assert len(hit)==1
    errors.extend([abs(hit[0][k]-n[k]) for k in ['source_on_sec','source_off_sec']])
assert max(errors)<1e-10
shift=R[0]['note_on']-R[0]['source_on_sec']
assert max(abs(n['note_on']-n['source_on_sec']-shift) for n in NOTES)<1e-10
old,new,nxt=[next(n for n in R if n['note_id']==id_) for id_ in ['R10','R11','R12']]
window=[old['note_on']-.18,new['note_off']+.18]
following=sorted([n for n in events if n['channel']==R[0]['channel'] and n['on_tick']>=cut],key=lambda n:n['on_tick'])[:3]
dump('EVENT_VERIFICATION.json',dict(ppq=mid.ticks_per_beat,tempos=tempos,cut_tick=cut,
    excerpt_count=len(excerpt),max_source_clock_error_sec=max(errors),presentation_shift_sec=shift,
    window_sec=window,notes=NOTES,following_right_context_not_searched=following))
license_text=(SEQ/'evidence/pianoplayer/LICENSE').read_text(encoding='utf8')
assert 'Permission is hereby granted' in license_text
revision=read(SEQ/'evidence/pianoplayer_tree.json')['sha']
assert revision=='6fb0e2114d7b21f75c0be5208172e1243a57323e'
original=[n['finger'] for n in R]
anchor_end=R.index(old)-2 # before the immediately preceding note (R09)
raw=[]; candidates=[dict(id='C1',fingers=original,source='Original approved C1 reference; local defects remain')]
for cfg in POL['configurations_in_fixed_order']:
    start=time.perf_counter(); ins=[]
    for i,n in enumerate(R):
        anchor=n['finger'] if cfg['id']=='P3' and i<=anchor_end else 0
        a=INote(name=n['note_name'][:-1],pitch=n['midi_note'],octave=n['midi_note']//12,
            time=n['source_on_sec'],duration=n['source_off_sec']-n['source_on_sec'],
            noteID=i,measure=n['measure'],isBlack=n['key_color']=='BLACK',fingering=anchor)
        a.x=keypos(a); ins.append(a)
    identities=[(a.pitch,a.time,a.duration,a.x) for a in ins]
    h=Hand(ins,side='right',size=cfg['size']); h.verbose=False
    h.preserve_posture_memory=cfg['preserve_posture_memory']; h.generate(start_measure=1,nmeasures=4)
    assert identities==[(a.pitch,a.time,a.duration,a.x) for a in ins]
    fs=[a.fingering for a in ins]; assert all(type(f)==int and 1<=f<=5 for f in fs)
    if cfg['id']=='P3': assert fs[:anchor_end+1]==original[:anchor_end+1]
    row=dict(id=cfg['id'],settings=cfg,fingers=fs,seconds=time.perf_counter()-start,
         reported_local_window_costs=[a.cost for a in ins],anchor_ids=[n['note_id'] for n in R[:anchor_end+1]] if cfg['id']=='P3' else [])
    same=next((c['id'] for c in candidates if c['fingers']==fs),None)
    row['duplicate_of']=same; raw.append(row)
    if same is None: candidates.append(dict(id=cfg['id'],fingers=fs,source='Native Hand.generate',settings=cfg))
dump('PIANOPLAYER_RUNS.json',dict(revision=revision,license='MIT; code-only rule engine, no weights',
    input_identity_unchanged=True,left_fingers_unchanged=[n['finger'] for n in L],runs=raw,
    distinct_alternatives=len(candidates)-1))
dump('CANDIDATES.json',dict(candidates=candidates,notes=R,left_notes=L,authority='ALTERNATIVES_ARE_UNAPPROVED_ADVICE'))

# Native-rest FK and weighted skin formulas use the historical frozen model,
# independently of any stopped portal or soft-IK solver.
M=read(MODEL/'SOURCE_MODEL_MANIFEST.json'); D=dict(np.load(MODEL/'SOURCE_MODEL.npz'))
SH=np.load(MODEL/'SHAPE_DELTA.npz')['delta']
REF=dict(np.load(C1/'R_approved_reference.npz'))
CAN=read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']['bones']
MARK=read(OLD/'FINGERTIP_CONTACT_MARKERS_R1.json')['markers']['R']
KEYS=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
NUM=dict(np.load(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/source_numeric.npz'))
BN={n:i for i,n in enumerate(M['bones'])}; REST=D['rest_matrices'].astype(float)
REL=np.array([np.linalg.inv(REST[p])@r if p>=0 else r for p,r in zip(D['parents'],REST)])
W=D['weights']; W=W/np.maximum(W.sum(1,keepdims=True),1e-12)
H=np.c_[D['rest_vertices'],np.ones(len(W))]@D['mesh_to_rig'].T
LOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),H)*W.T[:,:,None]
SHH=np.c_[SH,np.zeros(len(W))]@D['mesh_to_rig'].T
SHLOCAL=np.einsum('bij,vj->bvi',np.linalg.inv(REST),SHH)*W.T[:,:,None]
DIGITS=['THUMB','INDEX','MIDDLE','RING','LITTLE']; AXES=[]; NAMES=[]; SPREAD=[]
for d in DIGITS:
    names=[f'{d}_{j}_R' for j in (['CMC','MCP','IP'] if d=='THUMB' else ['MCP','PIP','DIP'])]
    rests=[np.array(CAN[n]['matrix']) for n in names]; axes=[]
    for mat in rests:
        a=np.cross(mat[:3,1],[0,0,-1]); a/=np.linalg.norm(a); axes.append(mat[:3,:3].T@a)
    AXES.append(axes); NAMES.append(names); SPREAD.append(rests[0][:3,:3]<REDACTED_EMAIL>([0,0,1]))

def rot(a,axis):
    v=np.asarray(axis,dtype=float);v/=np.linalg.norm(v);x,y,z=v
    K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    a=np.asarray(a);return np.eye(3)+np.sin(a)[...,None,None]*K+(1-np.cos(a))[...,None,None]*(K@K)

def forward(basis):
    mats=[]
    for b,p in enumerate(D['parents']):
        J=np.broadcast_to(np.eye(4),(len(basis),4,4)).copy();J[:,:3,:3]=basis[:,b]
        mat=REL[b]@J
        if p>=0:mat=mats[p]@mat
        mats.append(mat)
    return np.stack(mats,axis=1)

def skin(basis,world,ids):
    poses=forward(basis)
    opp=np.arctan2(basis[:,BN['THUMB_CMC_R'],2,1],basis[:,BN['THUMB_CMC_R'],2,2])
    mcp=np.arctan2(basis[:,BN['THUMB_MCP_R'],2,1],basis[:,BN['THUMB_MCP_R'],2,2])
    shape=np.maximum(np.clip((-opp-.37)/.06,0,1),np.clip((-opp-.15)/.15,0,1)*np.clip((-mcp-.175)/.175,0,1))
    local=LOCAL[:,ids]+shape[:,None,None,None]*SHLOCAL[None,:,ids]
    V=np.einsum('kbij,kbvj->kvi',poses,local)
    return np.einsum('kij,kvj->kvi',world,V)[:,:,:3],poses

ref_t=REF['music_times']+shift
check_idx=np.unique(np.linspace(0,len(ref_t)-1,48).astype(int))
vb,poses=skin(REF['joint_basis'][check_idx,:,:3,:3],REF['rig_world'][check_idx],np.arange(len(W)))
rebuild_error=float(np.max(np.linalg.norm(vb-REF['verts'][check_idx],axis=-1))*1000)
assert rebuild_error<.01, ('FROZEN_LBS_REBUILD_ERROR_MM',rebuild_error)
dump('FK_SELF_CHECK.json',dict(source_static_samples=len(check_idx),full_skin_max_error_mm=rebuild_error,
    vertex_count=len(W),model='Frozen native rest, original weighted LBS and original thumb corrective',
    historical_model_export_does_not_replace_frozen_blend=True))
qref=np.column_stack([np.interp(ref_t,NUM['times'],NUM['qdeg'].reshape(-1,20)[:,i]) for i in range(20)]).reshape(-1,5,4)
libraries=[]; legalcounts=[]
for j,d in enumerate(DIGITS):
    lo=np.array([0,0,0,-35 if j==0 else -28]);hi=np.array([40,55,55,35] if j==0 else [75,95,65,28])
    grid=np.array(list(itertools.product(*[np.linspace(a,b,5) for a,b in zip(lo,hi)])))
    mask=np.all((qref[:,j]>=lo-.002)&(qref[:,j]<=hi+.002),axis=1)
    source=np.clip(qref[mask,j],lo,hi); allq=np.r_[grid,source]
    mats=np.empty((len(allq),3,3,3))
    for k in range(3):
        mats[:,k]=rot(np.radians(allq[:,k]),AXES[j][k])
        if k==0:mats[:,k]=rot(np.radians(allq[:,3]),SPREAD[j])@mats[:,k]
    libraries.append((allq,mats));legalcounts.append(int(mask.sum()))

def surface_metrics(points,key,angle):
    pv=np.array(key['press_pivot']);p=(points-pv)@rot(-angle,key['press_axis']).T+pv
    scores=[];hm=[];vg=[];nearest=[]
    for s in key['key_top_playable_surface']:
        xy=np.clip(p[:,:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]);gap=p[:,2]-s['z']
        miss=np.linalg.norm(p[:,:2]-xy,axis=1)
        scores.append(np.sqrt(miss**2+np.maximum(np.abs(gap)-.003,0)**2));hm.append(miss);vg.append(gap)
        nearest.append(np.c_[xy,np.full(len(p),s['z'])])
    scores=np.array(scores);best=scores.argmin(0);rows=np.arange(len(p))
    return scores[best,rows],np.array(hm)[best,rows],np.array(vg)[best,rows],np.array(nearest)[best,rows]

# Read-only static probes for every finger at every original event phase; reused
# across proposals. No FK sample is chained into a motion.
geo=[]
for n in R:
    phases=[n['note_on'],min(n['note_on']+.035,(n['note_on']+n['note_off'])/2),(n['note_on']+n['note_off'])/2]
    for t in phases:
        ix=int(np.argmin(abs(ref_t-t))); actual_t=float(ref_t[ix]); world=REF['rig_world'][ix]
        base=REF['joint_basis'][ix,:,:3,:3]; key=KEYS[n['key_index']];angle=REF['key_angles'][ix,n['key_index']]
        sourceposes=forward(base[None])[0]
        for j,d in enumerate(DIGITS):
            allq,lib=libraries[j];basis=np.broadcast_to(base,(len(lib),)+base.shape).copy()
            for k,name in enumerate(NAMES[j]):basis[:,BN[name]]=lib[:,k]
            vertex=MARK[j]['mesh_vertex']; pads, pp=skin(basis,np.broadcast_to(world,(len(lib),4,4)),[vertex])
            score,miss,gap,near=surface_metrics(pads[:,0],key,angle)
            admissible=(miss*1000<=.03)&(np.abs(gap)*1000<=3)
            best=int(np.argmin(np.where(admissible,np.linalg.norm(allq-qref[ix,j],axis=1),np.inf))) if admissible.any() else int(np.argmin(score))
            # Virtual pad reach sphere: orientations cannot exceed sum of chain
            # lengths. Bound refers to the frozen rigid marker, not arbitrary skin.
            names=NAMES[j];first=BN[names[0]]
            center=(world@np.r_[sourceposes[first,:3,3],1])[:3]
            radius=sum(np.linalg.norm(REL[BN[name],:3,3]) for name in names[1:])+np.linalg.norm(MARK[j]['local_pad_point'])
            radius*=np.linalg.svd(world[:3,:3],compute_uv=False).max()
            # Conservative Euclidean sphere test locked in policy: target
            # surface distance minus radius and the entire contact tolerance.
            pv=np.array(key['press_pivot']);local_center=rot(-angle,key['press_axis'])@(center-pv)+pv
            surface_distance=min(np.linalg.norm(local_center-np.r_[np.clip(local_center[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']]),s['z']]) for s in key['key_top_playable_surface'])
            deficit=max(0.,float(surface_distance-radius-.003001))
            source_pad=REF['skin_pads'][ix,j]
            sm,sh,sg,snear=surface_metrics(source_pad[None],key,angle)
            # Nearby raised black-key risk at the unchanged source arrangement.
            srcinv=(source_pad-np.array(key['press_pivot']))@rot(-angle,key['press_axis']).T+np.array(key['press_pivot'])
            obstacle=[]
            for bk in KEYS:
                if bk['color']!='BLACK' or abs(bk['midi_note']-n['midi_note'])>3:continue
                s=bk['key_top_playable_surface'][0]
                if s['xmin']-.005<=source_pad[0]<=s['xmax']+.005 and s['ymin']-.005<=source_pad[1]<=s['ymax']+.005:
                    obstacle.append(dict(midi=bk['midi_note'],source_pad_top_height_delta_mm=float((source_pad[2]-s['z'])*1000)))
            witness_basis=basis[best:best+1]; allskin,_=skin(witness_basis,world[None],np.arange(len(W)))
            digitids=np.flatnonzero(W[:,[BN[x] for x in M['bones'] if x.startswith(d+'_')]].sum(1)>.55)
            keypenetrations=[]
            for kk in KEYS:
                if kk['midi_note']==n['midi_note'] or abs(kk['midi_note']-n['midi_note'])>3:continue
                akey=REF['key_angles'][ix,kk['key_index']];pv=np.array(kk['press_pivot'])
                v=(allskin[0,digitids]-pv)@rot(-akey,kk['press_axis']).T+pv
                for body in kk['geometry']:
                    vs=np.array(body['vertices']);cent=vs.mean(0);planes=[]
                    for tri in np.asarray(body['triangles']).reshape(-1,3):
                        aa,bb,cc=vs[tri];norm=np.cross(bb-aa,cc-aa);length=np.linalg.norm(norm)
                        if length<1e-12:continue
                        norm/=length
                        if np.dot(norm,cent-aa)>0:norm=-norm
                        planes.append(np.r_[norm,np.dot(norm,aa)])
                    planes=np.array(planes);depth=-np.max(v@planes[:,:3].T-planes[:,3],axis=1)*1000
                    if depth.max()>.5:keypenetrations.append(dict(midi=kk['midi_note'],component=body['name'],max_inside_vertex_depth_mm=float(depth.max())))
            geo.append(dict(event=n['note_id'],requested_time_sec=t,reference_time_sec=actual_t,reference_time_error_sec=actual_t-t,
                finger=j+1,sample_count=len(lib),sampled_contact_marker_supported=bool(admissible.any()),
                admissible_static_samples=int(admissible.sum()),best_marker_horizontal_miss_mm=float(miss[best]*1000),
                best_marker_vertical_gap_mm=float(gap[best]*1000),witness_angles_deg=allq[best],
                witness_distance_from_original_same_digit_angles_deg=float(np.linalg.norm(allq[best]-qref[ix,j])),
                fixed_root_virtual_marker_radius_mm=float(radius*1000),necessary_virtual_marker_extra_root_mm=deficit*1000,
                source_skin_marker_target_set_distance_mm=float(sm[0]*1000),
                source_skin_marker_horizontal_miss_mm=float(sh[0]*1000),source_skin_marker_vertical_gap_mm=float(sg[0]*1000),
                source_marker_near_black_key_obstacles=obstacle,witness_non_target_key_vertex_intrusions=keypenetrations,
                witness_full_skin_interfinger_collision='UNKNOWN: no triangle collision or continuous path evaluated',
                conclusion='STATIC_PROBE_ONLY_NOT_MOTION_FEASIBILITY'))
dump('STATIC_RIG_PROBES.json',dict(frozen_lbs_source_error_mm=rebuild_error,original_legal_library_counts=legalcounts,
    grid_samples_per_digit=625,rows=geo))

summaries=[]
for candidate in candidates:
    fs=candidate['fingers'];occupancy=[];transitions=[];samefinger=[]
    for i,a in enumerate(R):
        for k,b in enumerate(R[i+1:],i+1):
            if fs[i]==fs[k] and a['midi_note']!=b['midi_note'] and max(a['on_tick'],b['on_tick'])<min(a['off_tick'],b['off_tick']):occupancy.append([a['note_id'],b['note_id']])
        prev=[(k,b) for k,b in enumerate(R[:i]) if fs[k]==fs[i]]
        if prev:
            k,b=prev[-1];samefinger.append(dict(ids=[b['note_id'],a['note_id']],finger=fs[i],available_after_off_ms=(a['note_on']-b['note_off'])*1000,
                pitch_delta=a['midi_note']-b['midi_note'],release_follow_overlap_ms=max(0,.04-(a['note_on']-b['note_off']))*1000))
        if i:
            b=R[i-1];dp=a['midi_note']-b['midi_note'];reversal=dp*(fs[i]-fs[i-1])<0 and min(fs[i-1],fs[i])>1
            transitions.append(dict(ids=[b['note_id'],a['note_id']],fingers=[fs[i-1],fs[i]],pitch_delta=dp,
                nonthumb_direction_reversal=reversal,simultaneous_off_on=abs(a['note_on']-b['note_off'])<1e-10,
                finger_handoff_gap_ms=(a['note_on']-b['note_off'])*1000))
    selected=[g for g in geo if g['finger']==fs[next(i for i,n in enumerate(R) if n['note_id']==g['event'])]]
    changed=[n['note_id'] for n,f in zip(R,fs) if f!=n['finger']]
    changed_geo=[g for g in selected if g['event'] in changed]
    # Fixed-root marker bound is not the skin target proof; both are reported.
    summaries.append(dict(id=candidate['id'],fingers=fs,changed_event_ids=changed,occupancy_conflicts=occupancy,
        transitions=transitions,samefinger_reuse=samefinger,nonthumb_reversal_count=sum(t['nonthumb_direction_reversal'] for t in transitions),
        B02_fingers=fs[R.index(old):R.index(nxt)+1],
        static_marker_supported_phase_count=sum(g['sampled_contact_marker_supported'] for g in selected),total_phase_count=len(selected),
        max_necessary_virtual_marker_extra_root_mm=max(g['necessary_virtual_marker_extra_root_mm'] for g in selected),
        changed_static_probe_rows=changed_geo,
        new_continuous_skin_clearance='UNKNOWN',new_required_wrist_motion='UNKNOWN; static lower bounds and pose reconfiguration only',
        new_naturalness='UNKNOWN',left_unchanged=True))
dump('CANDIDATE_COMPARISON.json',dict(ranking_policy_sha256=digest(O/'EVALUATION_POLICY.json'),summaries=summaries))
# Historical counterexamples are retained; no old solver or motion is rerun.
hist={}
for label,path in [
    ('C01_motion',ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/FINAL_RECOMMENDATION.md'),
    ('R1_baseline',ROOT/'experiments/hands_role_aware_collision_avoidance_r1/BASELINE_AND_CAUSE.md'),
    ('R2_stop',ROOT/'experiments/hands_contact_continuous_release_r2/FINAL_HUMAN_REVIEW.md'),
    ('Human_C1',ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/HUMAN_AUTHORITY_RECEIPT.json'),
    ('A2',ROOT/'audits/minuet_stage_a_r2_natural_continuous_motion/coordinated_motion.py')]:
    contents=path.read_text(encoding='utf-8-sig');hist[label]=dict(path=str(path),sha256=BEFORE[str(path)],characters=len(contents))
dump('HISTORICAL_EVIDENCE.json',hist)
before=dict(BEFORE)
after={p:digest(p) for p in before};mismatch=[p for p in before if before[p]!=after[p]]
dump('SOURCE_SHA_CHECK.json',dict(before=before,after=after,mismatches=mismatch,unchanged=not mismatch,
    historical_protection_FAIL_preserved_not_overridden=True,excluded_piano_access_count=0))
assert not mismatch
dump('COMPUTE_LOG.json',dict(total_seconds=time.perf_counter()-START,search_seconds=sum(r['seconds'] for r in raw),
    native_search_runs=len(raw),static_probe_rows=len(geo),new_trajectories=0,new_actions=0,new_blends=0,new_videos=0,
    scipy_optimization_calls=0,blender_calls=0,source_sha_files=len(before)))
print(json.dumps(dict(runs=[{k:r[k] for k in ['id','fingers','seconds','duplicate_of']} for r in raw],
    rebuild_error_mm=rebuild_error,candidates=[dict(id=s['id'],B02=s['B02_fingers'],changed=s['changed_event_ids'],
    static_support=s['static_marker_supported_phase_count'],max_reach_root_mm=s['max_necessary_virtual_marker_extra_root_mm']) for s in summaries],
    seconds=time.perf_counter()-START),ensure_ascii=False))
