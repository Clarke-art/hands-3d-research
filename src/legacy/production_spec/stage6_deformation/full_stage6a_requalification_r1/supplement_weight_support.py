import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np
W=read(CAND.parent/'R2_CANDIDATE_CLEAN_REOPEN_PAYLOAD.json')['weights']
fresh=read(R3_PATH);web=set(fresh['FIRST_WEB21']['membership_vertex_ids'])
G=read(OUT/'POSED_COORDINATES_R1.json')['positions_world_m'];V0=np.asarray(G['BIND'])
mixed={i:sorted({g.split('_')[0] for g in row if g!='WRIST_R' and '_TIP_' not in g}) for i,row in enumerate(W)}
mixed={i:families for i,families in mixed.items() if len(families)>1}
A=read(OUT/'FULL_STAGE6A_CROSS_DIGIT_AUDIT_R1.json')
A['other_existing_mixed_driver_vertex_records']=[{'vertex_id':i,'families':families,'weights':W[i],'fresh_frozen_label':fresh['membership']['vertex_labels'].get(str(i),'OUTSIDE_BOUNDED_DOMAIN'),'declared_FIRST_WEB21':i in web} for i,families in mixed.items()]
A['mixed_support_semantics']='Existing current approved weight-support context only; mixed support outside FIRST_WEB21 is not automatically declared sanctioned anatomy or blanket contact acceptance. Inherited static-debt receipt remains separate.'
for cid,row in A['cases'].items():
 V=np.asarray(G[cid]);ids=sorted(mixed)
 row['all_existing_mixed_driver_motion']={'vertex_ids':ids,'displacement_mm':{str(i):float(np.linalg.norm(V[i]-V0[i])*1000) for i in ids}}
A['FIRST_WEB_semantic_checks']={'membership_frozen':True,'only_ALLOWED_WRIST_TH_CMC_TH_MCP_IDX_MCP':all(set(W[i])<={'WRIST_R','THUMB_CMC_R','THUMB_MCP_R','INDEX_MCP_R'} for i in web),'TH_IP_exact_zero':all(W[i].get('THUMB_IP_R',0)==0 for i in web),'TIP_exact_zero':all(not any('_TIP_' in g and w!=0 for g,w in W[i].items()) for i in web),'CMC_locked_all42':True}
dump('FULL_STAGE6A_CROSS_DIGIT_AUDIT_R1.json',A)
print('Supplemented explicit shared support context',len(mixed),'vertices,42 cases')
