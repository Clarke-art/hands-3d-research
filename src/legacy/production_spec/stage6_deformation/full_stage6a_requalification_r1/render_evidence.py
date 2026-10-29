"""Actual measured meshes, plain solid first. Display clones only, no blend saves."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,math
from mathutils import Vector
G=read(OUT/'POSED_COORDINATES_R1.json');E=read(OUT/'FULL_STAGE6A_MACHINE_EVIDENCE_R1.json')
D=read(OUT/'LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json');cap=read(CAP_PATH)
F=G['faces'];edges=G['edges'];V0=[Vector(v) for v in G['positions_world_m']['BIND']]
OUT.joinpath('renders').mkdir(exist_ok=True)
OUT.joinpath('renders/_parts').mkdir(exist_ok=True)
sc=bpy.context.scene
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
sc.render.engine='BLENDER_WORKBENCH'
sc.render.resolution_x=1280;sc.render.resolution_y=800;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.display.shading.light='STUDIO';sc.display.shading.studiolight_rotate_z=.25
sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=True
sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH'
sc.display.shading.curvature_ridge_factor=1.;sc.display.shading.curvature_valley_factor=.8
sc.display.shading.background_type='WORLD';sc.world.color=(.12,.14,.17)
sc.display.shading.show_specular_highlight=True
sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0
materials=[]
for name,color in [('plain skin',(.66,.68,.71,1)),('plain nail',(.85,.87,.89,1)),('compression',(.12,.4,.85,1)),('moderate stretch',(.96,.68,.2,1)),('high strain',(.85,.22,.14,1)),('face A',(.93,.31,.14,1)),('face B',(.19,.57,.94,1)),('exact segment',(.18,.95,.45,1)),('wire',(.12,.16,.2,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=color;materials.append(m)
nailfaces={fi for row in D['nail_material_components'] for fi in row['face_ids']}
camdata=bpy.data.cameras.new('evidence orthographic');camdata.type='ORTHO'
cam=bpy.data.objects.new('evidence orthographic',camdata);sc.collection.objects.link(cam);sc.camera=cam
DORS=Vector((.631289124,.775318801,-.0188387)).normalized()
render_objects=[];manifest=[]
def clear():
 for o in render_objects:
  data=o.data;bpy.data.objects.remove(o,do_unlink=True)
  if isinstance(data,bpy.types.Mesh):bpy.data.meshes.remove(data)
 render_objects.clear()
def mesh(V,name,shift=Vector((0,0,0)),face_ids=None,strain=None,highlight=None):
 ids=range(len(F)) if face_ids is None else face_ids
 me=bpy.data.meshes.new(name);me.from_pydata([list(v+shift) for v in V],[],[F[i] for i in ids]);me.update()
 ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);render_objects.append(ob)
 for m in materials:me.materials.append(m)
 for j,fi in enumerate(ids):
  p=me.polygons[j];p.use_smooth=True;p.material_index=1 if fi in nailfaces else 0
  if strain is not None:
   vv=F[fi];ratio=max((V[vv[k]]-V[vv[(k+1)%len(vv)]]).length/max((V0[vv[k]]-V0[vv[(k+1)%len(vv)]]).length,1e-18) for k in range(len(vv)))
   area=strain['face_ratio'][fi]
   p.material_index=2 if area<.5 else 4 if ratio>3 else 3 if ratio>1.5 else p.material_index
  if highlight is not None and fi in highlight:p.material_index=highlight[fi]
 return ob
def framing(V,ids,vd):
 vd=vd.normalized();r=Vector((0,0,1)).cross(vd).normalized();u=vd.cross(r).normalized()
 coords=[v for arr in [V0,V] for i,v in enumerate(arr) if i in set(ids)]
 a=[v.dot(r) for v in coords];b=[v.dot(u) for v in coords];z=[v.dot(vd) for v in coords]
 ctr=r*((max(a)+min(a))/2)+u*((max(b)+min(b))/2)+vd*((max(z)+min(z))/2)
 width=max(max(a)-min(a),.006);height=max(max(b)-min(b),.006)
 return ctr,r,u,vd,width,height
def save(name,V,ids,vd=DORS,strain=None,highlight=None,face_ids=None,paired=True):
 clear();ctr,r,u,vd,w,h=framing(V,ids,vd)
 # Render each panel independently so full local context from one clone cannot
 # occlude the other clone. Both panels retain identical camera and framing.
 sc.render.resolution_x=640 if paired else 1280
 fullw=w*1.2
 aspect=sc.render.resolution_x/sc.render.resolution_y
 camdata.ortho_scale=max(fullw,(h*1.15)*aspect)
 cam.location=ctr+vd*.7;cam.rotation_euler=(ctr-cam.location).to_track_quat('-Z','Y').to_euler()
 camdata.clip_start=.001;camdata.clip_end=5
 if paired:
  mesh(V0,'bind display clone',face_ids=face_ids)
  sc.render.filepath=str(OUT/'renders/_parts'/(name[:-4]+'_BIND.png'));bpy.ops.render.render(write_still=True)
  clear();mesh(V,'posed display clone',face_ids=face_ids,strain=strain,highlight=highlight)
  sc.render.filepath=str(OUT/'renders/_parts'/(name[:-4]+'_POSED.png'));bpy.ops.render.render(write_still=True)
 else:
  mesh(V,'posed forensic clone',face_ids=face_ids,strain=strain,highlight=highlight)
  sc.render.filepath=str(OUT/'renders'/name);bpy.ops.render.render(write_still=True)
 manifest.append({'path':'renders/'+name,'bind_left_posed_right':paired,'plain_solid':strain is None and highlight is None,'positions':'actual evaluated R2','camera_direction':list(vd),'ortho_scale_m':camdata.ortho_scale})
 print('EVIDENCE',name,flush=True)
def area(v,p):
 a=Vector();
 for i in range(len(p)):a+=v[p[i]].cross(v[p[(i+1)%len(p)]])
 return a.length*.5
def outward_view(face_ids):
 n=Vector()
 for fi in face_ids:
  p=F[fi]
  for k in range(len(p)):n+=V0[p[k]].cross(V0[p[(k+1)%len(p)]])
 return n.normalized() if n.length>1e-12 else DORS
basearea=[area(V0,p) for p in F]
for cid,row in E['cases'].items():
 V=[Vector(v) for v in G['positions_world_m'][cid]];case=row['case'];d=case['digit'];key=d+'_'+case['joint'];ids=set(D['patches'][key]);patchv=set(ids)
 # Contact focus enlarges the joint close-up envelope, preserving its position.
 for cr in row['crossings']:
  if cr['hard_blocker'] or cr['acceptance'].startswith('KNOWN_'):
   for fi in cr['face_ids']:ids.update(F[fi])
 vd=(DORS+Vector((-.3,-.1,.2))).normalized() if d=='THUMB' else DORS
 save(cid+'_FULL_SOLID.png',V,range(len(V)),vd)
 save(cid+'_LOCAL_SOLID.png',V,ids,vd)
 save(cid+'_LOCAL_PALMAR_SOLID.png',V,ids,-vd)
 strain={'face_ratio':[area(V,p)/max(basearea[j],1e-18) for j,p in enumerate(F)]}
 save(cid+'_LOCAL_STRAIN.png',V,ids,vd,strain=strain)
 nailids=row['nails'][d]['vertex_ids'];save(cid+'_NAIL_SOLID.png',V,nailids,outward_view(row['nails'][d]['face_ids']))
 if d=='THUMB' or case['bone']=='INDEX_MCP_R':save(cid+'_CAP37_SOLID.png',V,cap['vertex_ids'],outward_view(cap['face_ids']))
 if row['crossings']:
  hi={fi:5 if cr['hard_blocker'] else 6 for cr in row['crossings'] for fi in cr['face_ids']}
  ci={v for fi in hi for v in F[fi]}
  save(cid+'_CROSSING_CONTEXT.png',V,ci,vd,highlight=hi)
 for cr in row['crossings']:
  if not cr['hard_blocker'] and not cr['acceptance'].startswith('KNOWN_'):continue
  fa,fb=cr['face_ids'];pairids=set(F[fa]+F[fb]);hi={fa:5,fb:6}
  name=cid+'_PAIR_'+str(fa)+'_'+str(fb)
  normal=(V[F[fa][1]]-V[F[fa][0]]).cross(V[F[fa][2]]-V[F[fa][0]]).normalized()
  side=(normal+vd*.55).normalized()
  save(name+'_ISOLATED.png',V,pairids,side,highlight=hi,face_ids=[fa,fb])
  save(name+'_CONTEXT.png',V,pairids,side,highlight=hi,paired=False)
dump('EVIDENCE_RENDER_MANIFEST_R1.json',{'render_count':len(manifest),'renders':manifest,'renderer':'Blender Workbench actual solid surfaces; smooth shading. Independent matched-camera panels prevent display clones occluding each other. Diagnostic colors separately marked.','threshold_colors_are_gate':False,'all_42_cases':True,'production_loaded_or_saved':False,'display_geometry_changes_affect_production':False,'panel_assembly_pending':True})
print('RENDERING COMPLETE',len(manifest),flush=True)
