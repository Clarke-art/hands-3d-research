import os, sys, json, math, heapq
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
sys.path.append(os.path.join(HERE,"..","..","stage6b_r1b","scripts"))
import s6br1b_common as K
ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]; POLY=ref["TOPO0"]
PROD=K.B.RB.PROD if hasattr(K.B.RB,"PROD") else os.path.abspath(os.path.join(HERE,"..","..","..",".."))
R2A=os.path.join(PROD,"stage5_production_rig","stage5a_r2a","RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
bpy.ops.wm.open_mainfile(filepath=R2A)
ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]; MWo=ob.matrix_world.copy()
def hd(n): return MWo @ Vector(rig.data.bones[n].head_local)
def tl(n): return MWo @ Vector(rig.data.bones[n].tail_local)
CH={"THUMB":[hd("THUMB_CMC_R"),hd("THUMB_MCP_R"),hd("THUMB_IP_R"),tl("THUMB_IP_R")],
    "INDEX":[hd("INDEX_MCP_R"),hd("INDEX_PIP_R"),hd("INDEX_DIP_R"),tl("INDEX_DIP_R")],
    "MIDDLE":[hd("MIDDLE_MCP_R"),hd("MIDDLE_PIP_R"),hd("MIDDLE_DIP_R"),tl("MIDDLE_DIP_R")],
    "RING":[hd("RING_MCP_R"),hd("RING_PIP_R"),hd("RING_DIP_R"),tl("RING_DIP_R")],
    "LITTLE":[hd("LITTLE_MCP_R"),hd("LITTLE_PIP_R"),hd("LITTLE_DIP_R"),tl("LITTLE_DIP_R")]}
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
XIJ={D:[0.0]+[] for D in CH}
for D in CH:
    a=[0.0]; acc=0.0
    for i in range(3):
        acc+=(CH[D][i+1]-CH[D][i]).length; a.append(acc*1000.0)
    XIJ[D]=a
print("XIJ:", {D:[round(x,2) for x in XIJ[D]] for D in ("THUMB","INDEX")})
# robust index tube radius: median over the PIP..DIP band restricted to nearest-chain==INDEX
band=[DL["INDEX"][i] for i in range(NV)
      if XIJ["INDEX"][1]<=SL["INDEX"][i]<=XIJ["INDEX"][2]
      and min(CH,key=lambda D:DL[D][i])=="INDEX"]
band.sort()
print("index band n=%d  p10=%.3f p25=%.3f median=%.3f p75=%.3f"%(
    len(band),band[len(band)//10],band[len(band)//4],band[len(band)//2],band[3*len(band)//4]))
tb=[DL["THUMB"][i] for i in range(NV)
    if XIJ["THUMB"][1]<=SL["THUMB"][i]<=XIJ["THUMB"][2]
    and min(CH,key=lambda D:DL[D][i])=="THUMB"]
tb.sort()
print("thumb  band n=%d  p25=%.3f median=%.3f"%(len(tb),tb[len(tb)//4],tb[len(tb)//2]))
IDS=[693,689,699,698,692,704,2156,2160,2164,2172,2153,2155,2157,2159,2161,2163,2166,2169,3196,3197,3198,3201,3203,160,1080,2155]
print("\nv      dTHUMB  sTHUMB | dINDEX  sINDEX | nearestChain | pos(x,y,z) mm")
for v in IDS:
    ds={D:DL[D][v] for D in CH}
    nj=min(ds,key=ds.get)
    print("v%-5d %7.2f %7.2f | %7.2f %7.2f | %-7s | (%8.2f,%8.2f,%8.2f)"%(
        v,DL["THUMB"][v],SL["THUMB"][v],DL["INDEX"][v],SL["INDEX"][v],nj,
        V0[v].x*1000,V0[v].y*1000,V0[v].z*1000))
# are the two blocks connected only through the zipper? geodesic distance between blocks
ADJ={}
for a,b in EDGES:
    ADJ.setdefault(a,[]).append((b,(V0[a]-V0[b]).length)); ADJ.setdefault(b,[]).append((a,(V0[a]-V0[b]).length))
def dij(src):
    d={src:0.0}; pq=[(0.0,src)]
    while pq:
        dd,u=heapq.heappop(pq)
        if dd>d.get(u,1e18)+1e-15: continue
        for w,el in ADJ.get(u,()):
            nd=dd+el
            if nd<d.get(w,1e18)-1e-15: d[w]=nd; heapq.heappush(pq,(nd,w))
    return d
g=dij(2153)
print("\ngeodesic from v2153: v693=%.3f v689=%.3f v2176=%.3f v3196=%.3f v3203=%.3f (mm)"%(
    g.get(693,1e9)*1000,g.get(689,1e9)*1000,g.get(2176,1e9)*1000,g.get(3196,1e9)*1000,g.get(3203,1e9)*1000))
# face degree / structure around the zipper
from collections import Counter
deg=Counter()
for a,b in EDGES: deg[a]+=1; deg[b]+=1
print("vertex degrees: v693=%d v689=%d v2153=%d v2156=%d v3196=%d"%(
    deg[693],deg[689],deg[2153],deg[2156],deg[3196]))
# what materials are near
MAT=ref["MAT0"]
for v in (693,2153,3196,160,1080):
    mats=Counter(MAT[fi] for fi,p in enumerate(POLY) if v in p)
    print("v%-5d incident face materials=%s"%(v,dict(mats)))
