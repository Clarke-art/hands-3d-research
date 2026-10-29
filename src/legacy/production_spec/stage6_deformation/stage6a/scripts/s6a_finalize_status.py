# STAGE6A -- finalize the status file (render inventory + artifact list). Documentation only.
import json
import os
import hashlib

OUTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REND = os.path.join(OUTDIR, "renders")
HARNESS = os.path.join(OUTDIR, "RIGHT_HAND_STAGE6A_DEFORMATION_HARNESS_R1.blend")
MASTER = os.path.abspath(os.path.join(OUTDIR, "..", "..", "stage5_production_rig", "stage5b_r1a",
                                      "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1A.blend"))
MASTER_SHA = "c68e415aff80b56911cfe5646e47dff9100d7b54b8bf7aa8ba068bb3948c0ea6"
HARNESS_SHA = "8f223c979362a8c3414b58e2467c7cda2da60f993245cc95b2a38d76c718d3ef"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


st = json.load(open(os.path.join(OUTDIR, "STAGE6A_STATUS.json"), encoding="utf-8"))
files = sorted(f for f in os.listdir(REND) if f.endswith(".png"))
st["renders"] = {
    "dir": "stage6_deformation/stage6a/renders", "count": len(files), "files": files,
    "total_bytes": sum(os.path.getsize(os.path.join(REND, f)) for f in files),
    "max_angle_evidence": 14, "extra": ["FOUR_FINGER_OVERVIEW", "THUMB_MCP_CLOSEUP",
                                        "THUMB_IP_CLOSEUP", "BIND_RESTORE_PROOF"],
    "before_after_rule": "representative images render BOTH states inside ONE frame "
                         "(left = frozen bind copy, right = posed mesh) with identical camera, "
                         "lighting, material and scale"}
st["out_of_scope_this_round"] = [
    "THUMB_CMC opposition", "combined thumb opposition", "piano key press",
    "multi-joint playing action", "animation production", "MediaPipe retarget",
    "left hand", "GLB", "Three.js", "weight correction", "bone correction", "retopo",
    "topology change"]
st["hash_verification_after"] = {
    "stage5b_master": {"sha256": sha(MASTER), "expected": MASTER_SHA,
                       "unchanged": sha(MASTER) == MASTER_SHA},
    "stage6a_harness": {"sha256": sha(HARNESS), "expected": HARNESS_SHA,
                        "unchanged": sha(HARNESS) == HARNESS_SHA}}
st["human_review_authority"] = [
    "subtle pinching", "teaching readability", "organic finger contour", "nail shape quality",
    "crease quality", "volume preservation", "anatomical plausibility"]
st["note"] = ("machine gates are necessary but NOT sufficient; DEFORMATION_FINAL is NOT declared "
              "PASS by this stage.  No weight / bone / topology correction was performed.")
json.dump(st, open(os.path.join(OUTDIR, "STAGE6A_STATUS.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print("renders:", len(files), st["renders"]["total_bytes"])
print("hashes:", st["hash_verification_after"])
print("stage6a:", st["stage6a"], "|", st["isolated_flex_deformation"], "|", st["stage6b"])
print("all_gates_pass:", st["all_gates_pass"])
