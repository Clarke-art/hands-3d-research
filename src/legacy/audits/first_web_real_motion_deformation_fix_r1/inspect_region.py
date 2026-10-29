import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
check_inputs()
request=Path('<USER_HOME>/.codex/attachments/e75f8518-d13a-4d50-91ab-45dd062e5ed5/已粘贴的文本.txt')
dump('PRIOR_HUMAN_DECISION_BIND_R1.json',{'authority':'Current direct user-authored request','request_path':str(request),'request_sha256':sha(request),
    'phase':'PIANOVAM_FIRST_WEB_JOINT_CONTRIBUTION_ISOLATION_R1','Q1':'NONE','Q2':'NOT_RUN','Q3':'NO','PRIMARY_CAUSE_CLASSIFICATION':'CAUSE_NOT_ISOLATED',
    'stopped_research':['joint isolation','PIP/DIP splits','additional combinations','ROM','mapping forensic']})
ob,rig=load(SOURCE)
V=Varray(ob);W=weights(ob)
region=read(FIX/'WEIGHT_ITERATION_2.json')['allowed_vertex_ids']
rows=[]
for f in FRAMES:
    motion(rig,f);rows.append({'frame':f,'vertices_world':Varray(ob),'corrective_values':{k.name:float(k.value) for k in ob.data.shape_keys.key_blocks[1:]}})
neutral(rig)
dump('LOCAL_INPUT_R1.json',{'zero_world':V,'weights':W,'groups':[g.name for g in ob.vertex_groups],
    'region_prior_approved':region,'edges':[list(e.vertices) for e in ob.data.edges],
    'faces':[list(f.vertices) for f in ob.data.polygons],'motion_frames':rows,'modifiers':m.product_payload(ob,rig)['modifiers'],
    'region_world_range':[V[region].min(axis=0),V[region].max(axis=0)],
    'region_weight_totals':{g:float(W[region,j].sum()) for j,g in enumerate([g.name for g in ob.vertex_groups]) if W[region,j].sum()>0},
    'basis_vertex_writes':0})
print('REGION',len(region),'RANGE',V[region].min(axis=0),V[region].max(axis=0),'ACTIVE',[(g.name,round(float(W[region,g.index].sum()),3)) for g in ob.vertex_groups if W[region,g.index].sum()>0],flush=True)
