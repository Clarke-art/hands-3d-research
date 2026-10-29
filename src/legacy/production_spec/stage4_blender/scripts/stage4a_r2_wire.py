# STAGE4A_R2 -- wireframe close-up of the CMC cage (quad-flow evidence).
# usage: blender -b <blend> --python stage4a_r2_wire.py -- <out.png>
import bpy, sys, os, math, heapq
from mathutils import Vector, Matrix
OUT = sys.argv[sys.argv.index("--") + 1]
TIP = Vector((1.4977, 0.0358, 0.2421)); ROOT = Vector((1.4489, 0.0115, 0.3134))
M = Matrix(((1,0,0),(0,-1,0),(0,0,-1)))
ob = bpy.data.objects["Hand  - Realistic"]; mw = ob.matrix_world
CO = [mw @ v.co for v in ob.data.vertices]; loc = mw.translation
canon = lambda p: (M @ p) + (loc - (M @ loc))
nr = lambda p: min(range(len(CO)), key=lambda i: (CO[i]-p).length_squared)
TIP_V, ROOT_V = nr(canon(TIP)), nr(canon(ROOT))
adj = [[] for _ in CO]
for e in ob.data.edges:
    a,b = e.vertices[0], e.vertices[1]; L=(CO[a]-CO[b]).length
    adj[a].append((b,L)); adj[b].append((a,L))
def dij(s):
    d=[float('inf')]*len(CO); d[s]=0; pq=[(0,s)]
    while pq:
        du,u=heapq.heappop(pq)
        if du>d[u]+1e-15: continue
        for v,w in adj[u]:
            if du+w<d[v]-1e-16: d[v]=du+w; heapq.heappush(pq,(d[v],v))
    return d
gdt=dij(TIP_V); L=gdt[ROOT_V]
band=[i for i in range(len(CO)) if 0.25*L<=gdt[i]<=0.55*L]
cm=sum((CO[i] for i in band), Vector())/len(band)
AXIS=(CO[TIP_V]-cm).normalized(); CMC=CO[ROOT_V]
DORS=Vector((0,1,0)); d_perp=(DORS-AXIS*DORS.dot(AXIS)).normalized(); d_side=AXIS.cross(d_perp).normalized()
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'; sc.display.shading.type='WIREFRAME'
sc.display.shading.color_type='OBJECT'

sc.display.render_aa='8'; sc.render.resolution_x=1200; sc.render.resolution_y=1000
w=bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("W"); sc.world=w; w.color=(1,1,1)
cd=bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.clip_start=0.001
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
sc.display.shading.background_type='VIEWPORT'
sc.display.shading.background_color=(1.0,1.0,1.0)
ob.color=(0.05,0.05,0.10,1)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0035, location=tuple(CMC))
bpy.context.active_object.color=(1.0,0.5,0.0,1)
for nm,dv,tag in (("dorsal",d_perp,"dorsal"),("side",d_side,"side")):
    sc.render.filepath=os.path.join(OUT, "CMC_CAGE_WIRE_%s.png"%tag)
    cd.ortho_scale=0.085
    pos=CMC+dv*0.8; cam.location=pos
    cam.rotation_euler=(CMC-pos).to_track_quat('-Z','Y').to_euler()
    bpy.ops.render.render(write_still=True); print("RENDERED", tag)
print("DONE")
