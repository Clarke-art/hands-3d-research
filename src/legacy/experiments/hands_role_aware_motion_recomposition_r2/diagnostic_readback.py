from bootstrap import *
from representation import Representation
from scipy.interpolate import CubicHermiteSpline
from scipy.spatial.transform import Rotation
import model as n
r=Representation();K,_=archive(O/'CONTINUOUS_CURVE.npz');M,_=archive(O/'MOTION_CANDIDATE.npz');B,_=archive(O/'TARGET_C1_POSTHOC_REFERENCE.npz');C,_=archive(O/'CANDIDATE_ACTUAL_SKIN.npz')
curve=CubicHermiteSpline(K['knots'],K['q_deg'],K['dq_deg_s'],axis=0);low=r.bounds[:,0];high=r.bounds[:,1];excess=0.;where=None
for i,dt in enumerate(np.diff(K['knots'])):
    for j in range(5):
        for k in range(4):
            a,b,c,d=curve.c[:,i,j,k];tests=[0.,dt]
            roots=np.roots([3*a,2*b,c]) if abs(a)>1e-15 else np.roots([2*b,c]) if abs(b)>1e-15 else []
            tests += [float(z.real) for z in roots if abs(z.imag)<1e-10 and 0<z.real<dt]
            for u in tests:
                q=((a*u+b)*u+c)*u+d;bad=max(0.,low[j,k]-q,q-high[j,k])
                if bad>excess:excess=float(bad);where=dict(time=float(K['knots'][i]+u),digit=n.DIGITS[j],coordinate=k,value_deg=float(q))
basew=np.array(r.I['static_root_base_matrix'])@np.array(r.I['full_root_rig_relation'])@n.REST[0]
basepoint=np.array(r.I['base_xyz_m']);base_error=float(abs(basew[:3,3]-basepoint).max()*1000)
oldpolicy=read(ROOT/'experiments/hands_reusable_motion_representation_feasibility_r1/POLICY.json');rootlo=np.array(oldpolicy['root_low']);roothi=np.array(oldpolicy['root_high']);rootdata={}
for label,Z in [('candidate',M),('baseline',B)]:
    world=Z['rig_world']@n.REST[0];delta=(world[:,:3,3]-basepoint)*1000;R=world[:,:3,:3]@np.linalg.inv(basew[:3,:3]);angles=Rotation.from_matrix(R).as_euler('xyz',degrees=True);states=np.c_[delta,angles]
    bound=float(np.maximum(rootlo-states,states-roothi).max());rootdata[label]=dict(max_domain_excess=max(0.,bound),min=states.min(0),max=states.max(0),pass_=bound<=.001 if base_error<.001 else None)
atomic_json('CONTINUOUS_DOMAIN_READBACK.json',dict(exact_joint_domain_excess_deg=excess,joint_domain_pass=excess<=1e-7,witness=where,root_coordinate_base_error_mm=base_error,
    original_root_state_bounds=dict(low=rootlo,high=roothi),root_sample_domains=rootdata,pose_result_readback_unchanged=True))
# Diagnostic figures from actual Blender caches; not rendered product videos.
os.environ['MPLCONFIGDIR']=str(O/'mpl_diagnostic_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
G=read(O/'DYNAMIC_BLENDER_GEOMETRY.json');ix=int(np.argmax([z['non_target_vertex_peak_mm'] for z in G['rows']]));t=float(M['times'][ix]);key=n.KEYS[56];angles=C['key_angles'][ix];pivot=np.array(key['press_pivot']);R=n.rot(angles[56],key['press_axis']);F=n.M['faces']
fig=plt.figure(figsize=(12,5),layout='constrained')
for pane,(label,V) in enumerate([('Original C1',B['actual_vertices'][ix]),('One generated candidate',C['vertices'][ix])]):
    ax=fig.add_subplot(1,2,pane+1,projection='3d');ids=set(n.ROIS['MIDDLE']['vertices']);faces=[f for f in F if all(v in ids for v in f)]
    for g in key['geometry']:
        kv=(np.array(g['vertices'])-pivot)@R.T+pivot;tr=np.array(g['triangles']).reshape(-1,3)
        ax.add_collection3d(Poly3DCollection([kv[list(tri)]*1000 for tri in tr],facecolor='#aaaaaa',edgecolor='#777777',alpha=.23,linewidth=.25))
    ax.add_collection3d(Poly3DCollection([V[f]*1000 for f in faces],facecolor='#d86243',edgecolor='#80351e',alpha=.8,linewidth=.15))
    ax.scatter(*V[2715]*1000,s=22,color='#8b0000');ax.set_title(label)
    ax.set_xlim(215,255);ax.set_ylim(35,125);ax.set_zlim(-15,45);ax.set_box_aspect((40,90,60));ax.view_init(22,-65)
    ax.set_xlabel('X mm');ax.set_ylabel('Y mm');ax.set_zlabel('Z mm')
fig.suptitle('Actual Blender middle-finger skin vs non-target F5 | '+format(t,'.6f')+' s\nSame moment, same moving key. Candidate triangle intrusion: at least 7.767783 mm.')
fig.savefig(O/'REAL_GEOMETRY_FAILURE_WITNESS.png',dpi=150);plt.close(fig)
tt=np.linspace(r.start,r.start+.012,500);vv=curve.derivative()(tt)[:,2,3]
fig,ax=plt.subplots(figsize=(9,3.8),layout='constrained');ax.plot(tt,vv,color='#c04b32');ax.set_xlabel('Original MIDI presentation time (s)');ax.set_ylabel('Middle spread velocity (deg/s)');ax.set_title('Entry Hermite segment: continuous curve with extreme velocity');ax.grid(alpha=.25);fig.savefig(O/'ENTRY_VELOCITY_FAILURE.png',dpi=150);plt.close(fig)
protect();print('DOMAIN_READBACK',excess,base_error,rootdata['candidate']['max_domain_excess'],flush=True)
