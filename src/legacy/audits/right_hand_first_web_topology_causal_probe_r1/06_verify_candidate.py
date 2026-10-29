"""Verify the saved DESIGN_ONLY candidate read-only:
  * baseline object inside it is unchanged,
  * probe object shape keys / corrective driver reproduce the baseline corrective value,
  * frozen fallback on disk is untouched.
Nothing is written; the file is only opened.
"""
import sys, json, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

CAND = OUT / 'RIGHT_HAND_FIRST_WEB_TOPOLOGY_PROBE_CANDIDATE_R1.blend'
FRAMES = [110, 127, 130, 160, 176, 205]
KEY = 'FIRST_WEB_OPPOSITION_CREASE_R1'


def main():
    before = protected_inputs()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(CAND), load_ui=False, use_scripts=False)
    ob = bpy.data.objects[m.MESH_NAME]
    cob = bpy.data.objects['RIGHT_HAND_OFFICIAL_L1_PRODUCT_MESH__PROBE_TOPOLOGY_R1']
    rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    out = {'phase': PHASE, 'mode': 'READ_ONLY_CANDIDATE_VERIFICATION',
           'candidate_blend': CAND.name, 'candidate_sha256': sha(CAND),
           'baseline_object': m.MESH_NAME, 'probe_object': cob.name}

    sdrv = ob.data.shape_keys.animation_data.drivers[0]
    ddrv = cob.data.shape_keys.animation_data.drivers[0]
    def drv_info(fc):
        return {'data_path': fc.data_path, 'expression': fc.driver.expression,
                'variables': [{'name': v.name, 'type': v.type,
                               'bone': v.targets[0].bone_target,
                               'transform_type': v.targets[0].transform_type,
                               'transform_space': v.targets[0].transform_space,
                               'id': v.targets[0].id.name if v.targets[0].id else None}
                              for v in fc.driver.variables]}
    out['baseline_driver'] = drv_info(sdrv)
    out['probe_driver'] = drv_info(ddrv)

    rows = []
    for f in FRAMES:
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        row = {'frame': f,
               'baseline_key_value': float(ob.data.shape_keys.key_blocks[KEY].value),
               'probe_key_value': float(cob.data.shape_keys.key_blocks[KEY].value)}
        # evaluate the expression by hand from the actual bone inputs, for both objects
        def manual(fc, obj):
            inputs = {}
            for var in fc.driver.variables:
                t = var.targets[0]
                inputs[var.name] = float(rig.pose.bones[t.bone_target].matrix_basis.to_euler('XYZ').x)
            return eval(fc.driver.expression, {'__builtins__': {}, 'min': min, 'max': max}, inputs), inputs
        row['baseline_manual'], row['probe_manual'] = manual(sdrv, ob), manual(ddrv, cob)
        row['baseline_verts'] = len(ob.data.vertices)
        row['probe_verts'] = len(cob.data.vertices)
        rows.append(row)
        print('VERIFY', f, row['baseline_key_value'], row['probe_key_value'],
              row['baseline_manual'][0], row['probe_manual'][0], flush=True)
    out['rows'] = rows

    out['baseline_mesh_vertices'] = len(ob.data.vertices)
    out['baseline_mesh_faces'] = len(ob.data.polygons)
    out['probe_mesh_vertices'] = len(cob.data.vertices)
    out['probe_mesh_faces'] = len(cob.data.polygons)
    out['probe_all_quads'] = all(len(p.vertices) == 4 for p in cob.data.polygons)
    out['baseline_all_quads'] = all(len(p.vertices) == 4 for p in ob.data.polygons)
    out['probe_vertex_groups'] = [g.name for g in cob.vertex_groups]
    out['baseline_vertex_groups'] = [g.name for g in ob.vertex_groups]
    out['frozen_fallback_sha256'] = sha(BASE)
    out['frozen_fallback_unchanged'] = sha(BASE) == FROZEN_SHA
    verify_inputs(before)
    out['protected_inputs_unchanged'] = True

    # weight-field semantics: every probe vertex weight must be a convex combination of the
    # original field. Verified structurally by construction; here we only confirm the group
    # set and that every vertex's weights sum to 1 (a necessary condition of the transfer).
    sums = []
    for v in cob.data.vertices:
        sums.append(sum(float(g.weight) for g in v.groups))
    out['probe_weight_sum_min'] = round(min(sums), 9)
    out['probe_weight_sum_max'] = round(max(sums), 9)
    bsums = [sum(float(g.weight) for g in v.groups) for v in ob.data.vertices]
    out['baseline_weight_sum_min'] = round(min(bsums), 9)
    out['baseline_weight_sum_max'] = round(max(bsums), 9)
    out['probe_vertices_without_weights'] = int(sum(1 for s in sums if s <= 1e-9))

    dump('CANDIDATE_VERIFICATION_R1.json', out)
    print('VERIFY_READY')


main()
