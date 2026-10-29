param([ValidateSet('Verify','Rebuild')][string]$Mode='Verify')
$ErrorActionPreference='Stop'
$auditDirectory=$PSScriptRoot
if ($Mode -eq 'Verify') {
  python (Join-Path $auditDirectory '09_finish.py')
  if ($LASTEXITCODE -ne 0) { throw 'Delivery verification failed' }
  exit
}
# Explicit identical-candidate rebuild, not a parameter sweep. Requires the downloaded source and local _deps.
$blenderExecutable='D:\Blender\blender.exe'
foreach ($step in @('01_source_timeline.py','02_rig_probe.py','03_motion_plan.py','04_scene.py','05_audio.py','07_evaluate.py')) {
  $scriptPath=Join-Path $auditDirectory $step
  if ($step -in @('02_rig_probe.py','04_scene.py')) { & $blenderExecutable -b --factory-startup --python-exit-code 1 --python $scriptPath }
  else { python $scriptPath }
  if ($LASTEXITCODE -ne 0) { throw "Failed: $step" }
}
& $blenderExecutable -b --factory-startup --python-exit-code 1 --python (Join-Path $auditDirectory '06_render.py') -- --preview
if ($LASTEXITCODE -ne 0) { throw 'Preview failed' }
& $blenderExecutable -b --factory-startup --python-exit-code 1 --python (Join-Path $auditDirectory '06_render.py')
if ($LASTEXITCODE -ne 0) { throw 'Render failed' }
python (Join-Path $auditDirectory '08_media.py')
if ($LASTEXITCODE -ne 0) { throw 'Media failed' }
python (Join-Path $auditDirectory '09_finish.py')
if ($LASTEXITCODE -ne 0) { throw 'Delivery failed' }
