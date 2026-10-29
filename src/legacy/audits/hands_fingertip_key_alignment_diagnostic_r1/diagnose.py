import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter()
save_new=save
def save(name,value):
    if (OUT/name).exists():return
    save_new(name,value)
sc,rig,mesh,left,lrig=s.open_scene(SOURCE)
sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']]
before=s.protected_state();native_before={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
cam=sc.camera;camera_matrix=np.array(cam.matrix_world);assert cam.data.type=='ORTHO'
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
vf=np.array([list(v) for v in cam.data.view_frame(scene=sc)]);vlo=vf[:,:2].min(0);vhi=vf[:,:2].max(0)
def project(V):
    v=(np.c_[V,np.ones(len(V))]@np.linalg.inv(camera_matrix).T)[:,:2]
    uv=(v-vlo)/(vhi-vlo);return np.c_[uv[:,0]*1280,(1-uv[:,1])*720].tolist()
def world_key(V,key):
    pv=np.array(key['press_pivot']);return (np.asarray(V)-pv)@c.axisrot(s.keyangle(key),key['press_axis']).T+pv
def surfaces(key):
    return [dict(rest_m=a,pixels=project(world_key([[a['xmin'],a['ymin'],a['z']],[a['xmax'],a['ymin'],a['z']],[a['xmax'],a['ymax'],a['z']],[a['xmin'],a['ymax'],a['z']]],key))) for a in key['key_top_playable_surface']]
RNOTES=[n for n in NOTES if n['hand']=='R'];assert len(RNOTES)==16
assert all(n['midi_note']==KEYS[n['key_index']]['midi_note'] and n['note_name']==KEYS[n['key_index']]['note_name'] and 1<=n['finger']<=5 for n in RNOTES)
def role(t,finger):
    ns=[n for n in RNOTES if n['finger']==finger]
    for r,pred in [('ACTIVE',lambda n:n['note_on']<=t<n['note_off']),('RELEASE',lambda n:n['note_off']<=t<n['note_off']+.04),('PREPARE',lambda n:n['note_on']-.18<=t<n['note_on'])]:
        a=[n for n in ns if pred(n)]
        if a:return dict(role=r,event=a[0]['note_id'],key=a[0]['note_name'])
    return dict(role='IDLE',event=None,key=None)
# Fixed anatomical skin samples derived once from canonical rest geometry.
rv=np.array([list((rig.matrix_world.inverted()@mesh.matrix_world)@v.co) for v in mesh.data.vertices])
caps={};term={};padpatch={};axisdata={}
for i,d in enumerate(DIGITS):
    marker=c.MARKERS['R'][i];tip=np.array(rig.data.bones[marker['semantic_tip']].head_local)
    dip=np.array(rig.data.bones[marker['distal_frame']].head_local);a=tip-dip;a/=np.linalg.norm(a)
    ids=np.array(ROI[d]['vertices'],int);along=(rv-tip)@a
    cap=ids[along[ids]>=-.005];assert len(cap)>3
    caps[d]=cap;term[d]=int(ids[np.argmax(along[ids])]);padpatch[d]=ids[np.linalg.norm(rv[ids]-rv[marker['mesh_vertex']],axis=1)<=.007]
    axisdata[d]=dict(canonical_tip=tip,canonical_dip=dip,axis=a)
black=[k for k in KEYS if k['color']=='BLACK']
def finger(V,key,f):
    d=DIGITS[f-1];mk=c.MARKERS['R'][f-1];p=V[mk['mesh_vertex']];local=s.key_local(V,key);q=local[mk['mesh_vertex']]
    ss=key['key_top_playable_surface'];si=int(np.argmin([np.linalg.norm(q[:2]-np.clip(q[:2],[a['xmin'],a['ymin']],[a['xmax'],a['ymax']])) for a in ss]));a=ss[si]
    # Distance to true union boundary: remove the internal join between front/rear rectangles.
    edges=[]
    for b in ss:
        edges.extend([[[b['xmin'],b['ymin']],[b['xmax'],b['ymin']]],[[b['xmax'],b['ymin']],[b['xmax'],b['ymax']]],[[b['xmax'],b['ymax']],[b['xmin'],b['ymax']]],[[b['xmin'],b['ymax']],[b['xmin'],b['ymin']]]])
    dist=[]
    for aa,bb in edges:
        aa=np.array(aa);bb=np.array(bb);v=bb-aa;u=np.clip((q[:2]-aa)@v/(v@v),0,1);x=aa+u*v
        # shared front/rear seam is not an exterior boundary
        if any(b['xmin']+1e-8<x[0]<b['xmax']-1e-8 and abs(x[1]-b['ymin'])<1e-8 and abs(x[1]-a0['ymax'])<1e-8 for b in ss for a0 in ss if b is not a0):continue
        dist.append(float(np.linalg.norm(q[:2]-x)*1000))
    lateral=min(q[0]-a['xmin'],a['xmax']-q[0])*1000
    cap=local[caps[d]];inside=np.zeros(len(cap),bool)
    for b in ss:inside|=(cap[:,0]>=b['xmin'])&(cap[:,0]<=b['xmax'])&(cap[:,1]>=b['ymin'])&(cap[:,1]<=b['ymax'])
    virtual=np.array(<REDACTED_EMAIL>[mk['distal_frame']].matrix@Vector(mk['local_pad_point']))
    tip=V[term[d]];dip=np.array(<REDACTED_EMAIL>[mk['distal_frame']].head);bt=np.array(<REDACTED_EMAIL>[mk['semantic_tip']].head);axis=bt-dip;axis/=np.linalg.norm(axis)
    nb=[]
    for b in black:
        bp=s.key_local(V[[mk['mesh_vertex'],term[d]]],b);r=b['key_top_playable_surface'][0]
        distances=np.linalg.norm(bp[:,:2]-np.clip(bp[:,:2],[r['xmin'],r['ymin']],[r['xmax'],r['ymax']]),axis=1)*1000
        nb.append(dict(key=b['note_name'],pad_xy_edge_distance_mm=float(distances[0]),terminal_xy_edge_distance_mm=float(distances[1])))
    return dict(finger=f,digit=d,key=key['note_name'],contact=s.contact(V,key,'R',f),pad_world_m=p,pad_key_rest_m=q,virtual_marker_world_m=virtual,virtual_vs_skin_mm=float(np.linalg.norm(virtual-p)*1000),terminal_vertex=term[d],terminal_world_m=tip,terminal_key_rest_m=local[term[d]],
      pad_surface_index=si,pad_lateral_margin_mm=float(lateral),pad_union_boundary_distance_mm=min(dist),pad_x_fraction=float((q[0]-a['xmin'])/(a['xmax']-a['xmin'])),distal_cap_vertices=len(cap),distal_cap_xy_outside_fraction=float(1-inside.mean()),
      pad_to_terminal_xy_mm=float(np.linalg.norm((tip-p)[:2])*1000),distal_axis_world=axis,distal_axis_to_key_plane_deg=float(np.degrees(np.arcsin(abs(axis[2])))),nearest_black=sorted(nb,key=lambda n:n['terminal_xy_edge_distance_mm'])[:2],
      pad_pixel=project([p])[0],terminal_pixel=project([tip])[0],cap_pixels=project(V[caps[d]]),pad_patch_pixels=project(V[padpatch[d]]),target_surfaces=surfaces(key))

# Validate actual frozen key components, not just table boxes.
dm=types.ModuleType('existing_depth_math');pp=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py';exec(compile(safe(pp).read_text(encoding='utf8'),str(pp),'exec'),dm.__dict__);dm.selftest()
comps=[]
for key,g,pl in s.registered_components():
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
    me=ob.data;me.calc_loop_triangles();vv=np.array([list(v.co) for v in me.vertices]);tt=np.array([list(t.vertices) for t in me.loop_triangles],int);lp,_=dm.planes_from_mesh(vv,tt)
    comps.append((key,g,ob.name,vv,tt,lp))
def actual(comp):
    key,g,oname,vv,tt,lp=comp;ob=bpy.data.objects[oname];M=np.array(ob.matrix_world);kv=(np.c_[vv,np.ones(len(vv))]@M.T)[:,:3];pp=np.c_[lp[:,:3],-lp[:,3]]@np.linalg.inv(M);norm=np.linalg.norm(pp[:,:3],axis=1);P=np.c_[pp[:,:3]/norm[:,None],-pp[:,3]/norm]
    registered=world_key(g['vertices'],key);assert np.max(abs(kv-registered))<1e-6
    return kv,P
def light_black(V,d):
    ids=np.array(ROI[d]['vertices'],int);rows=[]
    for comp in comps:
        key=comp[0]
        if key['color']!='BLACK':continue
        kv,P=actual(comp)
        if np.any(V[ids].max(0)<kv.min(0)) or np.any(V[ids].min(0)>kv.max(0)):continue
        depth=np.maximum(0,np.min(P[:,3]-V[ids]@P[:,:3].T,axis=1))*1000;ix=int(np.argmax(depth))
        if depth[ix]>1e-6:rows.append(dict(key=key['note_name'],depth_mm=float(depth[ix]),vertex=int(ids[ix]),world_m=V[ids[ix]]))
    return sorted(rows,key=lambda r:-r['depth_mm'])
samples=[]
for n in RNOTES:
    for phase,t in [('ON',n['note_on']),('HOLD',(n['note_on']+n['note_off'])/2),('PRE_OFF',n['note_off']-.001)]:
        c.settime(sc,t);V,T,F=s.coords_tri(mesh)
        samples.append(dict(event=n['note_id'],note=n,phase=phase,time=t,state=role(t,n['finger']),finger=finger(V,KEYS[n['key_index']],n['finger']),black_vertex_checks=light_black(V,DIGITS[n['finger']-1])))
if not (OUT/'RIGHT_16_EVENTS_48_SAMPLES.json').exists():save('RIGHT_16_EVENTS_48_SAMPLES.json',samples)
else:assert read(OUT/'RIGHT_16_EVENTS_48_SAMPLES.json')==json.loads(json.dumps(samples,default=encode))
print('48_EVENT_SAMPLES_DONE',time.perf_counter()-begin,flush=True)

def deep(t,ki):
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);ids=np.array(ROI['INDEX']['vertices']);key=KEYS[ki];comp=next(a for a in comps if a[0]['key_index']==ki);kv,P=actual(comp)
    depth=np.maximum(0,np.min(P[:,3]-V[ids]@P[:,:3].T,axis=1))*1000;ii=int(np.argmax(depth));vid=int(ids[ii]);hit=ids[depth>1e-6]
    tris=V[T];mask=np.any(np.isin(T,ids),axis=1)&np.all(tris.max(1)>=kv.min(0),axis=1)&np.all(tris.min(1)<=kv.max(0),axis=1);cert=[]
    for ti in np.flatnonzero(mask):
        r=dm.max_triangle_depth(tris[ti],P)
        if r['upper_mm']>1e-6:cert.append(dict(triangle_index=int(ti),vertices=T[ti],**r))
    bvh=BVHTree.FromPolygons([Vector(v) for v in V],ROI['INDEX']['faces'],epsilon=0).overlap(BVHTree.FromPolygons([Vector(v) for v in kv],comp[4],epsilon=0))
    a=axisdata['INDEX'];long=float((rv[vid]-a['canonical_tip'])@a['axis']*1000)
    return dict(time=t,key=key['note_name'],index_state=role(t,2),inside_vertices=hit,vertex_peak_mm=float(depth[ii]),vertex=vid,witness_world_m=V[vid],witness_pixel=project([V[vid]])[0],canonical_distance_before_tip_mm=-long,terminal_cap_member=bool(vid in caps['INDEX']),actual_skin_key_bvh_pairs=len(bvh),surface_peak_lower_mm=max((r['lower_mm'] for r in cert),default=0),surface_peak_upper_mm=max((r['upper_mm'] for r in cert),default=0),triangle_certificates=cert,key_pixels=surfaces(key),penetration_pixels=project(V[hit]))
