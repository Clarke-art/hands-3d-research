import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bootstrap import *
import bpy,math,types
import blender_helpers as h
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
import model as n
assert read(O/'STAGE0_PYTHON_GATE.json')['pass_']
I=read(O/'INPUT_BINDINGS.json');man=I['scene'];clock,_=archive(O/'TARGET_CLOCK_REQUEST.npz')
names=['axisrot','digit_setup','joint_mats']
h.RIG={'R':read(OLD/'RIG_CANONICAL_PROBE_R1.json')['R']};h.MARKERS={'R':n.MARK};h.DIGITS=n.DIGITS;h.SETUPS={('R',d):h.digit_setup('R',d) for d in n.DIGITS}
c=h
functions_from(ROOT/'experiments/hands_role_aware_collision_avoidance_r1/baseline_blender.py',['degrees'],globals())
bpy.ops.wm.open_mainfile(filepath=str(valid_path(man['path'])),load_ui=False,use_scripts=False);assert not bpy.data.libraries
sc=bpy.data.scenes[man['scene']];bpy.context.window.scene=sc
rig=bpy.data.objects[man['mapping']['R']['rig']];mesh=bpy.data.objects[man['mapping']['R']['mesh']]
assert h.digest(h.native(mesh,rig))==I['native_sha256']
ka=[];keyerr=0.
for t in clock['times']:
    h.settime(sc,float(t));a=np.zeros(88)
    for ki,name in man['key_pivots'].items():a[int(ki)]=bpy.data.objects[name].rotation_euler.x
    ka.append(a)
for k in n.KEYS:
    for g in k['geometry']:
        ob=next(o for o in sc.objects if o.type=='MESH' and o.get('FROZEN_KEY_INDEX')==k['key_index'] and g['name'] in o.name)
        V,F=h.coords(ob);pv=np.array(k['press_pivot']);expected=(np.array(g['vertices'])-pv)@h.axisrot(ka[-1][k['key_index']],k['press_axis']).T+pv
        keyerr=max(keyerr,float(abs(V-expected).max()*1000))
assert keyerr<.001
start,end=I['target_window_sec'];dt=1/240;boundary_times=[start-dt,start,start+dt,end-dt,end,end+dt];q=[];world=[];errs=[]
for t in boundary_times:
    h.settime(sc,t);qq=np.array([degrees(d) for d in n.DIGITS]);ww=np.array(rig.matrix_world);V,F=h.coords(mesh)
    err=float(np.linalg.norm(n.native(qq,ww)[0]-V,axis=1).max()*1000);assert err<.01
    q.append(qq);world.append(ww);errs.append(err)
ka=np.array(ka)
atomic_record('TARGET_KEY_ACTION_CLOCK.npz',dict(times=clock['times'],key_angles=ka),dict(record_type='KEY_ACTION_ONLY_NO_TARGET_Q'))
atomic_record('TARGET_BOUNDARY_CONDITIONS.npz',dict(times=boundary_times,q=q,world=world),dict(record_type='ENTRY_EXIT_ONLY',purpose='Two endpoint positions plus +/-1/240s derivative measurements; never target interior trajectory'))
# Native BVH and actual skin contact adapter smoke checks.
tree=BVHTree.FromPolygons([Vector((0,0,0)),Vector((1,0,0)),Vector((0,1,0))],[[0,1,2]],epsilon=0)
other=BVHTree.FromPolygons([Vector((.25,.25,-1)),Vector((.25,.25,1)),Vector((.25,.75,0))],[[0,1,2]],epsilon=0);assert tree.overlap(other)
assert h.digest(h.native(mesh,rig))==I['native_sha256'] and sha(man['path'])==man['sha256']
atomic_json('STAGE0_BLENDER_GATE.json',dict(pass_=True,blender=bpy.app.version_string,actual_boundary_FK_skin_errors_mm=errs,actual_key_geometry_error_mm=keyerr,BVH_entry_pass=True,
    target_interior_q_samples_read=0,boundary_q_samples_read=6,target_key_action_samples=len(ka),no_pose_edits=True,no_save=True))
protect();print('STAGE0_BLENDER_PASS',max(errs),keyerr,flush=True)
