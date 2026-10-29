# STAGE4C_R2 -- nail face selector (shared by the probe and the finalizer).
#
# WHY R1 FAILED (measured, see _tmp/R1_SELECTOR_DIAGNOSIS.json):
#   R1 used only (face normal cone) + (axial span of the distal bone) + (outer radial share).
#   There was NO digit-ownership gate and NO distal-phalanx spatial domain gate.  Measured
#   consequences on the R1 result:
#     * adjacent finger nail normals are nearly parallel (index-middle 13.1 deg, middle-ring
#       11.8 deg, ring-little 15.2 deg, index-ring 24.3 deg), so a 63.3 deg cone swallows the
#       neighbours: 838 faces fall inside more than one digit's cone
#     * 204 face instances over only 155 unique faces -> 49 duplicate assignments
#     * the axial test constrains only ONE coordinate, so faces at the finger ROOT still
#       satisfy it: R1's union reaches 64.8 mm from the nearest distal bone, with 46 faces
#       further than 12 mm away (p90 = 43.6 mm) -- that is the pale band at the finger roots
#     * 36 of R1's union faces are actually owned by a different digit
#
# R2 uses three independent gates:
#   A. DIGIT OWNERSHIP  : the face must belong to the owning digit.  Ownership is decided on
#                         the digit's FULL bone chain (meta+prox+distal), which is strictly
#                         stronger than the distal-segment-only test the brief names -- and it
#                         has to be, because in this opposed RSSF pose the thumb's distal
#                         phalanx sits only ~9 mm from the INDEX knuckle, so a distal-segment
#                         rule alone would hand index-knuckle faces to the thumb.  The brief's
#                         literal distal-segment comparison is ALSO evaluated and reported.
#   B. DISTAL DOMAIN    : axial inside the distal phalanx + radial inside the digit's own
#                         measured surface envelope (so nothing at the finger root can pass)
#   C. DORSAL / NAIL-FACING : face normal inside a TIGHT cone (neighbours' nail normals are
#                         only ~13 deg apart) AND centroid on the dorsal side of the bone
#
# Gate A makes the five sets disjoint BY CONSTRUCTION: every face has exactly one owner.

import math
from mathutils import Vector

DIGITS = ["thumb", "index", "middle", "ring", "little"]
DISTAL = {"thumb": "THUMB_IP_R", "index": "INDEX_DIP_R", "middle": "MIDDLE_DIP_R",
          "ring": "RING_DIP_R", "little": "LITTLE_DIP_R"}
PROX = {"thumb": "THUMB_MCP_R", "index": "INDEX_PIP_R", "middle": "MIDDLE_PIP_R",
        "ring": "RING_PIP_R", "little": "LITTLE_PIP_R"}
META = {"thumb": "THUMB_CMC_R", "index": "INDEX_MCP_R", "middle": "MIDDLE_MCP_R",
        "ring": "RING_MCP_R", "little": "LITTLE_MCP_R"}

AX_LO, AX_HI = 0.18, 0.80      # distal phalanx span (0 = DIP/IP joint, 1 = fingertip)
CONE_MIN = 0.60                # ~53 deg; must be tight because neighbours are ~13 deg apart
OWN_MARGIN = 0.85              # own chain dist < 0.85 * nearest competing chain dist
RADIAL_FRAC_MIN = 0.25         # centroid radial offset >= 0.25 * digit envelope radius
COMP_MIN_M = 0.0040            # >= 4 mm from every other digit's distal bone (web guard)
SPECK_FRAC = 0.15              # drop islands smaller than 15% of the digit's largest island


def seg_dist(p, a, b):
    ab = b - a
    L2 = ab.length_squared
    if L2 < 1e-18:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length


def chain_dist(p, S, d):
    return min(seg_dist(p, S[k][0], S[k][1]) for k in (d + "_META", d + "_PROX", d))


