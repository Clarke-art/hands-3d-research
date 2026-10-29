"""Nine fresh historical Stage6B poses on frozen repaired R2; minimum safety only."""
import sys
sys.dont_write_bytecode=True
import ast,json,hashlib,math
from pathlib import Path
import bpy
from mathutils import Vector,Quaternion,Matrix
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];S6=ROOT/'production_spec/stage6_deformation'
SOURCE=ROOT/'production_spec/stage5_production_rig/geometry_propagation_after_palmar_donor_restoration_r1/RIGHT_HAND_STAGE5B_R2_DONOR_TRANSFER_PALMAR_ROOT_GEOMETRY_R1.blend'
EXPECTED='90d3ebd1c1973f94020b66281781db481d5a366271a9d6aac6b921861e2b45aa'
WEIGHT='1d9437a10354cdd98a2b5cb5e43be8cfabc519e232235483a615e76898129f55'
MM=1000.
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def ref(p):return {'path':str(p),'sha256':sha(p)}
def reuse(path,names):
 nodes=[n for n in ast.parse(path.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),globals())
 return {'source':ref(path),'functions':names,'top_level_executed':False}
helpers=[reuse(S6/'stage6a/scripts/s6a_common.py',['reset_pose','evaluate','face_area']),
 reuse(S6/'stage6b/scripts/s6b_common.py',['set_local_axis_rotation','rotation_vector_to_quaternion']),
 reuse(S6/'palmar_root_targeted_visual_deformation_r1/run_and_render.py',['native_payload','state_zero'])]
stage6a_path=S6/'stage6a_human_visible_product_qualification_r1/STAGE6A_HUMAN_VISIBLE_PRODUCT_QUALIFICATION_R1_STATUS.json'
s6a=read(stage6a_path)
assert s6a['DEFORMATION_FINAL']=='HUMAN_PASS_STAGE6A' and s6a['VERDICT']=='PASS_STAGE6A_HUMAN_VISIBLE_PRODUCT_QUALIFICATION'
for receipt in s6a['receipts'].values():assert sha(receipt['path'])==receipt['sha256']
assert sha(SOURCE)==EXPECTED
matrix_path=S6/'stage6b/STAGE6B_CASE_MATRIX.json';vector_path=S6/'stage6b/STAGE6B_OPPOSITION_VECTOR_AUDIT.json'
matrix=read(matrix_path);vector=read(vector_path)
raw=vector['CMC_OPPOSITION_UNIT_ROTATION']['coefficients_local_XYZ'];twist=vector['axial_twist_qualification']['CMC_AXIAL_TWIST_SIGN']
assert twist=='-1';norm=math.sqrt(sum(x*x for x in raw));unit=[x/norm for x in raw]
cases=[{k:c[k] for k in ['case_id','kind','level','cmc_deg','mcp_deg','ip_deg','cmc_quaternion_local']} for c in matrix['cases']]
assert len(cases)==9 and [c['case_id'] for c in cases]==['CMC_OPP_10','CMC_OPP_20','CMC_OPP_30','CMC_MCP_L1','CMC_MCP_L2','CMC_MCP_L3','FULL_OPP_L1','FULL_OPP_L2','FULL_OPP_L3']
for c in cases:
 c['rotation_semantics']={'CMC':'Single bone-local XYZ exponential-map quaternion from stored normalized opposition vector; no Euler sequence or additional twist-sign multiplication.','MCP':'bone_local_X negative flexion angle','IP':'bone_local_X negative flexion angle'}
 c['purpose']='DIAGNOSTIC_FULL_CHAIN_OPPOSITION_STRESS_CASE' if c['case_id']=='FULL_OPP_L3' else 'DIAGNOSTIC_STRESS_TEST_POSE'
 c['teaching_pose_or_human_ROM_definition']=False
