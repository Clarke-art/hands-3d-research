import bpy, sys, os, json, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; adj=ref["eadj"]; own=ref["OWN_V"]
TF=C.thumb_frame(ref); ARC=TF["arc_thumb_mm"]; sMCP,sIP=TF["s_MCP_joint_mm"],TF["s_IP_joint_mm"]
MED=ref["med_edge"]; TAU=MED
dth=[ref["dchain"][i]["THUMB"] for i in range(NV)]
RTT=9.44
b=C.load_weights(os.path.join(TOP,"stage5b_r1","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend")); W=b["W"]
thumb_set=set(i for i in range(NV) if own[i]=="THUMB")
T_wr=sorted(j for j in C.rings(adj,thumb_set,2) if own[j]=="wrist" and ARC[j]<=sMCP)
print("wrist-owned thenar band (s<=sMCP):",len(T_wr))
from collections import Counter
fc=Counter(); maxf=0
for i in T_wr:
    fz=[g for g in C.FROZEN_GROUPS if W[i].get(g,0.0)>0]
    fc[tuple(sorted(fz))]+=1
    maxf=max(maxf,len(fz))
for k,v in fc.most_common(10): print("  frozen set",k,"->",v)
print("max frozen groups on thenar band:",maxf)
for i in T_wr[:6]:
    print("  v%d s=%.1f dth=%.1f W=%s"%(i,ARC[i],dth[i],{k:round(v,3) for k,v in sorted(W[i].items(),key=lambda kv:-kv[1])}))
# frozen group counts across all AUTH
AUTH=set(i for i in range(NV) if own[i]=="THUMB")|set(T_wr)
mx=0; dist=Counter()
for i in AUTH:
    n=len([g for g in C.FROZEN_GROUPS if W[i].get(g,0.0)>0]); dist[n]+=1; mx=max(mx,n)
print("AUTH frozen-group-count distribution:",dict(sorted(dist.items())),"max=",mx)
# index chain arc table
print("INDEX chain arc mm:",[round(x,4) for x in C.chain_arc_table(ref["jf"],"INDEX")])
# R1 worst prune recompute
W4=[(i,round(1.0-sum(sorted(W[i].values(),reverse=True)[:3]),6)) for i in range(NV) if len(W[i])>=4]
W4.sort(key=lambda t:-t[1])
print("R1 worst discarded (recomputed):",W4[:5])
