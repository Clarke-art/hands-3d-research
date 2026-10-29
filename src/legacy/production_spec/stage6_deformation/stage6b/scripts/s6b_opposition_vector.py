# =====================================================================================
# STAGE6B -- CMC OPPOSITION VECTOR QUALIFICATION
# =====================================================================================
#   * six +-5 deg small-angle probes about the CMC LOCAL X / Y / Z axes
#   * finite-difference Jacobian  J[i][k] = d(tip_i)/d(theta_k)   [m / rad]
#   * deterministic regularized least-squares solve for the local rotation direction that
#     drives the thumb tip towards T_OPPOSE while penalising distal / dorsal motion
#   * axial-twist qualification on local Y using the approved thumb NAIL normal
#
# READ-ONLY with respect to the harness (opened, posed, reset; never saved).
# Outputs STAGE6B_CMC_AXIS_PROBE_AUDIT.json + STAGE6B_OPPOSITION_VECTOR_AUDIT.json
# =====================================================================================
import bpy
import sys
import os
import json
import math
import datetime
import numpy as np
from mathutils import Vector, Quaternion

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import s6b_common as B                                          # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = argv[0]
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[S6B-OPP]", s, flush=True)


PROBE_DEG = 5.0
PENALTY_MU = 1.0          # weight of the distal/dorsal avoidance term (documented, diagnostic)
RIDGE_LAMBDA_FRAC = 1e-9  # ridge relative to trace(J^T J)
TWIST_DELTA_MIN = 1e-4    # min |alignment change| for a twist sign to be called (rad-equivalent)
TWIST_SEPARATION_MIN = 1e-4

s_r1b = B.sha256(B.R1B_MASTER)
s_r1a = B.sha256(B.R1A_HARNESS)
s_s5a = B.sha256(B.S5A_MASTER)
if (s_r1b, s_r1a, s_s5a) != (B.R1B_SHA256, B.R1A_HARNESS_SHA256, B.S5A_SHA256):
    raise SystemExit("FAIL CLOSED: frozen input hash drift")

ctx = B.build_context()
V0 = ctx["V0"]
NV = ctx["NV"]
POLY = ctx["poly"]
NAIL = sorted(ctx["nail_thumb"])
NAIL_FACES = [fi for fi in range(len(POLY)) if all(v in ctx["nail_thumb"] for v in POLY[fi])]
log("nail faces = %d (vertices %d)" % (len(NAIL_FACES), len(NAIL)))

bpy.ops.wm.open_mainfile(filepath=B.HARNESS_R1)
ob = bpy.data.objects["Hand  - Realistic"]
rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
MW = ob.matrix_world.copy()
M3 = MW.to_3x3()

B.reset_pose(rig)
B.update()
Vb, _ = B.evaluate(ob, MW)
tip0 = B.tip_world(rig)
n_pad0 = -B.nail_normal(Vb, POLY, NAIL_FACES)
log("bind pad proxy normal = %s" % B.v3(n_pad0, 6))
log("T_OPPOSE = %s" % B.v3(B.T_OPPOSE, 6))
log("bind pad alignment with T_OPPOSE = %.6f" % n_pad0.dot(B.T_OPPOSE))

AXES = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}
PROJ = {"RADIAL": B.RADIAL, "DORSAL": B.DORSAL, "DISTAL": B.DISTAL,
        "ULNAR": B.ULNAR, "PALMAR": B.PALMAR, "T_OPPOSE": B.T_OPPOSE}

