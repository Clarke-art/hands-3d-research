from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;PRE=P.parent/'piano_hand_visual_first_short_phrase_validation_r1'
sys.path.insert(0,str(PRE));import phrase_common as previous
import numpy as np
c=previous.c;o=previous.o
read=previous.read;sha=previous.sha

def dump(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False,default=lambda a:a.tolist() if hasattr(a,'tolist') else a),encoding='utf8')
TL=read(PRE/'PERFORMANCE_TIMELINE.json');START=.4;END=3.1;FPS=60
