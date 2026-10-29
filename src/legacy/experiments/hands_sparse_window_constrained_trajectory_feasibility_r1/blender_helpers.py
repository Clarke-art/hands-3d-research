import bpy,numpy as np,math,json,hashlib
from mathutils import Matrix,Vector

def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def native(ob, rig):
    return dict(vertices=[list(v.co) for v in ob.data.vertices], faces=[list(p.vertices) for p in ob.data.polygons], weights=[[[ob.vertex_groups[g.group].name, g.weight] for g in v.groups] for v in ob.data.vertices], bones=[dict(name=b.name, parent=b.parent.name if b.parent else None, deform=b.use_deform, head=list(b.head_local), tail=list(b.tail_local), matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones], shapes={b.name: [list(v.co) for v in b.data] for b in ob.data.shape_keys.key_blocks}, corrective_drivers=[dict(path=f.data_path, expression=f.driver.expression, variables=[dict(name=v.name, type=v.type, targets=[dict(bone=t.bone_target, transform_type=t.transform_type, transform_space=t.transform_space, data_path=t.data_path) for t in v.targets]) for v in f.driver.variables]) for f in ob.data.shape_keys.animation_data.drivers] if ob.data.shape_keys.animation_data else [])

def settime(sc, t):
    f = 1 + 60 * t
    sc.frame_set(math.floor(f), subframe=f - math.floor(f))
    bpy.context.view_layer.update()

def coords(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    V = np.array([list(ob.matrix_world @ v.co) for v in me.vertices])
    faces = [list(p.vertices) for p in me.polygons]
    ev.to_mesh_clear()
    return (V, faces)

def component_planes(g):
    v = np.array(g['vertices'])
    center = v.mean(0)
    planes = []
    for tri in np.asarray(g['triangles']).reshape(-1, 3):
        a, b, c0 = v[tri]
        n = np.cross(b - a, c0 - a)
        l = np.linalg.norm(n)
        if l < 1e-12:
            continue
        n /= l
        if np.dot(n, center - a) > 0:
            n = -n
        planes.append(np.r_[n, np.dot(n, a)])
    planes = np.unique(np.round(planes, 10), axis=0)
    assert np.max(v @ planes[:, :3].T - planes[:, 3]) < 1e-07
    return planes

def axisrot(a, v):
    v = np.array(v)
    v = v / np.linalg.norm(v)
    x, y, z = v
    K = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + np.sin(a) * K + (1 - np.cos(a)) * (K @ K)

def digit_setup(s, d):
    names = [f'{d}_{j}_{s}' for j in (['CMC', 'MCP', 'IP'] if d == 'THUMB' else ['MCP', 'PIP', 'DIP'])]
    b = RIG[s]['bones']
    rests = [np.array(b[n]['matrix']) for n in names]
    rels = [rests[0]] + [np.linalg.inv(rests[j - 1]) @ rests[j] for j in [1, 2]]
    axes = []
    for M in rests:
        y = M[:3, 1]
        a = np.cross(y, [0, 0, -1])
        a /= np.linalg.norm(a)
        axes.append(M[:3, :3].T @ a)
    spread = rests[0][:3, :3].T @ np.array([0, 0, 1])
    pad = np.r_[MARKERS[s][DIGITS.index(d)]['local_pad_point'], 1]
    return (names, rels, axes, spread, pad)

def joint_mats(s, d, q):
    names, rels, axes, spread, pad = SETUPS[s, d]
    out = []
    for j in range(3):
        r = axisrot(q[j], axes[j])
        r = axisrot(q[3], spread) @ r if j == 0 else r
        out.append(r)
    return out
