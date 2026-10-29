"""Independent immutable-resource resolver. Never patches pathlib or executes legacy code."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,os,ctypes
from pathlib import Path
class PathAdapter:
 def __init__(self,registry):
  self.r=registry;self.hands=Path(registry['hands_root']);self.source=Path(registry['original_pilot']);self.formal=Path(registry['formal_proposed_pilot']);self.shadow=Path(registry['shadow_pilot']);self.rows={self.key(x['logical_legacy_path']):x for x in registry['inputs']};self.reverse={self.key(x['resolved_path']):x for x in registry['inputs']};self.reads=[];self.cache={}
 @staticmethod
 def key(p):return os.path.normcase(os.path.abspath(p))
 def row(self,path):
  p=Path(path)
  if not p.is_absolute() or '..' in p.parts:raise PermissionError('Absolute, non-traversing registered path required')
  if p.is_relative_to(self.formal):p=self.source/p.relative_to(self.formal)
  x=self.rows.get(self.key(p)) or self.reverse.get(self.key(p))
  if not x:raise PermissionError('Unregistered input; no fallback: '+str(path))
  return x
 def resolve(self,path):return Path(self.row(path)['resolved_path'])
 def bytes(self,path):
  row=self.row(path);p=Path(row['resolved_path']);key=self.key(p)
  if key not in self.cache:
   if p.stat(follow_symlinks=False).st_file_attributes&0x400:raise PermissionError('Reparse input denied')
   b=p.read_bytes();h=hashlib.sha256(b).hexdigest()
   if h!=row['expected_sha256']:raise RuntimeError('STOP: unapproved protected content change '+str(p))
   self.cache[key]=b
   self.reads.append({'requested':str(path),'resolved':str(p),'legacy_manifest_key':row['logical_legacy_path'],'sha256':h,'expected_sha256':row['expected_sha256'],'bytes':len(b),'compatibility':'VIA_PATH_ADAPTER' if p!=Path(path) else 'DIRECT_READ_COMPATIBLE','roles':row['roles'],'pass':True})
  return self.cache[key]
 def json(self,path):return json.loads(self.bytes(path).decode('utf-8-sig'))
 def pilot(self,name):
  if '..' in Path(name).parts or Path(name).is_absolute():raise PermissionError('Pilot traversal denied')
  return self.formal/name
 def legacy_parent_file(self,suffix):
  if Path(suffix).is_absolute() or '..' in Path(suffix).parts:raise PermissionError('Unsafe suffix')
  return self.resolve(self.source.parent/suffix)
 def pin(self):
  k=ctypes.WinDLL('kernel32',use_last_error=True);k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int;self.k=k;self.handles=[]
  try:
   for row in self.rows.values():
    p=row['resolved_path'];handle=k.CreateFileW(p,0x80000000,1,None,3,0x00200000,None)
    if handle==ctypes.c_void_p(-1).value:raise RuntimeError(f'STOP: cannot pin {p}: {ctypes.get_last_error()}')
    self.handles.append(handle)
  except:
   self.unpin();raise
 def unpin(self):
  for h in getattr(self,'handles',[]):self.k.CloseHandle(h)
  self.handles=[]
