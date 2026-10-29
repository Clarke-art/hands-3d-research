# =====================================================================================
# STAGE5A_R2 -- build the requalified 21-bone production rig
# =====================================================================================
# INPUT  (frozen, read-only): stage4c_r2/RIGHT_HAND_ENGINEERING_STAGE4C_R2.blend
#                             sha256 fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7
#        (candidates):        stage5a_r2/_tmp/S5A_R2_CANDIDATES.json
# OUTPUT (new):              stage5a_r2/RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend
#
# Requalified joints : WRIST_R / INDEX_MCP_R / THUMB_CMC_R / THUMB_MCP_R / THUMB_TIP_R
#                      (+ WRIST_R.tail = PALM_REFERENCE, + THUMB_IP_R.tail representation)
# Frozen joints      : the other 15 joints, byte-identical to Stage5A R1
# =====================================================================================
import bpy, sys, os, json, math, hashlib, datetime
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
S5AR2, MASTER = argv[0], argv[1]
S4 = r"<HANDS_ROOT>\production_spec\stage4_blender"
MM = 1000.0
NOW = datetime.datetime.now().astimezone().isoformat()
OUT_BLEND = os.path.join(S5AR2, "RIGHT_HAND_STAGE5A_PRODUCTION_RIG_R2.blend")
CAND = os.path.join(S5AR2, "_tmp", "S5A_R2_CANDIDATES.json")

jf = json.load(open(os.path.join(S4, "stage4c_r2", "STAGE4B_R2_JOINT_FRAME.json"), encoding="utf-8"))["bones"]
nail = json.load(open(os.path.join(S4, "stage4c_r2", "NAIL_AUDIT_R2.json"), encoding="utf-8"))
oa = json.load(open(os.path.join(S4, "stage4c_r2", "ORIGIN_AUDIT_R2.json"), encoding="utf-8"))
cand = json.load(open(CAND, encoding="utf-8"))
SEL = {k: Vector(v) for k, v in cand["selected_candidates"].items()}
ASSET_ORIGIN = Vector(oa["WRIST_ORIGIN"])
LOG = []


def log(m):
    print("[S5A-R2-BUILD]", m)
    LOG.append(str(m))


master_sha = hashlib.sha256(open(MASTER, "rb").read()).hexdigest()
if master_sha != "fde620b2cebd2b4cd894e32b58d7b59ba7fac9b00d3d2dfa5193cefb32513ab7":
    raise SystemExit("FAIL CLOSED: master sha256 mismatch")
log("master sha256 = %s" % master_sha)

bpy.ops.wm.open_mainfile(filepath=MASTER)
ob = bpy.data.objects["Hand  - Realistic"]
me = ob.data

# ---------------------------------------------------------------- dorsal references
FINGERS = ("INDEX", "MIDDLE", "RING", "LITTLE")
DIGITS = ["thumb", "index", "middle", "ring", "little"]
DORSAL = {}
for d in DIGITS:
    acc = Vector((0.0, 0.0, 0.0))
    for fi in nail["per_digit_faces"][d]:
        acc += me.polygons[fi].normal
    DORSAL[d] = acc.normalized()
PALM_PTS = [ASSET_ORIGIN] + [Vector(jf["%s_MCP_R" % f]["head"]) for f in FINGERS]
PA = sum(PALM_PTS, Vector()) / len(PALM_PTS)
cov = [[0.0] * 3 for _ in range(3)]
for q in PALM_PTS:
    dv = q - PA
    for a in range(3):
        for b in range(3):
            cov[a][b] += dv[a] * dv[b]
tr = cov[0][0] + cov[1][1] + cov[2][2]
N = [[(tr if a == b else 0.0) - cov[a][b] for b in range(3)] for a in range(3)]
vec = Vector((0.0, 1.0, 0.0))
for _ in range(200):
    nv = Vector((sum(N[0][t] * vec[t] for t in range(3)), sum(N[1][t] * vec[t] for t in range(3)),
                 sum(N[2][t] * vec[t] for t in range(3))))
    if nv.length < 1e-18:
        break
    vec = nv.normalized()
FLEX = [Vector(jf["%s_%s_R" % (f, s)]["head"]) for f in FINGERS for s in ("PIP", "DIP")]
FC = sum(FLEX, Vector()) / len(FLEX)
if (FC - PA).dot(vec) > 0:
    vec = -vec
DORSAL["wrist"] = vec

# ---------------------------------------------------------------- bone table
TIP_FRACTION = 0.30
CHAIN = {"THUMB": ["CMC", "MCP", "IP"], "INDEX": ["MCP", "PIP", "DIP"],
         "MIDDLE": ["MCP", "PIP", "DIP"], "RING": ["MCP", "PIP", "DIP"], "LITTLE": ["MCP", "PIP", "DIP"]}


def H(n):
    return Vector(jf[n]["head"])


def T(n):
    return Vector(jf[n]["tail"])


