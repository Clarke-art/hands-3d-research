import os, sys, json
from collections import Counter
import bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
K=R.K; B=R.B
PROD=R.PROD
R2A=os.path.join(PROD,"stage5_production_rig","stage5a_r2a","RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
JF=os.path.join(PROD,"stage4_blender","stage4c_r2","STAGE4B_R2_JOINT_FRAME.json")

ctx=K.B.build_context(); ref=ctx["ref"]; V0=ref["V0"]; NV=ref["NV"]; EDGES=ref["EDGES"]
MED=ctx["MED"]; tau=ref["med_edge"]
ARC_STALE=ctx["ARC"]; s_MCP=ctx["s_MCP"]; s_IP=ctx["s_IP"]; s_TIP=ctx["s_TIP"]
print("MED=%.4f  tau=%.4f  stale s_MCP=%.4f s_IP=%.4f s_TIP=%.4f"%(MED,tau,s_MCP,s_IP,s_TIP))
print("stale XIJ:",[round(x,4) for x in ctx["TF"]["XIJ_thumb_arc_mm"]])

# ---- LIVE polyline from R2A
bpy.ops.wm.open_mainfile(filepath=R2A)
ob=bpy.data.objects[K.MESH_OBJ]; rig=bpy.data.objects[K.RIG_OBJ]
MWo=ob.matrix_world.copy()
def head(n): return MWo @ Vector(rig.data.bones[n].head_local)
def tail(n): return MWo @ Vector(rig.data.bones[n].tail_local)
LIVE=[head("THUMB_CMC_R"), head("THUMB_MCP_R"), head("THUMB_IP_R"), tail("THUMB_IP_R")]
jf=json.load(open(JF,encoding="utf-8"))["bones"]
STALE=[Vector(jf["THUMB_CMC_R"]["head"]),Vector(jf["THUMB_CMC_R"]["tail"]),
       Vector(jf["THUMB_MCP_R"]["tail"]),Vector(jf["THUMB_IP_R"]["tail"])]
print("\njoint          LIVE(mm)                     STALE(mm)                    |delta| mm")
for lbl,a,b in zip(("CMC_head","MCP_head","IP_head","TIP"),LIVE,STALE):
    print("%-9s (%8.3f,%8.3f,%8.3f) (%8.3f,%8.3f,%8.3f)  %9.3f"%(lbl,
        a.x*1000,a.y*1000,a.z*1000,b.x*1000,b.y*1000,b.z*1000,(a-b).length*1000))
def arc_of(pts,v):
    best=(1e9,0.0); acc=0.0
    for i in range(len(pts)-1):
        a,b=pts[i],pts[i+1]; ab=b-a
        t=max(0.0,min(1.0,(v-a).dot(ab)/max(ab.length_squared,1e-18)))
        d=(v-(a+ab*t)).length
        if d<best[0]: best=(d,(acc+t*ab.length)*1000.0)
        acc+=ab.length
    return best[1],best[0]
LIVE_XIJ=[0.0]
acc=0.0
for i in range(3):
    acc+=(LIVE[i+1]-LIVE[i]).length; LIVE_XIJ.append(acc*1000.0)
print("LIVE XIJ:",[round(x,4) for x in LIVE_XIJ])
r_tt,r_max=K.RC.thumb_radii(ref,ctx["TF"])
print("r_tt=%.4f r_max=%.4f"%(r_tt,r_max))
ft=ctx["f_tube"]
def field(i,params):
    s=ARC_STALE[i] if params is None else None
    return None
P=dict(form="centered",W_IP=5.0,W_MCP=1.0,W_BASE=3.0,shift_IP=0.0,shift_MCP=0.0,profile="quintic")
# proposed live field
prof=K.RB.PROFILES["quintic"]
def live_field(i,live_xij):
    s,pd=arc_of(LIVE,V0[i])
    WIP=5.0*MED; WBASE=3.0*MED
    u=prof(0.5+(s-live_xij[2])/(2.0*WIP))
    vbase=1.0-prof(0.5+(s-live_xij[1])/(2.0*WBASE))
    if u+vbase>1.0:
        k=1.0/(u+vbase); u*=k; vbase*=k
    a=max(0.0,1.0-u-vbase)
    f=ft(ctx["dth"][i])
    return s,pd,{"THUMB_IP_R":round(u,4),"THUMB_MCP_R":round(a,4),
                 "THUMB_CMC_R":round(vbase*f,4),"WRIST_R":round(vbase*(1.0-f),4)}
probe=K.load_probe_sets(); PART=K.r2_partition(ctx,ref)
C=K.build_corrected_ownership(ctx,ref,PART["partition"],probe)
CORR=C["corrected"]; DOM=set(C["domain"])
# current R1B master weights
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob2=bpy.data.objects[K.MESH_OBJ]; G=[g.name for g in ob2.vertex_groups]
def W(i): return dict((G[g.group],round(g.weight,3)) for g in ob2.data.vertices[i].groups if g.weight>1e-3)
IDS=[693,2156,2172,3201,689,2160,697,2162,2191,2584,2176,704,2190,1062,2578,2071,651,154]
print("\nv      s_live  d_live | s_stale | ft    PROPOSED(live)                          R1B_now")
for v in IDS:
    s,pd,fl=live_field(v,LIVE_XIJ)
    print("v%-5d %7.2f %6.2f | %7.2f | %.3f %s  %s"%(v,s,pd,ARC_STALE[v],ft(ctx["dth"][v]),
        json.dumps(fl),json.dumps(W(v))))
print("\nR2 domain:",len(DOM),"of which corrected THUMB:",sum(1 for i in DOM if CORR[i]=="THUMB"))
