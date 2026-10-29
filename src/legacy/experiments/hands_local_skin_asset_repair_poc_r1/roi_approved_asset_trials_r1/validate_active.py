import sys,json
from pathlib import Path
sys.dont_write_bytecode=True;out=Path(__file__).resolve().parent;sys.path.insert(0,str(out))
samples=json.loads((out/'RIGHT16_ACTIVE48_SKIN_CONTACTS.json').read_text(encoding='utf8'))['BASE'];active=max(samples,key=lambda x:x['frozen_corrective_value']);t=active['time_sec']
code=(out/'validate_trials.py').read_text(encoding='utf8').split("save('MULTIPOSE_GEOMETRY_SUMMARY.json'")[0]
code=code.replace('for label,t in POSES:',f"for label,t in [('C1_CORRECTIVE_ACTIVE',{t!r})]:")
exec(compile(code,str(out/'validate_trials.py'),'exec'))
save('ACTIVE_CORRECTIVE_GEOMETRY_SUMMARY.json',results)
save('EXTRA_POSE_CONTEXT.json',{'label':'C1_CORRECTIVE_ACTIVE','time':t,'source':'Maximum original corrective activation among original C1 right16 active48 samples; existing legal Action, no new pose or motion','original_sample':active,'reason':'Detect actual Basis/relative-key coupling and B transfer behaviour when frozen corrective is active.'})
protection('ACTIVE_VALIDATION_INPUT_RECEIPT.json')
