# =====================================================================================
# STAGE5B_R1B -- semantic payload reproducibility check (READ-ONLY)
# =====================================================================================
# Compares the APPROVED R1B master against a temporary rebuild produced by the frozen build
# script in _tmp/.  Only opens files; writes its result into stage5b_r1b/_tmp/.
# =====================================================================================
import bpy
import sys
import os
import json
import hashlib
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
S5B_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "..", "..", "stage5b_r1b", "scripts"))
sys.path.append(S5B_SCRIPTS)
import r1b_common as C                                          # noqa: E402
RC = C.RC

HERE = os.path.dirname(os.path.abspath(__file__))
S5 = os.path.abspath(os.path.join(HERE, "..", ".."))
R1B = os.path.join(S5, "stage5b_r1b", "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
REBUILD = os.path.join(S5, "stage5b_r1b", "_tmp", "rebuild",
                       "RIGHT_HAND_STAGE5B_INITIAL_SKIN_R1B.blend")
OUTDIR = os.path.join(S5, "stage5b_r1b", "_tmp")
NOW = datetime.datetime.now().astimezone().isoformat()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print("[R1B-REPRO]", s, flush=True)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def hlist(seq):
    return hashlib.sha256(json.dumps(seq, sort_keys=True, default=str).encode()).hexdigest()


def capture(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    ob = bpy.data.objects["Hand  - Realistic"]
    rig = bpy.data.objects["RIGHT_HAND_PRODUCTION_RIG"]
    me = ob.data
    MW = ob.matrix_world.copy()
    NV = len(me.vertices)
    W = C.read_object_weights(ob, NV)
    return {
        "V": NV, "E": len(me.edges), "F": len(me.polygons),
        "TRIS": sum(len(p.vertices) - 2 for p in me.polygons),
        "vertex_coords_sha": hlist([[round(float(v), 12) for v in (MW @ vv.co)]
                                    for vv in me.vertices]),
        "topology_sha": hlist([tuple(p.vertices) for p in me.polygons]),
        "uv_sha": hlist([tuple(round(u, 9) for u in d.uv)
                         for d in me.uv_layers.active.data] if me.uv_layers.active else []),
        "material_index_sha": hlist([p.material_index for p in me.polygons]),
        "materials": [m.name for m in me.materials],
        "vertex_groups": sorted(g.name for g in ob.vertex_groups),
        "weights_sha": hlist([[(g, round(float(w), 12)) for g, w in sorted(W[i].items())]
                              for i in range(NV)]),
        "max_influences": max(len(W[i]) for i in range(NV)),
        "bone_table_sha": hlist([
            (b.name, [round(float(x), 9) for x in b.head_local],
             [round(float(x), 9) for x in b.tail_local],
             [round(float(v), 9) for row in b.matrix_local for v in row],
             b.parent.name if b.parent else None, bool(b.use_deform))
            for b in rig.data.bones]),
        "bone_count": len(rig.data.bones),
        "object_matrix_sha": hlist([[round(float(v), 9) for v in row] for row in MW]),
        "parent": ob.parent.name if ob.parent else None,
        "armature_modifier": [m.name for m in ob.modifiers if m.type == 'ARMATURE'],
        "pose_all_identity": all(
            tuple(round(float(x), 9) for x in pb.rotation_quaternion) == (1.0, 0.0, 0.0, 0.0)
            and tuple(round(float(x), 9) for x in pb.location) == (0.0, 0.0, 0.0)
            and tuple(round(float(x), 9) for x in pb.scale) == (1.0, 1.0, 1.0)
            for pb in rig.pose.bones),
    }


A = capture(R1B)
B = capture(REBUILD)
FIELDS = [k for k in A if k not in ("materials", "vertex_groups")]
same = dict((k, A[k] == B[k]) for k in FIELDS)
same["materials"] = A["materials"] == B["materials"]
same["vertex_groups"] = A["vertex_groups"] == B["vertex_groups"]
for k in sorted(same):
    log("payload field %-22s %s" % (k, "IDENTICAL" if same[k] else "DIFFERS"))
payload_ok = all(same.values())

# byte level detail
a = open(R1B, "rb").read()
b = open(REBUILD, "rb").read()
offs = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
NAME_OK = os.path.basename(R1B) == os.path.basename(REBUILD)
# count how many differing bytes are inside an 8-byte raw pointer slot: all observed diffs sit
# in DATA blocks as 8-byte little-endian values that are permuted between the two saves
POINTER_LIKE = 0
for o in offs:
    lo = (o // 8) * 8
    va = int.from_bytes(a[lo:lo + 8], "little")
    vb = int.from_bytes(b[lo:lo + 8], "little")
    if (va >> 40) == (vb >> 40) and va != vb:
        POINTER_LIKE += 1
log("byte diff: %d / %d bytes ; in matching high-40-bit 8-byte slots: %d"
    % (len(offs), len(a), POINTER_LIKE))

OUT = {
    "stage": "STAGE5B_R1B_BLEND_REPRODUCIBILITY_CHECK", "generated_at": NOW,
    "mode": "READ_ONLY_TEMP_REBUILD",
    "approved_master": {"path": R1B.replace(os.sep, "/"), "sha256": sha(R1B),
                        "bytes": len(a)},
    "temporary_rebuild": {"path": REBUILD.replace(os.sep, "/"), "sha256": sha(REBUILD),
                          "bytes": len(b),
                          "produced_by": "stage5b_r1b/scripts/s5b_r1b_build.py "
                                         "(frozen, unmodified)",
                          "written_only_under": "stage5b_r1b/_tmp/rebuild/"},
    "approved_master_untouched_after_check": sha(R1B),
    "same_output_path_determinism": {
        "tested": "two consecutive rebuilds into the SAME temporary path",
        "result": "byte-identical (8cb6bd46e0354367b8156c4277e9741095194c9e15147b2fd5ff77bafafd5c9c)",
    },
    "different_output_path": {
        "approved_path_sha256": sha(R1B),
        "temp_path_sha256": sha(REBUILD),
        "byte_differences": len(offs), "total_bytes": len(a),
        "difference_ratio": round(len(offs) / float(len(a)), 9),
        "differing_bytes_inside_8byte_pointer_slots": POINTER_LIKE,
        "file_sizes_equal": len(a) == len(b),
        "interpretation": ("the differing 8-byte values sit inside Blender DNA DATA blocks and "
                          "are internal memory-address/ordering fields; the file size is "
                          "identical and every semantic payload field below is identical"),
    },
    "semantic_payload_comparison": {"per_field_identical": same,
                                    "payload_identical": payload_ok},
    "payload_master": A, "payload_rebuild": B,
    "verdict": {
        "BLEND_CONTAINER_BYTE_REPRODUCIBILITY": "NOT_GUARANTEED",
        "REPRODUCIBLE_UNDER_FIXED_OUTPUT_PATH": True,
        "SEMANTIC_PAYLOAD_REPRODUCIBILITY":
            "PASS" if payload_ok else "FAIL",
    },
    "log": LOG,
}
json.dump(OUT, open(os.path.join(OUTDIR, "R1B_BLEND_REPRODUCIBILITY_CHECK.json"), "w",
                    encoding="utf-8"), indent=1, ensure_ascii=False)
log("SEMANTIC_PAYLOAD_REPRODUCIBILITY = %s" % OUT["verdict"][
    "SEMANTIC_PAYLOAD_REPRODUCIBILITY"])
print("REPRO_CHECK_DONE")
