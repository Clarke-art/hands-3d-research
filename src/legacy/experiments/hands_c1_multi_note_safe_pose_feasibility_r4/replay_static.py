"""Blender --python replay_static.py -- R08_ROUND_2_NOT_APPROVED_POSE.json
Apply a reproducible STATIC pose after evaluating the original exact frame.
No saving, Action mutation, animation muting, handlers or key insertion.
Changing the frame restores the original animation.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import session as w
args=sys.argv[sys.argv.index('--')+1:]
assert len(args)==1
p=w.safe(O/args[0]);assert p.parent==O and p.name.endswith('_NOT_APPROVED_POSE.json')
snap=w.read(p);assert snap['status']=='NOT_APPROVED'
assert w.sha(w.STARTCOPY)==snap['source_sha256']
w.c.settime(w.sc,snap['time'])
for name,r in snap['pose'].items():
 b=w.rig.pose.bones[name];b.location=r['location'];b.rotation_mode=r['rotation_mode'];b.rotation_quaternion=r['quaternion'];b.scale=r['scale']
w.bpy.context.view_layer.update()
V=w.s.coords_tri(w.mesh)[0]
assert w.c.digest(V.tolist())==snap['validation']['mesh_digest']
assert w.BASE_ACTIONS==w.s.protected_state()
print('NOT_APPROVED static pose reproduced; original animation remains assigned and unchanged.')