BONES = {}
BONES["WRIST_R"] = dict(head=SEL["WRIST_R.head"], tail=SEL["WRIST_R.tail"], parent=None,
                        connect=False, deform=True, dorsal="wrist",
                        authority="STAGE5A_R2_PROD_WRIST_TRANSITION_CENTRE")
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    d = D.lower()
    segs = CHAIN[D]
    tip_landmark = SEL["THUMB_TIP_R.head"] if D == "THUMB" else H("%s_TIP_R" % D)
    distal = "%s_%s_R" % (D, segs[-1])
    distal_dir = (tip_landmark - H(distal)).normalized()
    distal_len = (tip_landmark - H(distal)).length
    prev = "WRIST_R"
    for i, s in enumerate(segs):
        n = "%s_%s_R" % (D, s)
        if D == "THUMB" and s == "CMC":
            head = SEL["THUMB_CMC_R.head"]
            auth = "STAGE5A_R2_THENAR_INTERIOR_MEDIAL"
        elif D == "THUMB" and s == "MCP":
            head = SEL["THUMB_MCP_R.head"]
            auth = "STAGE5A_R2_THUMB_TUBE_INTERIOR_MEDIAL"
        elif D == "INDEX" and s == "MCP":
            head = SEL["INDEX_MCP_R.head"]
            auth = "STAGE5A_R2_INDEX_SECTION_INTERIOR_CENTRE"
        else:
            head = H(n)
            auth = "Stage4B_R2 candidate joint frame + Stage5A R1 validation (FROZEN)"
        if s == segs[-1]:
            tail = tip_landmark
        else:
            nxt = "%s_%s_R" % (D, segs[i + 1])
            tail = SEL["THUMB_MCP_R.head"] if (D == "THUMB" and segs[i + 1] == "MCP") else H(nxt)
        BONES[n] = dict(head=head, tail=tail, parent=prev, connect=(prev != "WRIST_R"),
                        deform=True, dorsal=d, authority=auth)
        prev = n
    n = "%s_TIP_R" % D
    BONES[n] = dict(head=tip_landmark, tail=tip_landmark + distal_dir * TIP_FRACTION * distal_len,
                    parent=prev, connect=True, deform=False, dorsal=d,
                    authority="Stage5A R2 fingertip landmark + TIP_FRACTION %.2f" % TIP_FRACTION)

ORDER = ["WRIST_R"]
for D in ("THUMB", "INDEX", "MIDDLE", "RING", "LITTLE"):
    ORDER += ["%s_%s_R" % (D, s) for s in CHAIN[D]] + ["%s_TIP_R" % D]
assert len(ORDER) == 21 and set(ORDER) == set(BONES)

arm_data = bpy.data.armatures.new("RIGHT_HAND_PRODUCTION_RIG_DATA")
rig = bpy.data.objects.new("RIGHT_HAND_PRODUCTION_RIG", arm_data)
bpy.context.scene.collection.objects.link(rig)
rig.location = ASSET_ORIGIN                       # object frame = the ASSET object origin (frozen)
rig.rotation_euler = (0.0, 0.0, 0.0)
rig.scale = (1.0, 1.0, 1.0)
arm_data.display_type = 'OCTAHEDRAL'
arm_data.show_names = True
rig.show_in_front = True

bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
ROLL = {}
MIS = {}
for n in ORDER:
    b = BONES[n]
    e = eb.new(n)
    # Armature bones live in ARMATURE (object) space.  The rig object is placed at the
    # ASSET object origin so that it shares the hand mesh's object frame, therefore the
    # authored bone coordinates must be world - ASSET_ORIGIN.
    e.head = b["head"] - ASSET_ORIGIN
    e.tail = b["tail"] - ASSET_ORIGIN
    e.use_deform = b["deform"]
    dv = DORSAL[b["dorsal"]]
    ydir = (b["tail"] - b["head"]).normalized()
    MIS[n] = round(abs(dv.dot(ydir)), 6)
    e.align_roll(dv)
    ROLL[n] = float(e.roll)
for n in ORDER:
    if BONES[n]["parent"]:
        eb[n].parent = eb[BONES[n]["parent"]]
        eb[n].use_connect = bool(BONES[n]["connect"])
bpy.ops.object.mode_set(mode='OBJECT')

prefs = bpy.context.preferences
prefs.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, copy=True, compress=False)
out_sha = hashlib.sha256(open(OUT_BLEND, "rb").read()).hexdigest()
log("SAVED %s" % OUT_BLEND)
log("SAVED sha256 = %s" % out_sha)

build = {"stage": "STAGE5A_R2_PRODUCTION_JOINT_LANDMARK_REQUALIFICATION", "generated_at": NOW,
         "runtime": {"blender": bpy.app.version_string, "executable": bpy.app.binary_path},
         "input_master": MASTER, "input_master_sha256": master_sha,
         "candidates_file": CAND,
         "output_blend": OUT_BLEND, "output_sha256": out_sha,
         "rig_object": {"name": rig.name, "location": [float(x) for x in rig.location],
                        "rotation_euler": [float(x) for x in rig.rotation_euler],
                        "scale": [float(x) for x in rig.scale]},
         "TIP_FRACTION": TIP_FRACTION,
         "dorsal_refs": {k: [round(float(x), 9) for x in DORSAL[k]] for k in DORSAL},
         "bones": {n: {"head": [round(float(x), 9) for x in BONES[n]["head"]],
                       "tail": [round(float(x), 9) for x in BONES[n]["tail"]],
                       "parent": BONES[n]["parent"],
                       "use_connect": bool(BONES[n]["connect"]),
                       "use_deform": bool(BONES[n]["deform"]),
                       "length_mm": round((BONES[n]["tail"] - BONES[n]["head"]).length * MM, 6),
                       "roll_rad": ROLL[n], "roll_deg": round(math.degrees(ROLL[n]), 6),
                       "dorsal_ref_dot_boneY": MIS[n],
                       "authority": BONES[n]["authority"]} for n in ORDER},
         "log": LOG}
json.dump(build, open(os.path.join(S5AR2, "_tmp", "S5A_R2_BUILD_LOG.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
for n in ("WRIST_R", "THUMB_CMC_R", "THUMB_MCP_R", "THUMB_IP_R", "THUMB_TIP_R", "INDEX_MCP_R"):
    b = BONES[n]
    log("%-15s L=%8.4f mm  head=%s" % (n, (b["tail"] - b["head"]).length * MM,
                                       [round(float(x), 6) for x in b["head"]]))
print("BUILD_LOG_WRITTEN")
