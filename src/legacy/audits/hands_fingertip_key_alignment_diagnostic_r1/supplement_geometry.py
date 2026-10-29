import sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent))
import blender_support as s
from blender_support import *
begin=time.perf_counter();sc,rig,mesh,left,lrig=s.open_scene(SOURCE);before=s.protected_state()
method=read(OUT/'ANATOMICAL_SAMPLES_AND_METHOD.json');samples=read(OUT/'RIGHT_16_EVENTS_48_SAMPLES.json')
dm=types.ModuleType('depth_math');p=ROOT/'audits/hands_saved_pose_geometry_closure_r1/depth_math.py';exec(compile(safe(p).read_text(encoding='utf8'),str(p),'exec'),dm.__dict__)
def component(key):
    g=key['geometry'][0];ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name);me=ob.data;me.calc_loop_triangles();kv=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);kt=np.array([list(t.vertices) for t in me.loop_triangles]);P,err=dm.planes_from_mesh(kv,kt);return kv,kt,P
rows=[]
for r in samples:
    t=r['time'];f=r['note']['finger'];d=DIGITS[f-1];key=KEYS[r['note']['key_index']];vid=c.MARKERS['R'][f-1]['mesh_vertex'];c.settime(sc,t);V,T,F=s.coords_tri(mesh)
    ts=V[T[np.any(T==vid,axis=1)]];normal=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]).sum(0);normal/=np.linalg.norm(normal);kn=c.axisrot(s.keyangle(key),key['press_axis'])@np.array([0,0,1]);angle=np.degrees(np.arccos(np.clip(normal@(-kn),-1,1)))
    capids=np.array(method['distal_cap_indices'][d],int);bounds=[]
    for k in KEYS:
        if k['color']!='BLACK' or abs(k['key_center'][0]-V[vid,0])>.04:continue
        kv,kt,P=component(k);local=s.key_local(V[capids],k);a=k['key_top_playable_surface'][0];mask=(local[:,0]>=a['xmin'])&(local[:,0]<=a['xmax'])&(local[:,1]>=a['ymin'])&(local[:,1]<=a['ymax'])
        if mask.any():
            zlo=np.array(k['geometry'][0]['vertices'])[:,2].min();zz=local[mask,2];bounds.append(dict(key=k['note_name'],cap_vertex_count_xy_over_black=int(mask.sum()),below_black_bottom=int((zz<zlo).sum()),above_black_top=int((zz>a['z']).sum()),inside_black_z=int(((zz>=zlo)&(zz<=a['z'])).sum()),skin_vertices=capids[mask]))
    rows.append(dict(event=r['event'],phase=r['phase'],time=t,pad_outward_normal_world=normal,pad_normal_to_opposing_key_normal_deg=float(angle),cap_world_bbox_m=[V[capids].min(0),V[capids].max(0)],black_projection= bounds))
deep=[]
for t,ki in [(3.45,52),(3.88571075,54)]:
    c.settime(sc,t);V,T,F=s.coords_tri(mesh);key=KEYS[ki];kv,kt,P=component(key);ids=np.array(ROI['MIDDLE']['vertices']);dep=np.maximum(0,np.min(P[:,3]-V[ids]@P[:,:3].T,axis=1))*1000
    tv=V[T];mask=np.any(np.isin(T,ids),axis=1)&np.all(tv.max(1)>=kv.min(0),axis=1)&np.all(tv.min(1)<=kv.max(0),axis=1);cert=[]
    for ti in np.flatnonzero(mask):
        r=dm.max_triangle_depth(tv[ti],P)
        if r['upper_mm']>1e-6:cert.append(dict(triangle_index=int(ti),vertices=T[ti],**r))
    pairs=BVHTree.FromPolygons([Vector(v) for v in V],ROI['MIDDLE']['faces'],epsilon=0).overlap(BVHTree.FromPolygons([Vector(v) for v in kv],kt,epsilon=0))
    ix=int(np.argmax(dep));deep.append(dict(time=t,digit='MIDDLE',key=key['note_name'],active_target='C5' if t<3.5 else 'E5',vertex_peak_mm=float(dep[ix]),vertex=int(ids[ix]),witness_world_m=V[ids[ix]],surface_peak_lower_mm=max((r['lower_mm'] for r in cert),default=0),surface_peak_upper_mm=max((r['upper_mm'] for r in cert),default=0),actual_skin_key_bvh_pairs=len(pairs),triangle_certificates=cert))
assert s.protected_state()==before
save('PAD_NORMAL_AND_BLACK_PROJECTION.json',rows);save('MIDDLE_ACTIVE_NEIGHBOR_BLACK_DEEP.json',deep);protection('SUPPLEMENT_SHA_RECEIPT.json');print('SUPPLEMENT_COMPLETE',time.perf_counter()-begin,flush=True)
