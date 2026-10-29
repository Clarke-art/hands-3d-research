from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent; ROOT=P.parents[1]; R4=ROOT/'audits/minuet_stage_c_r4_multi_finger_coordinated_clearance'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf8')
assert not (P/'STRATEGY_LOCK.json').exists()
prior=read(R4/'PROTECTED_INPUTS_BEFORE.json'); bad=[p for p,h in prior.items() if sha(p)!=h];assert not bad,bad
for p in R4.rglob('*'):
 if p.is_file() and '__pycache__' not in str(p):prior[str(p)]=sha(p)
save('PROTECTED_INPUTS_BEFORE.json',prior)
# Read-only export reuses the frozen local model at exact three sample times.
source=(R4/'export_local_model.py').read_text(encoding='utf8')
start=source.index('times=np.unique');end=source.index('\nR=[]',start)
source=source[:start]+'times=np.array([3.729,3.75,3.825,3.85,3.867])'+source[end:]
(P/'export_exact_model.py').write_text(source,encoding='utf8')
print('PROTECTED',len(prior),'EXACT_MODEL_EXPORT_READY')
