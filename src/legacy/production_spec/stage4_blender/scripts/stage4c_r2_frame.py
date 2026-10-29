# STAGE4C_R2 -- extract the joint measurement frame from the FROZEN Stage-4B provenance.
#
# The R2 master must NOT depend on the deleted TEMP rig, and must not re-create it.  This
# script reads the frozen Stage-4B R2 blend ONCE (read-only, never saved) and writes the 21
# posed bone head/tail positions to a plain JSON.  R2 then works from that JSON: it is an
# "equivalent measurement frame" derived from the frozen provenance.
#
# usage: blender -b <stage4b_r2.blend> --python stage4c_r2_frame.py -- <out.json>
import bpy, sys, os, json, hashlib

OUT = sys.argv[sys.argv.index("--") + 1]
SHA = hashlib.sha256(open(bpy.data.filepath, "rb").read()).hexdigest()
arm = None
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        arm = o
if arm is None:
    raise SystemExit("no armature in the frozen provenance blend")
aw = arm.matrix_world
bones = {}
for b in arm.data.bones:
    bones[b.name] = {"head": [float(x) for x in (aw @ b.head_local)],
                     "tail": [float(x) for x in (aw @ b.tail_local)],
                     "parent": b.parent.name if b.parent else None}
out = {
    "source_blend": bpy.data.filepath,
    "source_sha256": SHA,
    "source_object": arm.name,
    "source_flags": {k: str(arm[k]) for k in arm.keys() if k != "_RNA_UI"},
    "note": "READ-ONLY extraction of the posed joint frame from the frozen Stage-4B R2 "
            "provenance.  The R2 master does not contain this armature and does not depend "
            "on it at runtime; this JSON is the measurement frame only.",
    "bones": bones,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("source sha256:", SHA)
print("bones:", len(bones))
for n in ("WRIST_R", "THUMB_CMC_R", "THUMB_IP_R", "INDEX_DIP_R", "MIDDLE_DIP_R",
          "RING_DIP_R", "LITTLE_DIP_R"):
    print("  %-14s head %s" % (n, [round(x, 6) for x in bones[n]["head"]]))
