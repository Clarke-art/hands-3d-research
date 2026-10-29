import os,sys,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning'))
import whole_phrase_model as m
np=m.np
S=dict(np.load(P/'LIGHTWEIGHT_SOURCE_SAMPLES.npz'))
# Retain frozen rest/weights only. All dynamic matrices and joint coordinates
# come from the actual sole Lightweight R1 blend exported in this run.
m.D.update({k:S[k] for k in ['times','quat','rig_world','key_angles']})
def source_angles(t):return np.column_stack([np.interp(t,S['times'],S['qdeg'].reshape(-1,20)[:,j]) for j in range(20)]).reshape(-1,5,4)
m.source_angles=source_angles
