"""Read-only product-surface baseline: ZERO + 14 existing Stage6A 45-degree cases.
No production saves, solvers, crossing census, or historical audits.
"""
import sys
sys.dont_write_bytecode = True
import ast, hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion, Matrix

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
S6 = ROOT / 'production_spec/stage6_deformation'
SOURCE = ROOT / 'production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'
EXPECTED = '90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa'
MM = 1000.
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def dump(n,x): (OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def reuse(path,names):
    nodes=[n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),globals())
    return {'path':str(path),'sha256':sha(path),'functions':names,'top_level_executed':False}

provenance = [reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','set_joint_rotation','evaluate','face_area']),
              reuse(S6/'palmar_root_targeted_visual_deformation_r1/run_and_render.py',['native_payload','state_zero'])]
floor = read(S6/'palmar_root_targeted_visual_deformation_r1/MINIMUM_SAFETY_PROCEDURE_R1.json')['automatic_gates']
matrix_path = S6/'full_stage6a_requalification_r1/FULL_STAGE6A_CASE_MATRIX_R1.json'
cases = [c for c in read(matrix_path)['cases'] if c['angle_deg']==45]
assert len(cases)==14 and len({c['bone'] for c in cases})==14
assert all(c['axis']=='bone_local_X' and c['sign']==-1 and c['applied_rotation_deg']==-45 for c in cases)
for c in cases:
    c['stage6a_source_case_id']=c['case_id']
    c['case_id']=c['digit']+'_'+c['joint']+'_45'
assert sha(SOURCE)==EXPECTED
(OUT/'renders').mkdir(exist_ok=True)
dump('AUTHORIZED_POSE45_AND_INPUT_R1.json',{'source_asset':str(SOURCE),'source_sha256':EXPECTED,'case_matrix':str(matrix_path),'case_matrix_sha256':sha(matrix_path),'cases':cases,'thresholds':floor,'helper_reuse':provenance,'WRIST_R':'LOCKED_ZERO','THUMB_CMC_R':'LOCKED_ZERO','policy':'HUMAN_VISIBLE_PRODUCT_QUALITY_FIRST'})

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
ob=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)==3416)
rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG']; MW=ob.matrix_world.copy()
original=native_payload(ob,rig)
original_hash=digest(original)
reset_pose(rig);bpy.context.view_layer.update()
VB,F=evaluate(ob,MW)
assert state_zero(rig)
E=[list(e.vertices) for e in ob.data.edges]
A0=[face_area(VB,f) for f in F]
L0=[(VB[a]-VB[b]).length for a,b in E]
mi=[f.material_index for f in ob.data.polygons]
raw_zero=max((VB[i]-(<REDACTED_EMAIL>)).length*MM for i,v in enumerate(ob.data.vertices))
assert raw_zero<=floor['zero_mm']
assert all(a>floor['collapse_area_m2_le'] for a in A0)
assert all(l>floor['degenerate_edge_m_le'] for l in L0)

