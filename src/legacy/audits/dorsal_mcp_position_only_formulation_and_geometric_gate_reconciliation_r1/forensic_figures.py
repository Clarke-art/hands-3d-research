import sys
sys.dont_write_bytecode=True
from semantic_audit import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Polygon

FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f5f7fa','axes.facecolor':'white','savefig.facecolor':'#f5f7fa'})
blue='#1677a6';orange='#e69735';green='#247b5c';red='#b23f46'
def save(fig,name):fig.savefig(FIG/name,dpi=160,bbox_inches='tight');plt.close(fig)
def fan3(ax,pp,labels=None):
 ax.add_collection3d(Poly3DCollection([pp[[0,1,2]],pp[[0,2,3]]],facecolors=[blue,orange],alpha=.3,edgecolors='none'))
 for k in range(4):
  a,b=pp[k],pp[(k+1)%4];ax.plot(*np.array([a,b]).T,color=blue if k%2==0 else orange,lw=2)
 ax.plot(*pp[[0,2]].T,color='#626c78',ls='--',lw=1)
 ax.scatter(*pp.T,color='#243747',s=18)
 span=np.maximum(np.ptp(pp,axis=0),.08);ax.set_box_aspect(span);ax.auto_scale_xyz(pp[:,0],pp[:,1],pp[:,2]);ax.set_xticks([]);ax.set_yticks([]);ax.set_zticks([]);ax.text2D(.02,.03,'Centered world axes / mm; vertex IDs in chart at right',transform=ax.transAxes,fontsize=8);ax.view_init(25,-62)

def bows():
 d=read(OUT/'PROJECTED_BOWTIE_SEMANTICS_AUDIT_R1.json');fig=plt.figure(figsize=(13,15))
 for row,(fid,z) in enumerate(d['flags'].items()):
  ax=fig.add_subplot(3,2,row*2+1,projection='3d');pp=np.array(z['world_mm']);pp-=pp.mean(0);fan3(ax,pp,z['native_cycle']);gap=min(t['minimum_3D_distance_mm'] for t in z['opposite_boundary_edge_tests']);ax.set_title(f'Face {fid}: native 3D fan\nminimum opposite-edge gap = {gap:.6f} mm',pad=18)
  ax=fig.add_subplot(3,2,row*2+2);q=np.array(z['projection_diagnostic']['points_chart_mm'])
  for k in range(4):ax.plot(*q[[k,(k+1)%4]].T,color=blue if k%2==0 else orange,lw=2)
  ax.plot(*q[[0,2]].T,color='#626c78',ls='--',lw=1);ax.scatter(*q.T,color='#243747',s=20)
  for k,p in enumerate(q):ax.annotate(str(z['native_cycle'][k]),p,xytext=(5,6),textcoords='offset points',fontsize=9)
  for h in z['projection_diagnostic']['hits']:ax.scatter(*h['intersection_chart_mm'],marker='x',color=red,s=100,lw=2)
  ax.set_aspect('equal',adjustable='datalim');ax.grid(alpha=.15);ax.set_xlabel('SVD chart u / mm');ax.set_ylabel('SVD chart v / mm');ax.set_title(f'Face {fid}: projection-only crossing\nfan interiors share ONLY the legal native diagonal')
 fig.suptitle('Frozen source: projected bow-ties and actual 3D geometry',fontsize=17,y=.99);fig.text(.05,.005,'Classification concerns the intrinsic fan. Face 3351 also has separate source-existing contacts with faces 2784 and 2787; those remain structural evidence.',fontsize=10)
 fig.tight_layout(rect=(0,.025,1,.97));save(fig,'PROJECTED_BOWTIE_3D_VS_CHART.png')

def shared():
 d=read(OUT/'SHARED_EDGE_CONTACT_SEMANTICS_R1.json');fig=plt.figure(figsize=(14,10))
 for k,(label,v) in enumerate([('FROZEN_BASELINE',V),('R3_BEST_FAILED_POINT',P)]):
  ax=fig.add_subplot(2,2,k+1,projection='3d');center=v[[79,955]].mean(0);aa=v[[3025,955,79]]-center;bb=v[[79,955,3340]]-center
  ax.add_collection3d(Poly3DCollection([aa,bb],facecolors=[blue,orange],edgecolors=[blue,orange],alpha=.4,lw=1.5));pp=v[[3025,955,79,3340]]-center
  for vi,p in zip([3025,955,79,3340],pp):ax.text(*p,' '+str(vi),fontsize=9)
  ax.plot(*(v[[79,955]]-center).T,color=green,lw=4);span=np.maximum(np.ptp(pp,axis=0),.08);ax.set_box_aspect(span);ax.auto_scale_xyz(pp[:,0],pp[:,1],pp[:,2]);ax.view_init(23,-72)
  h=d['finite_shared_edge_fold_limit'][label]['preserved_signed_corner_to_opposite_triangle_plane_height_mm'];ax.set_title(f'{label.replace("_"," ")}\nshared edge 79/955: legal zero distance\nfinite corner-to-plane side margin = {h:.9g} mm',pad=15);ax.set_xticks([]);ax.set_yticks([]);ax.set_zticks([]);ax.text2D(.03,.02,'Centered world axes / mm',transform=ax.transAxes,fontsize=9)
 for slot,same in [(3,False),(4,True)]:
  ax=fig.add_subplot(2,2,slot);a=np.array([[0,0],[1,0],[.5,1]]);b=np.array([[0,0],[1,0],[.5,.5 if same else -.8]])
  ax.add_patch(Polygon(a,color=blue,alpha=.3));ax.add_patch(Polygon(b,color=orange,alpha=.5));ax.plot([0,1],[0,0],color=green,lw=4);ax.set_xlim(-.15,1.15);ax.set_ylim(-1.05,1.2);ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_title('SYNTHETIC same-side coplanar limit: HARD FAIL' if same else 'SYNTHETIC opposite-side flat adjacency: LEGAL');ax.text(.02,.03,'shared edge',color=green)
 fig.suptitle('2182 / 3330: release legal shared contact; retain off-edge protection',fontsize=16,y=.99);fig.tight_layout(rect=(0,.015,1,.965));save(fig,'SHARED_EDGE_FINITE_FEATURE_RELATION.png')

