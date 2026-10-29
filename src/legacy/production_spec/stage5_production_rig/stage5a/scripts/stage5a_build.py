# =====================================================================================
# STAGE5A_PRODUCTION_RIG_SKELETON_R1  --  build the 21-bone production rig
# =====================================================================================
# INPUT (frozen, read-only): stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend
#                            sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
# OUTPUT (new):              stage5a/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend
#
# This round builds the SKELETON ONLY:
#   * 21 bones, exact name set, exact hierarchy
#   * deterministic bone-local frames (no Blender default roll)
#   * NO skin weight, NO vertex groups, NO armature modifier, NO mesh parenting
#
# usage: blender -b <master> --python stage5a_build.py -- <stage5a_dir>
# =====================================================================================
import bpy, sys, os, json, math, hashlib, datetime
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
S5A = argv[0]
SCRATCH = os.path.join(S5A, "_tmp")
os.makedirs(SCRATCH, exist_ok=True)

S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MASTER = os.path.join(S4, "stage4c_r2", "RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend")
JOINT_FRAME = os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json")
NAIL_AUDIT = os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json")
ORIGIN_AUDIT = os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json")
OUT_BLEND = os.path.join(S5A, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R1.blend")
LOG = []


def log(m):
    print(m)
    LOG.append(str(m))


MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()

master_sha = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()
log("INPUT master: %s" % MASTER)
log("INPUT sha256: %s" % master_sha)
if master_sha != "fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7":
    raise SystemExit("FAIL CLOSED: master sha256 mismatch")

jf = json.load(open(JOINT_FRAME, encoding="utf-8"))["bones"]
nail = json.load(open(NAIL_AUDIT, encoding="utf-8"))
oa = json.load(open(ORIGIN_AUDIT, encoding="utf-8"))
WRIST_APPROVED = Vector(oa["WRIST_ORIGIN"])
STAGE4B_WRIST = Vector(oa["stage4b_WRIST_R_head"])

ob = bpy.data.objects["Hand  - Realistic"]
MW = ob.matrix_world
W = [(MW @ v.co).copy() for v in ob.data.vertices]

# -------------------------------------------------------------------------------------
# 1. deterministic PALM_REFERENCE  (derivation requested by the brief)
#    = centroid of the four finger MCP joint centres
# -------------------------------------------------------------------------------------
FINGERS = ("INDEX", "MIDDLE", "RING", "LITTLE")
PALM_REFERENCE = sum((Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS), Vector()) / 4.0
log("PALM_REFERENCE = centroid of the four finger MCP joint centres = %s"
    % [round(x, 9) for x in PALM_REFERENCE])
log("  |PALM_REFERENCE - Stage4B WRIST_R tail| = %.3e m"
    % (PALM_REFERENCE - Vector(jf["WRIST_R"]["tail"])).length)

WRIST_LEN = (PALM_REFERENCE - WRIST_APPROVED).length
log("WRIST_R head = approved Stage4C R2 origin %s" % [round(x, 9) for x in WRIST_APPROVED])
log("WRIST_R tail = PALM_REFERENCE                %s" % [round(x, 9) for x in PALM_REFERENCE])
log("WRIST_R length = %.4f mm" % (WRIST_LEN * MM))
log("  (Stage-4B TEMP rig WRIST_R length = %.4f mm, NOT reused)"
    % ((Vector(jf["WRIST_R"]["tail"]) - STAGE4B_WRIST).length * MM))
log("  |WRIST_R head - Stage4B WRIST_R head| = %.4f mm" % ((WRIST_APPROVED - STAGE4B_WRIST).length * MM))

# -------------------------------------------------------------------------------------
# 2. deterministic dorsal references
#    per-digit, from the APPROVED nail face sets of the frozen master (NAIL_AUDIT_R2)
# -------------------------------------------------------------------------------------
DIGITS = ["thumb", "index", "middle", "ring", "little"]
DORSAL = {}
me = ob.data
for d in DIGITS:
    acc = Vector((0.0, 0.0, 0.0))
    for fi in nail["per_digit_faces"][d]:
        acc += me.polygons[fi].normal
    DORSAL[d] = acc.normalized()

# WRIST dorsal reference = the PALM PLANE normal.
#   The mean of the finger dorsal references is unusable here: those are ~(+Z), i.e. nearly
#   PARALLEL to the wrist bone (wrist -> palm), which would make align_roll degenerate.
#   The palm plane is spanned by {wrist origin, four MCP joint centres}; its normal is the
#   dorsopalmar axis.  The sign is fixed by geometry: the flexed finger bodies (PIP + DIP
#   joint centres) lie on the PALMAR side, so the dorsal normal points away from them.
PALM_PTS = [WRIST_APPROVED] + [Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS]
PA = sum(PALM_PTS, Vector()) / len(PALM_PTS)
cov = [[0.0] * 3 for _ in range(3)]
for q in PALM_PTS:
    dv = q - PA
    for a in range(3):
        for b in range(3):
            cov[a][b] += dv[a] * dv[b]
# smallest eigenvector of cov, via inverse iteration on (trace*I - cov)
tr = cov[0][0] + cov[1][1] + cov[2][2]
N = [[(tr if a == b else 0.0) - cov[a][b] for b in range(3)] for a in range(3)]
vec = Vector((0.0, 1.0, 0.0))
for _ in range(200):
    nv = Vector((sum(N[0][t] * vec[t] for t in range(3)),
                 sum(N[1][t] * vec[t] for t in range(3)),
                 sum(N[2][t] * vec[t] for t in range(3))))
    if nv.length < 1e-18:
        break
    vec = nv.normalized()
FLEX_BODY = [Vector(jf["%s_%s_R" % (f, s)]["head"]) for f in FINGERS for s in ("PIP", "DIP")]
FLEX_C = sum(FLEX_BODY, Vector()) / len(FLEX_BODY)
if (FLEX_C - PA).dot(vec) > 0:            # finger bodies must be on the PALMAR side
    vec = -vec
DORSAL["wrist"] = vec
for k in list(DORSAL):
    log("dorsal_ref[%-6s] = %s" % (k, [round(x, 6) for x in DORSAL[k]]))
log("  palm-plane points: wrist origin + 4 MCP joint centres; dorsal sign test "
    "(mean PIP/DIP joint centre dot n) = %.6f" % ((FLEX_C - PA).dot(vec) / max(1e-9, (FLEX_C - PA).length)))

# -------------------------------------------------------------------------------------
# 3. bone table
# -------------------------------------------------------------------------------------
TIP_FRACTION = 0.30          # TIP helper = 30% of the preceding distal phalanx length

CHAIN = {
    "THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
    "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"],
    "LITTLE": ["MCP", "PIP", "DIP"],
}
BONES = {}          # name -> dict(head, tail, parent, connect, deform, dorsal_key, chain_key)


