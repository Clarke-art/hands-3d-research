# STAGE4C_RSSF_ASSET_FINALIZATION_R1 -- READ-ONLY wrist locator (v3, radius-limited).
#
# WHY THIS EXISTS
#   CON-6 wants the object origin at the WRIST JOINT ROTATION CENTER and explicitly forbids
#   the forearm cut-plane centre.  Three candidate values are already in the project:
#     * Stage-4B WRIST_R head z = 0.277349  -- its own log says "narrowest cross-section at
#       -1.9 mm from the forearm cap", and z equals the mesh bbox minimum: it IS the cut plane
#     * Stage-3 wrist_narrowest_z = 0.343    -- from a slice with n = 8 vertices (its
#       neighbours have n = 19..27), so that minimum is a sparse-slice artifact
#     * current object origin z = 0.353646
#
# METHOD (v3)
#   v2 sliced perpendicular to +Z but took every vertex in the slab, so the thumb and thenar
#   inflated the sections (the Stage-3 data shows x_span 100+ mm down at z=0.303).  v3
#   restricts each slab to vertices within R_MAX of the arm axis (the axis through the
#   forearm-cap centroid along +Z), which excludes the thumb column (the thumb CMC sits
#   ~50 mm from that axis).  Metric = convex-hull area of the retained vertices, which is
#   robust to how many vertices the slab happens to catch.
#
# usage: blender -b <blend> --python stage4c_wrist_probe.py -- <out.json>
import bpy, sys, os, json, math
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
ob = bpy.data.objects["Hand  - Realistic"]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]
NV = len(W)
AX = Vector((0.0, 0.0, 1.0))

bones = {}
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        aw = o.matrix_world
        bones = {b.name: {"head": [round(float(x), 6) for x in (aw @ b.head_local)]}
                 for b in o.data.bones}

z_lo = min(p.z for p in W)
cap_ring = [p for p in W if abs(p.z - z_lo) <= 0.004]
cap_c = sum(cap_ring, Vector()) / len(cap_ring)
mcp_z = sum(bones["%s_MCP_R" % n]["head"][2] for n in ("INDEX", "MIDDLE", "RING", "LITTLE")) / 4.0
scan_hi = mcp_z - 0.010
R_MAX = 0.045          # excludes the thumb column (CMC ~50 mm from the axis)
AXIS_XY = Vector((cap_c.x, cap_c.y, 0.0))


def hull_area(pts2):
    """monotone-chain convex hull area of 2-D points"""
    P = sorted(set((round(p[0], 9), round(p[1], 9)) for p in pts2))
    if len(P) < 3:
        return 0.0

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ((h[-1][0] - h[-2][0]) * (p[1] - h[-2][1])
                                   - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0])) <= 0:
                h.pop()
            h.append(p)
        return h
    lo = half(P); up = half(list(reversed(P)))
    poly = lo[:-1] + up[:-1]
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0


prof = []
N = 180
for k in range(N + 1):
    z = z_lo + (scan_hi - z_lo) * k / N
    sel = [p for p in W if abs(p.z - z) <= 0.0045]
    sel_axis = [p for p in sel if (Vector((p.x, p.y, 0)) - AXIS_XY).length <= R_MAX]
    if len(sel_axis) < 12:
        prof.append({"z_mm": round(z * 1000, 3), "n": len(sel_axis), "hull_area_mm2": None})
        continue
    c = sum(sel_axis, Vector()) / len(sel_axis)
    pts2 = [(p.x, p.y) for p in sel_axis]
    ha = hull_area(pts2)
    prof.append({"z_mm": round(z * 1000, 3), "n": len(sel_axis),
                 "hull_area_mm2": round(ha * 1e6, 2),
                 "equiv_radius_mm": round(math.sqrt(ha / math.pi) * 1000, 3),
                 "centre_world": [round(float(x), 6) for x in c]})

valid = [p for p in prof if p["hull_area_mm2"] is not None]
rmin = min(valid, key=lambda p: p["hull_area_mm2"])
# local-minimum search over a smoothed profile (the raw curve is noisy on a 3416-vertex mesh)
sm = []
for i in range(len(valid)):
    a = max(0, i - 4); b = min(len(valid), i + 5)
    sm.append((sum(v["hull_area_mm2"] for v in valid[a:b]) / (b - a), valid[i]))
locmin = min(sm, key=lambda t: t[0])

out = {
    "axis": [0.0, 0.0, 1.0],
    "R_MAX_mm": R_MAX * 1000,
    "forearm_cap_z_mm": round(z_lo * 1000, 3),
    "forearm_cap_centre": [round(float(x), 6) for x in cap_c],
    "scan_range_mm": [round(z_lo * 1000, 3), round(scan_hi * 1000, 3)],
    "mcp_z_mm": round(mcp_z * 1000, 3),
    "profile": prof,
    "min_hull_area_raw": rmin,
    "min_hull_area_smoothed": {"smoothed_area_mm2": round(locmin[0], 2),
                               "slice": locmin[1]},
    "CANDIDATES": {
        "stage4b_WRIST_R_head": bones.get("WRIST_R", {}).get("head"),
        "stage3_wrist_narrowest_z": 0.343,
        "current_object_origin": [round(float(x), 6) for x in MW.translation],
    },
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("forearm cap z = %.3f mm, centre %s" % (out["forearm_cap_z_mm"], out["forearm_cap_centre"]))
print("scan %.1f .. %.1f mm (MCP z %.1f mm)"
      % (out["scan_range_mm"][0], out["scan_range_mm"][1], out["mcp_z_mm"]))
print("raw min hull area: %s" % rmin)
print("smoothed min     : area %.1f mm2 at z=%.2f mm  centre=%s"
      % (locmin[0], locmin[1]["z_mm"], locmin[1]["centre_world"]))
print()
print("profile (hull-area equivalent radius vs z):")
for i, p in enumerate(prof):
    if p["hull_area_mm2"] is None or i % 9:
        continue
    print("   z=%8.2f mm  r_eq=%7.2f mm  area=%9.1f mm2  n=%3d"
          % (p["z_mm"], p["equiv_radius_mm"], p["hull_area_mm2"], p["n"]))
