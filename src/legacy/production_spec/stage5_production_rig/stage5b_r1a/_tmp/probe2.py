import bpy, sys, os, json, math
sys.path.append(r"<HANDS_ROOT>/production_spec/stage5_production_rig/stage5b_r1a/scripts")
import r1a_common as C
from mathutils import Vector
TOP = r"<HANDS_ROOT>/production_spec/stage5_production_rig"
ref = C.load_reference(TOP); NV=ref["NV"]; V0=ref["V0"]; jf=ref["jf"]
TF = C.thumb_frame(ref); ARC=TF["arc_thumb_mm"]; sMCP,sIP,sTIP=TF["s_MCP_joint_mm"],TF["s_IP_joint_mm"],TF["s_TIP_mm"]
MED=ref["med_edge"]; TAU=MED
dth=[ref["dchain"][i]["THUMB"] for i in range(NV)]
didx=[ref["dchain"][i]["INDEX"] for i in range(NV)]
own=ref["OWN_V"]
def pct(v,q):
    v=sorted(v); return v[min(len(v)-1,int(q*(len(v)-1)))]
wr=[i for i in range(NV) if own[i]=="wrist"]
print("wrist-owned=%d ; dThumb p5/p10/p25/med=%s"%(len(wr),[round(pct([dth[i] for i in wr],q),2) for q in (0.05,0.10,0.25,0.5)]))
for thr in (15,18,20,22,25,28,30,35):
    s=[i for i in wr if dth[i]<=thr]
    print("  wrist-owned dThumb<=%d : %d"%(thr,len(s)))
th=[i for i in range(NV) if own[i]=="THUMB"]
print("thumb-owned dThumb p50/p75/p90/p95/max=%s"%[round(pct([dth[i] for i in th],q),2) for q in (0.5,0.75,0.9,0.95,1.0)])
# index tube radius
ix=[i for i in range(NV) if own[i]=="INDEX" and 0<=ref["dchain"][i]["INDEX"]]
print("index-owned dIndex p25/med/p75=%s"%[round(pct([didx[i] for i in ix],q),2) for q in (0.25,0.5,0.75)])
# chain-chain min distance
pt= C.chp(jf,"THUMB"); pi=C.chp(jf,"INDEX")
best=(1e9,None)
for k in range(len(pt)-1):
    for m in range(len(pi)-1):
        for a in range(11):
            for b in range(11):
                p=pt[k]+(pt[k+1]-pt[k])*(a/10.0); q=pi[m]+(pi[m+1]-pi[m])*(b/10.0)
                dd=(p-q).length*1000
                if dd<best[0]: best=(dd,(k,m,a/10,b/10))
print("min THUMB-chain to INDEX-chain distance = %.3f mm (seg%d seg%d t=%.1f/%.1f)"%(best[0],best[1][0],best[1][1],best[1][2]*10,best[1][3]*10))
# tube radii p25 from the proximal-phalanx band
tt=[dth[i] for i in th if sMCP<=ARC[i]<=sIP]
ti=[didx[i] for i in ix if 0<=ref["dchain"][i]["INDEX"] and ref["dchain"][i]["INDEX"]<20]
RT=min(tt) if tt else 8
print("thumb phalanx band dThumb p10/p25/med=%s"%[round(pct(tt,q),2) for q in (0.1,0.25,0.5)])
RT25=pct(tt,0.25); RTmed=pct(tt,0.5); RI25=pct(ti,0.25); RImed=pct(ti,0.5)
print("RT25=%.2f RTmed=%.2f RI25=%.2f RImed=%.2f"%(RT25,RTmed,RI25,RImed))
def cnt(rule,name):
    ss=[i for i in range(NV) if rule(i)]
    ob={}
    for i in ss: ob[own[i]]=ob.get(own[i],0)+1
    ar=[ARC[i] for i in ss]
    print("%-42s n=%-4d own=%s arc=[%.1f,%.1f] nail=%d cap=%d"%(name,len(ss),ob,min(ar) if ar else -1,max(ar) if ar else -1,
        len(set(ss)&C.thumb_masks(ref,TF,TAU,0,0)["nail_thumb_vertices"]),len(set(ss)&set(ref["cap"]["thumb_cap_vertex_ids"]))))
W_WEB=2*MED
cnt(lambda i: dth[i]<=W_WEB and didx[i]<=W_WEB, "W1 R1 (d<=2*med both)")
cnt(lambda i: {ref["order2"][i][0][0],ref["order2"][i][1][0]}=={"THUMB","INDEX"}, "W2 2-nearest-chain")
cnt(lambda i: {ref["order2"][i][0][0],ref["order2"][i][1][0]}=={"THUMB","INDEX"} and ARC[i]<=sIP-TAU, "W2 + arc<=IP-tau")
cnt(lambda i: dth[i]<=RT25 and didx[i]<=RI25, "W3 d<=tube p25 both")
cnt(lambda i: dth[i]<=RTmed and didx[i]<=RImed, "W4 d<=tube med both")
cnt(lambda i: dth[i]<=RTmed+TAU and didx[i]<=RImed+TAU, "W5 tube med +1 edge both")
cnt(lambda i: dth[i]+didx[i] <= 2*min(dth[i],didx[i])+2*TAU, "W6 |dth-didx|<=1 edge")
cnt(lambda i: dth[i]<=RTmed and didx[i]<=RImed and ARC[i]<=sIP-TAU, "W7 tube med + arc<=IP-tau")