def descent():
 d=read(OUT/'LOCAL_FEASIBLE_DESCENT_ANALYSIS_R1.json');point=d['points']['R3_BEST_FAILED_POINT'];dirs=point['directions'];selected=[dirs[i] for i in [0,1,2,3,4,5,6]];names=['joint metric','joint cone','R3 side cone','valley tangent','cross tangent','surface normal','old net micro'];fields=['dent_depth_derivative_mm_per_mm_peak','edge6676_derivative_deg_per_mm_peak','reference_continuity_derivative_mm2_per_mm_peak'];titles=['Dent-depth derivative / mm per mm peak','6676 angle derivative / deg per mm peak','Reference continuity derivative / mm2 per mm peak']
 fig,axs=plt.subplots(2,2,figsize=(15,10));colors=[green,green,green,blue,red,blue,orange]
 for ax,key,title in zip(axs.ravel()[:3],fields,titles):
  vals=[r['derivatives'][key] for r in selected];ax.barh(names,vals,color=colors);ax.axvline(0,color='#233746',lw=.8);ax.invert_yaxis();ax.set_title(title);ax.grid(axis='x',alpha=.15)
 ax=axs.ravel()[3];ax.axis('off');rows=[]
 for name,r in zip(names,selected):
  step=next(z for z in r['micro_steps'] if z['step_max_mm']==1e-5);rows.append([name,'NO', 'YES' if step['CURRENT_R3_ITERATION_GATE_PASS'] else 'NO','YES' if step['true3D_gate_pass'] else 'NO','YES' if step['reconciled_gate_pass'] else 'NO'])
 t=ax.table(cellText=rows,colLabels=['direction','full R3*','iteration','true 3D','reconciled'],bbox=[0,.25,1,.65],cellLoc='center',colWidths=[.32,.17,.17,.17,.17]);t.auto_set_font_size(False);t.set_fontsize(9)
 for (r,c),cell in t.get_celld().items():
  cell.set_edgecolor('#d5dde5')
  if r==0:cell.set_facecolor('#e6edf4')
  elif c>0:cell.set_text_props(color=green if cell.get_text().get_text()=='YES' else red)
 ax.set_title('Gate comparison at a 0.00001 mm diagnostic micro step');ax.text(0,.05,'*Full R3 geometric eligibility rejects existing projected flags.\nIteration guards accept the certified joint directions.\nNo shape completion, geometry candidate or production write.',transform=ax.transAxes,fontsize=10)
 fig.suptitle('Local descent still exists at the R3 failed point',fontsize=17);fig.tight_layout(rect=(0,0,1,.96));save(fig,'LOCAL_DESCENT_AND_GATE_COMPARISON.png')

def coplanar():
 fig,axs=plt.subplots(2,3,figsize=(14,9));a=np.array([[0,0],[1,0],[0,1]]);start=a+[2,0]
 for ax,t,title in zip(axs[0],[0,.5,1],['t=0: disjoint','t=1/2: positive-area overlap','t=1: disjoint']):
  b=start+[-4*t,0];ax.add_patch(Polygon(a,color=blue,alpha=.4));ax.add_patch(Polygon(b,color=orange,alpha=.5));ax.set_xlim(-2.3,3.3);ax.set_ylim(-.3,1.3);ax.set_aspect('equal');ax.set_title(title,color=red if t==.5 else '#243747');ax.grid(alpha=.2);ax.set_xlabel('common-plane u / mm')
 axs[1,0].axis('off');axs[1,0].text(.03,.9,'All 3D four-point volume polynomials\nare identically zero on this path.\n\nEndpoint-only tests miss the collision.\nContinuous 2D finite-feature event\npartition detects the intermediate overlap.\n\nNo added surface clearance.',va='top',fontsize=13)
 for ax,same in zip(axs[1,1:],[False,True]):
  u=np.array([[0,0],[1,0],[.5,1]]);w=np.array([[0,0],[1,0],[.5,.5 if same else -1]])
  ax.add_patch(Polygon(u,color=blue,alpha=.35));ax.add_patch(Polygon(w,color=orange,alpha=.5));ax.plot([0,1],[0,0],color=green,lw=4);ax.set_xlim(-.2,1.2);ax.set_ylim(-1.2,1.2);ax.set_aspect('equal');ax.set_title('Off-edge area: HARD FAIL' if same else 'Only shared edge: LEGAL');ax.grid(alpha=.2)
 fig.suptitle('Persistent coplanarity needs feature-aware continuous checks',fontsize=17);fig.tight_layout(rect=(0,0,1,.95));save(fig,'PERSISTENT_COPLANAR_NEGATIVE_CONTROL.png')

if __name__=='__main__':bows();shared();descent();coplanar();print('FORENSIC_FIGURES 4 COMPLETE')