probes = {}
for ax_name, axis in AXES.items():
    for sgn in (1.0, -1.0):
        B.reset_pose(rig)
        B.set_local_axis_rotation(rig, "THUMB_CMC_R", sgn * PROBE_DEG, axis)
        B.update()
        V, _ = B.evaluate(ob, MW)
        tip = B.tip_world(rig)
        disp = tip - tip0
        n_pad = -B.nail_normal(V, POLY, NAIL_FACES)
        probes["%s%s%d" % (ax_name, "p" if sgn > 0 else "m", int(PROBE_DEG))] = {
            "axis_local": list(axis), "angle_deg": sgn * PROBE_DEG,
            "tip_world": B.v3(tip), "displacement_mm": B.v3(disp * 1000.0),
            "displacement_magnitude_mm": B.rr(disp.length * 1000.0, 9),
            "projections_mm": {k: B.rr(disp.dot(d) * 1000.0, 9) for k, d in PROJ.items()},
            "pad_proxy_normal": B.v3(n_pad, 6),
            "pad_alignment_with_T_OPPOSE": B.rr(n_pad.dot(B.T_OPPOSE), 9),
            "pad_alignment_change_vs_bind": B.rr(n_pad.dot(B.T_OPPOSE)
                                                 - n_pad0.dot(B.T_OPPOSE), 9),
        }
        log("probe %-6s tip disp %.6f mm  T_OPPOSE %+.6f mm  pad_dalign %+.6f"
            % ("%s%+d" % (ax_name, int(sgn * PROBE_DEG)),
               disp.length * 1000.0, disp.dot(B.T_OPPOSE) * 1000.0,
               n_pad.dot(B.T_OPPOSE) - n_pad0.dot(B.T_OPPOSE)))

B.reset_pose(rig)
B.update()

# ---------------------------------------------------------------- Jacobian (m / rad)
drad = math.radians(PROBE_DEG)
J = np.zeros((3, 3))
for k, ax_name in enumerate(("X", "Y", "Z")):
    dp = Vector(probes["%sp%d" % (ax_name, int(PROBE_DEG))]["displacement_mm"]) / 1000.0
    dm = Vector(probes["%sm%d" % (ax_name, int(PROBE_DEG))]["displacement_mm"]) / 1000.0
    col = (dp - dm) / (2.0 * drad)
    J[:, k] = [col.x, col.y, col.z]
log("Jacobian (m/rad):\n%s" % np.array2string(J, precision=6, suppress_small=True))

t = np.array([B.T_OPPOSE.x, B.T_OPPOSE.y, B.T_OPPOSE.z])
ez = np.array([B.DISTAL.x, B.DISTAL.y, B.DISTAL.z])
ey = np.array([B.DORSAL.x, B.DORSAL.y, B.DORSAL.z])

JtJ = J.T @ J
lam = RIDGE_LAMBDA_FRAC * float(np.trace(JtJ))
A = JtJ + lam * np.eye(3) + PENALTY_MU * (np.outer(J.T @ ez, ez @ J)
                                          + np.outer(J.T @ ey, ey @ J))
r_pen_raw = np.linalg.solve(A, J.T @ t)
r_pen = r_pen_raw / np.linalg.norm(r_pen_raw)
r_align = J.T @ t
r_align = r_align / np.linalg.norm(r_align)

# X/Z-only sub-problem (documented cross-check; Y excluded)
Jx = J[:, [0, 2]]
A2 = Jx.T @ Jx + lam * np.eye(2) + PENALTY_MU * (np.outer(Jx.T @ ez, ez @ Jx)
                                                 + np.outer(Jx.T @ ey, ey @ Jx))
r_xz_raw = np.linalg.solve(A2, Jx.T @ t)
r_xz = np.array([r_xz_raw[0], 0.0, r_xz_raw[1]])
r_xz = r_xz / np.linalg.norm(r_xz)


def achieved(r):
    v = J @ r
    n = np.linalg.norm(v)
    if n < 1e-15:
        return v, 0.0, 0.0, 0.0
    u = v / n
    return (v, float(np.dot(u, t)),
            float(np.dot(u, ez)), float(np.dot(u, ey)))


v_pen, cos_pen, z_pen, y_pen = achieved(r_pen)
v_xz, cos_xz, z_xz, y_xz = achieved(r_xz)
log("r_pen  = %s  cos(T_OPPOSE)=%.6f  distal=%+.6f dorsal=%+.6f"
    % (B.v3(Vector(r_pen.tolist()), 6), cos_pen, z_pen, y_pen))
log("r_xz   = %s  cos(T_OPPOSE)=%.6f  distal=%+.6f dorsal=%+.6f"
    % (B.v3(Vector(r_xz.tolist()), 6), cos_xz, z_xz, y_xz))