deep_rows=[deep(26/60,47),deep(2.6,49),deep(1.1,49)]
save('INDEX_BLACK_KEY_REAL_GEOMETRY.json',deep_rows)
print('DEEP_CHECKS_DONE',time.perf_counter()-begin,flush=True)
specs=[('01_INDEX_ACTIVE_A4',1.1,2,48),('02_MIDDLE_ACTIVE_B4',1.3,3,50),('03_MIDDLE_ACTIVE_C5',3.45,3,51),('04_INDEX_IDLE_GSHARP',26/60,2,47),('05_INDEX_IDLE_ASHARP',2.6,2,49),('06_C1_B01_HANDOFF',85/60,3,50)]
images=[];original_snap={}
folder=OUT/'raw_stills';folder.mkdir(exist_ok=True)
def still(name,t,f,ki,identity):
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);r=dict(name=name,time=t,identity=identity,state=role(t,f),finger=finger(V,KEYS[ki],f),active=[dict(event=n['note_id'],finger=n['finger'],key=n['note_name']) for n in RNOTES if n['note_on']<=t<n['note_off']],raw_path=str(folder/(name+'.png')))
    r['index_black']=light_black(V,'INDEX');r['ring_black']=light_black(V,'RING');r['index_pad_pixel']=project(V[[1750]])[0]
    images.append(r);sc.render.filepath=r['raw_path'];sc.render.image_settings.file_format='PNG'
    if not Path(r['raw_path']).exists():bpy.ops.render.render(write_still=True)
    return V.copy()
