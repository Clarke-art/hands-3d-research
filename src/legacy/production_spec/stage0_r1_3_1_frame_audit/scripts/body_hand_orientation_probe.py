# STAGE0 R1.3.1 -- body-hand orientation probe.  READ-ONLY, no save, no mesh creation.
# The realistic body carries explicit .L/.R eye + skeleton hand_center objects, so the
# body's own world-space handedness is known. We read the body's two hands and report
# the direction of the thumb relative to the body midline -> establishes the bundle's
# palm-side convention independently of any project document.
import bpy, json, sys, math
from mathutils import Vector

OUT = sys.argv[-1]

def wverts(ob):
    mw = ob.matrix_world
    return [mw @ v.co for v in ob.data.vertices]

def mean(V):
    return sum(V, Vector((0,0,0))) / len(V)

rep = {}

BODY = 'GEO-body_male_realistic'
if BODY in bpy.data.objects:
    V = wverts(bpy.data.objects[BODY])
    # eye positions give the body's left/right
    eyes = {}
    for side in 'LR':
        n = f'{BODY}.eye.{side}'
        if n in bpy.data.objects:
            eyes[side] = [round(c,4) for c in mean(wverts(bpy.data.objects[n]))]
    rep['eyes'] = eyes

    xmax = max(v.x for v in V); xmin = min(v.x for v in V)
    rep['body_x_range'] = [round(xmin,4), round(xmax,4)]
    rep['body_center_x'] = round((xmin+xmax)/2, 4)

    # skeleton hand centres (explicit .L/.R)
    sk = {}
    for n in bpy.data.objects.keys():
        if n.startswith('GEO-skeletion') and n.endswith(('.L','.R')):
            ob = bpy.data.objects[n]
            if ob.type != 'MESH':
                continue
            try:
                W = wverts(ob)
            except Exception:
                continue
            if not W:
                continue
            sk[n] = [round(c,4) for c in mean(W)]
    rep['skeleton_LR_objects'] = sk

    # the two hands = vertex clouds near the two x extremes
    for tag, ext in (('HIGH_X', xmax), ('LOW_X', xmin)):
        sel = [v for v in V if abs(v.x - ext) < 0.14]
        if not sel:
            continue
        c = mean(sel)
        # distal axis = away from the shoulder = direction of decreasing z for a hanging arm
        # use PCA of the selection
        n = len(sel)
        cov = [[0.0]*3 for _ in range(3)]
        for p in sel:
            d = p - c
            for i in range(3):
                for j in range(3):
                    cov[i][j] += d[i]*d[j]
        for i in range(3):
            for j in range(3):
                cov[i][j] /= n
        # power iteration for the dominant eigenvector
        v = Vector((0,0,1))
        for _ in range(200):
            w = Vector((sum(cov[i][j]*v[j] for j in range(3)) for i in range(3)))
            if w.length < 1e-12:
                break
            v = w.normalized()
        d = [p - c for p in sel]
        proj = sorted(d, key=lambda q: q.dot(v))
        axis = v if abs(proj[-1].length) > abs(proj[0].length) else -v
        # 5 fingertips = 5 extreme points along +axis, deduplicated
        cand = sorted(sel, key=lambda p: (p - c).dot(axis), reverse=True)
        tips = []
        for p in cand:
            if all((p - q).length > 0.02 for q in tips):
                tips.append(p)
            if len(tips) == 5:
                break
        rep[f'hand_{tag}'] = {
            "n_verts": n,
            "centroid": [round(x,4) for x in c],
            "bbox": [round(min(p.x for p in sel),4), round(max(p.x for p in sel),4),
                     round(min(p.y for p in sel),4), round(max(p.y for p in sel),4),
                     round(min(p.z for p in sel),4), round(max(p.z for p in sel),4)],
            "principal_axis": [round(x,4) for x in axis],
            "tip_candidates": [[round(x,4) for x in p] for p in tips],
        }

# authored camera of the standalone hand asset
cam = {}
for n in ['realistic_hand','stylized_hand']:
    if n in bpy.data.objects and bpy.data.objects[n].type == 'CAMERA':
        ob = bpy.data.objects[n]
        mw = ob.matrix_world
        loc = mw.translation
        fwd = -(mw.to_3x3() @ Vector((0,0,1)))   # cameras look along local -Z
        up = mw.to_3x3() @ Vector((0,1,0))
        cam[n] = {"parent": ob.parent.name if ob.parent else None,
                  "world_loc": [round(x,4) for x in loc],
                  "world_forward": [round(x,4) for x in fwd.normalized()],
                  "world_up": [round(x,4) for x in up.normalized()],
                  "lens": round(ob.data.lens,2)}
rep['authored_cameras'] = cam

rep['PASS'] = 'BODY_HAND_PROBE_DONE'
with open(OUT,'w',encoding='utf-8') as f:
    json.dump(rep,f,ensure_ascii=False,indent=1)
print("WROTE", OUT)
