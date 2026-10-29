import os, sys, json, math
from collections import Counter, defaultdict
import bpy
from mathutils import Vector, Quaternion
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R
ctx = R.B.build_context(); ref = ctx["ref"]; NV=ref["NV"]; V0=ref["V0"]; POLY=ctx["poly"]
probe = R.K.load_probe_sets(); PART = R.K.r2_partition(ctx, ref)
OWN = R.K.build_corrected_ownership(ctx, ref, PART["partition"], probe)["corrected"]
FOWN=[]
for p in POLY:
    c=Counter(OWN[v] for v in p); m=c.most_common(); top=[k for k,v in m if v==m[0][1]]
    FOWN.append(top[0] if len(top)==1 else sorted(top)[0])
FACE_TRIS={}
for fi,t in R.tris_of(POLY,V0): FACE_TRIS.setdefault(fi,[]).append(t)
def tri_of(V,t): return (V[t[0]],V[t[1]],V[t[2]])
CM=dict((c["case_id"],c) for c in json.load(open(R.K.PROVENANCE["stage6b_case_matrix"],encoding="utf-8"))["cases"])
bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob=bpy.data.objects[R.MESH_OBJ]; rig=bpy.data.objects[R.RIG_OBJ]; MW=ob.matrix_world.copy()
BASE=R.B.intersect_pairs(V0,POLY)
def pose(cid):
    c=CM[cid]; q=c["cmc_quaternion_local"]; R.B.reset_pose(rig)
    pb=rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
    pb.rotation_quaternion=Quaternion((q[0],q[1],q[2],q[3]))
    if c["mcp_deg"]:
        p=rig.pose.bones["THUMB_MCP_R"]; p.rotation_mode='QUATERNION'
        p.rotation_quaternion=Quaternion(Vector((1,0,0)), math.radians(-c["mcp_deg"]))
    if c["ip_deg"]:
        p=rig.pose.bones["THUMB_IP_R"]; p.rotation_mode='QUATERNION'
        p.rotation_quaternion=Quaternion(Vector((1,0,0)), math.radians(-c["ip_deg"]))
    R.B.update(); return R.B.evaluate(ob,MW)[0]
def cls_of(x,y):
    s={FOWN[x],FOWN[y]}
    if s=={"THUMB","INDEX"}: return "THUMB_INDEX"
    if "THUMB" in s and "wrist" in s: return "THUMB_PALM"
    if "THUMB" in s and (s&{"MIDDLE","RING","LITTLE"}): return "THUMB_OTHER_DIGIT"
    if s=={"THUMB"}: return "INTRA_THUMB"
    return "OTHER"
OUT={}
for cid in ("CMC_OPP_30","CMC_MCP_L3","FULL_OPP_L3"):
    V=pose(cid)
    newp=sorted(R.B.intersect_pairs(V,POLY)-BASE)
    per=defaultdict(lambda: {"n":0,"max":0.0,"over2":0,"over5":0,"maxseg":0.0})
    allv=[]
    for fa,fb in newp:
        ok=False; seg=0.0; dmax=0.0
        for ta in FACE_TRIS.get(fa,[]):
            for tb in FACE_TRIS.get(fb,[]):
                A=tri_of(V,ta); B3=tri_of(V,tb)
                pts,okk=R.tri_tri_intersection(A,B3)
                if okk:
                    ok=True; seg=max(seg,R.seg_len(pts)*R.MM)
                    for v in A: dmax=max(dmax,(v-R.closest_point_on_triangle(v,*B3)).length*R.MM)
                    for v in B3: dmax=max(dmax,(v-R.closest_point_on_triangle(v,*A)).length*R.MM)
        if not ok: continue
        k=cls_of(fa,fb); st=per[k]
        st["n"]+=1; st["max"]=max(st["max"],dmax); st["maxseg"]=max(st["maxseg"],seg)
        if dmax>2.0: st["over2"]+=1
        if dmax>5.0: st["over5"]+=1
        allv.append(dmax)
    allv.sort()
    OUT[cid]={"per_class":dict((k,dict(v)) for k,v in per.items()),
              "vertex_to_surface_dist": {"n":len(allv),
                 "median_mm": round(allv[len(allv)//2],4) if allv else 0,
                 "p90_mm": round(allv[int(0.9*(len(allv)-1))],4) if allv else 0,
                 "max_mm": round(allv[-1],4) if allv else 0,
                 "over_2mm": sum(1 for x in allv if x>2.0),
                 "over_5mm": sum(1 for x in allv if x>5.0)}}
    print(cid, json.dumps(OUT[cid]))
json.dump(OUT, open(os.path.join(R.S6B_R1C,"_tmp","R1C_DEPTH2.json"),"w",encoding="utf-8"), indent=1, ensure_ascii=False)
