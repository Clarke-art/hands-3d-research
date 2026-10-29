import sys,json,time
from pathlib import Path
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));from rig_model import *
sys.path.insert(0,str(O/'deps'));import casadi as ca

def symbolic_model():
 z=ca.MX.sym('z',12);st=ca.vertcat(z[:10],*[((1-z[10])*Q0[j,k]+z[10]*Q1[j,k]) if not(j==2 and k<3) else (1-z[11])*((1-z[10])*Q0[j,k]+z[10]*Q1[j,k])+z[11]*ACTIVE[k] for j in range(1,5) for k in range(4)]);q=ca.reshape(st[6:],4,5).T*np.pi/180
 def R(a,axis):
  x,y,zz=np.array(axis)/np.linalg.norm(axis);K=ca.DM([[0,-zz,y],[zz,0,-x],[-y,x,0]]);return ca.DM.eye(3)+ca.sin(a)*K+(1-ca.cos(a))*(K@K)
 basis=[ca.DM.eye(3) for _ in REST]
 for j,d in enumerate(c.DIGITS):
  names,_,axes,spread,_=c.SETUPS['R',d]
  for k,name in enumerate(names):basis[BN[name]]=R(q[j,k],axes[k]) if k else R(q[j,3],spread)@R(q[j,k],axes[k])
 opp=ca.atan2(basis[BN['THUMB_CMC_R']][2,1],basis[BN['THUMB_CMC_R']][2,2]);mcp=ca.atan2(basis[BN['THUMB_MCP_R']][2,1],basis[BN['THUMB_MCP_R']][2,2]);clip=lambda a:ca.fmin(1,ca.fmax(0,a));shape=ca.fmax(clip((-opp-.37)/.06),clip((-opp-.15)/.15)*clip((-mcp-.175)/.175))
 poses=[];VV=ca.MX.zeros(4,len(W))
 for b,p in enumerate(RAW['parents']):
  J=ca.vertcat(ca.horzcat(basis[b],ca.DM.zeros(3,1)),ca.DM([[0,0,0,1]]));mat=ca.DM(REL[b])@J
  if p>=0:mat=poses[int(p)]@mat
  poses.append(mat);VV+=<REDACTED_EMAIL>(ca.DM(LOCAL[b].T))+shape*(<REDACTED_EMAIL>(ca.DM(SHLOCAL[b].T)))
 world=ca.DM(RAW['base_rig_world']);V=(world@VV)[:3,:];rootR=R(z[5]*np.pi/180,[0,0,1])@R(z[4]*np.pi/180,[0,1,0])@R(z[3]*np.pi/180,[1,0,0]);base=ca.DM(BASE);V=rootR@(V-ca.repmat(base,1,len(W)))+ca.repmat(base+z[:3]/1000,1,len(W));wr=(world@poses[BN['WRIST_R']])[:3,3];wr=rootR@(wr-base)+base+z[:3]/1000
 return ca.Function('frozen_skin',[z],[V,wr,st]),R
if __name__=='__main__':
 t=time.perf_counter();f,R=symbolic_model();prev=O.parent/'hands_contact_junction_compatibility_r1';rows=[]
 for name in ['junction_2','path_1','path_2','path_3','path_4','hold_corrected']:
  a=json.loads((prev/'runs'/(name+'_actual.json')).read_text());v,wr,st=f(a['latent']);V=skin(state(np.array(a['latent'])));audit=np.load(prev/('AUDIT_'+name+'_ACTUAL_SKIN.npz'));print('AUDIT_KEYS',audit.files) if not rows else None
  rows.append(dict(id=name,numeric_skin_max_error_mm=float(abs(np.array(v).T-V).max()*1000),wrist_vs_Blender_mm=float(np.linalg.norm(np.array(wr).ravel()-a['wrist_world_m'])*1000)))
 f.save(str(O/'FROZEN_SKIN_SYMBOLIC.casadi'));out=dict(casadi_version=ca.__version__,rows=rows,build_validation_seconds=time.perf_counter()-t,verified=all(r['numeric_skin_max_error_mm']<1e-6 and r['wrist_vs_Blender_mm']<.001 for r in rows));(O/'SYMBOLIC_MODEL_VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
