import json as _lock_json
from pathlib import Path as _LockPath
if __name__ == "__main__" and _lock_json.loads((_LockPath(__file__).resolve().parent / "POLICY_LOCK.json").read_text(encoding="utf-8"))["no_more_solves"]:
    raise SystemExit("STOP — HUMAN REVIEW: completed experiment is locked; use a separately authorized run")
"""Branch-local clipped triangle surface derivative. No note/time identifiers in API."""
import sys,time,json
from pathlib import Path
sys.dont_write_bytecode=True;O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import derivative_probe as d
from derivative_probe import np,ca,save

def surface_chart(rig_state,contact_set,moving_key_geometry,event_time,joint_domain):
 """RigState supplies skin function, triangles, pad face membership and latent vector.
 MovingKeyGeometry is keyed by ContactSet keys and sampled at EventTime.
 Chart includes derivatives of intersections with playable-region boundaries.
 Rebuild every evaluation; face/clip signature changes invalidate prior derivative.
 """
 z=np.asarray(rig_state['z']);F=rig_state['skin'];V=np.array(F(z)[0]);sym=ca.MX.sym('V',3,V.shape[1]);out=[];expr=[]
 if not np.all((z>=joint_domain[0]-1e-8)&(z<=joint_domain[1]+1e-8)):raise ValueError('JointDomain')
 for ct in contact_set:
  if not ct.get('required_contact',True):continue
  key=moving_key_geometry[ct['key']];pv=np.asarray(key['pivot']);R=np.asarray(key['world_to_key_rotation']);loc=R@(V-pv[:,None])+pv[:,None];sy=ca.DM(R)@(sym-ca.repmat(ca.DM(pv),1,V.shape[1]))+ca.repmat(ca.DM(pv),1,V.shape[1]);candidates=[]
  for face in rig_state['pad_faces'][ct['finger']]:
   ids=rig_state['triangles'][face]
   for si,s in enumerate(key['surfaces']):
    poly=[(loc[:,v],sy[:,int(v)],('v',int(v))) for v in ids]
    for axis,lim,sgn in [(0,s['xmin'],-1),(0,s['xmax'],1),(1,s['ymin'],-1),(1,s['ymax'],1)]:
     result=[]
     for aa,bb in zip(poly,poly[1:]+poly[:1]):
      a,sa,ia=aa;b,sb,ib=bb;da=sgn*(a[axis]-lim);db=sgn*(b[axis]-lim)
      if da<=1e-12:result.append(aa)
      if da*db<0:
       alpha=da/(da-db);ssda=sgn*(sa[axis]-lim);ssdb=sgn*(sb[axis]-lim);result.append((a+(b-a)*alpha,sa+(sb-sa)*ssda/(ssda-ssdb),('clip',axis,lim,ia,ib)))
     poly=result
     if not poly:break
    for a,sa,tag in poly:candidates.append((float((a[2]-s['z'])*1000),(sa[2]-s['z'])*1000,int(face),si,tag))
  if not candidates:out.append(dict(status='NON_SMOOTH_OR_UNVERIFIED',reason='no projected pulp face overlaps surface'));continue
  candidates.sort(key=lambda a:a[0]);best=candidates[0];expr.append(best[1]);out.append(dict(signed_min_gap_mm=best[0],face=best[2],surface=best[3],clip_signature=best[4],tied_candidates=sum(abs(x[0]-best[0])<1e-7 for x in candidates),status='BRANCH_LOCAL_ONLY'))
 if not expr:return dict(event_time=event_time,contacts=out,jacobian=np.zeros((0,len(z))),gap=[],signature=[])
 zsym=ca.MX.sym('z',len(z));gg=ca.Function('face_geometry',[sym],[ca.vertcat(*expr)])(F(zsym)[0]);fn=ca.Function('face_value_jac',[zsym],[gg,ca.jacobian(gg,zsym)]);g,j=fn(z)
 return dict(event_time=event_time,contacts=out,jacobian=np.array(j),gap=np.array(g).ravel(),signature=[(x.get('face'),str(x.get('clip_signature'))) for x in out])

if __name__=='__main__':
 start=time.monotonic();I=d.I;patchfaces={}
 for finger in range(1,6):
  ids=set(d.META['pad_patches'][finger-1]);patchfaces[finger]=[int(i) for i in np.flatnonzero(d.LABEL==finger-1) if all(int(v) in ids for v in d.TR[i])]
 source=json.loads((O/'RECOVERY_INPUT.json').read_text());rec=json.loads((O/'runs/recovery_dynamic.json').read_text());angles=np.array(source['actual']['key_angles']);cases=[]
 for label,z in [('original_failure',source['sample']['latent']),('recovered',rec['latent'])]:
  cts=[dict(key=ct['midi'],finger=ct['finger'],required_contact=True) for ct in rec['contacts']];keys={ct['midi']:dict(pivot=d.c.KEYS[ct['midi']-21]['press_pivot'],world_to_key_rotation=d.c.axisrot(-angles[ct['midi']-21],d.c.KEYS[ct['midi']-21]['press_axis']),surfaces=d.c.KEYS[ct['midi']-21]['key_top_playable_surface']) for ct in rec['contacts']}
  def evaluate(zz):return surface_chart(dict(z=zz,skin=d.F,triangles=d.TR,pad_faces=patchfaces),cts,keys,rec['display_time'],(d.LOW-1e-2,d.HIGH+1e-2))
  z=np.array(z);base=evaluate(z);checks=[]
  for h in [1e-3,1e-4,1e-5]:
   cols=[];switch=[]
   for i in range(12):
    step=h*(.1 if i>=10 else 1);delta=np.eye(12)[i]*step;a=evaluate(z+delta);b=evaluate(z-delta);cols.append((a['gap']-b['gap'])/(2*step))
    if a['signature']!=base['signature'] or b['signature']!=base['signature']:switch.append(i)
   fd=np.array(cols).T;checks.append(dict(step=h,max_abs_error=float(abs(fd-base['jacobian']).max()),relative_frobenius=float(np.linalg.norm(fd-base['jacobian'])/max(np.linalg.norm(fd),1e-12)),face_or_clip_switch_variables=switch))
  cases.append(dict(id=label,chart=base,checks=checks))
  save('FACE_SURFACE_VALIDATION.json',dict(cases=cases,scope='Clipped face lower envelope; full crossing/area acceptance remains independent'))
 sequence=json.loads((O/'CONTACT_STATE_SEQUENCE.json').read_text());release=next(x for x in sequence['all_source_sequence'] if x['mode']=='RELEASE' and x['midi']!=rec['contacts'][0]['midi'])
 release_test=surface_chart(dict(z=z,skin=d.F,triangles=d.TR,pad_faces=patchfaces),[dict(key=release['midi'],finger=release['finger'],required_contact=release['required_contact'])],{},release['display_interval'][0],(d.LOW,d.HIGH))
 save('CROSS_MIDI_INTERFACE_CHECK.json',dict(source_episode=release,result=release_test,passed=len(release_test['gap'])==0,scope='Another existing MIDI RELEASE type: no required contact equality. No other-song motion solved. Collision and joint gates are not waived by release.'))
 save('FACE_BUDGET.json',dict(charged_seconds=time.monotonic()-start))
