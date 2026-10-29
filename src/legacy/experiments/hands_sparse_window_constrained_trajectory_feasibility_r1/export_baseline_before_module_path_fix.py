from native_model import *
import bpy,math,types
import blender_helpers as h
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
extract(ROOT/'audits/hands_recomposition_saved_result_verification_r2/source_actual.py',['curves','actions_digest'],globals())
extract(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
h.RIG={'R':read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']};h.MARKERS={'R':MARK};h.DIGITS=DIGITS
h.SETUPS={('R',d):h.digit_setup('R',d) for d in DIGITS};c=h
man=I['scene'];bpy.ops.wm.open_mainfile(filepath=str(valid_path(man['path'])),load_ui=False,use_scripts=False)
assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
left=bpy.data.objects[man['mapping']['L']['mesh']]
native_before=h.digest(h.native(mesh,rig));assert native_before==I['native_sha256']
actions_before=actions_digest()
def coords_tri(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    try:
        me.calc_loop_triangles()
        return np.array([list(<REDACTED_EMAIL>) for v in me.vertices]),np.array([list(t.vertices) for t in me.loop_triangles],dtype=np.int32)
    finally:ev.to_mesh_clear()
times=archive(O/'BASELINE_REQUEST.npz')['times'];V=[];LV=[];QQ=[];WW=[];AA=[];errors=[]
for ix,t in enumerate(times):
    h.settime(sc,float(t));v,tris=coords_tri(mesh);lv,ltris=coords_tri(left)
    q=np.array([degrees(d) for d in DIGITS]);world=np.array(rig.matrix_world);a=np.zeros(88)
    for ki,name in man['key_pivots'].items():a[int(ki)]=bpy.data.objects[name].rotation_euler.x
    err=float(np.linalg.norm(v-native(q,world)[0],axis=-1).max()*1000);assert err<.01
    V.append(v);LV.append(lv);QQ.append(q);WW.append(world);AA.append(a);errors.append(err)
    if ix%60==0:print('BASELINE_ACTUAL',ix,len(times),err,flush=True)
keyerr=0.
for key,g,pl in COMPONENTS:
    ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==key['key_index'] and g['name'] in o.name)
    actual=np.array([list(<REDACTED_EMAIL>) for v in ob.data.vertices]);pv=np.array(key['press_pivot'])
    expected=(np.array(g['vertices'])-pv)@rot(AA[-1][key['key_index']],key['press_axis']).T+pv
    keyerr=max(keyerr,float(abs(actual-expected).max()*1000))
assert keyerr<.001
tri=BVHTree.FromPolygons([Vector((0,0,0)),Vector((1,0,0)),Vector((0,1,0))],[[0,1,2]],epsilon=0)
cross=BVHTree.FromPolygons([Vector((.25,.25,-1)),Vector((.25,.25,1)),Vector((.25,.75,0))],[[0,1,2]],epsilon=0)
assert tri.overlap(cross)
atomic_record('BASELINE_ACTUAL.npz',dict(times=times,q_deg=QQ,rig_world=WW,vertices=V,left_vertices=LV,key_angles=AA,triangles=tris,left_triangles=ltris),dict(kind='REAL_C1_WINDOW_READ_ONLY'))
assert h.digest(h.native(mesh,rig))==native_before and actions_digest()==actions_before
atomic_json('STAGE0_BLENDER.json',dict(pass_=True,version=bpy.app.version_string,samples=len(times),skin_rebuild_max_mm=max(errors),key_geometry_max_mm=keyerr,native_sha=native_before,actions_sha=actions_before,original_unchanged=True,Blends_saved=0,Actions_created=0,BVH_selftest=True))
protect('PROTECTION_BASELINE_EXPORT.json')
