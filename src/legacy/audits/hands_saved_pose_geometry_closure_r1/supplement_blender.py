"""Read keys and original scene only; no corrected pose evaluation or pose edits."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import bpy,numpy as np,math,types,itertools
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from depth_math import planes_from_mesh
extract(R2/'blender_helpers.py',['digest','native','settime','coords','axisrot'],globals())
h=types.SimpleNamespace(digest=digest)
extract(R2/'source_actual.py',['curves','actions_digest'],globals())
def tree(V,F):return BVHTree.FromPolygons([Vector(v) for v in V],F,epsilon=0)
def pairs(a,b):return sorted(set((int(i),int(j)) for i,j in a.overlap(b)))
def triangulate_cache(V,F,world):
    inv=np.linalg.inv(world);local=np.c_[V,np.ones(len(V))]@inv.T
    temp=bpy.data.meshes.new('AUDIT_ONLY_CACHED_TESSELLATION_NOT_SAVED')
    try:
        temp.from_pydata(local[:,:3].tolist(),[],F);temp.update();temp.calc_loop_triangles()
        T=np.array([list(t.vertices) for t in temp.loop_triangles],dtype=int)
        pid=np.array([t.polygon_index for t in temp.loop_triangles],dtype=int)
        rt=np.c_[np.array([v.co for v in temp.vertices]),np.ones(len(V))]@world.T
        error=float(np.linalg.norm(rt[:,:3]-V,axis=1).max()*1000)
        assert error<.001,'CACHE_TRIANGULATION_ROUNDTRIP'
        return T,pid,error
    finally:bpy.data.meshes.remove(temp)

def run():
    assert read(O/'TOOLCHAIN_PREFLIGHT.json')['pass_']
    cache,cm=archive(R2/'ACTUAL_BLENDER_STATIC_SKIN.npz');S,sm=archive(SRC/'SOURCE_LOCAL_STATES.npz')
    I=read(SRC/'INPUT_BINDINGS.json');man=I['scene'];K=read(OLD/'KEYBOARD_88_KEY_TABLE_R1.json')['keys']
    flat=cache['face_vertices'];off=cache['face_offsets'];F=[flat[off[i]:off[i+1]].tolist() for i in range(len(off)-1)]
    roi=read(ROOT/'experiments/hands_c01_whole_hand_motion_feasibility_r1/DIGIT_SKIN_ROI.json');digits=['THUMB','INDEX','MIDDLE','RING','LITTLE']
    # Native BVH adapter tests before opening original C1.
    a=tree([[0,0,0],[1,0,0],[0,1,0]],[[0,1,2]])
    hit=tree([[.25,.25,-1],[.25,.25,1],[.25,.75,0]],[[0,1,2]])
    miss=tree([[2,2,-1],[2,2,1],[2,3,0]],[[0,1,2]])
    assert pairs(a,hit) and not pairs(a,miss)
    dump('BLENDER_BVH_SELFTEST.json',dict(pass_=True,known_crossing=pairs(a,hit),known_nonintersection=pairs(a,miss)))
    bpy.ops.wm.open_mainfile(filepath=str(path(man['path'])),load_ui=False,use_scripts=False);assert not bpy.data.libraries
    sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
    rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']];left=bpy.data.objects[man['mapping']['L']['mesh']]
    native_before=digest(native(mesh,rig));assert native_before==I['native_sha256']
    action_before=actions_digest();assert action_before==read(R2/'FROZEN_PROTECTION.json')['actions_before']
    rows=[];numeric={'times':np.array(TIMES)};keyparity=0.;convexerr=0.
    for ix,t in enumerate(TIMES):
        settime(sc,t);B=cache['baseline_vertices'][ix];V=cache['corrected_vertices'][ix];actualB,Factual=coords(mesh)
        assert Factual==F and np.linalg.norm(actualB-B,axis=1).max()*1000<.01
        ka=np.zeros(88)
        for ki,n in man['key_pivots'].items():ka[int(ki)]=bpy.data.objects[n].rotation_euler.x
        assert np.array_equal(ka,S['key_angles'][ix])
        world=np.array(mesh.matrix_world);tb,pb,eb=triangulate_cache(B,F,world);tn,pn,en=triangulate_cache(V,F,world)
        numeric['baseline_triangles_'+str(ix)]=tb;numeric['corrected_triangles_'+str(ix)]=tn
        numeric['baseline_triangle_polygon_'+str(ix)]=pb;numeric['corrected_triangle_polygon_'+str(ix)]=pn
        numeric['mesh_world_'+str(ix)]=world;numeric['key_angles_'+str(ix)]=ka
        bt=tree(B,F);nt=tree(V,F);LV,LF=coords(left);lt=tree(LV,LF)
        bt_digit={d:tree(B,roi[d]['faces']) for d in digits};nt_digit={d:tree(V,roi[d]['faces']) for d in digits}
        allself=[]
        for tr in [bt,nt]:
            allself.append([(a,b) for a,b in pairs(tr,tr) if a<b and set(F[a]).isdisjoint(F[b])])
        digitpairs={d+'_'+e:dict(baseline=pairs(bt_digit[d],bt_digit[e]),corrected=pairs(nt_digit[d],nt_digit[e])) for d,e in itertools.combinations(digits,2)}
        components=[]
        for k in K:
            obs=[o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==k['key_index']];assert len(obs)==len(k['geometry'])
            for g in k['geometry']:
                ob=next(o for o in obs if g['name'] in o.name)
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
                try:
                    me.calc_loop_triangles();kv=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);kf=[list(f.vertices) for f in me.polygons];kt=[list(tr.vertices) for tr in me.loop_triangles]
                finally:ev.to_mesh_clear()
                pv=np.array(k['press_pivot']);expected=(np.array(g['vertices'])-pv)@axisrot(ka[k['key_index']],k['press_axis']).T+pv
                keyparity=max(keyparity,float(abs(kv-expected).max()*1000));assert keyparity<.001
                pl,err=planes_from_mesh(kv,kt);convexerr=max(convexerr,err)
                ktr=tree(kv,kf)
                components.append(dict(key_index=k['key_index'],note=k['note_name'],name=g['name'],object=ob.name,vertices_world_m=kv,polygons=kf,triangles=kt,planes=pl,
                    baseline_skin_key_BVH_pairs=pairs(bt,ktr),corrected_skin_key_BVH_pairs=pairs(nt,ktr)))
        rows.append(dict(time=t,key_angles_exact=True,actual_key_components=components,baseline_full_self_pairs=allself[0],corrected_full_self_pairs=allself[1],digit_pairs=digitpairs,
            left_hand_skin_pairs=dict(baseline=pairs(bt,lt),corrected=pairs(nt,lt)),cache_tessellation_roundtrip_mm=dict(baseline=eb,corrected=en),baseline_actual_readback_mm=float(np.linalg.norm(actualB-B,axis=1).max()*1000)))
        print('SUPPLEMENT_CAPTURED',t,'components',len(components),'cache_only_skin',len(tn),flush=True)
    assert digest(native(mesh,rig))==native_before and actions_digest()==action_before
    np.savez_compressed(O/'ACTUAL_TRIANGULATION_AND_KEY_CLOCK.npz',**numeric)
    dump('ACTUAL_KEY_AND_BVH_SUPPLEMENT.json',dict(source_sha256=man['sha256'],blender=bpy.app.version_string,rows=rows,
        key_geometry_registered_parity_mm=keyparity,convex_mesh_plane_vertex_violation_m=convexerr,corrected_poses_applied=0,original_actions_unchanged=True,native_identity_unchanged=True,
        action_sha256=action_before,native_sha256=native_before,no_blend_action_or_video_saved=True))
    snapshot('SUPPLEMENT_INPUT_SHA.json')
    print('SUPPLEMENT_PASS',keyparity,flush=True)

if __name__=='__main__':
    try:run()
    except BaseException:
        import traceback
        dump('BLENDER_SUPPLEMENT_FAILURE.json',dict(error=traceback.format_exc()))
        raise
