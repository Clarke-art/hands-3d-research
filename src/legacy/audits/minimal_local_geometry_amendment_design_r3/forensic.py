import sys
sys.dont_write_bytecode=True
from contact_geometry import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ca=read(OUT/'FACE204_207_CONTACT_CAUSAL_AUDIT_R3.json');ca['onset_cause']['mechanism']='Both face fields are required in the face-motion counterfactual. Tangent-X or tangent-Y alone produces a crossing, while normal-only does not. Restoring 3308 or 3324 individually removes it; no individual moved vertex alone creates it. Starting at vertex2531 versus face207 interior with 0.024319952mm separation, relative tangential motion changes the closest feature ordering and exhausts the separation at t=0.735918486. Face rotations are only 5.778deg and0.738deg. Therefore the observed recurrence is a jointly driven local tangential side/feature reordering, rather than a large-normal-rotation event or one uniquely faulty vertex.'
dump('FACE204_207_CONTACT_CAUSAL_AUDIT_R3.json',ca)
r2=ROOT/'audits/minimal_local_geometry_amendment_design_r2';vv=np.array(read(r2/'REVIEW_COORDINATES_R2.json')['states']['FAILED_SOLVE_S5']['RSSF_RAW']);delta=vv-V
fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained');grid=ca['interpolation_onset_sweep'];t=np.array([p['fraction'] for p in grid]);distance=np.array([p['minimum_separation_mm'] for p in grid]);cross=np.array([p['segment_mm'] for p in grid])
axes[0].plot(t,distance,color='#246b82');axes[0].set(xlabel='baseline to R2-S5 fraction',ylabel='Separation (mm)',title='Initial separation 0.024319952 mm');axes[1].plot(t,cross,color='#ac4032');axes[1].set(xlabel='baseline to R2-S5 fraction',ylabel='Exact crossing length (mm)',title='New204/207 crossing onset')
for ax in axes:
 for key,color in [('first_near_contact','#ce9d27'),('first_exact_contact','#8d295a')]:ax.axvline(ca[key]['fraction'],color=color,ls='--',label=key)
 ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.savefig(OUT/'renders/CONTACT_ONSET_SWEEP.png',dpi=150);plt.close(fig)
fig=plt.figure(figsize=(16,4.5),layout='constrained')
for j,(label,tau) in enumerate([('BASELINE',0),('JUST BEFORE',ca['first_near_contact']['fraction']),('FIRST CROSSING',ca['first_crossing']['fraction']),('R2-S5 FAILED',1)]):
 ax=fig.add_subplot(1,4,j+1,projection='3d');v=V+tau*delta;q=(v-origin)@B
 for fi,color in [(204,'#327f91'),(207,'#c65545')]:
  p=q[F[fi]];ax.add_collection3d(Poly3DCollection([p],facecolor=color,edgecolor=color,alpha=.45))
  for i in F[fi]:ax.text(*q[i],str(i),fontsize=7)
 m=face_pair_metrics(v);p=np.array(m['closest_features']['closest_world_mm']);p=(p-origin)@B;ax.plot(*p.T,color='black',lw=2)
 ax.set(xlim=(-5.5,1.5),ylim=(-1,11),zlim=(-2,2),title=label+'\nt='+format(tau,'.9f'));ax.view_init(elev=22,azim=-38);ax.set_box_aspect((7,12,4));ax.set_xlabel('x');ax.set_ylabel('y');ax.set_zlabel('normal')
fig.suptitle('204/207 native cycles + closest features; computational geometry forensic');fig.savefig(OUT/'renders/FACE204_207_FORENSIC.png',dpi=150);plt.close(fig)
print('CAUSAL FORENSICS COMPLETE')