def build_frame(FR):
    """FR = the joint-frame JSON 'bones' dict.  Returns segment + nail-normal tables."""
    mcp = sum((Vector(FR["%s_MCP_R" % n.upper()]["head"])
               for n in ("index", "middle", "ring", "little")), Vector()) / 4
    wrist = Vector(FR["WRIST_R"]["head"])
    tips = {n: Vector(FR["%s_TIP_R" % n.upper()]["head"])
            for n in ("index", "middle", "ring", "little")}
    fw = (sum(tips.values(), Vector()) / 4 - wrist).normalized()
    rad = (tips["index"] - tips["little"]).normalized()
    rad = (rad - fw * rad.dot(fw)).normalized()
    dorsal = fw.cross(rad).normalized()
    seg = {}
    nn = {}
    for d in DIGITS:
        seg[d] = (Vector(FR[DISTAL[d]]["head"]), Vector(FR[DISTAL[d]]["tail"]))
        seg[d + "_PROX"] = (Vector(FR[PROX[d]]["head"]), Vector(FR[PROX[d]]["tail"]))
        seg[d + "_META"] = (Vector(FR[META[d]]["head"]), Vector(FR[META[d]]["tail"]))
        h, t = seg[d]
        dirv = (t - h).normalized()
        mu = (Vector(FR[META[d]]["tail"]) - Vector(FR[META[d]]["head"])).normalized()
        lat = dorsal.cross(mu)
        lat = lat.normalized() if lat.length > 1e-9 else rad.copy()
        v = lat.cross(dirv)
        v = v.normalized() if v.length > 1e-9 else dorsal.copy()
        nn[d] = v if v.dot(dorsal) >= 0 else -v
    return {"seg": seg, "nail_normal": nn, "dorsal": dorsal, "radial": rad, "wrist": wrist,
            "mcp_centre": mcp}


def face_records(FACES, FC, FN, fr):
    """per-face ownership (full chain) + the quantities every gate needs"""
    S = fr["seg"]
    NN = fr["nail_normal"]
    out = []
    for fi in range(len(FACES)):
        c = FC[fi]
        ch = {d: chain_dist(c, S, d) for d in DIGITS}
        order = sorted(ch, key=ch.get)
        owner, comp = order[0], order[1]
        dd = {d: seg_dist(c, S[d][0], S[d][1]) for d in DIGITS}
        dorder = sorted(dd, key=dd.get)
        h, t = S[owner]
        dirv = (t - h).normalized()
        L = (t - h).length
        a = (c - h).dot(dirv)
        proj = h + dirv * a
        radial = (c - proj).dot(NN[owner])
        out.append({"fi": fi, "centroid": c, "normal": FN[fi],
                    "owner": owner, "chain_dist": ch[owner], "chain_comp": ch[comp],
                    "comp_digit": comp,
                    "distal_dist": dd[owner], "distal_comp_digit": dorder[1],
                    "distal_comp_dist": dd[dorder[1]],
                    "all_distal": dd, "all_chain": ch,
                    "axial_frac": a / L, "radial": radial,
                    "cone": FN[fi].dot(NN[owner])})
    return out


def envelopes(rec):
    """per-digit surface envelope radius at the distal phalanx = 95th pct of the distance to
    that digit's OWN distal segment over its own faces in the axial band.  A measured property
    of the digit, not a tuned constant, so it adapts to the thin little finger."""
    R = {}
    for d in DIGITS:
        vals = sorted(r["distal_dist"] for r in rec
                      if r["owner"] == d and 0.15 <= r["axial_frac"] <= 0.85)
        R[d] = vals[int(0.95 * (len(vals) - 1))] if vals else 0.010
    return R


