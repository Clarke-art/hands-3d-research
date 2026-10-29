import os, sys, json, math
import bpy
from mathutils import Quaternion, Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import s6br1b_common as K
ctx = K.B.build_context(); ref = ctx["ref"]; V0 = ref["V0"]; EDGES = ref["EDGES"]; NV = ref["NV"]
probe = K.load_probe_sets(); part = K.r2_partition(ctx, ref)["partition"]
C = K.build_corrected_ownership(ctx, ref, part, probe); corr = C["corrected"]
EDGE_LEN0 = [(V0[a]-V0[b]).length for a,b in EDGES]
bnd = [k for k,(a,b) in enumerate(EDGES) if corr[a]!=corr[b] and {corr[a],corr[b]}=={"THUMB","INDEX"}]
bep = sorted(set([v for k in bnd for v in EDGES[k]]))
web = set(ctx["first_web"]); web2 = set()
adj = {}
for a,b in EDGES:
    adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
for w in web:
    web2 |= adj[w]
print("boundary endpoints=%d ; web(21)+1ring=%d ; overlap=%d" % (len(bep), len(web2), len(set(bep) & (web|web2))))

bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]; rig = bpy.data.objects[K.RIG_OBJ]; MW = ob.matrix_world.copy()
W0 = K.read_weights(ob, NV)
VER, FOR = K.weight_consistency(corr, W0)
base_primary = sorted(i for i in C["domain"] if VER[i]=="WEIGHT_RECONCILIATION_REQUIRED"
                      and i not in web)
VARIANTS = {
    "A_base": set(base_primary),
    "C_boundary_added": set(base_primary) | set(bep),
    "D_web_excluded_all": set(i for i in C["domain"] if VER[i]=="WEIGHT_RECONCILIATION_REQUIRED"
                              and i not in web and i not in web2 and i not in set(bep)),
}
CM = json.load(open(K.PROVENANCE["stage6b_case_matrix"], encoding="utf-8"))
CASES = dict((c["case_id"], c) for c in CM["cases"])

def apply_and_measure(primary, tag):
    Wn, info = K.trusted_interpolation(ref, W0, corr, set(primary))
    W2 = [dict(W0[i]) for i in range(NV)]
    for i in primary:
        nv = Wn[i]
        if not nv: continue
        items = sorted(nv.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
        s = sum(v for _g,v in items)
        if s<=0: continue
        W2[i] = dict((g, v/s) for g,v in items)
    K.push_weights(ob, NV, W2)
    res = {}
    for cid in ("CMC_OPP_30", "CMC_MCP_L3", "FULL_OPP_L3"):
        c = CASES[cid]; q = c["cmc_quaternion_local"]
        K.B.reset_pose(rig)
        pb = rig.pose.bones["THUMB_CMC_R"]; pb.rotation_mode='QUATERNION'
        pb.rotation_quaternion = Quaternion((q[0],q[1],q[2],q[3]))
        if c["mcp_deg"]:
            pbm = rig.pose.bones["THUMB_MCP_R"]; pbm.rotation_mode='QUATERNION'
            pbm.rotation_quaternion = Quaternion(Vector((1,0,0)), math.radians(-c["mcp_deg"]))
        if c["ip_deg"]:
            pbi = rig.pose.bones["THUMB_IP_R"]; pbi.rotation_mode='QUATERNION'
            pbi.rotation_quaternion = Quaternion(Vector((1,0,0)), math.radians(-c["ip_deg"]))
        K.B.update(); V = K.B.evaluate(ob, MW)[0]
        rs = sorted(((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k])) for k in bnd)
        torn = sum(1 for k in bnd if ((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k])>3.0) and ((V[EDGES[k][0]]-V[EDGES[k][1]]).length*1000>5.0))
        hrows = sorted((((V[EDGES[k][0]]-V[EDGES[k][1]]).length/max(1e-18,EDGE_LEN0[k])) for k,_,_ in probe["CLASS_B"]), reverse=True)
        res[cid] = {"bnd_max": round(rs[-1],3), "bnd_torn": torn,
                    "hist_max": round(hrows[0],4),
                    "hist_torn": sum(1 for r in hrows if r>3.0)}
    K.push_weights(ob, NV, W0)
    print("%-20s %s" % (tag, json.dumps(res)))

for tag, pr in VARIANTS.items():
    apply_and_measure(pr, tag)
