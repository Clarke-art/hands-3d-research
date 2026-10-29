"""Small read-only scope/geometry/SHA supplement; no Jacobian or optimizer."""
import review_diagnostics as r
import numpy as np
io,n,w=r.io,r.n,r.w
from pathlib import Path
import time
begin=time.perf_counter()
results=io.read(r.OUT/'DIAGNOSTIC_RESULTS.json')
little005=np.flatnonzero(w.DW[:,4]>.05)
ids=w.REGIONS['LITTLE'];missing=np.setdiff1d(little005,ids)
raw=w.RAWBASE
e=next(e for e in w.EVENTS if e['note_id']=='R05')
it=np.flatnonzero((raw['times']>=e['note_on'])&(raw['times']<e['note_off']))
V=raw['vertices'][it][:,little005];angles=raw['key_angles'][it]
peak=np.zeros(len(it));witness=[]
for key,g,pl in w.COMPONENTS:
    if key['key_index']==e['key_index']:continue
    pv=np.asarray(key['press_pivot']);local=(V-pv)@w.rot(angles[:,key['key_index']],key['press_axis'])+pv
    depth=np.maximum(0,-np.max(local@pl[:,:3].T-pl[:,3],axis=2)*1000)
    p=depth.max(1);peak=np.maximum(peak,p)
    if p.max()>.5:
        row,col=np.unravel_index(depth.argmax(),depth.shape)
        witness.append(dict(time=float(raw['times'][it[row]]),key=key['note_name'],component=g['name'],vertex=int(little005[col]),depth_mm=float(depth[row,col])))
scope=dict(legacy_little_vertices=len(ids),original_influence_gt005_vertices=len(little005),influence_vertices_outside_legacy_little=missing,
           all_keys=88,all_components=139,active_reference_samples=len(it),active_reference_violating_samples=int((peak>.5).sum()),
           active_reference_peak_mm=float(peak.max()),witnesses=witness,
           legacy_regions_cover_all_vertices=len(set(int(x) for ids in w.REGIONS.values() for x in ids))==3300,
           continuous_coverage='UNKNOWN',legacy_planning_components=32,
           note='Supplementary original-C1 scope check only; not inserted into the frozen 11149-row benchmark; not a new motion candidate')
io.atomic_json('SCOPE_SUPPLEMENT.json',scope)
# Evidence sources used in the report, no tree scan and no external project traversal.
sources=[r.ROOT/'AGENTS.md',
 r.ROOT/'audits/hands_continuous_motion_technical_route_decision_r1/FINAL_TECHNICAL_ROUTE_DECISION.md',
 r.ROOT/'audits/hands_saved_pose_geometry_closure_r1/FINAL_GEOMETRY_CLOSURE.md',
 r.ROOT/'audits/hands_saved_pose_geometry_closure_r1/analyze_cached_geometry.py',
 r.ROOT/'audits/hands_recomposition_saved_result_verification_r2/source_actual.py',
 r.ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement/HUMAN_AUTHORITY_RECEIPT.json',
 r.HIST/'FINAL_HUMAN_REVIEW.md',r.HIST/'SPARSE_WINDOW_EXECUTION.md',r.HIST/'BOUNDARY_CONTRACT_WITNESS.json',
 r.HIST/'COST_PREFLIGHT_CLOCK_FIXED.json',r.HIST/'PROTECTION_FINAL.json',r.HIST/'STAGE0_BLENDER.json',
 r.ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid',
 r.ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/STAGE_C_R1_DUAL_HAND_SYNCHRONIZED_DESIGN_ONLY.blend']
prior=io.read(r.HIST/'PROTECTION_FINAL.json')
priorhash={row['path']:row['before'] for row in prior['files']}
checks=[]
for p in sources:
    p=io.valid_path(p);h=io.sha(p)
    old=priorhash.get(str(p));checks.append(dict(path=str(p),sha256=h,prior_protection_sha=old,matches_prior=None if old is None else old==h))
assert all(x['matches_prior'] is not False for x in checks)
io.atomic_json('KEY_SOURCE_SHA.json',dict(files=checks,reference_scope='Historical protection match where available; remaining prose sources hashed now, not claimed as pre-run snapshots'))
io.protect('SUPPLEMENT_SHA_CHECK.json')
io.atomic_json('SUPPLEMENT_LEDGER.json',dict(seconds=time.perf_counter()-begin,formal_optimization=False))
print('SCOPE',len(ids),len(little005),len(missing),scope['active_reference_peak_mm'],flush=True)