dump('STAGE6B_CURRENT_9_CASE_MATRIX_R1.json',{'source_pose_definition':ref(matrix_path),'source_opposition_authority':ref(vector_path),'stored_authority_raw':raw,'normalized_authority_as_historical_execution':unit,'twist_sign':twist,'cases':cases,'formal_count':9,'angles_modified_for_pass':False,'fresh_asset':ref(SOURCE)})
floor=read(S6/'whole_hand_surface_integrity_baseline_r1/MINIMUM_MACHINE_SAFETY_R1.json')['thresholds']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
ob=next(o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)==3416);rig=bpy.data.objects['RIGHT_HAND_PRODUCTION_RIG'];MW=ob.matrix_world.copy()
original=native_payload(ob,rig);names={g.index:g.name for g in ob.vertex_groups}
weights=[{names[g.group]:float(g.weight) for g in v.groups if g.weight>0} for v in ob.data.vertices]
weight_hash=digest(weights)
assert weight_hash==WEIGHT and len(rig.data.bones)==21
dump('PREREQUISITE_VERIFICATION_R1.json',{'status':'PASS','Stage6A_Human_PASS':ref(stage6a_path),'closure_receipts_hash_match':True,'asset':ref(SOURCE),'weight_hash_actual':weight_hash,'weight_hash_expected':WEIGHT,'weight_hash_match':True,'helpers':helpers,'opposition_authority_reused':ref(vector_path),'pose_definition_reused':ref(matrix_path),'no_axis_probe_or_sign_search':True})
reset_pose(rig);bpy.context.view_layer.update();VB,F=evaluate(ob,MW);assert state_zero(rig)
E=[list(e.vertices) for e in ob.data.edges];A0=[face_area(VB,p) for p in F];L0=[(VB[a]-VB[b]).length for a,b in E];mi=[p.material_index for p in ob.data.polygons]
assert all(a>floor['collapse_area_m2_le'] for a in A0) and all(l>floor['degenerate_edge_m_le'] for l in L0)
raw_zero=max((VB[i]<REDACTED_EMAIL>).length*MM for i,v in enumerate(ob.data.vertices));assert raw_zero<=floor['zero_mm']
sc=bpy.data.scenes.new('UNSAVED_STAGE6B_DISPLAY');sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sc.world=bpy.data.worlds.new('NEUTRAL_WORLD');sc.world.color=(.15,.17,.20);sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.25;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=False;sh.show_specular_highlight=True;sh.background_type='WORLD'
cd=bpy.data.cameras.new('DISPLAY_CAMERA');cd.type='ORTHO';cd.clip_start=.001;cd.clip_end=5
cam=bpy.data.objects.new('DISPLAY_CAMERA',cd);sc.collection.objects.link(cam);sc.camera=cam
mats=[]
for n,col in [('NEUTRAL_SOLID',(.66,.68,.71,1)),('NEUTRAL_NAIL',(.86,.88,.90,1))]:
 mat=bpy.data.materials.new(n);mat.diffuse_color=col;mats.append(mat)
D=Vector((.631289124,.775318801,-.0188387)).normalized();Z=Vector((0,0,1));radial=Z.cross(D).normalized()
th=<REDACTED_EMAIL>['THUMB_MCP_R'].head_local;li=<REDACTED_EMAIL>['LITTLE_MCP_R'].head_local
if (th-li).dot(radial)<0:radial=-radial
domains=read(S6/'full_stage6a_requalification_after_donor_transfer_r1/LOCAL_PATCH_AND_MEASUREMENT_DOMAINS_R1.json')
thumb_ids=sorted(i for i,w in enumerate(weights) if any(k.startswith('THUMB_') for k in w))
web_ids=domains['FIRST_WEB21'];palm_ids=sorted(set(web_ids)|set(domains['patches']['THUMB_MCP'])|set(range(3348,3364)))
all_ids=list(range(len(VB)))
families={'FULL_HAND_SOLID':{'direction':(D*.65+Z*.75).normalized(),'ids':all_ids,'size':(1100,1300)},
 'THUMB_PALMAR_OBLIQUE_SOLID':{'direction':(-D*.85+radial*.30+Z*.12).normalized(),'ids':sorted(set(thumb_ids)|set(web_ids)),'size':(1200,1000)},
 'THUMB_CLOSE':{'direction':(-D*.75+radial*.55+Z*.10).normalized(),'ids':thumb_ids,'size':(1100,1100)},
 'FIRST_WEB_CLOSE':{'direction':(-D*.85+radial*.30+Z*.12).normalized(),'ids':web_ids,'size':(1100,1100)},
 'PALMAR_CLOSE':{'direction':-D,'ids':palm_ids,'size':(1100,1100)}}
def frame(V,ids,direction,size,padding=1.30,scale=None):
 d=Vector(direction).normalized();r=Z.cross(d).normalized();u=d.cross(r).normalized();ps=[V[i] for i in ids]
 x=[p.dot(r) for p in ps];y=[p.dot(u) for p in ps];z=[p.dot(d) for p in ps];aspect=size[0]/size[1]
 center=r*((min(x)+max(x))/2)+u*((min(y)+max(y))/2)+d*((min(z)+max(z))/2)
 width=max(max(x)-min(x),(max(y)-min(y))*aspect,.006)/min(1.,aspect)*padding
 return {'center':list(center),'direction':list(d),'ortho_scale_m':scale or width,'resolution':list(size)}
