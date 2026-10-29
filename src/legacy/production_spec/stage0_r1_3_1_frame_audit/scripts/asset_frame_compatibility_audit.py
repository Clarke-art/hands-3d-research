# STAGE0 R1.3.1 -- ASSET_FRAME_COMPATIBILITY_AUDIT
# READ-ONLY. Opens the official CC0 master .blend, computes geometry diagnostics,
# writes a JSON report. NEVER saves / modifies the master file, NEVER creates a working mesh.
import bpy, json, math, sys
from mathutils import Vector, Matrix

TARGET = "Hand  - Realistic"
OUT_PATH = sys.argv[-1] if sys.argv[-1].endswith('.json') else None

def wverts(name):
    ob = bpy.data.objects[name]
    mw = ob.matrix_world
    return ob, [mw @ v.co for v in ob.data.vertices]

def bbox(V):
    return [round(min(v.x for v in V),4), round(max(v.x for v in V),4),
            round(min(v.y for v in V),4), round(max(v.y for v in V),4),
            round(min(v.z for v in V),4), round(max(v.z for v in V),4)]

rep = {}

# ---------------------------------------------------------------- 1. side calibration
# Objects in the bundle carry explicit .L / .R suffixes -> establishes the bundle's
# own world-space handedness convention, independent of any project document.
cal = {}
for name in list(bpy.data.objects.keys()):
    ob = bpy.data.objects[name]
    if ob.type != 'MESH':
        continue
    if (name.startswith('GEO-hand_') and (name.endswith('.L') or name.endswith('.R'))) \
       or name.startswith('GEO-body_male_realistic') or name.startswith('GEO-body_female_realistic') \
       or name.startswith('GEO-arm_lower_male_primitive_realistic'):
        _, V = wverts(name)
        if not V:
            continue
        b = bbox(V)
        cal[name] = {"bbox": b, "world_loc": [round(c,4) for c in ob.matrix_world.translation],
                     "vcount": len(V),
                     "bbox_center_x": round((b[0]+b[1])/2, 4),
                     "bbox_center_y": round((b[2]+b[3])/2, 4)}
rep["side_calibration"] = cal

# ---------------------------------------------------------------- 2. standalone hand
ob, V = wverts(TARGET)
rep["standalone_hand"] = {
    "name": TARGET,
    "vcount": len(V),
    "bbox": bbox(V),
    "object_origin_world": [round(c,4) for c in ob.matrix_world.translation],
    "dimensions": [round(d,4) for d in ob.dimensions],
}

# 2a. slab profile along Z (distal-proximal), to locate fingertips / palm / wrist / forearm
zs = sorted(v.z for v in V)
zmin, zmax = zs[0], zs[-1]
step = 0.006
slabs = {}
for v in V:
    k = int((v.z - zmin) / step)
    slabs.setdefault(k, []).append(v)
prof = []
for k in sorted(slabs):
    ps = slabs[k]
    cx = sum(p.x for p in ps)/len(ps)
    cy = sum(p.y for p in ps)/len(ps)
    prof.append({
        "z": round(zmin + k*step, 4), "n": len(ps),
        "x_min": round(min(p.x for p in ps),4), "x_max": round(max(p.x for p in ps),4),
        "y_min": round(min(p.y for p in ps),4), "y_max": round(max(p.y for p in ps),4),
        "cx": round(cx,4), "cy": round(cy,4),
    })
rep["z_slab_profile"] = prof

# 2b. fingertip clustering at the distal end (lowest-z band)
band = [v for v in V if v.z <= zmin + 0.030]
band.sort(key=lambda p: p.x)
clusters, cur = [], [band[0]] if band else []
for p in band[1:]:
    if p.x - cur[-1].x > 0.012:
        clusters.append(cur); cur = [p]
    else:
        cur.append(p)
if cur: clusters.append(cur)
rep["distal_tip_clusters"] = [
    {"n": len(c), "x": round(sum(p.x for p in c)/len(c),4),
     "y": round(sum(p.y for p in c)/len(c),4), "z": round(min(p.z for p in c),4)}
    for c in clusters
]