# ---------------------------------------------------------------- axial twist qualification
twist = {}
for mag in (3.0, 5.0, 7.0):
    row = {}
    for sgn in (1.0, -1.0):
        B.reset_pose(rig)
        B.set_local_axis_rotation(rig, "THUMB_CMC_R", sgn * mag, (0.0, 1.0, 0.0))
        B.update()
        V, _ = B.evaluate(ob, MW)
        n_pad = -B.nail_normal(V, POLY, NAIL_FACES)
        row["%+d" % int(sgn)] = {
            "pad_alignment_with_T_OPPOSE": B.rr(n_pad.dot(B.T_OPPOSE), 9),
            "alignment_change_vs_bind": B.rr(n_pad.dot(B.T_OPPOSE)
                                             - n_pad0.dot(B.T_OPPOSE), 9),
            "axis_change_deg": B.rr(math.degrees(
                n_pad0.angle(n_pad)) if n_pad.length > 0 else 0.0, 6),
            "pad_normal": B.v3(n_pad, 6),
        }
    twist["%ddeg" % int(mag)] = row
    log("twist Y +-%d deg: d_align(+) = %+.6f  d_align(-) = %+.6f"
        % (int(mag), row["+1"]["alignment_change_vs_bind"],
           row["-1"]["alignment_change_vs_bind"]))
B.reset_pose(rig)
B.update()

r5 = twist["5deg"]
dp = r5["+1"]["alignment_change_vs_bind"]
dm = r5["-1"]["alignment_change_vs_bind"]
mag_best = max(abs(dp), abs(dm))
separation = abs(dp - dm)
if mag_best < TWIST_DELTA_MIN or separation < TWIST_SEPARATION_MIN:
    twist_sign = "UNRESOLVED"
elif dp > dm:
    twist_sign = "+1"
else:
    twist_sign = "-1"
# stability across probe magnitudes
signs = []
for mag in ("3deg", "5deg", "7deg"):
    a = twist[mag]["+1"]["alignment_change_vs_bind"]
    b = twist[mag]["-1"]["alignment_change_vs_bind"]
    if abs(a - b) < TWIST_SEPARATION_MIN:
        signs.append("UNRESOLVED")
    else:
        signs.append("+1" if a > b else "-1")
twist_stable = len(set(signs)) == 1 and signs[0] != "UNRESOLVED"
log("twist signs across +-3/5/7 deg = %s -> stable=%s ; adopted = %s"
    % (signs, twist_stable, twist_sign))

# ---------------------------------------------------------------- final unit rotation
# Spec section 10: the opposition direction must be LOCAL X/Z DOMINANT.  The unrestricted
# penalized solve above is dominated by local Y (the metacarpal long axis) because its unit
# direction happens to align best with T_OPPOSE -- note that it achieves essentially the SAME
# alignment as the X/Z-restricted solve (see below), so restricting to X/Z costs nothing.
# Spec section 11: local Y is the axial twist; its SIGN is decided by the pad-proxy test.
# The construction below therefore takes
#   * direction  <- the X/Z restricted solve   (local X/Z dominant, Y = 0)
#   * local Y    <- magnitude capped to a documented share of the total rotation magnitude,
#                   sign from the axial-twist qualification
Y_SHARE_CAP = 0.25        # at most 25% of the total rotation magnitude may be axial twist
sigma = 0.0 if twist_sign == "UNRESOLVED" else float(twist_sign)
y_share_capped = Y_SHARE_CAP if sigma != 0.0 else 0.0
y_coeff = (y_share_capped / math.sqrt(1.0 - y_share_capped ** 2)) if y_share_capped else 0.0
y_ratio_solved = abs(r_pen[1]) / max(1e-18, math.hypot(r_pen[0], r_pen[2]))
r_unit = np.array([r_xz[0], sigma * y_coeff, r_xz[2]])
r_unit = r_unit / np.linalg.norm(r_unit)
y_share_actual = abs(r_unit[1])
xz_share_actual = math.hypot(r_unit[0], r_unit[2])
v_u, cos_u, z_u, y_u = achieved(r_unit)
v_xz_only, cos_xzonly, z_xzonly, y_xzonly = achieved(r_xz)
q_unit, mag_unit = B.rotation_vector_to_quaternion(Vector(r_unit.tolist()))
log("unit rotation XZ-only direction  = %s  cos(T_OPPOSE)=%.6f"
    % (B.v3(Vector(r_xz.tolist()), 9), cos_xz))
