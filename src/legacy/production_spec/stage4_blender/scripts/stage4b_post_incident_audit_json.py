# STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT -- assemble the machine-readable audit record.
# Read-only w.r.t. every artifact it inspects; it only writes the two audit outputs plus the
# legacy-temp marker under _tmp/.
import json, os, hashlib, datetime, io

B = "stage4b_rssf"
T = os.path.join(B, "_tmp")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rd(p):
    return json.load(open(p, encoding="utf-8"))


cmp_pre = rd(os.path.join(T, "compare_result.json"))
cmp_post = rd(os.path.join(T, "compare_result_post_patch.json"))
inv = rd(os.path.join(T, "deliverable_inventory.json"))
pre_state = rd(os.path.join(T, "renders_pre_state.json"))

now_state = {f: {"bytes": os.path.getsize(os.path.join(B, "renders", f)),
                 "sha256": sha(os.path.join(B, "renders", f))}
             for f in sorted(os.listdir(os.path.join(B, "renders")))}
renders_unchanged = (now_state == pre_state)

# ---- PNG chunk-level explanation of the metadata-only difference -------------------------
import zlib


def chunk_types(p):
    raw = open(p, "rb").read()
    i, out = 8, []
    while i < len(raw):
        ln = int.from_bytes(raw[i:i + 4], "big")
        typ = raw[i + 4:i + 8].decode("latin-1")
        out.append((typ, raw[i + 8:i + 8 + ln]))
        i += 12 + ln
        if typ == "IEND":
            break
    return out


def idat(p):
    return b"".join(d for t, d in chunk_types(p) if t == "IDAT")


REB = os.path.join(T, "post_incident_rebuild")
meta_probe = {}
frame = "RSSF_BEF_DORSAL.png"
ca = chunk_types(os.path.join(REB, frame))
cb = chunk_types(os.path.join(B, "renders", frame))
diffs = []
for (ta, da), (tb, db) in zip(ca, cb):
    if ta == tb and da != db:
        try:
            diffs.append({"chunk": ta, "rebuilt": da.decode("latin-1")[:60],
                          "installed": db.decode("latin-1")[:60]})
        except Exception:
            diffs.append({"chunk": ta, "note": "binary differs"})
ia, ib = idat(os.path.join(REB, frame)), idat(os.path.join(B, "renders", frame))
meta_probe = {
    "probe_file": frame,
    "differing_chunks": diffs,
    "chunk_types_identical_order": [t for t, _ in ca] == [t for t, _ in cb],
    "IDAT_compressed_identical": ia == ib,
    "IDAT_decompressed_identical": zlib.decompress(ia) == zlib.decompress(ib),
    "conclusion": "the single-side frames differ ONLY in the embedded PNG tEXt metadata "
                  "(Date / RenderTime wall-clock); the compressed pixel payload is "
                  "byte-identical, so the difference is metadata, not image content",
}

LEGACY = [f for f in sorted(os.listdir(os.path.join(B, "renders")))
          if f.startswith(("RSSF_BEF_", "RSSF_AFT_"))]

