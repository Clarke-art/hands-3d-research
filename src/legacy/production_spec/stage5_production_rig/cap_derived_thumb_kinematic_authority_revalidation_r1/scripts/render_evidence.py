from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.lines import Line2D
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];R=OUT/'renders';R.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
D=read(OUT/'RAW_READ_ONLY_GEOMETRY_AND_BONES.json');G=read(OUT/'GEOMETRIC_EVIDENCE_COMPUTATION.json');Q=read(OUT/'STATIC_GEOMETRY_GATES_AND_FRAME_METRICS.json')
A=read(OUT.parent/'stage5b_r1e_human_cap_authority_freeze_r1/THUMB_DISTAL_CAP_CANONICAL_AUTHORITY_R1.json')
V=np.array(D['RSSF']['vertices_world_m']);F=D['RSSF']['faces'];H=np.array(G['IP_current_head_world_m']);domain=set(G['native_domain_vertex_ids']);C=G['candidate'];M=np.array(C['THUMB_IP_R']['frame_XYZ']);x,y,z=M.T
colors={'current':'#d94b4b','evidence':'#009ab0','candidate':'#27a45c','cap':'#edae28','nail':'#9562cd','tip':'#111827'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
def unit(v):return v/np.linalg.norm(v)
def projection(camera,up):
 camera=unit(camera);right=unit(np.cross(up,camera));up=unit(np.cross(camera,right));return np.array([right,up,camera]).T
def legends(ax):
 items=[Line2D([0],[0],color=colors[k],lw=3,label=t) for k,t in [('current','Current R2A'),('evidence','Independent geometry'),('candidate','Candidate (not applied)'),('cap','Frozen cap37 surface'),('nail','Approved nail')]]
 items.append(Line2D([0],[0],color=colors['tip'],marker='*',lw=0,label='Mapped native v284'))
 ax.legend(handles=items,loc='center left',bbox_to_anchor=(1.02,.7),fontsize=9,framealpha=.96)
def base(ax,P):
 W=(V-H)@P*1000
 fi=[i for i,f in enumerate(F) if all(v in domain for v in f) and max(W[f,1])>-33]
 ax.add_collection(PolyCollection([W[F[i],:2] for i in fi],facecolors='#e4eaf0',edgecolors='#a6b1bf',lw=.45,alpha=.65))
 context=[i for i,f in enumerate(F) if not all(v in domain for v in f) and np.min(np.linalg.norm(V[f]-H,axis=1))<.042]
 ax.add_collection(PolyCollection([W[F[i],:2] for i in context],facecolors='none',edgecolors='#bdc3ca',lw=.3,alpha=.3,zorder=0))
 for fs,col in [(A['face_ids'],colors['cap']),(G['nail_face_ids'],colors['nail'])]:
  ax.add_collection(PolyCollection([W[F[i],:2] for i in fs],facecolors=col,edgecolors=col,lw=.8,alpha=.5,zorder=2))
 for loop in G['IP_true_edge_loops']:
  ax.add_collection(LineCollection([W[D['RSSF']['edges'][e],:2] for e in loop['edge_ids']],colors=colors['evidence'],lw=1,alpha=.65,zorder=3))
 sections=np.array([s['center_world_m'] for s in G['RSSF_locator']['sections']]);s=(sections-H)@P*1000
 ax.plot(s[:,0],s[:,1],':',c=colors['evidence'],lw=2,zorder=5)
 v=W[284];ax.scatter(*v[:2],marker='*',s=160,c=colors['tip'],zorder=12,edgecolors='white',lw=.8)
 return W
def bones(ax,P):
 for key,table in [('current',D['R2A']['bones']),('candidate',C)]:
  for name in ['THUMB_IP_R','THUMB_TIP_R']:
   b=table[name];pts=(np.array([b['head_world_m'],b['tail_world_m']])-H)@P*1000
   ax.plot(pts[:,0],pts[:,1],'-' if name=='THUMB_IP_R' else '--',c=colors[key],lw=2.8,marker='o' if key=='current' else 's',ms=4,zorder=7 if key=='current' else 8)
def finish(ax,title):
 ax.set_aspect('equal');ax.set_xlabel('Local projected distance (mm)');ax.set_ylabel('Local projected distance (mm)');ax.grid(alpha=.18);ax.set_title(title,loc='left',fontsize=15,fontweight='bold',pad=14)
def render(name,camera,up):
 P=projection(camera,up);fig,ax=plt.subplots(figsize=(13,9));W=base(ax,P);bones(ax,P);legends(ax)
 if name=='TIP':
  ax.scatter(*W[284,:2],s=260,facecolors='none',edgecolors=colors['candidate'],lw=2,zorder=11)
  ax.annotate('Candidate axis projects to v284',xy=W[284,:2],xytext=(7,-14),arrowprops=dict(arrowstyle='->',color=colors['candidate']),color=colors['candidate'],fontsize=9)
 pts=np.vstack([W[A['vertex_ids'],:2],(np.array([D['R2A']['bones']['THUMB_TIP_R']['tail_world_m'],C['THUMB_TIP_R']['tail_world_m'],H])-H)@P[:,:2]*1000])
 lo=pts.min(0)-np.array([17,15]);hi=pts.max(0)+np.array([14,12]);ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);finish(ax,'Thumb distal kinematics / '+name)
 fig.text(.12,.015,'READ ONLY  |  IP head retained  |  TIP head delta 12.027 mm  |  axis delta 13.934 deg\nGrey background is RSSF geometry context; surface membership is not an endpoint rule.',fontsize=10)
 fig.subplots_adjust(bottom=.13,right=.72);fig.savefig(R/('THUMB_DISTAL_KINEMATIC_CURRENT_VS_INDEPENDENT_'+name+'.png'),dpi=160);plt.close(fig)