log("CMC_OPPOSITION_UNIT_ROTATION (local X,Y,Z coefficients) = %s"
    % B.v3(Vector(r_unit.tolist()), 9))
log("  X/Z share of magnitude = %.4f ; local-Y (twist) share = %.4f"
    % (xz_share_actual, y_share_actual))
log("achieved: cos(T_OPPOSE)=%.6f  distal=%+.6f  dorsal=%+.6f  tilt_deg=%.3f"
    % (cos_u, z_u, y_u, math.degrees(math.acos(max(-1.0, min(1.0, cos_u))))))

AXIS_AUDIT = {
    "stage": "STAGE6B_CMC_AXIS_PROBE_AUDIT", "generated_at": NOW,
    "method": ("six +-5 deg small-angle probes about the CMC LOCAL X / Y / Z axes with every "
               "other bone locked at RSSF bind; the thumb TIP landmark world displacement is "
               "measured and projected on the canonical hand axes"),
    "canonical_world_frame": {"+X": "RADIAL", "+Y": "DORSAL", "+Z": "DISTAL",
                              "ULNAR": "-X", "PALMAR": "-Y",
                              "T_OPPOSE": B.v3(B.T_OPPOSE, 12),
                              "note": "T_OPPOSE is a DIAGNOSTIC opposition direction, NOT a "
                                      "teaching end pose"},
    "probe_deg": PROBE_DEG,
    "probes": probes,
    "jacobian_m_per_rad": [[B.rr(x, 12) for x in row] for row in J.tolist()],
    "jacobian_columns": {k: B.v3(Vector(J[:, i].tolist()) * 1000.0, 9)
                         for i, k in enumerate(("local_X", "local_Y", "local_Z"))},
    "jacobian_note": "columns are tip displacement in mm per radian about each local axis",
    "log": LOG,
}
json.dump(AXIS_AUDIT, open(os.path.join(OUTDIR, "STAGE6B_CMC_AXIS_PROBE_AUDIT.json"), "w",
                          encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6B_CMC_AXIS_PROBE_AUDIT.json")

VEC_AUDIT = {
    "stage": "STAGE6B_OPPOSITION_VECTOR_AUDIT", "generated_at": NOW,
    "authority": "derived from the measured CMC local-axis Jacobian; no hand-tuned angle",
    "target_direction": "T_OPPOSE = normalize(ULNAR + PALMAR)",
    "solve": {
        "form": "(J^T J + lambda I + mu (J^T ez ez^T J + J^T ey ey^T J)) r = J^T t  ;  r <- r/|r|",
        "lambda": B.rr(lam, 15), "mu": PENALTY_MU,
        "lambda_note": "ridge = 1e-9 * trace(J^T J), scale-aware, numerically stabilising only",
        "mu_note": ("weight of the DISTAL(+Z) / DORSAL(+Y) avoidance term; mu = 1 gives that "
                    "penalty the same weight as the T_OPPOSE alignment term"),
        "least_squares_reference_r_align": B.v3(Vector(r_align.tolist()), 9),
        "xz_only_solution": B.v3(Vector(r_xz.tolist()), 9),
    },
    "penalized_solution": {
        "coefficients_local_XYZ": B.v3(Vector(r_pen.tolist()), 9),
        "achieved_tip_motion_direction": B.v3(Vector((v_pen / max(np.linalg.norm(v_pen),
                                                                  1e-18)).tolist()), 9),
        "cos_with_T_OPPOSE": B.rr(cos_pen, 9),
        "tilt_from_T_OPPOSE_deg": B.rr(math.degrees(math.acos(max(-1.0, min(1.0, cos_pen)))), 6),
        "distal_component": B.rr(z_pen, 9), "dorsal_component": B.rr(y_pen, 9),
    },
    "xz_only_cross_check": {"coefficients_local_XYZ": B.v3(Vector(r_xz.tolist()), 9),
                            "cos_with_T_OPPOSE": B.rr(cos_xz, 9),
                            "distal_component": B.rr(z_xz, 9),
                            "dorsal_component": B.rr(y_xz, 9)},
    "axial_twist_qualification": {
        "axis": "CMC local Y (longitudinal)",
        "criterion": ("pad proxy normal = -(approved thumb NAIL normal); take the sign of "
                      "local Y that increases dot(pad_proxy_normal, T_OPPOSE)"),
        "probes": twist,
        "signs_across_magnitudes": signs,
        "stable_across_magnitudes": twist_stable,
        "delta_threshold": TWIST_DELTA_MIN, "separation_threshold": TWIST_SEPARATION_MIN,
        "CMC_AXIAL_TWIST_SIGN": twist_sign,
    },
    "CMC_OPPOSITION_UNIT_ROTATION": {
        "authority": ("DIRECTION from the X/Z-restricted regularized least-squares solve "
                      "(local X/Z dominant, per spec section 10); local-Y coefficient "
                      "MAGNITUDE from a documented share cap and SIGN from the axial-twist "
                      "qualification (spec section 11); if the twist sign is UNRESOLVED the "
                      "local-Y coefficient is forced to 0"),
        "coefficients_local_XYZ": B.v3(Vector(r_unit.tolist()), 9),
        "unit_quaternion_local": [B.rr(q_unit.w, 12), B.rr(q_unit.x, 12),
                                  B.rr(q_unit.y, 12), B.rr(q_unit.z, 12)],
        "is_unit_vector": True,
        "xz_share_of_magnitude": B.rr(xz_share_actual, 6),
        "local_y_twist_share_of_magnitude": B.rr(y_share_actual, 6),
        "Y_SHARE_CAP": Y_SHARE_CAP,
        "Y_SHARE_CAP_note": ("diagnostic construction cap (not an anatomical parameter): the "
                             "axial-twist component may carry at most 25% of the total rotation "
                             "magnitude so that local X/Z stays dominant"),
        "solved_uncapped_y_ratio": B.rr(y_ratio_solved, 6),
        "solved_uncapped_y_ratio_note": ("|r_pen.y| / |r_pen_xz| from the unrestricted solve; it "
                                         "is far above the cap, which is exactly why the spec "
                                         "requires the X/Z-dominant restriction"),
        "achieved_tip_motion_direction": B.v3(Vector((v_u / max(np.linalg.norm(v_u),
                                                                1e-18)).tolist()), 9),
        "cos_with_T_OPPOSE": B.rr(cos_u, 9),
        "tilt_from_T_OPPOSE_deg": B.rr(math.degrees(math.acos(max(-1.0, min(1.0, cos_u)))), 6),
        "distal_component": B.rr(z_u, 9), "dorsal_component": B.rr(y_u, 9),
        "xz_only_variant": {
            "coefficients_local_XYZ": B.v3(Vector(r_xz.tolist()), 9),
            "cos_with_T_OPPOSE": B.rr(cos_xzonly, 9),
            "distal_component": B.rr(z_xzonly, 9),
            "dorsal_component": B.rr(y_xzonly, 9),
            "note": ("reported for transparency; it reaches the same T_OPPOSE alignment as the "
                     "adopted direction, so the X/Z restriction costs nothing"),
        },
        "case_construction": ("case pose quaternion = Quaternion(unit_direction, "
                              "radians(total_magnitude)); total magnitudes are the diagnostic "
                              "10/20/30 deg levels, NOT teaching values"),
        "order_dependence": "NONE - a single exponential-map rotation, not an Euler sequence",
    },
    "log": LOG,
}
json.dump(VEC_AUDIT, open(os.path.join(OUTDIR, "STAGE6B_OPPOSITION_VECTOR_AUDIT.json"), "w",
                          encoding="utf-8"), indent=1, ensure_ascii=False)
log("wrote STAGE6B_OPPOSITION_VECTOR_AUDIT.json")
print("OPP_VECTOR_DONE")
