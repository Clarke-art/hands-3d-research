"""Small atomic evidence writer. A final optimizer record is immutable.

One NPZ contains both numerical arrays and metadata, so a failed secondary JSON
export cannot orphan or erase the numerical result. No optimizer implementation.
"""
from support import *
import numpy as np
def json_bytes(value):
 return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,default=lambda v:v.tolist() if hasattr(v,'tolist') else v.item()).encode('utf8')
def atomic_json(name,value,replace=False,fail_before_commit=False):
 target=O/name;temporary=O/(name+'.pending')
 if target.exists() and not replace:raise FileExistsError('IMMUTABLE_EXISTING_EVIDENCE: '+name)
 with temporary.open('wb') as f:f.write(json_bytes(value));f.flush();os.fsync(f.fileno())
 if fail_before_commit:raise RuntimeError('INJECTED_EXPORT_FAILURE_BEFORE_REPLACE')
 os.replace(temporary,target)
def atomic_record(name,arrays,metadata,replace=False,fail_before_commit=False):
 target=O/name;temporary=O/(name+'.pending')
 if target.exists() and not replace:raise FileExistsError('IMMUTABLE_EXISTING_EVIDENCE: '+name)
 clean={k:np.asarray(v) for k,v in arrays.items()}
 for k,v in clean.items():
  if v.dtype.kind not in 'biuf':raise TypeError('NUMERIC_ARRAY_REQUIRED: '+k)
  if not np.isfinite(v).all():raise ValueError('NONFINITE_ARRAY: '+k)
 clean['metadata_utf8']=np.frombuffer(json_bytes(metadata),dtype=np.uint8)
 with temporary.open('wb') as f:
  np.savez_compressed(f,**clean);f.flush();os.fsync(f.fileno())
 # Independently read the pending file before committing it.
 with np.load(temporary,allow_pickle=False) as pending:
  assert set(pending.files)==set(clean)
  assert all(np.array_equal(pending[k],clean[k]) for k in clean)
 if fail_before_commit:raise RuntimeError('INJECTED_EXPORT_FAILURE_BEFORE_REPLACE')
 os.replace(temporary,target)
 return sha(target)
def load_record(name):
 with np.load(O/name,allow_pickle=False) as p:
  arrays={k:p[k].copy() for k in p.files if k!='metadata_utf8'}
  metadata=json.loads(p['metadata_utf8'].tobytes().decode('utf8'))
 return arrays,metadata
def save_last(name,x,fun,metadata,replace=True):
 return atomic_record(name,dict(x=x,fun=fun),dict(record_type='INTERMEDIATE_RESIDUAL_EVALUATION',not_final_optimizer_result=True,**metadata),replace=replace)