for name,t,f,ki in specs:still(name,t,f,ki,'ORIGINAL_C1')
# Exact-frame projections for original complete video; no collision audit over the phrase.
frames=[]
for frame in range(1,358):
    t=(frame-1)/60;c.settime(sc,t);V,_=c.coords(mesh);active=[]
    for n in RNOTES:
        if n['note_on']<=t<n['note_off']:
            f=n['finger'];d=DIGITS[f-1];active.append(dict(event=n['note_id'],key=n['note_name'],finger=f,pad=project(V[[c.MARKERS['R'][f-1]['mesh_vertex']]])[0],terminal=project(V[[term[d]]])[0],surfaces=surfaces(KEYS[n['key_index']])))
    risk=None
    if .40<=t<=.48 or 2.5<=t<=2.7:
        ki=47 if t<1 else 49;comp=next(a for a in comps if a[0]['key_index']==ki);kv,P=actual(comp);ids=np.array(ROI['INDEX']['vertices']);dep=np.maximum(0,np.min(P[:,3]-V[ids]@P[:,:3].T,axis=1))*1000;hit=ids[dep>1e-6]
        risk=dict(key=KEYS[ki]['note_name'],index_role=role(t,2)['role'],vertex_depth_mm=float(dep.max()),pixels=project(V[hit]))
    frames.append(dict(frame=frame,time=t,active=active,risk=risk))
