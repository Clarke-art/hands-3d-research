import sys
sys.dont_write_bytecode=True
from common import *
import bpy
PROV=reuse(OLD/'payload.py',['plain','props','rna','object_payload','rig_payload','material_payload','snapshot','read_rolls_last','load'],globals())
original_snapshot=snapshot
def snapshot():
 s=original_snapshot();ob=bpy.data.objects[s['object_name']]
 # Preserve all pre-existing metadata; the old helper's GEOMETRY_PROPAGATION exclusion is overridden.
 s['protected']['object']['custom_properties']=props(ob)
 return s
