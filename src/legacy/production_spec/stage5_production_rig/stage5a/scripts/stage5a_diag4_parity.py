# STAGE5A -- decisive inside/outside test: ray-crossing parity against the FULL mesh.
# Read-only.
import bpy, sys, os, json, math, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
MASTER, OUT = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data
MW = ob.matrix_world
inv = MW.inverted()
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
         "LITTLE": ["MCP", "PIP", "DIP"]}
ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]

random.seed(20260929)


def parity(p, ndir=64):
    hits = 0
    pl = inv @ Vector(p)
    for k in range(ndir):
        # fixed quasi-random directions, deterministic
        th = 2.399963229728653 * k
        z = 1.0 - 2.0 * (k + 0.5) / ndir
        r = math.sqrt(max(0.0, 1.0 - z * z))
        d = Vector((r * math.cos(th), r * math.sin(th), z))
        n = 0
        o = pl.copy()
        for _ in range(40):
            ok, loc, nor, idx = ob.ray_cast(o, d, distance=1.0)
            if not ok:
                break
            n += 1
            o = loc + d * 1e-7
        if n % 2 == 1:
            hits += 1
    return hits, ndir


res = {}
for n in ORDER:
    p = Vector(jf[n]["head"])
    h, t = parity(p)
    res[n] = {"inside_votes": h, "total": t,
              "inside": h > t / 2, "vote_fraction": round(h / t, 4),
              "world": [round(float(x), 6) for x in p]}
json.dump({"method": "ray-crossing parity, 64 quasi-random directions, full mesh",
           "note": "a point that is inside a closed mesh has an ODD crossing count for "
                   "essentially every direction; a point outside or in a neighbouring gap has "
                   "an EVEN count.  Contested votes mean the point sits on a thin web/bridge.",
           "joints": res}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
INSIDE = [n for n in ORDER if res[n]["inside"]]
OUTSIDE = [n for n in ORDER if not res[n]["inside"]]
print("INSIDE (%d): %s" % (len(INSIDE), INSIDE))
print("OUTSIDE(%d): %s" % (len(OUTSIDE), OUTSIDE))
for n in OUTSIDE:
    print("   ", n, res[n]["inside_votes"], "/", res[n]["total"])
