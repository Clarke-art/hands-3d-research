import sys
sys.dont_write_bytecode=True
from geometry import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
RE=read(OUT/'REVIEW_COORDINATES_R2.json');labels=list(RE['states']);data={k:np.array(RE['states'][k]['RSSF_RAW']) for k in labels}
manifest=[]
for tag,faceids,ei in [('EDGE6675',[3344,3345],6675),('EDGE6602',[3298,3301],6602),('NEW_CONTACT_204_207',[204,207],None)]:
 vids=sorted({i for fi in faceids for i in F[fi]});center=V[vids].mean(0);allq=np.vstack([(v[vids]-center)@B for v in data.values()]);mid=(allq.max(0)+allq.min(0))*.5;radius=float(np.max(np.ptp(allq,axis=0)))*.6
 fig=plt.figure(figsize=(13,4.5),layout='constrained');results={}
 for j,(label,v) in enumerate(data.items()):
  ax=fig.add_subplot(1,3,j+1,projection='3d');q=(v-center)@B
  for fi,color in zip(faceids,['#39a1b2','#d99742']):
   p=F[fi];polys=[q[[p[0],p[k],p[k+1]]] for k in range(1,len(p)-1)];ax.add_collection3d(Poly3DCollection(polys,facecolor=color,edgecolor='#33434c',alpha=.5,linewidth=.8))
   pos=q[p].mean(0);ax.text(*pos,'f'+str(fi),fontsize=8);nn=normal(v,p)@B;ax.quiver(*pos,*nn,length=.7,color=color)
  for i in vids:ax.text(*q[i],str(i),fontsize=7)
  segments=[]
  if ei is not None:
   p=q[E[ei]];ax.plot(*p.T,color='#c72d38',linewidth=3);title=f'{label}\nedge{ei}: {angles(v)[ei]:.4f} degrees'
  else:
   fa,fb=faceids
   for aidx in range(1,len(F[fa])-1):
    a=v[[F[fa][0],F[fa][aidx],F[fa][aidx+1]]]-center
    for bidx in range(1,len(F[fb])-1):
     b=v[[F[fb][0],F[fb][bidx],F[fb][bidx+1]]]-center;pts=[]
     for aa,bb in [(a,b),(b,a)]:
      for p,r in zip(aa,np.roll(aa,-1,axis=0)):
       hit=edge_tri(p,r,bb)
       if hit is not None:pts.append(hit)
     if len(pts)>1:
      pp,rr=max(((p,r) for p in pts for r in pts),key=lambda z:np.linalg.norm(z[0]-z[1]))
      if np.linalg.norm(pp-rr)>eps:
       segment=np.array([pp,rr])@B;ax.plot(*segment.T,color='#c72d38',linewidth=4);segments.append({'native_face_ids':faceids,'fan_triangle_indices':[aidx,bidx],'world_mm':[(pp+center).tolist(),(rr+center).tolist()],'length_mm':float(np.linalg.norm(pp-rr))})
   title=label+'\n'+('NEW exact segment' if segments else 'No exact segment')
  ax.set_title(title,fontsize=10);ax.set(xlim=(mid[0]-radius,mid[0]+radius),ylim=(mid[1]-radius,mid[1]+radius),zlim=(mid[2]-radius,mid[2]+radius),xlabel='tangent x mm',ylabel='tangent y mm',zlabel='normal mm');ax.set_box_aspect((1,1,1));ax.view_init(elev=24,azim=-65)
  results[label]={'intersection_segments':segments,'dihedral_deg':float(angles(v)[ei]) if ei is not None else None}
 fig.suptitle(tag+' | isolated native incident faces; normal arrows / red edge or exact segment; diagnostic only',fontsize=11);name=tag+'_FORENSIC.png';fig.savefig(OUT/'renders'/name,dpi=150);plt.close(fig);manifest.append({'path':'renders/'+name,'faces':faceids,'edge':ei,'data':results,'not_production_surface_view':True})
profiles=read(OUT/'R2_ACTUAL_CROSS_SECTIONS.json')['profiles'];fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
from matplotlib.collections import LineCollection
for j,ax in enumerate(axes):
 for label,col in zip(labels,['#aa4034','#bd9229','#197e8b']):ax.add_collection(LineCollection([s['profile_mm'] for s in profiles[label]['RSSF_RAW'][j]['segments']],colors=col,lw=1.5,label=label))
 ax.set(xlim=(-8,8),ylim=(-3,3),xlabel='Section distance mm',ylabel='Normal height mm',title=f'{[0,60,120][j]} degrees | central zoom');ax.set_aspect('equal',adjustable='box');ax.grid(alpha=.15)
axes[0].legend(fontsize=8);fig.suptitle('Same measured sections, matched central zoom; no anatomical acceptance threshold');fig.savefig(OUT/'renders'/'CENTRAL_SECTION_ZOOM.png',dpi=150);plt.close(fig)
dump('R2_ISOLATED_BOUNDARY_AND_CONTACT_FORENSIC.json',{'plots':manifest,'native_ids_unchanged':True,'coordinates_not_changed_for_plot':True,'fan_visualization_only_not_topology_edit':True})
print('FORENSIC',len(manifest))
