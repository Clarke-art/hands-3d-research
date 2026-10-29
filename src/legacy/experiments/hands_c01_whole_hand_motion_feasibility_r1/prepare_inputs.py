from pathlib import Path
import json,hashlib,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
CAND=O.parent/'hands_sequence_fingering_planning_r1/SEQUENCE_CANDIDATES.json';cs=read(CAND);cand=next(x for x in cs['candidates'] if x['candidate_id']=='C01_PIANOPLAYER')
notes=sorted([n for n in cand['notes'] if n['note_id'] in [f'R{i:02}' for i in range(6,15)]],key=lambda n:n['on_tick'])
assert [(n['note_id'],n['midi'],n['finger']) for n in notes]==[(f'R{i:02}',m,f) for i,m,f in [(6,67,1),(7,67,1),(8,76,3),(9,72,1),(10,74,2),(11,76,3),(12,78,4),(13,79,5),(14,67,1)]]
TL=ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/PERFORMANCE_TIMELINE.json';tl=read(TL)
for n in notes:
 src=next(x for x in tl['notes'] if x['note_id']==n['note_id'])
 for a,b in [('midi','midi_note'),('on_tick','on_tick'),('off_tick','off_tick'),('velocity','velocity'),('source_on_sec','source_on_sec'),('source_off_sec','source_off_sec')]:assert n[a]==src[b]
 n.update(midi_note=n['midi'],key_index=n['midi']-21,note_on=src['note_on'],note_off=src['note_off'])
rp=read(ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json');lp=read(ROOT/'production_spec/LEFT_HAND_PRODUCT_BASELINE.json');sm=read(ROOT/'audits/piano_hand_static_posture_clearance_refinement_r2/STATIC_SCENE_MANIFEST_R2.json');scene=read(ROOT/'audits/minuet_stage_c_r1_dual_hand_synchronized_performance/SCENE_MANIFEST.json')
inputs=[CAND,TL,ROOT/'audits/minuet_in_g_longer_phrase_validation_r1/source/anna-magdalena-04.mid',ROOT/rp['asset']['path'],ROOT/lp['asset']['path'],Path(sm['candidate_path']),Path(scene['path']),ROOT/'production_spec/RIGHT_HAND_PRODUCT_BASELINE.json',ROOT/'production_spec/LEFT_HAND_PRODUCT_BASELINE.json']
for folder in ['minuet_stage_a_r2_natural_continuous_motion','minuet_stage_b_r3_budget_policy_candidate_recovery_r1','minuet_stage_c_r1_dual_hand_synchronized_performance','piano_pedagogical_motion_refinement_r1']:
 for name in ['SCENE_MANIFEST.json','PERFORMANCE_TIMELINE.json','FINAL_STATUS.json']:
  p=ROOT/'audits'/folder/name
  if p.exists():inputs.append(p)
assert sha(ROOT/rp['asset']['path'])==rp['asset']['sha256'];assert sha(ROOT/lp['asset']['path'])==lp['asset']['sha256'];assert sha(Path(scene['path']))==scene['sha256'];assert sha(Path(sm['candidate_path']))==sm['candidate_sha256']
(O/'PROTECTED_FILES_BEFORE.json').write_text(json.dumps({str(p):sha(p) for p in inputs},indent=2)+'\n',encoding='utf8')
(O/'INPUT_BINDINGS.json').write_text(json.dumps(dict(task='PIANO_C01_WHOLE_HAND_MOTION_FEASIBILITY_R1',candidate_source=str(CAND),candidate_sha256=sha(CAND),candidate_id='C01_PIANOPLAYER',authority='Human authorized isolated dynamic candidate; DESIGN_PROVISIONAL',source_scene=scene,static_scene=sm,right_pointer=rp,left_pointer=lp,timeline=str(TL),notes=notes,source_lead_sec=.35,clip_start_sec=notes[0]['note_on']-.15,clip_end_sec=notes[-1]['note_off'],no_pianoplayer_cm_as_control=True),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('INPUT_IDENTITY_PASS',len(notes),'context R06 plus core R07-R14')
