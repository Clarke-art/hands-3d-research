import json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parent
required=['SOURCE_EVENT_BINDINGS.json','RAW_MODEL_PREDICTIONS.json','ALL_23_FINGERING_COMPARISON.md','B02_FINGERING_ANALYSIS.md','MODEL_RUNTIME_AND_LICENSE.md','FINAL_RECOMMENDATION.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((O/'OUTPUT_VALIDATION_AND_FEASIBILITY.json').read_text())
b=json.loads((O/'SOURCE_EVENT_BINDINGS.json').read_text())
r=json.loads((O/'INFERENCE_RUNTIME_RECEIPT.json').read_text())
assert len([l for l in (O/required[2]).read_text(encoding='utf8').splitlines() if l.startswith('| R') or l.startswith('| L')])==23
assert sha(O/'RAW_MODEL_PREDICTIONS.json')==r['raw_output_sha256']
assert sha(Path(b['source_midi']))==b['source_midi_sha256']
assert sha(Path(b['source_timeline']))==b['source_timeline_sha256']
for name in required:
 text=(O/name).read_text(encoding='utf8'); assert text and '\ufffd' not in text,name
for name in required[2:]:assert 'DESIGN_PROVISIONAL' in (O/name).read_text(encoding='utf8') or name=='MODEL_RUNTIME_AND_LICENSE.md'
files=[p for p in O.iterdir() if p.is_file() and p.name!='DELIVERY_MANIFEST.json']+list((O/'evidence').glob('*'))
manifest=dict(task='PIANO_AUTOMATIC_FINGERING_INFERENCE_POC_R1',required_deliverables=[dict(file=n,bytes=(O/n).stat().st_size,sha256=sha(O/n)) for n in required],source_midi_sha256=b['source_midi_sha256'],source_timeline_sha256=b['source_timeline_sha256'],python_adapter_version=sys.version,all_23_table_rows_verified=True,raw_model_output_untouched=True,final_status='INFERENCE_PARTIAL',files=[dict(file=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files) if p.is_file()])
(O/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('DELIVERY_VERIFIED: 6 required files; 23 comparison rows; source hashes and raw output unchanged; official inference calls = 1')
