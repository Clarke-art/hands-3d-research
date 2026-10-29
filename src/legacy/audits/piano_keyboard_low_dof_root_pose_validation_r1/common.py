from pathlib import Path
import json,hashlib,math,ast
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[1];PRE=P.parent/'piano_keyboard_spatial_anchor_and_contact_validation_r1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False,default=lambda v:v.item() if hasattr(v,'item') else v.tolist()),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def locked():
 for n,v in read(P/'PRE_RESULT_POLICY_LOCK_R1.json')['hashes'].items():assert sha(P/n)==v,('POLICY_DRIFT',n)
 for n,v in read(P/'INHERITED_IDENTITIES_R1.json').items():assert sha(P/n)==sha(v['source'])==v['source_sha256'],('INPUT_DRIFT',n)
tl=read(P/'PERFORMANCE_TIMELINE_R1.json');keys=read(P/'KEYBOARD_88_KEY_TABLE_R1.json')['keys'];policy=read(P/'CONTACT_TOLERANCE_POLICY_R1.json');ex=read(PRE/'HAND_EXTRACTION_R1.json');N=421;times=np.arange(N)/60
tree=ast.parse((PRE/'05_solve.py').read_text(encoding='utf-8-sig'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['active','rot','target_for','measurement']],type_ignores=[]),'inherited_geometry_queries','exec'))
def rotations(ang):
 y,p,r=ang.T;cy,sy=np.cos(y),np.sin(y);cp,sp=np.cos(p),np.sin(p);cr,sr=np.cos(r),np.sin(r)
 # Rz(yaw) Rx(pitch) Ry(roll)
 out=np.empty((len(ang),3,3));out[:,0,0]=cy*cr-sy*sp*sr;out[:,0,1]=-sy*cp;out[:,0,2]=cy*sr+sy*sp*cr;out[:,1,0]=sy*cr+cy*sp*sr;out[:,1,1]=cy*cp;out[:,1,2]=sy*sr-cy*sp*cr;out[:,2,0]=-cp*sr;out[:,2,1]=sp;out[:,2,2]=cp*cr;return out
def spline_basis():
 K=36;B=np.zeros((N,K))
 for i in range(N):
  u=i/12;j=int(u);f=u-j;weights=[(1-f)**3/6,(3*f**3-6*f*f+4)/6,(-3*f**3+3*f*f+3*f+1)/6,f**3/6]
  for k,w in zip(range(j-1,j+3),weights):B[i,min(max(k,0),K-1)]+=w
 assert np.allclose(B.sum(1),1);return B
