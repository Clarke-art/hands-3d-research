param([ValidateSet('Verify','Rebuild','Render')][string]$Mode='Verify')
$ErrorActionPreference='Stop'
$auditRoot=$PSScriptRoot
function RunPython($name) { & python (Join-Path $auditRoot $name); if ($LASTEXITCODE -ne 0) { throw "$name failed" } }
function RunBlender($name) { & 'D:\Blender\blender.exe' -b --factory-startup --python-exit-code 1 --python (Join-Path $auditRoot $name); if ($LASTEXITCODE -ne 0) { throw "$name failed" } }
if ($Mode -eq 'Rebuild') {
 RunPython '00_inherit.py'
 RunPython '01_coordinate.py'
 RunPython '02_build_scripts.py'
 RunBlender '03_scene.py'
 RunPython '04_evaluate.py'
}
if ($Mode -ne 'Verify') {
 RunBlender '05_render.py'
 RunPython '06_media.py'
 RunPython '07_finish.py'
}
RunPython '08_verify.py'
