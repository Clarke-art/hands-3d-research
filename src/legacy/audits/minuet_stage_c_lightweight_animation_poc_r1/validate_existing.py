"""Resume read-only validation of the already saved sole candidate; no re-bake."""
from pathlib import Path
code=Path(__file__).with_name('bake_validate.py').read_text(encoding='utf8')
prefix=code.split('# Keep exact source sample times;')[0].replace(';assert not dest.exists()',';assert dest.exists()')
suffix='bpy.ops.wm.open_mainfile(filepath=str(dest)'+code.split('bpy.ops.wm.open_mainfile(filepath=str(dest)',1)[1]
exec(compile(prefix+'\n'+suffix,str(Path(__file__).with_name('bake_validate.py')),'exec'))
