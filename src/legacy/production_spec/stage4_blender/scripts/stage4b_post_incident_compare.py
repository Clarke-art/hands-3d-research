# STAGE4B_POST_INCIDENT_INTEGRITY_AUDIT -- pixel-level comparison of the rebuilt evidence
# images against the ones currently installed in renders/.
#
# Read-only: nothing is written except the report JSON.  No blend is opened or saved.
#
# Why Blender rather than PIL: the managed Python has neither PIL nor numpy, but Blender
# ships numpy and can decode PNG itself.  Both sides of every comparison are therefore
# decoded by the SAME decoder, which is what makes "the decoded pixels are identical"
# a meaningful statement.
#
# usage: blender -b --python stage4b_post_incident_compare.py -- <pairs.json> <out.json>
import bpy, sys, os, json, hashlib
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
PAIRS_JSON, OUT_JSON = argv[0], argv[1]
PAIRS = json.load(open(PAIRS_JSON, encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def decode(path):
    """Decode a PNG to a float32 HxWx4 array plus its decoded dimensions and channel count.

    colorspace is forced to Non-Color so the decoder performs no colour transform; both
    sides get the identical treatment.
    """
    img = bpy.data.images.load(os.path.abspath(path), check_existing=False)
    try:
        try:
            img.colorspace_settings.name = 'Non-Color'
        except Exception:
            pass
        w, h = img.size
        ch = img.channels
        buf = np.empty(w * h * ch, dtype=np.float32)
        img.pixels.foreach_get(buf)
        buf = buf.reshape(h, w, ch)
        return buf, (w, h), ch
    finally:
        bpy.data.images.remove(img)


def png_header_info(path):
    """Pull width/height/bit-depth/colour-type straight out of the IHDR chunk, so the
    reported dimensions do not depend on the decoder."""
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        return {"format": "not-png", "bytes": len(raw)}
    w = int.from_bytes(raw[16:20], "big")
    h = int.from_bytes(raw[20:24], "big")
    return {"format": "png", "ihdr_width": w, "ihdr_height": h,
            "bit_depth": raw[24], "color_type": raw[25]}


out = {"comparisons": [], "all_pixel_exact": True}
for pr in PAIRS:
    a, b = pr["rebuilt"], pr["installed"]
    ra = {"path": a, "exists": os.path.exists(a)}
    rb = {"path": b, "exists": os.path.exists(b)}
    rec = {"name": pr["name"], "rebuilt": ra, "installed": rb}
    if not (ra["exists"] and rb["exists"]):
        rec["verdict"] = "MISSING_SIDE"
        out["all_pixel_exact"] = False
        out["comparisons"].append(rec)
        continue
    for side, path, d in (("rebuilt", a, ra), ("installed", b, rb)):
        d["bytes"] = os.path.getsize(path)
        d["sha256"] = sha256(path)
        d["header"] = png_header_info(path)
    rec["file_bytes_identical"] = ra["sha256"] == rb["sha256"]

    A, sa, ca = decode(a)
    B, sb, cb = decode(b)
    rec["decoded_pixels_rebuilt"] = {"width": sa[0], "height": sa[1], "channels": ca}
    rec["decoded_pixels_installed"] = {"width": sb[0], "height": sb[1], "channels": cb}
    same_shape = (sa == sb and ca == cb)
    rec["decoded_shape_identical"] = bool(same_shape)
    if not same_shape:
        rec["verdict"] = "DECODED_SHAPE_DIFFERS"
        out["all_pixel_exact"] = False
        out["comparisons"].append(rec)
        continue

    d = np.abs(A - B)
    maxdiff = float(d.max())
    nch = d.shape[2]
    any_diff = d.reshape(-1, nch)
    px_any = int((any_diff.max(axis=1) > 0).sum())
    px_gt1 = int((any_diff.max(axis=1) > 1.0 / 255.0).sum())
    rec["pixel_count_total"] = int(sa[0] * sa[1])
    rec["pixel_difference_count"] = px_any
    rec["pixel_difference_count_gt_1_255"] = px_gt1
    rec["max_abs_channel_difference_0_1"] = round(maxdiff, 8)
    rec["max_abs_channel_difference_8bit"] = round(maxdiff * 255.0, 6)
    rec["pixel_exact"] = bool(px_any == 0)
    rec["verdict"] = "PIXEL_EXACT" if px_any == 0 else "PIXELS_DIFFER"
    if px_any != 0:
        out["all_pixel_exact"] = False
    out["comparisons"].append(rec)

json.dump(out, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT_JSON)
for c in out["comparisons"]:
    print("  %-32s %-16s px_diff=%s max=%s bytes_identical=%s"
          % (c["name"], c["verdict"], c.get("pixel_difference_count"),
             c.get("max_abs_channel_difference_8bit"), c.get("file_bytes_identical")))
print("ALL_PIXEL_EXACT", out["all_pixel_exact"])