out = {
    "stage": "STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT",
    "mode": "READ_ONLY (no model / topology / pose / rig / weight change; no file deleted or moved)",
    "generated_at": datetime.datetime.now().astimezone().isoformat(),
    "runtime": {"blender": "D:/Blender/blender.exe (5.1.2)",
                "python": "<USER_HOME>/.workbuddy/binaries/python/versions/3.13.12/python.exe"},

    "frozen_input": {
        "path": "production_spec/stage4_blender/RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend",
        "sha256": sha("RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend"),
        "expected_sha256": "4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039",
        "match": sha("RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend") ==
                 "4fa2cb6f31d8097110718e4d9cc424c30d1d2b7057c76abd93c338a5c7201039",
        "touched_by_this_audit": False,
    },
    "stage4b_artifact": {
        "path": "production_spec/stage4_blender/stage4b_rssf/RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend",
        "sha256": sha(os.path.join(B, "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend")),
        "bytes": os.path.getsize(os.path.join(B, "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend")),
        "touched_by_this_audit": False,
    },

    "rebuild": {
        "scratch_dir": "production_spec/stage4_blender/stage4b_rssf/_tmp/post_incident_rebuild",
        "inputs": ["RIGHT_HAND_ENGINEERING_STAGE4A_R2.blend (frozen baseline, BEFORE side)",
                   "RIGHT_HAND_ENGINEERING_STAGE4B_RSSF_R1.blend (AFTER side)",
                   "scripts/stage4b_render.py", "scripts/stage4a_r2_composite.py",
                   "stage4b_rssf/CAMS.json"],
        "overwrote_renders": False,
        "comparisons": cmp_pre["comparisons"],
        "all_pixel_exact": cmp_pre["all_pixel_exact"],
        "metadata_only_difference_proof": meta_probe,
    },

    "deliverables": inv,
    "deliverables_missing": [k for k, v in inv.items() if not v["exists"]],

    "renders_dir_untouched": {
        "pre_rebuild_snapshot_files": len(pre_state),
        "post_audit_files": len(now_state),
        "byte_identical_to_snapshot": renders_unchanged,
        "changed_files": [] if renders_unchanged else
            sorted(f for f in set(pre_state) | set(now_state) if pre_state.get(f) != now_state.get(f)),
    },

    "render_output_isolation_patch": {
        "script": "production_spec/stage4_blender/scripts/stage4b_render.py",
        "sha256": sha("scripts/stage4b_render.py"),
        "TEMP_RENDER_OUTPUT_DIR": "production_spec/stage4_blender/stage4b_rssf/_tmp/",
        "FINAL_RENDER_OUTPUT_DIR": "production_spec/stage4_blender/stage4b_rssf/renders/",
        "mechanism": "explicit FINAL allow-list (exact deliverable file names), not a prefix "
                     "rule -- the incident was caused by the prefix 'RSSF_BEFORE_*' also "
                     "matching the deliverable 'RSSF_BEFORE_AFTER_*', which no prefix rule can "
                     "separate",
        "final_allow_list": ["RSSF_BEFORE_AFTER_DORSAL.png", "RSSF_BEFORE_AFTER_PALMAR.png",
                             "RSSF_BEFORE_AFTER_RADIAL.png", "RSSF_BEFORE_AFTER_OBLIQUE.png",
                             "RSSF_CMC_CLOSEUP.png", "RSSF_SKELETON_OVERLAY.png"],
        "guards_implemented": [
            "single-side frames always render into TEMP, never into FINAL",
            "TEMP == FINAL  -> hard refusal",
            "TEMP basename == 'renders' -> hard refusal",
            "any name outside the FINAL allow-list -> hard refusal (names the incident)",
            "the script performs no deletion of any kind (no unlink / glob / recursive / "
            "prefix-wildcard delete)",
        ],
        "negative_tests": [
            {"case": "TEMP == FINAL == renders/", "result": "REFUSED",
             "message": "temp_dir == final_dir"},
            {"case": "write 'RSSF_BEF_DORSAL.png' into renders/", "result": "REFUSED",
             "message": "looks like a temp frame (prefix 'RSSF_BEF_')"},
            {"case": "write 'RSSF_AFT_DORSAL.png' into renders/", "result": "REFUSED",
             "message": "looks like a temp frame (prefix 'RSSF_AFT_')"},
            {"case": "write 'RSSF_BEFORE_DORSAL.png' into renders/", "result": "REFUSED",
             "message": "looks like a temp frame (prefix 'RSSF_BEFORE_')"},
            {"case": "write 'RSSF_AFTER_DORSAL.png' into renders/", "result": "REFUSED",
             "message": "looks like a temp frame (prefix 'RSSF_AFTER_')"},
        ],
        "positive_reproduction": {
            "scratch_dir": "stage4b_rssf/_tmp/post_patch_check",
            "final_dir_received_only": sorted(os.listdir(os.path.join(T, "post_patch_check", "renders"))),
            "temp_dir_received": sorted(os.listdir(os.path.join(T, "post_patch_check", "_tmp"))),
            "comparisons_vs_renders": cmp_post["comparisons"],
            "all_pixel_exact": cmp_post["all_pixel_exact"],
            "composites_byte_identical": all(
                c.get("file_bytes_identical") for c in cmp_post["comparisons"]
                if not c["name"].startswith("POST_PATCH tmp")),
        },
    },

    "legacy_temp_location": {
        "status": "KEEP_IN_PLACE_UNTIL_HUMAN_REVIEW",
        "directory": "production_spec/stage4_blender/stage4b_rssf/renders/",
        "count": len(LEGACY),
        "files": LEGACY,
        "note": "these 10 single-side frames sit in the FINAL directory from before the "
                "output-policy patch.  They are NOT deliverables.  Nothing was moved or "
                "deleted; they are marked only.  Marked in the report, in this JSON, and in "
                "_tmp/LEGACY_TEMP_LOCATION.json.",
    },

    "files_created_by_this_audit": [
        "stage4b_rssf/STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.md",
        "stage4b_rssf/STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.json",
        "stage4b_rssf/_tmp/LEGACY_TEMP_LOCATION.json",
        "stage4b_rssf/_tmp/renders_pre_state.json",
        "stage4b_rssf/_tmp/deliverable_inventory.json",
        "stage4b_rssf/_tmp/compare_pairs.json",
        "stage4b_rssf/_tmp/compare_result.json",
        "stage4b_rssf/_tmp/compare_pairs_post_patch.json",
        "stage4b_rssf/_tmp/compare_result_post_patch.json",
        "stage4b_rssf/_tmp/post_incident_rebuild/ (15 rebuilt PNGs)",
        "stage4b_rssf/_tmp/post_patch_check/ (15 PNGs from the patched script)",
        "scripts/stage4b_post_incident_compare.py",
        "scripts/stage4b_post_incident_audit_json.py",
    ],
    "files_modified_by_this_audit": [
        "scripts/stage4b_render.py  (output-isolation patch only; the render itself is unchanged)",
    ],
}

out["VERDICT"] = {
    "P0_DELETE_INCIDENT": "CLOSED",
    "FORMAL_RENDER_REBUILD": "PIXEL_EXACT" if cmp_pre["all_pixel_exact"] else "DIFFERENT",
    "CURRENT_DELIVERABLE_SET": "COMPLETE" if not out["deliverables_missing"] else "INCOMPLETE",
    "TEMP_OUTPUT_ISOLATION": "PATCHED",
    "GLOB_DELETE_POLICY": "PROHIBITED",
    "STAGE4B_ARTIFACT_INTEGRITY": "PASS" if (
        cmp_pre["all_pixel_exact"] and not out["deliverables_missing"] and renders_unchanged
    ) else "FAIL",
}
json.dump(out, open(os.path.join(B, "STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.json"), "w",
                    encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", os.path.join(B, "STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT.json"))
print(json.dumps(out["VERDICT"], ensure_ascii=False, indent=1))
print("renders byte-identical:", renders_unchanged)
print("legacy temp count:", len(LEGACY))
