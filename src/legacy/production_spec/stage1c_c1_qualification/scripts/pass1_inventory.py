# STAGE1C - Pass 1: read-only inventory of human_base_meshes_bundle.blend
import bpy, json, sys, os

OUT = r"<HANDS_ROOT>\production_spec\stage1c_c1_qualification\stats\pass1_inventory.json"

report = {}
report["blender_version_running"] = bpy.app.version_string
report["file_path"] = bpy.data.filepath

objs = []
for ob in bpy.data.objects:
    entry = {
        "name": ob.name,
        "type": ob.type,
        "parent": ob.parent.name if ob.parent else None,
        "in_scene_collection": ob.users_collection[0].name if ob.users_collection else None,
        "is_asset": ob.asset_data is not None,
    }
    if ob.type == "MESH":
        me = ob.data
        entry["mesh_name"] = me.name
        entry["verts"] = len(me.vertices)
        entry["faces"] = len(me.polygons)
        entry["has_uv"] = len(me.uv_layers)
        entry["materials"] = [m.name for m in me.materials if m]
        entry["shape_keys"] = bool(me.shape_keys) and len(me.shape_keys.key_blocks)
        entry["modifiers"] = [m.type for m in ob.modifiers]
        entry["dim"] = [round(v, 4) for v in ob.dimensions]
    if ob.type == "ARMATURE":
        entry["bones"] = len(ob.data.bones)
    # asset metadata
    if ob.asset_data:
        ad = ob.asset_data
        entry["asset_catalog"] = ad.catalog_id
        entry["asset_tags"] = [t.name for t in ad.tags]
        md = {}
        for key in ("author", "license", "description", "copyright"):
            try:
                v = ad.get(key, None)
                if v is not None:
                    md[key] = str(v)
            except Exception:
                pass
        # header/custom props
        entry["asset_custom_props_sample"] = {k: str(v)[:120] for k, v in list(ad.items())[:12]}
        entry["asset_metadata"] = md
    objs.append(entry)
report["objects"] = objs

report["meshes"] = []
for me in bpy.data.meshes:
    report["meshes"].append({
        "name": me.name,
        "verts": len(me.vertices),
        "faces": len(me.polygons),
        "users": me.users,
        "use_auto_smooth": getattr(me, "use_auto_smooth", None),
    })

report["armatures"] = [{"name": a.name, "bones": len(a.bones)} for a in bpy.data.armatures]
report["scenes"] = [s.name for s in bpy.data.scenes]
report["node_groups"] = sorted([n.name for n in bpy.data.node_groups])
report["images"] = [{"name": i.name, "size": list(i.size), "filepath": i.filepath} for i in bpy.data.images][:40]
report["materials"] = [m.name for m in bpy.data.materials]
report["worlds"] = [w.name for w in bpy.data.worlds]
report["texts"] = [t.name for t in bpy.data.texts]

# asset catalog file contents if present
cats = os.path.join(os.path.dirname(bpy.data.filepath), "blender_assets.cats.txt")
if os.path.exists(cats):
    report["catalog_file"] = open(cats, encoding="utf-8").read()

# custom properties on file
try:
    report["file_custom_props"] = {k: str(v)[:200] for k, v in bpy.data.filefields.items()} if hasattr(bpy.data, "filefields") else None
except Exception:
    pass

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("PASS1_DONE", OUT)