save('FULL_VIDEO_357_FRAME_PROJECTIONS.json',dict(size=[1280,720],fps=60,frames=frames))
assert before==s.protected_state()
assert native_before=={a:c.digest(c.native(o,r)) for a,o,r in [('R',mesh,rig),('L',left,lrig)]}
save('C1_IN_MEMORY_UNCHANGED.json',dict(actions=before,native_hashes=native_before,camera_matrix=camera_matrix,orthographic_scale=cam.data.ortho_scale,source_sha256=sha(SOURCE)))
compare_times=[1.1333333333333333,1.3,1.4208333333333334,1.4214275,1.4914275,1.675]
for t in compare_times:
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);original_snap[t]=dict(V=V.copy(),middle=finger(V,KEYS[50],3),ring=finger(V,KEYS[51],4))
candidate=ROOT/'experiments/hands_b01_visual_animation_refinement_r1/B01_MULTIJOIN_SINGLE_CANDIDATE_NOT_APPROVED.blend';READS[str(candidate)]=sha(candidate)
assert sha(candidate)=='1984d92bf437c5f833b2ad62e3aaeed5abd16e3e2979e5356b120a14af6a44ed'
sc,rig,mesh,left,lrig=s.open_scene(candidate);sc.camera=bpy.data.objects[MAN['cameras']['OVERHEAD']];assert np.array_equal(np.array(sc.camera.matrix_world),camera_matrix)
cb=s.protected_state();sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
comparison=[]
for t in compare_times:
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);B=original_snap[t];ids=np.array(ROI['INDEX']['vertices']);comparison.append(dict(time=t,baseline={k:v for k,v in B.items() if k!='V'},candidate=dict(middle=finger(V,KEYS[50],3),ring=finger(V,KEYS[51],4)),index_pad_change_mm=float(np.linalg.norm(V[1750]-B['V'][1750])*1000),index_roi_max_change_mm=float(np.max(np.linalg.norm(V[ids]-B['V'][ids],axis=1))*1000),middle_qdeg=s.degrees('MIDDLE'),ring_qdeg=s.degrees('RING')))
still('07_B01_CANDIDATE_B4',1.3,3,50,'B01_NOT_APPROVED')
still('08_B01_CANDIDATE_PRE_C5',1.4208333333333334,4,51,'B01_NOT_APPROVED')
assert cb==s.protected_state()
save('B01_SAME_TIME_COMPARISON.json',comparison);save('STILL_PROJECTIONS.json',images)
save('ANATOMICAL_SAMPLES_AND_METHOD.json',dict(markers=c.MARKERS['R'],terminal_vertices=term,distal_cap_indices=caps,pad_neighborhood_indices=padpatch,method='Canonical strong digit ROI; distal cap longitudinal >= TIP minus 5 mm; terminal maximum canonical distal projection; pad neighborhood canonical radius 7 mm. These are skin samples, NOT pressure/contact patches.',camera_matrix=camera_matrix,camera_type=sc.camera.data.type,orthographic_scale=sc.camera.data.ortho_scale,frame_bounds=sc.frame_start))
protection('BLENDER_INPUT_SHA_RECEIPT.json');save('DIAGNOSIS_PROCESS_COST.json',dict(seconds=time.perf_counter()-begin,light_event_samples=48,deep_times=3,still_count=8,motion_edits=0,optimizer_calls=0))
print('DIAGNOSIS_COMPLETE',time.perf_counter()-begin,flush=True)
