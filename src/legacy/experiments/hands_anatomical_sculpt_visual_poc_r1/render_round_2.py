import os
from pathlib import Path
os.environ['SCULPT_RENDER_ROUND']='2'
exec(compile((Path(__file__).resolve().parent/'render_round.py').read_text(encoding='utf8'),str(Path(__file__).resolve().parent/'render_round.py'),'exec'))
