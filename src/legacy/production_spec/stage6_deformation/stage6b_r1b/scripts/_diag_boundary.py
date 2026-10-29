import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import s6br1b_common as K
ctx = K.B.build_context()
ref = ctx["ref"]
V0 = ref["V0"]; EDGES = ref["EDGES"]
own = ctx["own_r1a"]
probe = K.load_probe_sets()
part = K.r2_partition(ctx, ref)["partition"]
C = K.build_corrected_ownership(ctx, ref, part, probe)
corr = C["corrected"]
idA = set(x[0] for x in probe["CLASS_A"]); idB = set(x[0] for x in probe["CLASS_B"])
all67 = idA | idB
bnd = [k for k, (a, b) in enumerate(EDGES) if corr[a] != corr[b] and {corr[a], corr[b]} == {"THUMB", "INDEX"}]
print("R2 boundary operative edges:", len(bnd))
for k in sorted(bnd):
    a, b = EDGES[k]
    print("  e%-6d bind=%.4f mm  own=[%s,%s] corr=[%s,%s] in67=%s  v%d/v%d  domain=%s/%s" % (
        k, (V0[a] - V0[b]).length * 1000, own[a], own[b], corr[a], corr[b],
        (k in all67), a, b, a in set(C["domain"]), b in set(C["domain"])))
print()
print("of the 67: in-boundary count =", sum(1 for k in bnd if k in all67))
# R1 weights on the worst boundary edge endpoints
bpy = None
import bpy
bpy.ops.wm.open_mainfile(filepath=K.R1B_MASTER)
ob = bpy.data.objects[K.MESH_OBJ]
NV = ref["NV"]
W = K.read_weights(ob, NV)
for k in sorted(bnd):
    a, b = EDGES[k]
    print("e%-6d  W(v%d)=%s" % (k, a, {g: round(v,3) for g,v in W[a].items()}))
    print("        W(v%d)=%s" % (b, {g: round(v,3) for g,v in W[b].items()}))
