import sys,os
from pathlib import Path
out=Path(__file__).resolve().parent;sys.path.insert(0,str(out));sys.dont_write_bytecode=True
os.environ['TRIAL_RENDER_EXTRA']='1'
exec(compile((out/'render_trials.py').read_text(encoding='utf8'),str(out/'render_trials.py'),'exec'))
