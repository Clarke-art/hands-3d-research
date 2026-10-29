import os, sys, json, heapq
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]; POLY=ref["TOPO0"]; MAT0=ref["MAT0"]
PROD=os.path.abspath(os.path.join(HERE,"..","..",".."))
R2A=os.path.join(PROD,"stage5_production_rig","stage5a_r2a","RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
bpy.ops.wm.open_mainfile(filepath=R2A)
ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]; MWo=ob.matrix_world.copy()
def hd(n): return MWo @ Vector(rig.data.bones[n].head_local)
def tl(n): return MWo @ Vector(rig.data.bones[n].tail_local)
CH={"THUMB":[hd("THUMB_CMC_R"),hd("THUMB_MCP_R"),hd("THUMB_IP_R"),tl("THUMB_IP_R")],
    "INDEX":[hd("INDEX_MCP_R"),hd("INDEX_PIP_R"),hd("INDEX_DIP_R"),tl("INDEX_DIP_R")]}
def arc_of(pts,v):
    bd,bs,acc=1e18,0.0,0.0
    for i in range(len(pts)-1):
        a,b=pts[i],pts[i+1]; ab=b-a
        t=max(0.0,min(1.0,(v-a).dot(ab)/max(ab.length_squared,1e-18)))
        d=(v-(a+ab*t)).length
        if d<bd: bd,bs=d,(acc+t*ab.length)*1000.0
        acc+=ab.length
    return bs,bd*1000.0
SL={};DL={}
for D in CH:
    SL[D]=[0.0]*NV; DL[D]=[0.0]*NV
    for i in range(NV): SL[D][i],DL[D][i]=arc_of(CH[D],V0[i])
XIJ={}
for D in CH:
    a=[0.0]; acc=0.0
    for i in range(3):
        acc+=(CH[D][i+1]-CH[D][i]).length; a.append(acc*1000.0)
    XIJ[D]=a
CAP=set(ref["cap"]["thumb_cap_vertex_ids"]); NAILT=set(ctx["nail"])
NAILF=[fi for fi in range(len(POLY)) if MAT0[fi]==1]
NAIL={}
for fi in NAILF:
    c=sum((V0[v] for v in POLY[fi]),Vector())/len(POLY[fi])
    b=min(CH,key=lambda D:arc_of(CH[D],c)[1]); NAIL.setdefault(b,set()).update(POLY[fi])
NI=NAIL.get("INDEX",set())
IDX_DISTAL=set(i for i in range(NV) if DL["INDEX"][i]<=8.058 and SL["INDEX"][i]>=XIJ["INDEX"][2])
print("anchors: CAP=%d NAIL_THUMB=%d NAIL_INDEX=%d INDEX_DISTAL_PHALANX=%d"%(len(CAP),len(NAILT),len(NI),len(IDX_DISTAL)))
ADJ={}
for a,b in EDGES:
    ADJ.setdefault(a,[]).append((b,(V0[a]-V0[b]).length)); ADJ.setdefault(b,[]).append((a,(V0[a]-V0[b]).length))
def dij(srcs):
    d=[1e18]*NV; pq=[]
    for s in srcs: d[s]=0.0; heapq.heappush(pq,(0.0,s))
    while pq:
        dd,u=heapq.heappop(pq)
        if dd>d[u]+1e-15: continue
        for w,el in ADJ.get(u,()):
            nd=dd+el
            if nd<d[w]-1e-15: d[w]=nd; heapq.heappush(pq,(nd,w))
    return [x*1000.0 for x in d]
gCAP=dij(CAP); gNAILT=dij(NAILT); gNI=dij(NI); gIDP=dij(IDX_DISTAL)
IDS=[693,689,699,698,692,704,2156,2160,2164,2172,2153,2155,2157,2159,2161,2163,2166,2169,3196,3197,3198,3201,3203,160,1080]
print("\nv      gCAP   gNAILT | gNAIL_I gIDXdist | dTHUMB dINDEX  sTHUMB  sINDEX  nearestGeodesically")
for v in IDS:
    t=min(gCAP[v],gNAILT[v]); i=min(gNI[v],gIDP[v])
    print("v%-5d %6.2f %6.2f | %7.2f %8.2f | %6.2f %6.2f %7.2f %7.2f  %s"%(
        v,gCAP[v],gNAILT[v],gNI[v],gIDP[v],DL["THUMB"][v],DL["INDEX"][v],SL["THUMB"][v],SL["INDEX"][v],
        "THUMB" if t<i else "INDEX"))
# global: how many vertices are geodesically closer to the thumb landmarks vs the index landmarks
closer={"THUMB":0,"INDEX":0}
for i in range(NV):
    t=min(gCAP[i],gNAILT[i]); ii=min(gNI[i],gIDP[i])
    closer["THUMB" if t<ii else "INDEX"]+=1
print("\nglobal geodesic landmark preference:",closer)
# how many vertices change if we use landmark-geodesic instead of chain-distance
PART=K.r2_partition(ctx,ref); R2=K.build_corrected_ownership(ctx,ref,PART["partition"],K.load_probe_sets())["corrected"]
S=[i for i in range(NV) if R2[i] in ("THUMB","INDEX")]
diff=0; rows=[]
for i in S:
    t=min(gCAP[i],gNAILT[i]); ii=min(gNI[i],gIDP[i])
    lab="THUMB" if t<ii else "INDEX"
    if lab!=R2[i]:
        diff+=1
        if len(rows)<25: rows.append((i,R2[i],lab,round(t,2),round(ii,2),round(DL["THUMB"][i],2),round(DL["INDEX"][i],2)))
print("vertices where landmark-geodesic differs from R2 chain-distance: %d of %d"%(diff,len(S)))
for r in rows: print("   v%-5d R2=%-6s geo=%-6s gThumb=%7.2f gIndex=%7.2f (dT=%.2f dI=%.2f)"%r)
