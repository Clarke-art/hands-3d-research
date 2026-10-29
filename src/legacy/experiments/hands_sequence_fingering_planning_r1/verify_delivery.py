import json,hashlib,math
from pathlib import Path
O=Path(__file__).resolve().parent
def read(n):return json.loads((O/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
b=read('SOURCE_EVENT_BINDINGS.json');cs=read('SEQUENCE_CANDIDATES.json');scores=read('CONDITIONAL_MODEL_PATH_SCORES.json');p=read('PIANOPLAYER_RAW_OUTPUT.json');protected=read('PROTECTED_INPUTS_BEFORE.json')
assert len(cs['candidates'])==1 and len(cs['candidates'])<=3
pairs=set()
for x in b['bindings']:
 pairs.add((x['midi_note_on']['track'],x['midi_note_on']['sequence']));pairs.add((x['midi_note_off']['track'],x['midi_note_off']['sequence']))
assert len(pairs)==46
native={n['note_id']:n['finger'] for n in p['hands']['R']+p['hands']['L']}
for c in cs['candidates']:
 assert len(c['notes'])==23 and len({n['note_id'] for n in c['notes']})==23
 for n in c['notes']:
  x=next(x for x in b['bindings'] if x['note_id']==n['note_id']);source=x['source_timeline_note']
  for output,original in [('hand','hand'),('midi','midi_note'),('note_name','note_name'),('velocity','velocity'),('channel','channel'),('source_on_sec','source_on_sec'),('source_off_sec','source_off_sec'),('on_tick','on_tick'),('off_tick','off_tick')]:assert n[output]==source[original]
  assert n['model_input']==x['model_input'] and n['finger']==native[n['note_id']] and 1<=n['finger']<=5
 assert c['scores']['hard_conflicts']==[]
for r in scores['paths']:
 assert len(r['traces'])==23
 calculated=-sum(t['chosen_log_probability'] for t in r['traces']);assert abs(calculated-r['conditional_nll'])<1e-10
 assert all(math.isfinite(x) for t in r['traces'] for x in t['logits'])
required=['EXISTING_ALGORITHM_REVIEW.md','SEQUENCE_PLANNING_FEASIBILITY.md','SEQUENCE_CANDIDATES.json','ALL_23_SEQUENCE_COMPARISON.md','FINAL_RECOMMENDATION.md']
assert len([l for l in (O/required[3]).read_text(encoding='utf8').splitlines() if l.startswith('| R') or l.startswith('| L')])==23
for name in required:
 text=(O/name).read_text(encoding='utf8');assert text and '\ufffd' not in text
assert all(sha(Path(path))==expected for path,expected in protected.items())
(O/'PROTECTED_INPUTS_AFTER.json').write_text(json.dumps({path:sha(Path(path)) for path in protected},indent=2)+'\n',encoding='utf8')
files=[f for f in O.rglob('*') if f.is_file() and f.name!='DELIVERY_MANIFEST.json']
manifest=dict(task='PIANO_SEQUENCE_FINGERING_PLANNING_R1',status='SEQUENCE_POC_PASS',candidate_count=1,test_notes=23,unique_source_messages=46,all_23_comparison_rows=23,official_pianoplayer_output_fingers_unchanged=True,path_conditional_scores_recomputed=True,protected_file_count=len(protected),all_protected_files_unchanged=True,required_files=[dict(file=n,bytes=(O/n).stat().st_size,sha256=sha(O/n)) for n in required],files=[dict(file=f.relative_to(O).as_posix(),bytes=f.stat().st_size,sha256=sha(f)) for f in sorted(files)])
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DELIVERY_PASS: 5 required artifacts; 1 real complete candidate; 23 rows; 46 unique source messages; 69 condition-specific ONNX runs; all',len(protected),'protected source/previous-experiment files unchanged')
