import sys,types,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O))
import session as w
spec=importlib.util.spec_from_file_location('r4_blender_mcp',r'<USER_HOME>/AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons/addon.py')
addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
print('R4_MCP_READY',flush=True)
