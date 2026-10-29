# STAGE5A_R2B -- strict 64-ray parity verification of the key positions (READ-ONLY)
import bpy, sys, os, json, math, hashlib, datetime
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
TOP = os.path.dirname(os.path.dirname(os.path.dirname(OUT)))   # .../stage5_production_rig
DIAGDIR = os.path.join(TOP, "stage5a_r2b")
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
R2A_BLEND = os.path.join(TOP, "stage5a_r2a", "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2A.blend")
R2A_SHA = "c4fafc56c591411bb5ddf07bde44b5fcd6e6a9aa5e0d43b22f9734c0884c2845"
MCP = Vector((1.454060912, 0.001536574, 0.436873049))
IP0 = Vector((1.450860858, 0.006127121, 0.464001149))
TIP = Vector((1.45281744, 0.019802358, 0.493028343))

if hashlib.sha256(open(R2A_BLEND, "rb").read()).hexdigest() != R2A_SHA:
    raise SystemExit("FAIL CLOSED: R2A sha mismatch")
bpy.ops.wm.open_mainfile(filepath=R2A_BLEND)
ob = bpy.data.objects["Hand  - Realistic"]
MW = ob.matrix_world; MINV = MW.inverted(); M3 = MW.to_3x3()
MM = 1000.0


def closest(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(MINV @ Vector(p))
    return (MW @ loc, (M3 @ nor).normalized(), idx) if ok else (None, None, None)


def parity(p, ndir=64):
    pl = MINV @ Vector(p); hits = 0
    for k in range(ndir):
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0; o = pl.copy()
        for _ in range(48):
            ok, loc, nor, idx = ob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 2e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


def seg(a, b, n):
    ins = 0; mmin = 1e9
    for k in range(1, n + 1):
        t = k / (n + 1.0)
        q = a + (b - a) * t
        h, tot = parity(q)
        if h > tot / 2:
            ins += 1
        mmin = min(mmin, (Vector(q) - closest(q)[0]).length * MM)
    return "%d/%d" % (ins, n), round(mmin, 4)


D = json.load(open(os.path.join(DIAGDIR, "THUMB_STRAIGHT_BONE_COMPATIBILITY_DIAGNOSIS.json"),
                   encoding="utf-8"))
w = D["wide_scan_maxima"]
TARGETS = {
    "R2A_current_THUMB_IP": IP0,
    "best_near_feasible_in_zone": Vector(D["best_near_feasible_candidate_in_zone"]["world_position"]),
    "max_IP_TO_TIP_position": Vector(w["max_IP_TO_TIP_position"]["world_position"]),
    "best_combined_position": Vector(w["best_combined_position"]["world_position"]),
}
R = {}
for nm, p in TARGETS.items():
    R[nm] = {"world_position": [round(float(x), 9) for x in p],
             "STRICT_MCP_TO_IP_20": seg(MCP, p, 20)[0],
             "STRICT_MCP_TO_IP_40": seg(MCP, p, 40)[0],
             "STRICT_IP_TO_TIP_20": seg(p, TIP, 20)[0],
             "STRICT_IP_TO_TIP_40": seg(p, TIP, 40)[0],
             "STRICT_min_margin_mm": min(seg(MCP, p, 40)[1], seg(p, TIP, 40)[1])}
    print("[VERIFY]", nm, R[nm]["STRICT_MCP_TO_IP_40"], R[nm]["STRICT_IP_TO_TIP_40"])
json.dump({"stage": "STAGE5A_R2B_STRICT_PARITY_VERIFICATION",
           "generated_at": datetime.datetime.now().astimezone().isoformat(),
           "input_blend": R2A_BLEND, "input_sha256": R2A_SHA,
           "method": "64-direction ray parity, t = k/(n+1), k=1..n (n = 20 and 40)",
           "targets": R}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("VERIFY_DONE")
