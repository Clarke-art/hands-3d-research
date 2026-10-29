import sys,types,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
w=types.ModuleType('exit_session');w.__file__=str(O/'diagnose.py');sys.modules[w.__name__]=w
exec(compile(Path(w.__file__).read_text(encoding='utf8'),w.__file__,'exec'),w.__dict__)
spec=importlib.util.spec_from_file_location('hands_exit_mcp',r'<USER_HOME>/AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons/addon.py')
addon=importlib.util.module_from_spec(spec);sys.modules[spec.name]=addon;spec.loader.exec_module(addon);addon.register()
print('R2_MCP_READY',flush=True)
