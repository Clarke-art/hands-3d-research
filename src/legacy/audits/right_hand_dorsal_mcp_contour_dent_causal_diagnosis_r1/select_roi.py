"""Recover Human-selected A by an orthographic image ray, not by anatomy labels."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=read(OUT/'LINEAGE_RAW_READONLY_EXTRACTION.json');F=L['topology']['faces'];E=L['topology']['edges']
FULL=S6/'full_stage6a_requalification_r1'
G=read(FULL/'POSED_COORDINATES_R1.json')['positions_world_m']
V=[Vector(v) for v in G['BIND']];VP=[Vector(v) for v in G['IDX_MCP_15']]
m=next(r for r in read(FULL/'EVIDENCE_RENDER_MANIFEST_R1.json')['renders'] if r['path']=='renders/IDX_MCP_15_FULL_SOLID.png')
vd=Vector(m['camera_direction']).normalized();r=Vector((0,0,1)).cross(vd).normalized();u=vd.cross(r).normalized()
coords=V+VP;ctr=r*((max(v.dot(r) for v in coords)+min(v.dot(r) for v in coords))/2)+u*((max(v.dot(u) for v in coords)+min(v.dot(u) for v in coords))/2)+vd*((max(v.dot(vd) for v in coords)+min(v.dot(vd) for v in coords))/2)
scale=m['ortho_scale_m'];BVH=BVHTree.FromPolygons(V,F,all_triangles=False)
sc=bpy.context.scene;sc.render.resolution_x=640;sc.render.resolution_y=800
cd=bpy.data.cameras.new('readonly screen ray camera');cd.type='ORTHO';cd.ortho_scale=scale
cam=bpy.data.objects.new('readonly screen ray camera',cd);sc.collection.objects.link(cam)
cam.location=ctr+vd*.7;cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
frame=cd.view_frame(scene=sc);fw=max(v.x for v in frame)-min(v.x for v in frame);fh=max(v.y for v in frame)-min(v.y for v in frame)
r=cam.matrix_world.to_3x3()@Vector((1,0,0));u=cam.matrix_world.to_3x3()@Vector((0,1,0))
def pick(x,y):
 origin=cam.matrix_world@Vector(((x+.5-320)/640*fw,(400-(y-44+.5))/800*fh,0))
 hit,n,fi,dist=BVH.ray_cast(origin,-vd,2.)
 return None if hit is None else {'pixel':[x,y],'face_id':fi,'hit_world_m':list(hit),'normal_world':list(n),'ray_origin_world_m':list(origin),'distance_m':dist}
central=pick(410,159);assert central is not None
samples=[pick(x,y) for y in range(149,170,4) for x in range(400,421,4) if (x-410)**2+(y-159)**2<=100]
samples=[s for s in samples if s is not None and (Vector(s['hit_world_m'])-Vector(central['hit_world_m'])).length<=.006]
corefaces=sorted({s['face_id'] for s in samples});coreverts=sorted({v for fi in corefaces for v in F[fi]})
ADJ={i:set() for i in range(len(V))}
for a,b in E:ADJ[a].add(b);ADJ[b].add(a)
ring1=sorted({v for i in coreverts for v in ADJ[i]}-set(coreverts))
ring2=sorted({v for i in ring1 for v in ADJ[i]}-set(coreverts)-set(ring1))
roi=set(coreverts+ring1+ring2)
fs=[fi for fi,p in enumerate(F) if set(p)<=roi];es=[j for j,(a,b) in enumerate(E) if a in roi and b in roi]
center=min(coreverts,key=lambda i:(V[i]-Vector(central['hit_world_m'])).length)
data={'status':'ESTABLISHED_FROM_HUMAN_CONFIRMED_A_SCREEN_RAY','human_confirmation':'User replied A in this chat; location only, no repair approval.','anatomy_authority':False,'source_image':ref(FULL/'renders/IDX_MCP_15_FULL_SOLID.png'),'source_review':ref(FULL/'review.html'),'screen_anchor_xy':[410,159],'screen_origin':'Top left of1280x844 source image; bind panel640x800 starts at y44.','selection_method':'Reconstruct exact measured bind/posed common-frame camera using Blender native view_frame (portrait sensor fit), cast view ray for Human A; sample radius10 pixels in4px increments; retain surface hits within6mm of central hit; collect hit faces and native1/2rings. Pixel/radius distances are diagnostic selection parameters, not anatomical thresholds.','camera':{'direction':list(vd),'center_world_m':list(ctr),'right':list(r),'up':list(u),'ortho_scale_m':scale,'frame_width_m':fw,'frame_height_m':fh,'source_panel_width':640,'source_panel_height':800,'image_header_height':44},'center_pick':central,'center_vertex_id':center,'core_vertices':coreverts,'core_faces':corefaces,'vertices':sorted(roi),'faces':fs,'edges':es,'1_ring':ring1,'2_ring':ring2,'visible_hit_samples':samples,'topology_hash':digest(L['topology']),'new_digit_ownership_label':False,'repair_write_scope_authorized':False}
dump('DORSAL_MCP_DENT_ROI_R1.json',data)
record=read(OUT/'HUMAN_PRODUCT_REQUIREMENT_RECORD_R1.json');record['ROI_location_confirmation_pending']=False;record['confirmed_screen_location']='A';record['ROI_confirmation_is_repair_approval']=False;dump('HUMAN_PRODUCT_REQUIREMENT_RECORD_R1.json',record)
print('Selected A:',central['face_id'],'center vertex',center,'core',len(coreverts),'ROI',len(roi),'faces',len(fs),'rings',len(ring1),len(ring2))