# 2c. transverse profile of the palm / metacarpal region, binning by X.
#     For each X bin we report the two "sheets" (palmar-most and dorsal-most) as
#     y_min / y_max, so that the surface shape across the hand can be read off directly.
def shell_profile(zlo, zhi, xlo, xhi, binw=0.004, label=""):
    reg = [v for v in V if zlo <= v.z <= zhi and xlo <= v.x <= xhi]
    bins = {}
    for p in reg:
        bins.setdefault(int((p.x - xlo)/binw), []).append(p)
    rows = []
    for k in sorted(bins):
        ps = bins[k]
        ys = sorted(p.y for p in ps)
        rows.append({
            "x": round(xlo + k*binw + binw/2, 4), "n": len(ps),
            "y_min": round(ys[0],4), "y_max": round(ys[-1],4),
            "y_mean": round(sum(ys)/len(ys),4),
        })
    return {"label": label, "z_range": [zlo,zhi], "x_range": [xlo,xhi], "rows": rows}

rep["transverse_shells"] = [
    shell_profile(0.235, 0.270, 1.34, 1.50, 0.004, "MCP / knuckle level (across the hand)"),
    shell_profile(0.270, 0.310, 1.34, 1.50, 0.004, "metacarpal / palm body"),
    shell_profile(0.310, 0.350, 1.34, 1.50, 0.004, "wrist"),
]

# 2d. where is the single most-protruding point on each Y sheet?
#     (palmar side must be dominated by the thenar eminence = radial/large-X, proximal;
#      dorsal side must be dominated by the central metacarpal arch)
def extreme_point(region, key, sign):
    best = None
    for p in region:
        val = sign * getattr(p, key)
        if best is None or val > best[0]:
            best = (val, p)
    return {"y": round(best[1].y,4), "x": round(best[1].x,4), "z": round(best[1].z,4)} if best else None

body_region = [v for v in V if 0.23 <= v.z <= 0.40 and 1.34 <= v.x <= 1.50]
rep["sheet_extremes_body"] = {
    "most_negative_Y_point": extreme_point(body_region, "y", -1),
    "most_positive_Y_point": extreme_point(body_region, "y", +1),
}
palm_region = [v for v in V if 0.235 <= v.z <= 0.320 and 1.34 <= v.x <= 1.50]
rep["sheet_extremes_palm_band"] = {
    "most_negative_Y_point": extreme_point(palm_region, "y", -1),
    "most_positive_Y_point": extreme_point(palm_region, "y", +1),
}

# 2e. thumb tip vs 4 fingertips -- radial side test
rep["radial_side_test"] = {
    "note": "in a hand the thumb is the most laterally offset digit; compare its X to the 4 fingertip Xs",
    "four_fingertip_x": rep["distal_tip_clusters"],
}

# 2f. finger centre-line drift: for the central finger band, track the Y centroid
#     as we walk from the finger tip up to the MCP, to detect palmar-ward curvature.
mid = [v for v in V if 1.395 <= v.x <= 1.430 and 0.145 <= v.z <= 0.245]
mbins = {}
for p in mid:
    mbins.setdefault(int((p.z-0.145)/0.010), []).append(p)
rep["central_finger_centreline"] = [
    {"z": round(0.145 + k*0.010 + 0.005, 4), "n": len(mbins[k]),
     "cx": round(sum(p.x for p in mbins[k])/len(mbins[k]),4),
     "cy": round(sum(p.y for p in mbins[k])/len(mbins[k]),4)}
    for k in sorted(mbins)
]

# 2g. thumb distal segment cross-section (palmar pad faces the palm)
th = [v for v in V if 1.455 <= v.x <= 1.505 and 0.235 <= v.z <= 0.275]
if th:
    rep["thumb_tip_region"] = {
        "n": len(th), "bbox": bbox(th),
        "y_mean": round(sum(p.y for p in th)/len(th),4),
        "x_mean": round(sum(p.x for p in th)/len(th),4),
        "z_mean": round(sum(p.z for p in th)/len(th),4),
    }

rep["PASS"] = "ASSET_FRAME_AUDIT_DONE"

if OUT_PATH:
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print("WROTE", OUT_PATH)
else:
    print(json.dumps(rep, ensure_ascii=False, indent=1))