# Separate scene holds an evaluated display copy. Production mesh/materials are untouched.
sc=bpy.data.scenes.new('UNSAVED_WHOLE_HAND_REVIEW')
sc.render.engine='BLENDER_WORKBENCH'
sc.render.resolution_x=1100;sc.render.resolution_y=1300;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.world=bpy.data.worlds.new('UNSAVED_NEUTRAL_WORLD');sc.world.color=(.15,.17,.20)
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL'
sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=True;sh.background_type='WORLD'
cd=bpy.data.cameras.new('UNSAVED_REVIEW_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=5
cam=bpy.data.objects.new('UNSAVED_REVIEW_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
clay=bpy.data.materials.new('UNSAVED_NEUTRAL_SOLID');clay.diffuse_color=(.66,.68,.71,1)
nail=bpy.data.materials.new('UNSAVED_NEUTRAL_NAIL');nail.diffuse_color=(.86,.88,.90,1)
D=Vector((.631289124,.775318801,-.0188387)).normalized()
Z=Vector((0,0,1));side=Z.cross(D).normalized()
th=<REDACTED_EMAIL>['THUMB_MCP_R'].head_local
li=<REDACTED_EMAIL>['LITTLE_MCP_R'].head_local
if (th-li).dot(side)<0: side=-side
views={'DORSAL_FULL':D,'PALMAR_FULL':-D,'RADIAL_SIDE':side,'ULNAR_SIDE':-side,
       'THUMB_WEB_OBLIQUE':(-D*.7+side*.7+Z*.18).normalized(),
       'FINGERTIP_DISTAL_OBLIQUE':(D*.65+Z*.75).normalized()}
primary=(D+side*.25+Z*.20).normalized()
aspect=sc.render.resolution_x/sc.render.resolution_y
def framing(V,ids,direction,padding=1.14):
    d=Vector(direction).normalized();r=Z.cross(d).normalized();u=d.cross(r).normalized()
    ps=[V[i] for i in ids];xx=[p.dot(r) for p in ps];yy=[p.dot(u) for p in ps];zz=[p.dot(d) for p in ps]
    center=r*((min(xx)+max(xx))/2)+u*((min(yy)+max(yy))/2)+d*((min(zz)+max(zz))/2)
    scale=max(max(xx)-min(xx),(max(yy)-min(yy))*aspect,.006)/min(1.,aspect)*padding
    return {'center':list(center),'direction':list(d),'ortho_scale_m':scale}
full_ids=list(range(len(VB)))
jobs={k:framing(VB,full_ids,d) for k,d in views.items()}
jobs['FULL_HAND_SOLID']=framing(VB,full_ids,primary,1.20)
unified_scale=max(j['ortho_scale_m'] for j in jobs.values())
for j in jobs.values():j['ortho_scale_m']=unified_scale
manifest=[];active=None
def display(V,P):
    global active
    if active:
        me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
    me=bpy.data.meshes.new('UNSAVED_EVALUATED_DISPLAY');me.from_pydata(V,[],P)
    me.materials.append(clay);me.materials.append(nail)
    for f,m in zip(me.polygons,mi):f.use_smooth=True;f.material_index=1 if m==1 else 0
    me.update();active=bpy.data.objects.new('UNSAVED_EVALUATED_DISPLAY',me);sc.collection.objects.link(active)
    assert [tuple(p.vertices) for p in me.polygons]==P
def draw(cid,view,V,P,job):
    display(V,P)
    center=Vector(job['center']);direction=Vector(job['direction'])
    cam.location=center+direction*.7;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cd.ortho_scale=job['ortho_scale_m'];sh.studiolight_rotate_z=1.8 if view=='GRAZING' else .25
    fn=f'{cid}__{view}.png';sc.render.filepath=str(OUT/'renders'/fn)
    bpy.ops.render.render(write_still=True,scene=sc.name)
    manifest.append({'case_id':cid,'view':view,'path':'renders/'+fn,'camera':job,'resolution':[1100,1300],
                     'studio_rotation_z':sh.studiolight_rotate_z,'ordinary_solid':True,'all_native_faces_present':True,
                     'smooth_display_only':True,'production_mesh_materials_modified':False})
    dump('RENDER_MANIFEST_R1.json',{'renders':manifest,'unified_full_hand_scale_m':unified_scale,'native_face_count':len(F),'production_saves':0})
    print('RENDER',cid,view,flush=True)

for view,job in jobs.items():
    if view!='FULL_HAND_SOLID': draw('ZERO',view,VB,F,job)
# Two existing repair areas are visual sentinels only, without quantification.
dg=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')
dj={'center':[x/1000 for x in dg['frame']['origin_world_mm']],'direction':list(D),'ortho_scale_m':.05}
pc=read(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_DEFECT_CORE_R1.json')
pn=read(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_EXCLUDED_NORMAL_CONTEXT_R1.json')
pal_ids=sorted(set(pc['visible_upper_box_hit_vertex_ids'])|set(range(3348,3364))|set(pn['vertex_ids']))
pj=framing(VB,pal_ids,-D,1.4)
pj['ortho_scale_m']=max(pj['ortho_scale_m'],.055)
draw('ZERO','DORSAL54_SENTINEL',VB,F,dj)
draw('ZERO','PALMAR16_SENTINEL',VB,F,pj)

coordinates={'ZERO':[list(v) for v in VB]};rows=[];resets=[]
for c in cases:
    cid=c['case_id'];reset_pose(rig);bpy.context.view_layer.update()
    Vz,Pz=evaluate(ob,MW);pre=max((a-b).length*MM for a,b in zip(Vz,VB))
    assert state_zero(rig) and pre<=floor['zero_mm'] and Pz==F
    set_joint_rotation(rig,c['bone'],c['applied_rotation_deg']);bpy.context.view_layer.update()
    V,P=evaluate(ob,MW)
    finite=sum(not math.isfinite(float(x)) for v in V for x in v)
    areas=[face_area(V,f) for f in P];lengths=[(V[a]-V[b]).length for a,b in E]
    collapsed=sum(a<=floor['collapse_area_m2_le'] or a/a0<=floor['collapse_ratio_le'] for a,a0 in zip(areas,A0))
    degenerate=sum(l<=floor['degenerate_edge_m_le'] for l in lengths)
    severe=sum(l0*MM>=floor['severe_bind_mm_ge'] and l/l0>floor['severe_ratio_gt'] for l,l0 in zip(lengths,L0))
    active_bones=[b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle)>1e-7]
    locked=all(rig.pose.bones[n].matrix_basis==Matrix.Identity(4) for n in ['WRIST_R','THUMB_CMC_R'])
    row={'case_id':cid,'NaN_Inf_count':finite,'collapsed_faces':collapsed,'degenerate_edges':degenerate,
         'obvious_severe_stretch_count':severe,'only_authorized_bone_rotated':active_bones==[c['bone']],
         'locked_bones_zero':locked,'topology_exact':P==F,'active_bones':active_bones,
         'automatic_minimum_gate':'PASS' if not(finite or collapsed or degenerate or severe) and locked and active_bones==[c['bone']] and P==F else 'FAIL',
         'obvious_penetration_and_gross_non_target_screen':'PENDING_ORDINARY_SOLID_INSPECTION'}
    coordinates[cid]=[list(v) for v in V]
    draw(cid,'FULL_HAND_SOLID',V,P,jobs['FULL_HAND_SOLID'])
    reset_pose(rig);bpy.context.view_layer.update();Vr,Pr=evaluate(ob,MW)
    post=max((a-b).length*MM for a,b in zip(Vr,VB))
    reset={'case_id':cid,'pre_zero_error_mm':pre,'post_zero_error_mm':post,'all_channels_zero':state_zero(rig),
           'status':'PASS' if pre<=floor['zero_mm'] and post<=floor['zero_mm'] and state_zero(rig) and Pr==F else 'FAIL'}
    resets.append(reset);row['ZERO_restore']=reset['status'];rows.append(row)
    dump('MINIMUM_MACHINE_AUTOMATIC_R1.json',{'thresholds':floor,'rows':rows,'raw_zero_error_mm':raw_zero,
         'automatic_status':'PASS' if all(x['automatic_minimum_gate']=='PASS' and x['ZERO_restore']=='PASS' for x in rows) else 'FAIL',
         'visual_machine_gate':'PENDING_ORDINARY_SOLID_INSPECTION','hidden_crossing_census':False})
    dump('ZERO_RESET_R1.json',{'status':'PASS' if all(x['status']=='PASS' for x in resets) else 'FAIL','rows':resets,'final_pose':'ZERO'})
    print('CASE_DONE',cid,row['automatic_minimum_gate'],reset['status'],flush=True)
    assert reset['status']=='PASS'
assert state_zero(rig) and native_payload(ob,rig)==original and sha(SOURCE)==EXPECTED
dump('DISPLAY_COORDINATES_R1.json',{'positions_world_m':coordinates,'faces':[list(f) for f in F],'material_indices':mi})
dump('SOURCE_PROTECTION_R1.json',{'source':str(SOURCE),'source_sha256_before':EXPECTED,'source_sha256_after':sha(SOURCE),
     'native_payload_hash_before':original_hash,'native_payload_hash_after':digest(native_payload(ob,rig)),'native_payload_unchanged':True,
     'final_pose':'ZERO','GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'RIG_WRITES':0,'JOINT_WRITES':0,'BLEND_PRODUCTION_SAVES':0,
     'temporary_authorized_pose_applications':14,'FULL42_runs':0,'Stage6B_runs':0,'hidden_crossing_census_runs':0})
print('BASELINE_RENDER_COMPLETE: 6 static + 2 sentinels + 14 full poses; source unchanged; ZERO restored',flush=True)
