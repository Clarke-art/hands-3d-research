import sys
sys.dont_write_bytecode = True
import ast, hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Matrix, Quaternion, Vector

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
S6 = ROOT / 'production_spec/stage6_deformation'
OLD = S6 / 'palmar_thenar_volume_source_zero_pose_comparison_r1'
LINEAGE = ROOT / 'audits/original_source_dorsal_mcp_lineage_and_patch_transfer_feasibility_r1'
CURRENT = ROOT / 'production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'
EXPECTED = '90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa'
CANDIDATE = OUT / 'RIGHT_HAND_STAGE5B_PALMAR_THENAR_RESTORATION_CANDIDATE_R1.blend'
PHASE = 'PALMAR_THENAR_SOURCE_SHAPE_RESTORATION_R1'
MM = 1000.

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n, x):
    def cv(v):
        if hasattr(v, 'tolist'): return v.tolist()
        if hasattr(v, 'item'): return v.item()
        raise TypeError(type(v))
    (OUT / n).write_text(json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False, default=cv) + '\n', encoding='utf-8')
def ref(p): return {'path': Path(p).relative_to(ROOT).as_posix(), 'sha256': sha(p)}
def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
def reuse(path, names):
    nodes = [n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), globals())
    return {'source': ref(path), 'functions': names, 'top_level_executed': False}

HELPERS = [reuse(S6 / 'stage6a/scripts/s6a_common.py', ['reset_pose', 'evaluate', 'face_area']),
           reuse(S6 / 'stage6b/scripts/s6b_common.py', ['set_local_axis_rotation', 'rotation_vector_to_quaternion']),
           reuse(S6 / 'palmar_root_targeted_visual_deformation_r1/run_and_render.py', ['state_zero']),
           reuse(ROOT / 'production_spec/stage5_production_rig/geometry_propagation_after_donor_transfer_r1/payload.py',
                 ['plain', 'props', 'rna', 'object_payload', 'rig_payload', 'material_payload', 'snapshot'])]