def H(n):
    return Vector(jf[n]["head"])


def T(n):
    return Vector(jf[n]["tail"])


# wrist
BONES["WRIST_R"] = dict(head=WRIST_APPROVED, tail=PALM_REFERENCE, parent=None,
                        connect=False, deform=True, dorsal="wrist", digit="wrist",
                        authority="STAGE4C_R2_APPROVED_WRIST_ORIGIN + deterministic PALM_REFERENCE")

for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    d = D.lower()
    segs = CHAIN[D]
    tip_landmark = H("%s_TIP_R" % D)              # the fingerTIP landmark from the frozen frame
    distal_bone = "%s_%s_R" % (D, segs[-1])
    distal_dir = (T(distal_bone) - H(distal_bone)).normalized()
    distal_len = (T(distal_bone) - H(distal_bone)).length
    tip_len = TIP_FRACTION * distal_len
    prev = "WRIST_R"
    for i, s in enumerate(segs):
        n = "%s_%s_R" % (D, s)
        head = H(n)
        tail = H("%s_TIP_R" % D) if i == len(segs) - 1 else H("%s_%s_R" % (D, segs[i + 1]))
        BONES[n] = dict(head=head, tail=tail, parent=prev, connect=(prev != "WRIST_R"),
                        deform=True, dorsal=d, digit=d,
                        authority="Stage4B_R2 candidate joint frame + Stage5A current-mesh validation")
        prev = n
    n = "%s_TIP_R" % D
    BONES[n] = dict(head=tip_landmark, tail=tip_landmark + distal_dir * tip_len,
                    parent=prev, connect=True, deform=False, dorsal=d, digit=d,
                    authority="fingertip landmark (Stage4B_R2 frame) + TIP_FRACTION %.2f rule" % TIP_FRACTION)

log("bone table entries: %d" % len(BONES))
for n in BONES:
    b = BONES[n]
    log("  %-15s L=%7.3f mm  parent=%-15s connect=%s deform=%s"
        % (n, (b["tail"] - b["head"]).length * MM, b["parent"], str(b["connect"]), str(b["deform"])))

# -------------------------------------------------------------------------------------
# 4. build the armature
# -------------------------------------------------------------------------------------
arm_data = bpy.data.armatures.new("RIGHT_HAND_PRODUCTION_RIG_DATA")
rig = bpy.data.objects.new("RIGHT_HAND_PRODUCTION_RIG", arm_data)
bpy.context.scene.collection.objects.link(rig)
rig.location = WRIST_APPROVED
rig.rotation_euler = (0.0, 0.0, 0.0)
rig.scale = (1.0, 1.0, 1.0)
arm_data.display_type = 'OCTAHEDRAL'
arm_data.show_names = True
rig.show_in_front = True

bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]
assert len(ORDER) == 21 and set(ORDER) == set(BONES.keys()), "bone table / order mismatch"

