"""Read source scene, apply the sole terminal iterate in memory, save evidence.

No keyframe insertion, no new Action, no Blend save, no numerical optimization.
"""
import sys,hashlib,json,itertools
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'audits/minuet_stage_c_r2_local_finger_overlap_refinement'))
from blender_local import *
def save(n,v):
    (OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False,default=lambda x:x.tolist() if hasattr(x,'tolist') else x.item()),encoding='utf8')
man=read(C1/'SCENE_MANIFEST.json');assert sha(man['path'])==read(OUT/'STRATEGY_LOCK.json')['source_sha256']
tl=read(C1/'PERFORMANCE_TIMELINE.json');result=dict(np.load(OUT/'TERMINAL_TRAJECTORY_EVIDENCE.npz'))
meta=read(OUT/'SOURCE_MODEL_MANIFEST.json')
weights=np.load(OUT/'SOURCE_MODEL.npz')['weights']
influence=np.column_stack([weights[:,[i for i,n in enumerate(meta['bones']) if n.startswith(d+'_')]].sum(1) for d in c.DIGITS])
owner=influence.argmax(1);owner[influence.max(1)<1e-12]=5
owned={j:np.flatnonzero(owner==j) for j in range(6)}
bpy.ops.wm.open_mainfile(filepath=man['path'],load_ui=False,use_scripts=False)
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
info=man['mapping']['R'];rig=bpy.data.objects[info['rig']];mesh=bpy.data.objects[info['mesh']]
protected={n:payload(bpy.data.objects[n].animation_data.action) for n in [man['mapping']['L']['root'],man['mapping']['L']['rig'],info['root']]+list(man['key_pivots'].values())}
oldrois=read(ROOT/'audits/minuet_stage_c_r3_right_hand_local_spatial_clearance/LOCAL_SKIN_ROI.json')
rois=meta['rois'];pairs=list(itertools.combinations(c.DIGITS,2))
times=result['times'];ix=np.unique(np.r_[[np.argmin(abs(times-t)) for t in np.arange(358)/60],
    [np.argmin(abs(times-v)) for n in tl['notes'] if n['hand']=='R' for v in [n['note_on'],n['note_off'],n['note_on']-.09,n['note_off']+.04]],np.argmin(abs(times-3.825)),0,len(times)-1])
keys=[k for k in c.KEYS if 64<=k['midi_note']<=82]
geometry_parity=[];rows=[];terminal_skin=[];source_skin=[]
def getkeys():
    out=[]
    for key in keys:
        obs=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and f"KEY_RENDER_{key['midi_note']:03d}" in o.name]
        for ob in obs:
            V,F=mesh_pose(ob);center=V.mean(0);pl=[]
            # Actual rendered white-key objects may combine two components;
            # use native table decomposition only after geometric bounds proof.
            out.append((key,ob.name,V,F))
    return out