for f in families.values():f['scale']=frame(VB,f['ids'],f['direction'],f['size'])['ortho_scale_m']
families['FIRST_WEB_CLOSE']['scale']=max(families['FIRST_WEB_CLOSE']['scale'],.075)
families['PALMAR_CLOSE']['scale']=max(families['PALMAR_CLOSE']['scale'],.115)
(OUT/'renders').mkdir(exist_ok=True);manifest=[];active=None
def display(V,P):
 global active
 if active:
  me=active.data;bpy.data.objects.remove(active,do_unlink=True);bpy.data.meshes.remove(me)
 me=bpy.data.meshes.new('EVALUATED_DISPLAY_COPY');me.from_pydata(V,[],P)
 for m in mats:me.materials.append(m)
 for p,idx in zip(me.polygons,mi):p.use_smooth=True;p.material_index=1 if idx==1 else 0
 me.update();active=bpy.data.objects.new('EVALUATED_DISPLAY_COPY',me);sc.collection.objects.link(active)
 assert [tuple(p.vertices) for p in me.polygons]==P
def draw(cid,view,V,P,job):
 display(V,P);center=Vector(job['center']);d=Vector(job['direction']);cam.location=center+d*.7
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=job['ortho_scale_m']
 sc.render.resolution_x,sc.render.resolution_y=job['resolution'];sc.render.filepath=str(OUT/'renders'/f'{cid}__{view}.png')
 bpy.ops.render.render(write_still=True,scene=sc.name)
 manifest.append({'case_id':cid,'view':view,'path':f'renders/{cid}__{view}.png','camera':job,'ordinary_solid':True,'all_native_faces_present':True,'smooth_display_copy_only':True,'source_material_or_geometry_modified':False,'rendered_before_pose_reset':True,'lighting':'WORKBENCH STUDIO; cavity OFF; neutral material'})
 dump('RENDER_MANIFEST_R1.json',{'renders':manifest,'camera_family_scale_fixed':{n:f['scale'] for n,f in families.items()},'production_saves':0})
 print('RENDER',cid,view,flush=True)
