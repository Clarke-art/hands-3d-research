# STAGE4A_R2 -- compose the side-by-side BEFORE / AFTER evidence panel.
# usage: blender -b --python stage4a_r2_composite.py -- <before.png> <after.png> <out.png> <label_left> <label_right>
import bpy, sys, os, numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
A, B, OUT = argv[0], argv[1], argv[2]
la = bpy.data.images.load(os.path.abspath(A))
lb = bpy.data.images.load(os.path.abspath(B))
W, H = la.size
ga = np.empty(W * H * 4, dtype=np.float32)
gb = np.empty(W * H * 4, dtype=np.float32)
la.pixels.foreach_get(ga)
lb.pixels.foreach_get(gb)
ga = ga.reshape(H, W, 4)
gb = gb.reshape(H, W, 4)
gap = np.ones((H, 14, 4), dtype=np.float32)
gap[:, :, :3] = 0.10
strip = np.concatenate([ga, gap, gb], axis=1)
img = bpy.data.images.new("ba", width=strip.shape[1], height=H, alpha=True)
img.pixels.foreach_set(strip.ravel())
img.filepath_raw = os.path.abspath(OUT)
img.file_format = 'PNG'
img.save()
print("WROTE", OUT, os.path.exists(OUT))
