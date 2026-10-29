import bpy, sys, os, json, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; jf=ref["jf"]
TF=C.thumb_frame(ref); ARC=TF["arc_thumb_mm"]; sMCP,sIP,sTIP=TF["s_MCP_joint_mm"],TF["s_IP_joint_mm"],TF["s_TIP_mm"]
MED=ref["med_edge"]; TAU=MED
dth=[ref["dchain"][i]["THUMB"] for i in range(NV)]; didx=[ref["dchain"][i]["INDEX"] for i in range(NV)]
own=ref["OWN_V"]
# min chain-chain distance per thumb segment
pt=C.chp(jf,"THUMB"); pi=C.chp(jf,"INDEX")
segname=["CMC","MCP","IP"]
for k in range(3):
    best=1e9; bp=None
    for m in range(len(pi)-1):
        for a in range(21):
            for b in range(21):
                p=pt[k]+(pt[k+1]-pt[k])*(a/20.0); q=pi[m]+(pi[m+1]-pi[m])*(b/20.0)
                dd=(p-q).length*1000
                if dd<best: best=dd; bp=(m,a/20)
    print("thumb %s segment -> nearest INDEX %s chain dist = %.2f mm"%(segname[k],["MCP","PIP","DIP"][bp[0]],best))
# smallest dth+didx
sc=sorted(range(NV), key=lambda i: dth[i]+didx[i])
print("\nverts with smallest dThumb+dIndex:")
print("%-6s %-7s %-7s %-6s %-6s %-8s %s"%("v","dThumb","dIndex","sum","arc","own","pos"))
for i in sc[:30]:
    p=V0[i]*1000
    print("%-6d %7.2f %7.2f %6.2f %6.1f %-8s (%.0f,%.0f,%.0f)"%(i,dth[i],didx[i],dth[i]+didx[i],ARC[i],own[i],p.x,p.y,p.z))
# ownership boundary between THUMB and INDEX
adj=ref["eadj"]
bnd=set()
for a,b in ref["EDGES"]:
    if (own[a]=="THUMB" and own[b]=="INDEX") or (own[a]=="INDEX" and own[b]=="THUMB"):
        bnd.add(a); bnd.add(b)
print("\nTHUMB|INDEX ownership-boundary vertices: %d ; arc range [%.1f, %.1f]"%(len(bnd),min((ARC[i] for i in bnd),default=0),max((ARC[i] for i in bnd),default=0)))
k=max(1,int(math.ceil(13.3/MED)))
band = C.rings(adj, bnd, k)
print("boundary band + %d rings = %d verts ; arc [%.1f,%.1f] ; own=%s"%(k,len(band),min((ARC[i] for i in band),default=0),max((ARC[i] for i in band),default=0),{o:sum(1 for i in band if own[i]==o) for o in set(own[i] for i in band)}))
PB=[i for i in band if ARC[i]<=sIP-TAU]
print("band restricted arc<=IP-tau: %d verts ; own=%s"%(len(PB),{o:sum(1 for i in PB if own[i]==o) for o in set(own[i] for i in PB)}))
