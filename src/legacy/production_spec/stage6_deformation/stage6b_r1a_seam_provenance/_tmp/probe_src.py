import bpy
bpy.ops.wm.open_mainfile(filepath=r"<HANDS_ROOT>/references/licenses/blender_human_base_meshes/extracted/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend")
cands=[]
for o in bpy.data.objects:
    if o.type=='MESH' and 'Hand' in o.name:
        cands.append((o.name,len(o.data.vertices),o.data.name))
print("HAND-OBJECTS:",len(cands))
seen={}
for n,nv,dn in cands:
    seen.setdefault((n,nv,dn),0); seen[(n,nv,dn)]+=1
for k,v in sorted(seen.items()): print("  %-28s verts=%-6d mesh=%-28s x%d"%(k[0],k[1],k[2],v))
