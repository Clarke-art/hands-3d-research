"""Presentation-only camera correction and one visually prompted supplement.
Reads evaluated coordinates; never opens production blends or applies poses.
"""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
OUT=Path(__file__).resolve().parent
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def dump(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
G=read('DISPLAY_COORDINATES_R1.json');M=read('RENDER_MANIFEST_R1.json')
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1100;sc.render.resolution_y=1300
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sc.world=bpy.data.worlds.new('NEUTRAL_WORLD');sc.world.color=(.15,.17,.20);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL'
sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=True;sh.background_type='WORLD'
cd=bpy.data.cameras.new('DISPLAY_ONLY_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=5
cam=bpy.data.objects.new('DISPLAY_ONLY_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
for name,c in [('NEUTRAL_SOLID',(.66,.68,.71,1)),('NEUTRAL_NAIL',(.86,.88,.90,1))]:
    m=bpy.data.materials.new(name);m.diffuse_color=c
materials=[bpy.data.materials['NEUTRAL_SOLID'],bpy.data.materials['NEUTRAL_NAIL']]
D=Vector((.631289124,.775318801,-.0188387)).normalized();Z=Vector((0,0,1));aspect=1100/1300
active=None
def frame(V,ids,direction,padding=1.15,scale=None):
    d=direction.normalized();r=Z.cross(d).normalized();u=d.cross(r).normalized();ps=[V[i] for i in ids]
    x=[p.dot(r) for p in ps];y=[p.dot(u) for p in ps];z=[p.dot(d) for p in ps]
    center=r*((min(x)+max(x))/2)+u*((min(y)+max(y))/2)+d*((min(z)+max(z))/2)
    s=scale or max(max(x)-min(x),(max(y)-min(y))*aspect,.006)/aspect*padding
    return {'center':list(center),'direction':list(d),'ortho_scale_m':s}
def draw(cid,view,direction,ids=None,scale=None):
    global active
    if active:
        me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
    V=[Vector(v) for v in G['positions_world_m'][cid]];F=G['faces']
    me=bpy.data.meshes.new('FROZEN_EVALUATED_DISPLAY');me.from_pydata(V,[],F)
    for m in materials:me.materials.append(m)
    for p,mi in zip(me.polygons,G['material_indices']):p.use_smooth=True;p.material_index=1 if mi==1 else 0
    me.update();active=bpy.data.objects.new('FROZEN_EVALUATED_DISPLAY',me);sc.collection.objects.link(active)
    assert [list(p.vertices) for p in me.polygons]==F
    assert all(list(v.co)==G['positions_world_m'][cid][i] for i,v in enumerate(me.vertices))
    job=frame(V,ids or list(range(len(V))),direction,scale=scale)
    center=Vector(job['center']);d=Vector(job['direction']);cam.location=center+d*.7
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=job['ortho_scale_m']
    sh.studiolight_rotate_z=1.8 if view=='GRAZING' else .25
    fn=f'{cid}__{view}.png';sc.render.filepath=str(OUT/'renders'/fn);bpy.ops.render.render(write_still=True)
    M['renders']=[r for r in M['renders'] if r['path']!='renders/'+fn]
    M['renders'].append({'case_id':cid,'view':view,'path':'renders/'+fn,'camera':job,'resolution':[1100,1300],
        'studio_rotation_z':sh.studiolight_rotate_z,'ordinary_solid':True,'all_native_faces_present':True,'smooth_display_only':True,
        'production_mesh_materials_modified':False,'render_only_from_frozen_evaluated_coordinates':True,
        'posed_coordinate_sha256':hashlib.sha256(json.dumps(G['positions_world_m'][cid],separators=(',',':')).encode()).hexdigest(),
        'additional_pose_applications':0,'reason':'Resolve target occlusion in ordinary full-hand view' if view=='FULL_HAND_SOLID' else 'Visual prompt: INDEX_MCP45 first-web sharp edge'})
    dump('RENDER_MANIFEST_R1.json',M)
    print('DISPLAY_ONLY_RENDER',cid,view,flush=True)

top=(D*.65+Z*.75).normalized()
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args==['FULL_CONTEXT']:
    side=Vector(next(r for r in M['renders'] if r['view']=='RADIAL_SIDE')['camera']['direction'])
    draw('INDEX_MCP_45','ALTERNATE_FULL_HAND_SOLID',(D+side*.25+Z*.20).normalized(),scale=M['unified_full_hand_scale_m'])
elif args==['SUPPLEMENT']:
    # Actual saved local patch provides ordinary joint/web context, without metrics.
    root=OUT.parents[2]
    domain=json.loads((root/'production_spec/stage6_deformation/full_stage6a_requalification_after_donor_transfer_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json').read_text())
    ids=sorted(set(domain['patches']['INDEX_MCP'])|set(domain['FIRST_WEB21']))
    side=Vector(next(r for r in M['renders'] if r['view']=='RADIAL_SIDE')['camera']['direction'])
    close=(D+side*.25+Z*.20).normalized()
    draw('INDEX_MCP_45','LOCAL_CLOSE',close,ids=ids)
    draw('INDEX_MCP_45','ALTERNATE',(-D+side*.35).normalized(),ids=ids)
    draw('INDEX_MCP_45','GRAZING',close,ids=ids)
    dump('VISUALLY_PROMPTED_SUPPLEMENT_R1.json',{'case_id':'INDEX_MCP_45','prompt':'Apparent sharp fold at first-web edge in initial ordinary full-hand image.','images':['LOCAL_CLOSE','ALTERNATE','GRAZING'],'pose_applications':0,'source_blend_opens':0,'numerical_root_cause_or_hidden_crossing_analysis':False})
else:
    for cid in G['positions_world_m']:
        if cid!='ZERO' and not cid.startswith('THUMB_'):
            draw(cid,'FULL_HAND_SOLID',top,scale=M['unified_full_hand_scale_m'])
    dump('PRESENTATION_CAMERA_CORRECTION_R1.json',{'reason':'Initial side oblique occluded ring/little target joints; replace four-finger ordinary main images with distal/dorsal oblique.','pose_applications':0,'source_blend_opens':0,'replaced_main_images':12,'additional_forensic_images':0})
