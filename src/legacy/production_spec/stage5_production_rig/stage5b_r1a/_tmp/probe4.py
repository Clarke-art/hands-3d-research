import bpy, sys, os, json, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; jf=ref["jf"]; adj=ref["eadj"]
TF=C.thumb_frame(ref); ARC=TF["arc_thumb_mm"]; sMCP,sIP=TF["s_MCP_joint_mm"],TF["s_IP_joint_mm"]
MED=ref["med_edge"]; TAU=MED; own=ref["OWN_V"]
dth=[ref["dchain"][i]["THUMB"] for i in range(NV)]; didx=[ref["dchain"][i]["INDEX"] for i in range(NV)]
NAIL=C.thumb_masks(ref,TF,TAU,0,0)["nail_thumb_vertices"]; CAP=set(ref["cap"]["thumb_cap_vertex_ids"])
pt_i=C.chp(jf,"INDEX"); XIJ_I=C.chain_arc_table(jf,"INDEX"); sPIP=XIJ_I[1]
ARCI=[C.arc_of(pt_i,V0[i])[0] for i in range(NV)]
RTT=9.44; RMAX=30.0
# THUMB|INDEX ownership boundary
bnd=set()
for a,b in ref["EDGES"]:
    if (own[a]=="THUMB" and own[b]=="INDEX") or (own[a]=="INDEX" and own[b]=="THUMB"):
        bnd.add(a); bnd.add(b)
print("BND(THUMB|INDEX)=%d arc[%.1f,%.1f]"%(len(bnd),min(ARC[i] for i in bnd),max(ARC[i] for i in bnd)))
for k in (1,2,3):
    band=C.rings(adj,bnd,k)
    W=[i for i in band if own[i] in ("THUMB","INDEX") and ARC[i]<=sIP-TAU and ARCI[i]<=sPIP+TAU and i not in NAIL and i not in CAP]
    print("  web k=%d: band=%d -> FIRST_WEB=%d own=%s arc=[%.1f,%.1f] idxArc=[%.1f,%.1f] nail=%d cap=%d dIdx[min=%.1f max=%.1f]"%(
      k,len(band),len(W),{o:sum(1 for i in W if own[i]==o) for o in set(own[i] for i in W)},
      min([ARC[i] for i in W],default=-1),max([ARC[i] for i in W],default=-1),
      min([ARCI[i] for i in W],default=-1),max([ARCI[i] for i in W],default=-1),
      len(set(W)&NAIL),len(set(W)&CAP),min([didx[i] for i in W],default=-1),max([didx[i] for i in W],default=-1)))
    if k==2: WEB2=W
# THENAR_BASE candidates
thumb_set=set(i for i in range(NV) if own[i]=="THUMB")
for k in (1,2,3):
    wr_band=set(j for j in C.rings(adj,thumb_set,k) if own[j]=="wrist")
    T=[i for i in range(NV) if (own[i]=="THUMB" and ARC[i]<=sMCP+TAU and dth[i]>RTT)] + sorted(wr_band)
    T=[i for i in T if ARC[i]<=sMCP+TAU or own[i]=="THUMB"]
    print("thenar k=%d: wrist_band=%d total=%d own=%s arc=[%.1f,%.1f] dThumb[min=%.1f max=%.1f]"%(
      k,len(wr_band),len(T),{o:sum(1 for i in T if own[i]==o) for o in set(own[i] for i in T)},
      min(ARC[i] for i in T),max(ARC[i] for i in T),min(dth[i] for i in T),max(dth[i] for i in T)))
# FINAL masks
WEB = WEB2
T_wr = set(j for j in C.rings(adj,thumb_set,2) if own[j]=="wrist")
THEN = set(i for i in range(NV) if own[i]=="THUMB" and ARC[i]<=sMCP+TAU and dth[i]>RTT) | T_wr
DIST = set(i for i in range(NV) if (own[i]=="THUMB" and ARC[i]>=sIP-TAU) or i in NAIL or i in CAP)
PROX = set(i for i in range(NV) if own[i]=="THUMB" and sMCP-TAU<=ARC[i]<=sIP+TAU)
META = set(i for i in range(NV) if own[i]=="THUMB" and ARC[i]<=sMCP+TAU)
AUTH = DIST|PROX|META|THEN|set(WEB)
print("\nFINAL: DIST=%d PROX=%d META=%d THEN=%d WEB=%d -> AUTH=%d (%.1f%% of mesh)"%(
  len(DIST),len(PROX),len(META),len(THEN),len(WEB),len(AUTH),100.0*len(AUTH)/NV))
print("AUTH own:",{o:sum(1 for i in AUTH if own[i]==o) for o in set(own[i] for i in AUTH)})
# THUMB_IP nonzero vertices vs AUTH
import json as J
r1w=[None]*NV
b=C.load_weights(os.path.join(TOP,"stage5b_r1","RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1.blend"))
W=b["W"]
ipnz=[i for i in range(NV) if W[i].get("THUMB_IP_R",0.0)>0]
nonz=[i for i in range(NV) if i in AUTH]
out=[i for i in ipnz if i not in AUTH]
print("THUMB_IP nonzero=%d ; of which OUTSIDE AUTH = %d %s"%(len(ipnz),len(out),out[:20]))
# which groups appear on AUTH vertices
gs=set()
for i in AUTH: gs|=set(W[i].keys())
print("groups present on AUTH vertices (R1):",sorted(gs))
