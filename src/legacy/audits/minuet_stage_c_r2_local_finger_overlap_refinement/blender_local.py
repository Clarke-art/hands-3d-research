from local_common import *
import bpy,math,importlib.util
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
spec=importlib.util.spec_from_file_location('readonly_hand_identity',ROOT/'audits/left_hand_product_baseline_r1_promotion_r1/common.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
sys.path.insert(0,str(OLD))
import performance_core as c
def settime(sc,t):
    f=1+60*t;i=math.floor(f);sc.frame_set(i,subframe=f-i);bpy.context.view_layer.update()
def curves(action):return [f for l in action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
def payload(action):
    return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,points=[dict(co=list(k.co),interpolation=k.interpolation) for k in f.keyframe_points]) for f in curves(action)]
def mesh_pose(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();V=np.array([list(<REDACTED_EMAIL>) for v in me.vertices]);F=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return V,F
def snapshot(sc,info,side,t):
    settime(sc,t);rt,rig,mesh=[bpy.data.objects[info[k]] for k in ['root','rig','mesh']];V,F=mesh_pose(mesh)
    pads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS[side]])
    return dict(root=np.array(rt.matrix_world),basis=np.array([np.array(b.matrix_basis) for b in rig.pose.bones]),V=V,F=F,pads=pads,skin_pads=V[[r['mesh_vertex'] for r in c.MARKERS[side]]])
def finger_roi(mesh,rig,digit):
    native_to_rig=rig.matrix_world.inverted()@mesh.matrix_world
    rest=np.array([list(<REDACTED_EMAIL>) for v in mesh.data.vertices]);mcp=np.array(rig.data.bones[digit+'_MCP_R'].head_local);pip=np.array(rig.data.bones[digit+'_PIP_R'].head_local);tip=np.array(rig.data.bones[digit+'_TIP_R'].head_local);axis=(tip-mcp)/np.linalg.norm(tip-mcp)
    group={g.index:g.name for g in mesh.vertex_groups};weight=np.array([sum(g.weight for g in v.groups if group[g.group].startswith(digit+'_')) for v in mesh.data.vertices])
    ids=np.flatnonzero((weight>.55)&((rest-mcp)@axis>np.dot(pip-mcp,axis)-.005))
    mask=set(ids);faces=[list(p.vertices) for p in mesh.data.polygons if all(v in mask for v in p.vertices)]
    assert len(faces)>20,(digit,len(ids),len(faces),rest.min(axis=0),rest.max(axis=0),mcp,pip,tip,[(g.index,g.name) for g in mesh.vertex_groups])
    return dict(vertices=ids.tolist(),faces=faces,weights_threshold=.55,proximal_cut='5mm proximal to PIP, rest-axis based, excludes shared palm/web')
def local_relation(V,rois,camera):
    # Two explicitly identified distal skin patches only; no whole-hand forensic
    # search or hidden-angle optimization.
    v1=V[rois['MIDDLE']['vertices']];v2=V[rois['RING']['vertices']]
    trees=[BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],all_triangles=False,epsilon=0) for d in ['MIDDLE','RING']]
    overlap=trees[0].overlap(trees[1]);dist=[]
    for vertices,tree in [(v1,trees[1]),(v2,trees[0])]:
        for pt in vertices[::4]:
            hit=tree.find_nearest(Vector(pt))
            if hit[0] is not None:dist.append(hit[3]*1000)
    inv=camera.matrix_world.inverted()
    projected=[np.array([list(inv@Vector(v))[:2] for v in vs]) for vs in [v1,v2]]
    lo=np.maximum(projected[0].min(axis=0),projected[1].min(axis=0));hi=np.minimum(projected[0].max(axis=0),projected[1].max(axis=0))
    return dict(intersecting_patch_triangle_pairs=len(overlap),nearest_sampled_patch_distance_mm=min(dist),projection_envelope_overlap_mm=np.maximum(0,hi-lo)*1000,patch_scope='MIDDLE/RING distal strong-weight skin only')
def contact(point,k,angle):
    pivot=np.array(k['press_pivot']);R=c.axisrot(angle,[1,0,0]);p=(point-pivot)@R+pivot;sur=k['key_top_playable_surface'];d=[np.linalg.norm(p[:2]-np.clip(p[:2],[s['xmin'],s['ymin']],[s['xmax'],s['ymax']])) for s in sur];i=int(np.argmin(d))
    return dict(gap_mm=float((p[2]-sur[i]['z'])*1000),horizontal_mm=float(d[i]*1000))