align_report = []
EDIT_ROLL = {}
for n in ORDER:
    b = BONES[n]
    e = eb.new(n)
    e.head = b["head"]
    e.tail = b["tail"]
    e.use_deform = b["deform"]
    dv = DORSAL[b["dorsal"]]
    ydir = (b["tail"] - b["head"]).normalized()
    mis = abs(dv.dot(ydir))
    e.align_roll(dv)                 # deterministic: local +Z is the projected dorsal ref
    EDIT_ROLL[n] = float(e.roll)
    align_report.append({"bone": n, "dorsal_ref_dot_boneY": round(mis, 6)})
    b["dorsal_misalignment"] = mis
for n in ORDER:
    b = BONES[n]
    if b["parent"]:
        eb[n].parent = eb[b["parent"]]
        eb[n].use_connect = bool(b["connect"])
bpy.ops.object.mode_set(mode='OBJECT')

# closest-point probe needs object-local space
inv = MW.inverted()
from mathutils import Vector as _V


def closest_world(p):
    ok, loc, nor, idx = ob.closest_point_on_mesh(inv @ _V(p))
    return (MW @ loc, (MW.to_3x3() @ nor).normalized()) if ok else (None, None)


# -------------------------------------------------------------------------------------
# 5. build-time measurements + evidence
# -------------------------------------------------------------------------------------
bones_json = {}
band_check = {}
for n in ORDER:
    b = arm_data.bones[n]
    _mm = b.matrix_local.to_3x3()
    ydir = _mm.col[1].normalized()
    zax = _mm.col[2].normalized()
    xax = _mm.col[0].normalized()
    ychk = (Vector(b.tail_local) - Vector(b.head_local)).normalized()
    assert (ydir - ychk).length < 1e-5, "bone Y axis mismatch on %s" % n
    bones_json[n] = {
        "head": [round(float(x), 9) for x in b.head_local],
        "tail": [round(float(x), 9) for x in b.tail_local],
        "parent": b.parent.name if b.parent else None,
        "use_connect": bool(b.use_connect),
        "use_deform": bool(b.use_deform),
        "length_mm": round(float((Vector(b.tail_local) - Vector(b.head_local)).length) * MM, 6),
        "roll_rad": EDIT_ROLL[n], "roll_deg": round(math.degrees(EDIT_ROLL[n]), 6),
        "local_X": [round(float(x), 9) for x in xax],
        "local_Y": [round(float(x), 9) for x in ydir],
        "local_Z": [round(float(x), 9) for x in zax],
        "dorsal_ref": [round(float(x), 9) for x in DORSAL[BONES[n]["dorsal"]]],
        "dorsal_ref_dot_boneY": round(BONES[n]["dorsal_misalignment"], 6),
        "authority": BONES[n]["authority"],
    }
    p = Vector(b.head_local)
    loc, nor = closest_world(p)
    band_check[n] = {"inside": bool((p - loc).dot(nor) < 0) if loc else None,
                     "nearest_surface_mm": round((p - loc).length * MM, 4) if loc else None}

topo = {}
bm_ok = True
import bmesh
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
h = hashlib.sha256()
h.update(b"V%d E%d F%d|" % (len(bm.verts), len(bm.edges), len(bm.faces)))
for e in bm.edges:
    a, b = e.verts[0].index, e.verts[1].index
    h.update(b"%d-%d;" % (a, b) if a < b else b"%d-%d;" % (b, a))
for f in bm.faces:
    h.update(b"%d:" % len(f.verts))
    h.update(",".join(str(v.index) for v in f.verts).encode() + b";")
topo["signature"] = h.hexdigest()
topo["V"] = len(bm.verts); topo["E"] = len(bm.edges); topo["F"] = len(bm.faces)
bm.free()

prefs = bpy.context.preferences
prefs.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest())

build = {
    "stage": "STAGE5A_PRODUCTION_RIG_SKELETON_R1", "generated_at": NOW,
    "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
    "input_master": MASTER, "input_master_sha256": master_sha,
    "output_blend": OUT_BLEND,
    "output_sha256": hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest(),
    "TIP_FRACTION": TIP_FRACTION,
    "PALM_REFERENCE": [round(float(x), 9) for x in PALM_REFERENCE],
    "WRIST_R_length_mm": round(WRIST_LEN * MM, 6),
    "wrist_head_vs_stage4b_mm": round((WRIST_APPROVED - STAGE4B_WRIST).length * MM, 6),
    "dorsal_refs": {k: [round(float(x), 9) for x in DORSAL[k]] for k in DORSAL},
    "dorsal_alignment_vs_boneY": align_report,
    "bones": bones_json,
    "inside_mesh_at_head": band_check,
    "topology": topo,
    "log": LOG,
}
json.dump(build, open(os.path.join(SCRATCH, "S5A_BUILD_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("BUILD_LOG=" + os.path.join(SCRATCH, "S5A_BUILD_LOG.json"))
