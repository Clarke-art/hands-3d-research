import bpy
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import *

def scalar(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    try:
        return [scalar(v) for v in value]
    except TypeError:
        return getattr(value, 'name', str(type(value)))

def editable_properties(obj):
    result = {}
    for prop in obj.bl_rna.properties:
        if prop.identifier == 'rna_type' or prop.is_readonly or prop.type in ('POINTER', 'COLLECTION'):
            continue
        try:
            result[prop.identifier] = scalar(getattr(obj, prop.identifier))
        except (AttributeError, TypeError):
            continue
    return result

def material_snapshot(mat):
    if mat is None:
        return None
    result = {'name': mat.name, 'properties': editable_properties(mat)}
    if mat.node_tree:
        result['nodes'] = []
        for node in sorted(mat.node_tree.nodes, key=lambda n: n.name):
            row = {'name': node.name, 'type': node.bl_idname, 'properties': editable_properties(node),
                   'inputs': [{'identifier': socket.identifier, 'default_value': scalar(socket.default_value)} for socket in node.inputs if hasattr(socket, 'default_value')],
                   'outputs': [{'identifier': socket.identifier, 'default_value': scalar(socket.default_value)} for socket in node.outputs if hasattr(socket, 'default_value')]}
            if hasattr(node, 'image') and node.image:
                row['image'] = {'name': node.image.name, 'filepath': node.image.filepath, 'colorspace': node.image.colorspace_settings.name}
            if hasattr(node, 'color_ramp'):
                row['color_ramp'] = {'interpolation': node.color_ramp.interpolation,
                                     'elements': [{'position': e.position, 'color': list(e.color)} for e in node.color_ramp.elements]}
            result['nodes'].append(row)
        result['links'] = sorted((link.from_node.name, link.from_socket.identifier, link.to_node.name, link.to_socket.identifier) for link in mat.node_tree.links)
    return result

snapshots = {}
for tag, path in [('R1', R1), ('R2', CANDIDATE)]:
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    ob = bpy.data.objects['Hand  - Realistic']
    snapshots[tag] = [material_snapshot(mat) for mat in ob.data.materials]
assert snapshots['R1'] == snapshots['R2'], 'FAIL_CLOSED material semantic drift'
dump('R2_MATERIAL_SEMANTIC_NO_DRIFT.json', {'status': 'PASS', 'material_count': len(snapshots['R1']),
                                        'R1_snapshot_hash': digest(snapshots['R1']), 'R2_snapshot_hash': digest(snapshots['R2']),
                                        'material_properties_nodes_socket_defaults_links_images_exact': True,
                                        'snapshots': snapshots, 'blend_writes': 0, 'deformation_runs': 0, 'Stage6_runs': 0})
print('Material properties / shader nodes / socket defaults / links exact PASS', flush=True)
