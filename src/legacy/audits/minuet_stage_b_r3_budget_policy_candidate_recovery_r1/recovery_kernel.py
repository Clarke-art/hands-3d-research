from stage_common import *
from left_continuous_motion import *
import importlib.util
spec=importlib.util.spec_from_file_location('unchanged_region_functions',R3/'contact_region.py');region=importlib.util.module_from_spec(spec);spec.loader.exec_module(region)
activity_envelope=region.activity_envelope
skin_caps_batch=region.skin_caps_batch