def connected_components(faces_set, FACES):
    par = {fi: fi for fi in faces_set}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    E = {}
    for fi in faces_set:
        f = FACES[fi]
        for i in range(len(f)):
            k = (f[i], f[(i + 1) % len(f)])
            E.setdefault(k if k[0] < k[1] else (k[1], k[0]), []).append(fi)
    for _k, fs in E.items():
        if len(fs) == 2:
            ra, rb = find(fs[0]), find(fs[1])
            if ra != rb:
                par[ra] = rb
    comps = {}
    for fi in faces_set:
        comps.setdefault(find(fi), []).append(fi)
    return sorted(comps.values(), key=len, reverse=True)


def select(FACES, FC, FN, fr, verbose=False):
    rec = face_records(FACES, FC, FN, fr)
    R = envelopes(rec)
    sel = {d: set() for d in DIGITS}
    for r in rec:
        d = r["owner"]
        ok = (r["chain_dist"] < OWN_MARGIN * r["chain_comp"]          # gate A (chain ownership)
              and r["distal_dist"] < r["distal_comp_dist"]            # gate A (literal, as briefed)
              and r["distal_comp_dist"] >= COMP_MIN_M                 # web guard
              and AX_LO <= r["axial_frac"] <= AX_HI                   # gate B (axial)
              and 0 < r["radial"] <= R[d]                             # gate B (dorsal side)
              and r["radial"] >= RADIAL_FRAC_MIN * R[d]               # gate B (outer shell)
              and r["cone"] >= CONE_MIN)                              # gate C
        if ok:
            sel[d].add(r["fi"])
    speck = {}
    for d in DIGITS:
        if not sel[d]:
            speck[d] = {"islands_before": 0, "island_sizes_before": [], "dropped_as_specks": []}
            continue
        comps = connected_components(sel[d], FACES)
        big = len(comps[0])
        keep = [c for c in comps if len(c) >= SPECK_FRAC * big]
        dropped = [fi for c in comps if len(c) < SPECK_FRAC * big for fi in c]
        sel[d] = set(fi for c in keep for fi in c)
        speck[d] = {"islands_before": len(comps), "island_sizes_before": [len(c) for c in comps],
                    "dropped_as_specks": sorted(dropped)}
    if verbose:
        for d in DIGITS:
            print("   %-7s R_env=%5.2f mm  faces=%3d  islands=%s  dropped=%d"
                  % (d, R[d] * 1000, len(sel[d]), speck[d]["island_sizes_before"],
                     len(speck[d]["dropped_as_specks"])))
    return {"records": rec, "envelopes_m": R, "selection": sel, "speck": speck}


def stats(FACES, FC, rec, sel):
    """the per-digit evidence block required by the brief"""
    import math as _m
    out = {}
    for d in DIGITS:
        fs = sorted(sel[d])
        if not fs:
            out[d] = {"faces": 0}
            continue
        cs = [FC[fi] for fi in fs]
        cen = sum(cs, Vector()) / len(cs)
        lo = [min(c[i] for c in cs) for i in range(3)]
        hi = [max(c[i] for c in cs) for i in range(3)]
        own = [rec[fi]["distal_dist"] for fi in fs]
        comp = [rec[fi]["distal_comp_dist"] for fi in fs]
        ax = [rec[fi]["axial_frac"] for fi in fs]
        out[d] = {
            "faces": len(fs),
            "centroid_world": [round(float(x), 6) for x in cen],
            "bbox_world": [[round(float(x), 6) for x in lo], [round(float(x), 6) for x in hi]],
            "distal_bone": DISTAL[d],
            "axial_frac_min_max": [round(min(ax), 3), round(max(ax), 3)],
            "nearest_owning_bone_distance_mm": {"min": round(min(own) * 1000, 2),
                                                "max": round(max(own) * 1000, 2),
                                                "mean": round(sum(own) / len(own) * 1000, 2)},
            "nearest_competing_digit_distance_mm": {"min": round(min(comp) * 1000, 2),
                                                    "mean": round(sum(comp) / len(comp) * 1000, 2)},
            "bbox_extent_mm": [round((hi[i] - lo[i]) * 1000, 2) for i in range(3)],
        }
    return out