def measure(V,t):
    keyhits=[]
    for key in keys:
        pv=np.array(key['press_pivot']);ang=bpy.data.objects[man['key_pivots'][str(key['key_index'])]].rotation_euler.x if str(key['key_index']) in man['key_pivots'] else 0
        R=c.axisrot(-ang,[1,0,0]);pts=(V-pv)@R.T+pv
        for component in key['geometry']:
            vv=np.array(component['vertices']);lo=vv.min(0);hi=vv.max(0)
            depth=np.minimum(pts-lo,hi-pts).min(1)*1000
            for j,ids in owned.items():
                if not len(ids):continue
                vid=int(ids[np.argmax(depth[ids])])
                if depth[vid]>.02:
                    digit=c.DIGITS[j] if j<5 else 'FIXED_PALM'
                    active_target=any(n['hand']=='R' and n['finger']==j+1 and n['midi_note']==key['midi_note'] and n['note_on']-1e-8<=t<=n['note_off']+1e-8 for n in tl['notes'])
                    keyhits.append(dict(midi=key['midi_note'],key=key['note_name'],color=key['color'],component=component['name'],vertex=vid,digit=digit,active_target_for_dominant_digit=active_target,
                        depth_mm=float(depth[vid]),inside_vertex_count=int(np.sum(depth[ids]>.02)),point_world_m=V[vid]))
    trees={d:BVHTree.FromPolygons([Vector(v) for v in V],rois[d]['faces'],epsilon=0) for d in c.DIGITS}
    pairrows=[]
    for a,b in pairs:
        overlaps=trees[a].overlap(trees[b])
        if overlaps:pairrows.append(dict(digits=[a,b],face_pairs=len(overlaps),example_face_pairs=overlaps[:3]))
    oldtrees={d:BVHTree.FromPolygons([Vector(v) for v in V],oldrois[d]['faces'],epsilon=0) for d in ['MIDDLE','RING']}
    historical_pairs=len(oldtrees['MIDDLE'].overlap(oldtrees['RING']))
    contacts=[]
    for n in tl['notes']:
        if n['hand']=='R' and n['note_on']-1e-8<=t<=n['note_off']+1e-8:
            key=c.KEYS[n['key_index']];ang=bpy.data.objects[man['key_pivots'][str(n['key_index'])]].rotation_euler.x
            contacts.append(dict(note=n['note_id'],name=n['note_name'],finger=n['finger'],**contact(V[c.MARKERS['R'][n['finger']-1]['mesh_vertex']],key,ang)))
    return dict(key_hits=keyhits,finger_intersections=pairrows,historical_middle_ring_face_pairs=historical_pairs,contacts=contacts)
settime(sc,0)
for key,name,V,F in getkeys():
    # Compare the actual undeformed key vertices with the authoritative table.
    vv=np.concatenate([np.array(g['vertices']) for g in key['geometry']]);err=np.sqrt(((V[:,None]-vv[None])**2).sum(2)).min(1).max()*1000
    geometry_parity.append(dict(key=key['note_name'],object=name,max_nearest_table_vertex_mm=float(err)))
assert max(r['max_nearest_table_vertex_mm'] for r in geometry_parity)<.03
for count,i in enumerate(ix):
    t=float(times[i]);settime(sc,t);before=mesh_pose(mesh)[0];src=measure(before,t)
    for j,d in enumerate(c.DIGITS):
        mats=c.joint_mats('R',d,np.radians(result['qdeg'][i,j]));names=c.SETUPS['R',d][0]
        for name,mat in zip(names,mats):rig.pose.bones[name].rotation_quaternion=Matrix(mat.tolist()).to_quaternion()
    bpy.context.view_layer.update();after=mesh_pose(mesh)[0];dst=measure(after,t)
    rows.append(dict(video_sec=t,source=src,terminal=dst))
    source_skin.append(before);terminal_skin.append(after)
    if count%75==0:print('R6_ACTUAL_EVIDENCE',count,len(ix),flush=True)
assert all(payload(bpy.data.objects[n].animation_data.action)==v for n,v in protected.items())
np.savez_compressed(OUT/'ACTUAL_TERMINAL_SKIN.npz',times=times[ix],indices=ix,source=source_skin,terminal=terminal_skin)
save('ACTUAL_SPATIAL_VALIDATION.json',dict(rows=rows,key_geometry_parity=geometry_parity,
    protected_actions_unchanged=True,source_blend_sha256=sha(man['path']),new_actions=0,new_blends=0,
    note='Terminal numerical iterate in memory only; not a candidate or human-approved performance',
    coverage='Whole phrase 60Hz plus finite event probes; all skin vertices against actual-verified moving key components; all 10 strong digit skin ROI pairs; historical distal MIDDLE/RING ROI also measured',
    limitations='Skin-vertex interior witnesses do not exclude triangle-only key crossings; finger BVH counts certify intersections but are not volume depth measurements'))
print('R6_ACTUAL_VALIDATION_DONE',len(ix),flush=True)