def open_asset(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    ob = next(o for o in bpy.data.objects if o.type == 'MESH' and len(o.data.vertices) == 3416)
    rig = bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']
    reset_pose(rig)
    bpy.context.view_layer.update()
    return ob, rig

def smoothstep(a, b, x):
    t = max(0., min(1., (x - a) / (b - a)))
    return t * t * (3. - 2. * t)

def safety_check(V, F, E, A0=None):
    floor = read(S6 / 'whole_hand_surface_integrity_baseline_r1/MINIMUM_MACHINE_SAFETY_R1.json')['thresholds']
    areas = [face_area(V, p) for p in F]
    finite = sum(not math.isfinite(float(x)) for v in V for x in v)
    collapse = sum(a <= floor['collapse_area_m2_le'] or (A0 is not None and a / A0[i] <= floor['collapse_ratio_le']) for i, a in enumerate(areas))
    degenerate = sum((V[a] - V[b]).length <= floor['degenerate_edge_m_le'] for a, b in E)
    return {'NaN_Inf': finite, 'collapsed_faces': collapse, 'degenerate_edges': degenerate,
            'automatic_status': 'PASS' if finite == collapse == degenerate == 0 else 'FAIL'}, areas

def frame(points, direction, size, padding=1.15, scale=None):
    Z = Vector((0, 0, 1)); d = Vector(direction).normalized(); r = Z.cross(d).normalized(); u = d.cross(r).normalized()
    xyz = [[v.dot(a) for v in points] for a in [r, u, d]]
    center = sum((a * ((min(v) + max(v)) / 2) for a, v in zip([r, u, d], xyz)), Vector())
    aspect = size[0] / size[1]
    s = scale or max(max(xyz[0]) - min(xyz[0]), (max(xyz[1]) - min(xyz[1])) * aspect) / min(1., aspect) * padding
    return {'center': list(center), 'direction': list(d), 'ortho_scale_m': s, 'resolution': size}

class Renderer:
    def __init__(self, cameras, subdir='renders'):
        self.cameras = cameras; self.records = []; self.active = None; self.subdir = subdir
        (OUT / subdir).mkdir(exist_ok=True)
        self.sc = bpy.data.scenes.new('UNSAVED_PRODUCT_VISUAL_REVIEW')
        self.sc.render.engine = 'BLENDER_WORKBENCH'; self.sc.render.resolution_percentage = 100
        self.sc.render.image_settings.file_format = 'PNG'; self.sc.world = bpy.data.worlds.new('UNSAVED_NEUTRAL_WORLD')
        self.sc.view_settings.view_transform = 'Standard'; self.sc.view_settings.look = 'None'
        sh = self.sc.display.shading; sh.color_type = 'MATERIAL'; sh.background_type = 'WORLD'; sh.show_cavity = False; sh.studiolight_rotate_z = .25
        self.cd = bpy.data.cameras.new('UNSAVED_REVIEW_CAMERA'); self.cd.type = 'ORTHO'; self.cd.clip_start = .001; self.cd.clip_end = 5
        self.cam = bpy.data.objects.new('UNSAVED_REVIEW_CAMERA', self.cd); self.sc.collection.objects.link(self.cam); self.sc.camera = self.cam
        self.clay = bpy.data.materials.new('UNSAVED_NEUTRAL_CLAY'); self.clay.diffuse_color = (.66, .68, .71, 1)
        self.white = bpy.data.materials.new('UNSAVED_WHITE_SILHOUETTE'); self.white.diffuse_color = (.96, .96, .96, 1)
    def draw(self, asset, pose, V, F, views):
        if self.active:
            me = self.active.data; bpy.data.objects.remove(self.active, do_unlink=True); bpy.data.meshes.remove(me)
        me = bpy.data.meshes.new('UNSAVED_DISPLAY_COPY'); me.from_pydata(V, [], F); me.materials.append(self.clay); me.materials.append(self.white)
        for p in me.polygons: p.use_smooth = True
        me.update(); self.active = bpy.data.objects.new('UNSAVED_DISPLAY_COPY', me); self.sc.collection.objects.link(self.active)
        assert [tuple(p.vertices) for p in me.polygons] == F
        for view in views:
            job = self.cameras[view]; sil = view == 'SILHOUETTE'; sh = self.sc.display.shading
            sh.light = 'FLAT' if sil else 'STUDIO'; sh.show_shadows = not sil; sh.show_specular_highlight = not sil
            self.sc.world.color = (.025, .030, .040) if sil else (.15, .17, .20)
            for p in me.polygons: p.material_index = 1 if sil else 0
            center, direction = Vector(job['center']), Vector(job['direction'])
            self.cam.location = center + direction * .7; self.cam.rotation_euler = (center - self.cam.location).to_track_quat('-Z', 'Y').to_euler()
            self.cd.ortho_scale = job['ortho_scale_m']; self.sc.render.resolution_x, self.sc.render.resolution_y = job['resolution']
            name = f'{asset}__{pose}__{view}.png'; self.sc.render.filepath = str(OUT / self.subdir / name)
            bpy.ops.render.render(write_still=True, scene=self.sc.name)
            self.records.append({'asset': asset, 'pose': pose, 'view': view, 'path': self.subdir + '/' + name,
                                 'camera': job, 'same_camera_current_candidate': True, 'all_native_faces_present': True,
                                 'display_only_smooth_shading': True, 'neutral_material': True, 'cavity': False})
            print('RENDER', name, flush=True)
        return self.records
    def dispose(self):
        if self.active:
            me = self.active.data; bpy.data.objects.remove(self.active, do_unlink=True); bpy.data.meshes.remove(me)
            self.active = None
        bpy.data.objects.remove(self.cam, do_unlink=True); bpy.data.cameras.remove(self.cd)
        world = self.sc.world; bpy.data.scenes.remove(self.sc); bpy.data.worlds.remove(world)
        bpy.data.materials.remove(self.clay); bpy.data.materials.remove(self.white)
