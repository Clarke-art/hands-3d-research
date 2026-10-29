import sys
sys.dont_write_bytecode = True
import json, hashlib, ast
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PHASE = 'CAP_FIXTURE_STATIC_VALIDATION_AND_TARGETED_DEFORMATION_R1'
R2D = ROOT / 'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_r2'
R1D = ROOT / 'production_spec/stage5_production_rig/targeted_rig_and_skin_data_rebuild_after_approval_r1'
AUTH = ROOT / 'audits/cap_skin_driver_and_weight_authority_reconciliation_r1'
S5 = ROOT / 'production_spec/stage5_production_rig'
S6 = ROOT / 'production_spec/stage6_deformation'
CAND = R2D / 'RIGHT_HAND_STAGE5B_TARGETED_SKIN_REBUILD_R2.blend'
EXPECTED = 'adf757aeace8a0d69070b94f102b9bef9eb99da9847dd7a5639c4c2c3799dde9'
VECTOR = '1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n, d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def digest(d): return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def inventory(): return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and OUT not in p.parents}
def reuse_functions(path, names, namespace):
    # Execute only existing function definitions. Legacy top-level selectors, writes,
    # anatomical solvers, output directories and full suites are never executed.
    tree=ast.parse(Path(path).read_text(encoding='utf-8-sig'))
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
    return {n.name:digest(ast.dump(n)) for n in nodes}
