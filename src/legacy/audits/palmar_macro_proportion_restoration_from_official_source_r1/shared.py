import sys
sys.dont_write_bytecode = True
import importlib.util
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
spec = importlib.util.spec_from_file_location('macro_readonly_common', ROOT / 'audits/palmar_thenar_source_shape_restoration_r1/common.py')
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
lib.OUT = OUT
lib.PHASE = 'PALMAR_MACRO_PROPORTION_RESTORATION_FROM_OFFICIAL_SOURCE_R1'
lib.CANDIDATE = OUT / 'RIGHT_HAND_STAGE5B_PALMAR_MACRO_RESTORATION_CANDIDATE_R1.blend'
for name in dir(lib):
    if not name.startswith('_'): globals()[name] = getattr(lib, name)

def protected_static(payload):
    import copy
    result=copy.deepcopy(payload)
    settings=result['mesh']['settings']
    if settings.get('use_auto_texspace'):
        for k in ('texspace_location','texspace_size'):settings.pop(k,None)
    return result
