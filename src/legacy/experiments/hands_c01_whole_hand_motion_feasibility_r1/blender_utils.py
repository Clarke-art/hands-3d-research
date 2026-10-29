import sys,json,math,hashlib,ast
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parent;ROOT=O.parent/'hands'
sys.path.insert(0,str(ROOT/'audits/midi_driven_dual_hand_piano_performance_poc_r1'))
import performance_core as c
I=json.loads((O/'INPUT_BINDINGS.json').read_text());man=I['source_scene'];pf=json.loads((O/'RIG_PREFLIGHT.json').read_text());BASE=np.array(pf['base_xyz_m']);BASEMAT=Matrix(pf['static_root_base_matrix']);rois=json.loads((O/'DIGIT_SKIN_ROI.json').read_text())
tree=ast.parse((O/'blender_preflight.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['out','digest','native','settime','coords']],type_ignores=[]),'shared_actual_geometry','exec'))
tree=ast.parse((ROOT/'audits/minuet_stage_c_r6_whole_phrase_spatial_planning/whole_phrase_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='component_planes'],type_ignores=[]),'existing_convex_piece_planes','exec'))
PLANES={(k['key_index'],j):component_planes(g) for k in c.KEYS for j,g in enumerate(k['geometry'])}
def curves(a):return [f for layer in a.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves]
def payload(a):return [dict(path=f.data_path,index=f.array_index,extrapolation=f.extrapolation,points=[dict(co=list(k.co),interpolation=k.interpolation,handle_left=list(k.handle_left),handle_right=list(k.handle_right),handle_left_type=k.handle_left_type,handle_right_type=k.handle_right_type) for k in f.keyframe_points]) for f in curves(a)]
def root_rotation(deg):
 a=np.radians(deg);return c.axisrot(a[2],[0,0,1])@c.axisrot(a[1],[0,1,0])@c.axisrot(a[0],[1,0,0])
def apply(state,rt,rig):
 RR=Matrix(root_rotation(state[3:6]).tolist()).to_4x4();rt.matrix_world=Matrix.Translation(Vector(BASE+state[:3]/1000))@<REDACTED_EMAIL>(Vector(-BASE))@BASEMAT
 q=np.radians(state[6:].reshape(5,4))
 for j,d in enumerate(c.DIGITS):
  for name,R in zip(c.SETUPS['R',d][0],c.joint_mats('R',d,q[j])):rig.pose.bones[name].rotation_mode='QUATERNION';rig.pose.bones[name].rotation_quaternion=Matrix(R.tolist()).to_quaternion()
 bpy.context.view_layer.update()
def keyangles():
 a=np.zeros(88)
 for k,n in man['key_pivots'].items():a[int(k)]=bpy.data.objects[n].rotation_euler.x
 return a
def contact(p,key,angle):
 pv=np.array(key['press_pivot']);p=(p-pv)@c.axisrot(angle,key['press_axis'])+pv;s=key['key_top_playable_surface'];ds=[np.linalg.norm(p[:2]-np.clip(p[:2],[v['xmin'],v['ymin']],[v['xmax'],v['ymax']])) for v in s];j=int(np.argmin(ds));return dict(gap_mm=float((p[2]-s[j]['z'])*1000),horizontal_mm=float(ds[j]*1000),key_local_xyz_m=p.tolist())
def measure(sc,mesh,rig,t,active=None):
 V,F=coords(mesh);ang=keyangles();pads=V[[r['mesh_vertex'] for r in c.MARKERS['R']]];bonepads=np.array([list(<REDACTED_EMAIL>[r['distal_frame']].matrix@Vector(r['local_pad_point'])) for r in c.MARKERS['R']]);pairs={};trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in c.DIGITS}
 for i,d in enumerate(c.DIGITS):
  for e in c.DIGITS[i+1:]:pairs[d+'_'+e]=len(trees[d].overlap(trees[e]))
 hits=[];allmax=0;passivemax=0
 for key in c.KEYS:
  pv=np.array(key['press_pivot']);local=(V-pv)@c.axisrot(ang[key['key_index']],key['press_axis'])+pv
  for j,g in enumerate(key['geometry']):
   bounds=np.array(g['vertices']);lo=bounds.min(0);hi=bounds.max(0)
   if np.any(local.max(0)<lo) or np.any(local.min(0)>hi):continue
   pl=PLANES[key['key_index'],j];depth=-np.max(local@pl[:,:3].T-pl[:,3],axis=1)*1000;positive=np.flatnonzero(depth>.25)
   peak=max(float(depth.max()),0);allmax=max(allmax,peak)
   if len(positive):
    affected={d:float(np.max(depth[rois[d]['vertices']])) for d in c.DIGITS if np.max(depth[rois[d]['vertices']])>.25}
    if active:
     for d,v in affected.items():
      if not(d==c.DIGITS[active['finger']-1] and key['midi_note']==active['midi_note']):passivemax=max(passivemax,v)
    else:passivemax=max(passivemax,peak)
    allowed=set(rois[c.DIGITS[active['finger']-1]]['vertices']) if active and key['midi_note']==active['midi_note'] else set()
    wrong=[v for v in positive if int(v) not in allowed]
    if wrong:passivemax=max(passivemax,float(depth[wrong].max()))
    hits.append(dict(key=key['note_name'],midi=key['midi_note'],key_color=key['color'],piece=j,maximum_depth_mm=peak,penetrating_vertices=len(positive),digit_depths_mm=affected))
 row=dict(time=float(t),finger_intersection_pairs=pairs,key_penetrations=hits,max_key_vertex_depth_mm=allmax,max_inactive_or_wrong_key_depth_mm=passivemax,pad_vs_skin_max_mm=float(np.linalg.norm(pads-bonepads,axis=1).max()*1000))
 if active:row.update(note=active['note_id'],finger=active['finger'],contact=contact(pads[active['finger']-1],c.KEYS[active['key_index']],ang[active['key_index']]))
 return row,V

