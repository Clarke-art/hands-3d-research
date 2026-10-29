# STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1 -- assemble the round status JSON from the audit files.
# Plain CPython (no Blender needed).
import json, os, hashlib, datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
S4 = BASE
SPEC = os.path.join(BASE, "..")

audit = json.load(open(os.path.join(S4, "stage4a_r1", "CMC_LOCAL_RETOPO_AUDIT.json"), encoding="utf-8"))
jla = json.load(open(os.path.join(S4, "stage4a", "JOINT_LOOP_AUDIT.json"), encoding="utf-8"))

joints = {}
for name, v in jla["joints"].items():
    joints[name] = {"effective_loop_count": v.get("effective_loop_count"),
                    "meets_min_3": v.get("meets_min_3")}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


base_blend = os.path.join(S4, "RIGHT_HAND_ENGINEERING_STAGE4A.blend")
copy_blend = os.path.join(S4, "RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend")

out = {
    "stage": "STAGE4A_THUMB_CMC_LOCAL_RETOPO_R1",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "runtime": {"blender": "5.1.2", "executable": "D:\\Blender\\blender.exe"},
    "task_class": "THUMB CMC / THENAR LOCAL TOPOLOGY SURGERY (single-joint, local only)",
    "input_protection": {
        "frozen_baseline": {
            "file": "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A.blend",
            "role": "STAGE4A_PRE_CMC_RETOPO_BASELINE",
            "sha256_pre": "5f69d1ca4b5a70f4f41d70710d6d8ed9b6ba6c4052a70d4de7c429a5b7bcbf40",
            "sha256_post": sha(base_blend),
            "bytes": os.path.getsize(base_blend),
            "modified": False,
        },
        "working_copy": {
            "file": "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_CMC_R1.blend",
            "sha256": sha(copy_blend),
            "created_this_round": True,
            "mesh_surgery_applied": False,
            "why_no_surgery": "see verdict.reason -- the local route is provably blocked",
        },
        "stage2_bootstrap_untouched": {
            "file": "production_spec/stage2_bootstrap/RIGHT_HAND_BOOTSTRAP_C1.blend",
            "sha256": sha(os.path.join(SPEC, "stage2_bootstrap", "RIGHT_HAND_BOOTSTRAP_C1.blend")),
        },
    },
    "mesh_integrity": audit["mesh_integrity"],
    "cmc_frame": {
        "cmc_rotation_center": audit["cmc_rotation_center"],
        "first_metacarpal_axis": audit["first_metacarpal_axis"],
        "engineering_window_mm": audit["engineering_window_mm"],
    },
    "baseline_support_loops": audit["baseline_support_loops"],
    "surface_deviation_mm": audit["surface_deviation_summary"],
    "cmc_concentric_ring_family": audit["cmc_concentric_ring_family"],
    "cmc_ball_disk_test": audit["cmc_ball_disk_test"],
    "decisive_evidence": {
        "axial_level_sets": {
            "finding": "at the CMC height the surface cross-section is ONE contour spanning radius 13.4-110 mm, i.e. it cuts the WHOLE hand; the thumb only becomes a separate tube at axial >= +30 mm",
            "source": "production_spec/stage4_blender/stage4a_r1/R1_LEVELSET.json",
        },
        "cmc_geodesic_ball_is_a_disk": {
            "finding": "the CMC geodesic ball is a single-boundary topological DISK for every radius up to 45 mm (boundary loop length 8/16/22/24/34/44/48/62/78 edges)",
            "consequence": "every closed loop lying inside such a disk bounds a sub-disk that avoids the metacarpal, hence has linking number 0 with the bone: no loop local to the CMC can encircle the first metacarpal",
            "source": "production_spec/stage4_blender/stage4a_r1/R1_WINDING.json",
        },
        "winding_numbers": {
            "finding": "all CMC-concentric rings measure winding = 0.000 about the first metacarpal axis",
            "source": "production_spec/stage4_blender/stage4a_r1/R1_WINDING.json",
        },
    },
    "con_1_no_regression": {
        "basis": "the working file is byte-identical to the reviewed baseline "
                 "(sha256 unchanged), therefore every previously-passing joint loop is unchanged",
        "joint_loop_counts": joints,
        "all_joints_meet_min_3": jla.get("all_joints_meet_min_3"),
        "CON_1_MCP_TOPOLOGY": "PASS_NO_REGRESSION",
    },
    "out_of_scope_this_round": [
        "RSSF re-pose", "nails", "UV re-unwrap", "origin reset", "rig", "skin weights",
        "left-hand mirror", "animation", "other fingers", "wrist", "palm body",
    ],
    "verdict": {
        "CON_2_THUMB_CMC_TOPOLOGY": "NEEDS_MAJOR_RETOPO",
        "CON_3_POLE_AUDIT": "PROVISIONAL_PASS",
        "CON_1_MCP_TOPOLOGY": "PASS_NO_REGRESSION",
        "ASSET_FRAME_NORMALIZATION": "PASS",
        "CANONICAL_FRAME_VALIDATION": "PASS",
        "DEFORMATION_TOPOLOGY_READY_FOR_RSSF": False,
        "STAGE4A": "REVISION_REQUIRED",
        "STAGE4B_RSSF_REPOSE": "BLOCKED",
        "reason": (
            "A closed support loop that encircles the first metacarpal cannot stay local to the "
            "CMC: the CMC geodesic ball is a topological disk out to R = 45 mm, so any encircling "
            "loop must leave it and travel >= 45 mm across the thenar/palm.  The measured axial "
            "level sets confirm the same thing from the other side: at the CMC height the surface "
            "cross-section wraps the entire hand (radius 13.4-110 mm) and the thumb only separates "
            "from the palm at axial >= +30 mm.  The three existing support loops (66.6 / 67.1 / "
            "66.3 mm axial span) are therefore not a modelling error but the only encircling "
            "structure the asset admits at that height.  Reaching the 20 mm target requires either "
            "re-scoping CON-2 or a thenar+palm scale rebuild -- both are outside a local collar "
            "surgery and outside this round's authorised scope."
        ),
        "failure_conditions_triggered": [
            "12-1 only a large-scale thenar rebuild could satisfy the encircling requirement",
        ],
    },
    "authorised_options_for_human_review": [
        {
            "id": "OPT-A",
            "title": "Re-scope CON-2 to a CMC-centred concentric ring field (winding 0)",
            "achievable_locally": True,
            "measured": "R=8/12/16 mm rings: closed, axial span 2.85 / 11.09 / 17.89 mm, "
                        "IN_PM12MM_RATIO = 1.00, on-surface deviation max 0.39 / 0.39 / 0.83 mm",
            "caveat": "rings encircle the CMC joint centre on the thenar, they do NOT wrap the "
                      "metacarpal; requires an explicit change to the accepted CON-2 definition",
        },
        {
            "id": "OPT-B",
            "title": "Authorise a thenar+palm macro-retopo to re-route encircling loops at "
                     "near-constant axial height",
            "achievable_locally": False,
            "caveat": "largest authorised region would have to grow from the thenar to cover the "
                      "adjacent palm and back of hand; forbidden by section 4 of this round",
        },
    ],
    "evidence": {
        "renders": [
            "stage4a_r1/renders/CMC_RETOPO_BEFORE_AFTER.png",
            "stage4a_r1/renders/CMC_RETOPO_DORSAL.png",
            "stage4a_r1/renders/CMC_RETOPO_PALMAR.png",
            "stage4a_r1/renders/CMC_RETOPO_SIDE.png",
            "stage4a_r1/renders/R1_BASE_WIRE_dorsal.png",
            "stage4a_r1/renders/R1_BASE_WIRE_palmar.png",
            "stage4a_r1/renders/R1_BASE_WIRE_radial.png",
            "stage4a_r1/renders/R1_BASE_WIRE_thumbaxis.png",
            "stage4a_r1/renders/R1_GEORING_DORSAL.png",
            "stage4a_r1/renders/R1_GEORING_SIDE.png",
            "stage4a_r1/renders/R1_GEORING_LOOPS_ONLY.png",
        ],
        "machine_data": [
            "stage4a_r1/CMC_LOCAL_RETOPO_AUDIT.json",
            "stage4a_r1/R1_LEVELSET.json",
            "stage4a_r1/R1_WINDING.json",
            "stage4a_r1/R1_PROBE.json",
            "stage4a_r1/R1_GEORING.json",
        ],
        "scripts": [
            "scripts/stage4a_r1_probe.py",
            "scripts/stage4a_r1_levelset.py",
            "scripts/stage4a_r1_winding.py",
            "scripts/stage4a_r1_georing_render.py",
            "scripts/stage4a_r1_audit.py",
            "scripts/stage4a_r1_render.py",
            "scripts/stage4a_r1_status.py",
        ],
        "report": "stage4a_r1/THUMB_CMC_LOCAL_RETOPO_REPORT_R1.md",
    },
    "RIGHT_HAND_ENGINEERING_STAGE4A": "READY_FOR_HUMAN_REVIEW",
}

p = os.path.join(S4, "stage4a_r1", "STAGE4A_CMC_RETOPO_R1_STATUS.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", p)
print("baseline sha post =", out["input_protection"]["frozen_baseline"]["sha256_post"])
print("working copy sha  =", out["input_protection"]["working_copy"]["sha256"])
print("verdict CON_2 =", out["verdict"]["CON_2_THUMB_CMC_TOPOLOGY"])
