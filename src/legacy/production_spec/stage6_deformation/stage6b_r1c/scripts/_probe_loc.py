import os, sys, json
from collections import Counter
import bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.append(HERE)
import r1c_pen_common as R

ctx = R.B.build_context(); ref = ctx["ref"]; V0 = ref["V0"]; POLY = ctx["poly"]
probe = R.K.load_probe_sets()
PART = R.K.r2_partition(ctx, ref)
C = R.K.build_corrected_ownership(ctx, ref, PART["partition"], probe)
OWN = C["corrected"]; DOM = set(C["domain"])
cap = set(ref["cap"]["thumb_cap_vertex_ids"])
web = set(ctx["first_web"])

bpy.ops.wm.open_mainfile(filepath=R.K.S6B_R1B_HARNESS)
ob = bpy.data.objects[R.MESH_OBJ]
G = [g.name for g in ob.vertex_groups]


def W(i):
    return dict((G[g.group], round(g.weight, 3)) for g in ob.data.vertices[i].groups if g.weight > 1e-3)


def dom(i):
    w = W(i)
    return max(w.items(), key=lambda kv: kv[1])[0] if w else None


def group_extreme(name):
    gi = ob.vertex_groups[name].index
    best = (-1.0, None)
    for v in ob.data.vertices:
        for g in v.groups:
            if g.group == gi and g.weight > best[0]:
                best = (g.weight, v.index)
    return best


TIPV = group_extreme("THUMB_IP_R")[1]
ITIP = group_extreme("INDEX_DIP_R")[1]
WTIP = group_extreme("THUMB_CMC_R")[1]
print("THUMB_IP max-weight v%d bind=%s" % (TIPV, [round(x * 1000, 1) for x in V0[TIPV]]))
print("INDEX_DIP max-weight v%d bind=%s" % (ITIP, [round(x * 1000, 1) for x in V0[ITIP]]))
print("THUMB_CMC max-weight v%d bind=%s" % (WTIP, [round(x * 1000, 1) for x in V0[WTIP]]))
capc = sum((V0[i] for i in cap), Vector()) / max(1, len(cap))
print("thumb distal cap centroid bind=%s  n=%d" % ([round(x * 1000, 1) for x in capc], len(cap)))

ids = [693, 2156, 2172, 3201, 689, 2160, 697, 2162, 2191, 2584, 2176, 704, 2190,
       1062, 2578, 2071, 651, 154, 1066, 1067, 2580, 2058, 2583, 2066, 649]
print("\nv      dCAP    dINDEX_DIP dCMCmax  dominant_weight          own_R2   inDomain inCap inWeb")
for v in ids:
    print("v%-5d %7.2f %9.2f %8.2f  %-24s %-8s %-8s %-5s %s" % (
        v, (V0[v] - capc).length * 1000, (V0[v] - V0[ITIP]).length * 1000,
        (V0[v] - V0[WTIP]).length * 1000, str(dom(v)), OWN[v], v in DOM, v in cap, v in web))

flip = {}
for fi, p in enumerate(POLY):
    n = len(p)
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        wa, wb = W(a), W(b)
        if len(wa) == 1 and len(wb) == 1 and list(wa)[0] != list(wb)[0]:
            if list(wa.values())[0] > 0.95 and list(wb.values())[0] > 0.95:
                flip[fi] = (a, b)
print("\nfaces touching a HARD 0/1 weight flip (both >0.95, different single bone): %d" % len(flip))
print("  by dominant weight bone:", Counter(dom(POLY[f][0]) for f in flip).most_common())
print("  by R2 ownership       :", Counter(OWN[POLY[f][0]] for f in flip).most_common())
vv = set(v for f in flip for v in POLY[f])
if vv:
    dv = [(V0[v] - capc).length * 1000 for v in vv]
    di = [(V0[v] - V0[ITIP]).length * 1000 for v in vv]
    print("  vertices=%d ; dist to CAP centroid min %.1f max %.1f mm ; dist to INDEX_DIP max-weight min %.1f max %.1f"
          % (len(vv), min(dv), max(dv), min(di), max(di)))
    print("  in thumb distal cap set:", len(vv & cap), "| in first_web:", len(vv & web),
          "| in R2 correction domain:", len(vv & DOM))
    print("  their dominant bones:", Counter(dom(v) for v in vv).most_common())