for name,camera,up in [('DORSAL',z,y),('PALMAR',-z,y),('RADIAL',-x,y),('ULNAR',x,y),('SIDE',unit(x+z),y),('TIP',y,z)]:render(name,camera,up)
P=projection(G['RSSF_locator']['axis'],G['dorsal_cue']);fig,ax=plt.subplots(figsize=(10,9));W=(V-H)@P*1000
for loop in G['IP_true_edge_loops']:
 ax.add_collection(LineCollection([W[D['RSSF']['edges'][e],:2] for e in loop['edge_ids']],colors=colors['evidence'],lw=1.4,alpha=.5))
for key,col in [('current',colors['current']),('independent',colors['evidence'])]:
 row=Q['cross_sections'][key];hits=np.array([r['hit_world_m'] for r in row['rays']]);poly=(hits-H)@P*1000;poly=np.vstack([poly,poly[0]]);ax.plot(poly[:,0],poly[:,1],c=col,lw=2,label=key+' plane / 16 radial hits');p=(np.array(row['center_world_m'])-H)@P*1000;ax.scatter(*p[:2],c=col,s=90,marker='o' if key=='current' else 'x',zorder=10)
ax.scatter(0,0,s=160,marker='s',facecolors='none',edgecolors=colors['candidate'],lw=2,label='Candidate = current head',zorder=11)
ax.autoscale();ax.margins(.22);ax.legend(loc='upper left');finish(ax,'IP cross-section / independently reconstructed')
fig.text(.12,.025,'Independent locator vs current head: 1.116 mm (3D); width sensitivity: 0.708–2.005 mm.\nCurrent clearance: 6.220 mm; all 16 radial directions intersect the native thumb surface.\nCyan loops: approved topological opposite-edge traversal, rerun on current RSSF topology.',fontsize=10)
fig.subplots_adjust(bottom=.16);fig.savefig(R/'THUMB_IP_CROSS_SECTION_REVALIDATION.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(15,8));P=projection(unit(x+z),y)
for ax,name in zip(axs,['THUMB_IP_R','THUMB_TIP_R']):
 for key,table in [('current',D['R2A']['bones']),('candidate',C)]:
  b=table[name];m=np.array(b['matrix_local'])[:3,:3] if key=='current' else np.array(b['frame_XYZ']);h=np.array(b['head_world_m']);hp=(h-H)@P*1000
  for i,lab in enumerate('XYZ'):
   ep=(h+m[:,i]*.012-H)@P*1000;ax.annotate('',xy=ep[:2],xytext=hp[:2],arrowprops=dict(arrowstyle='->',color=colors[key],lw=2,linestyle='-' if key=='candidate' else '--'));ax.text(ep[0],ep[1],lab,color=colors[key],fontweight='bold')
  ax.scatter(*hp[:2],c=colors[key],label=key,s=50)
 ev=np.array(G['RSSF_locator']['IP']['center_world_m'] if name=='THUMB_IP_R' else G['mapping']['rssf_v284_world_m']);p=(ev-H)@P*1000;ax.scatter(*p[:2],c=colors['evidence'],marker='x',s=80,label='Independent landmark')
 ax.set_xlim(-19,20);ax.set_ylim(-10,48 if name=='THUMB_TIP_R' else 20);finish(ax,name);ax.legend()
fig.suptitle('Local axes / nail-oriented frame comparison',fontsize=18,fontweight='bold');fig.text(.08,.03,'Solid green: candidate; dashed red: current. +Y longitudinal, +Z projected nail dorsal, +X = Y cross Z (ulnar cue).\nAxis change 13.934 deg | Blender roll coordinate change 0.457 deg | transported twist change 1.964 deg | no 180-degree flip',fontsize=11)
fig.subplots_adjust(bottom=.16,top=.87,wspace=.2);fig.savefig(R/'THUMB_IP_TIP_FRAME_AXES_COMPARISON.png',dpi=160);plt.close(fig)
print('WROTE 8 evidence PNGs')