dg=read(ROOT/'production_spec/stage4_blender/stage4c_donor_transfer_r1/APPLICATION_MATCHED_REVIEW_GEOMETRY_R1.json')
draw('ZERO','DORSAL54_SENTINEL',VB,F,{'center':[v/1000 for v in dg['frame']['origin_world_mm']],'direction':list(D),'ortho_scale_m':.05,'resolution':[1100,1100]})
palcore=read(ROOT/'audits/palmar_digit_root_local_donor_shape_restoration_design_r1/PALMAR_ROOT_DEFECT_CORE_R1.json');palids=sorted(set(palcore['visible_upper_box_hit_vertex_ids'])|set(range(3348,3364)))
draw('ZERO','PALMAR16_SENTINEL',VB,F,frame(VB,palids,-D,(1100,1100),scale=.07))
rows=[];resets=[];coords={'ZERO':[list(v) for v in VB]}
for c in cases:
 cid=c['case_id'];reset_pose(rig);bpy.context.view_layer.update();Vz,Pz=evaluate(ob,MW)
 pre=max((a-b).length*MM for a,b in zip(Vz,VB));assert state_zero(rig) and pre<=floor['zero_mm'] and Pz==F
 q,mag=rotation_vector_to_quaternion(Vector(unit)*math.radians(c['cmc_deg']))
 rig.pose.bones['THUMB_CMC_R'].rotation_quaternion=q
 if c['mcp_deg']:set_local_axis_rotation(rig,'THUMB_MCP_R',-c['mcp_deg'])
 if c['ip_deg']:set_local_axis_rotation(rig,'THUMB_IP_R',-c['ip_deg'])
 bpy.context.view_layer.update();V,P=evaluate(ob,MW);coords[cid]=[list(v) for v in V]
 views=['FULL_HAND_SOLID','THUMB_PALMAR_OBLIQUE_SOLID']+(['THUMB_CLOSE','FIRST_WEB_CLOSE','PALMAR_CLOSE'] if c['level']==3 else [])
 for view in views:
  f=families[view];draw(cid,view,V,P,frame(V,f['ids'],f['direction'],f['size'],scale=f['scale']))
 # Minimum catastrophic-safety checks only; no crossing census or normal audit.
 finite=sum(not math.isfinite(float(x)) for p in V for x in p);areas=[face_area(V,p) for p in P];lengths=[(V[a]-V[b]).length for a,b in E]
 collapse=sum(a<=floor['collapse_area_m2_le'] or a/a0<=floor['collapse_ratio_le'] for a,a0 in zip(areas,A0))
 degenerate=sum(l<=floor['degenerate_edge_m_le'] for l in lengths)
 severe=sum(l0*MM>=floor['severe_bind_mm_ge'] and l/l0>floor['severe_ratio_gt'] for l,l0 in zip(lengths,L0))
 activebones=[b.name for b in rig.pose.bones if abs(b.rotation_quaternion.angle)>1e-7]
 expectedbones=['THUMB_CMC_R']+(['THUMB_MCP_R'] if c['mcp_deg'] else [])+(['THUMB_IP_R'] if c['ip_deg'] else [])
 rig_channels=set(activebones)==set(expectedbones) and rig.pose.bones['WRIST_R'].matrix_basis==Matrix.Identity(4)
 row={'case_id':cid,'NaN_Inf_count':finite,'collapsed_faces':collapse,'degenerate_edges':degenerate,'obvious_severe_stretch_count':severe,'topology_exact':P==F,'only_authorized_channels_active':rig_channels,'active_bones':activebones,'automatic_minimum_status':'PASS' if not(finite or collapse or degenerate or severe) and P==F and rig_channels else 'FAIL','ordinary_solid_gross_surface_screen':'PENDING_VISUAL_INSPECTION','actual_CMC_quaternion_local':list(q),'angles_unchanged':True}
 reset_pose(rig);bpy.context.view_layer.update();Vr,Pr=evaluate(ob,MW);post=max((a-b).length*MM for a,b in zip(Vr,VB))
 reset={'case_id':cid,'pre_zero_error_mm':pre,'post_zero_error_mm':post,'all21_channels_zero':state_zero(rig),'status':'PASS' if pre<=floor['zero_mm'] and post<=floor['zero_mm'] and state_zero(rig) and Pr==F else 'FAIL'}
 resets.append(reset);row['ZERO_restore']=reset['status'];rows.append(row)
 dump('STAGE6B_MINIMUM_MACHINE_AUTOMATIC_R1.json',{'thresholds':floor,'source_thresholds':ref(S6/'whole_hand_surface_integrity_baseline_r1/MINIMUM_MACHINE_SAFETY_R1.json'),'rows':rows,'automatic_status':'PASS' if all(x['automatic_minimum_status']=='PASS' and x['ZERO_restore']=='PASS' for x in rows) else 'FAIL','minimum_visual_gates_pending':True,'hidden_crossing_census':False})
 dump('STAGE6B_ZERO_RESET_R1.json',{'status':'PASS' if all(x['status']=='PASS' for x in resets) else 'FAIL','rows':resets,'final_pose':'ZERO / RSSF','raw_zero_error_mm':raw_zero,'procedure':'fresh RESET ZERO -> apply existing case -> evaluate -> render -> minimum safety -> RESET ZERO'})
 print('CASE_DONE',cid,row['automatic_minimum_status'],reset['status'],flush=True);assert reset['status']=='PASS'
assert state_zero(rig) and native_payload(ob,rig)==original and sha(SOURCE)==EXPECTED
dump('DISPLAY_COORDINATES_R1.json',{'positions_world_m':coords,'faces':[list(f) for f in F],'material_indices':mi,'display_families':{n:{'direction':list(f['direction']),'scale':f['scale'],'resolution':list(f['size'])} for n,f in families.items()}})
dump('SOURCE_PROTECTION_R1.json',{'source':ref(SOURCE),'source_sha256_before':EXPECTED,'source_sha256_after':sha(SOURCE),'weight_hash_before':weight_hash,'weight_hash_after':digest(weights),'native_payload_hash_before':digest(original),'native_payload_hash_after':digest(native_payload(ob,rig)),'native_payload_unchanged':True,'final_pose':'ZERO / RSSF','GEOMETRY_WRITES':0,'WEIGHT_WRITES':0,'RIG_WRITES':0,'JOINT_WRITES':0,'MODIFIER_WRITES':0,'BLEND_PRODUCTION_SAVES':0,'pose_case_applications':9,'Full42_runs':0,'crossing_classifier_runs':0,'CMC_axis_probe_runs':0,'R3_runs':0,'true_cap_runs':0})
print('FRESH_STAGE6B_9_COMPLETE; native asset unchanged; ZERO restored',flush=True)
