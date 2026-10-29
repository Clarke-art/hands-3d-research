import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parent;D=json.loads((OUT/'REVIEW_VIEW_DATA.json').read_text());R=OUT/'renders';R.mkdir(exist_ok=True)
F=D['faces'];E=D['edges'];GV=set(D['graph']);T=set(D['THUMB']);I=set(D['INDEX']);N=set(D['neutral']);W=set(D['WEB']);V=np.array(D['vertices'])
C={'THUMB':'#c5533c','INDEX':'#286bb3','neutral':'#91a5b5','web':'#d59826','boundary':'#7440a6','removed':'#e13178'}
def projection(Q,state,view):
 fr=D['frames'][state];dist=np.array(fr['distal_axis']);dors=np.array(fr['dorsal_axis_from_approved_nail']);rad=np.array(fr['radial_axis_away_from_frozen_web']);vertical=dist
 normal=dors if view=='DORSAL' else -dors if view=='PALMAR' else rad
 horizontal=np.cross(vertical,normal);horizontal/=np.linalg.norm(horizontal);vertical=np.cross(normal,horizontal);vertical/=np.linalg.norm(vertical)
 return np.stack([Q@horizontal,Q@vertical],axis=1)*1000
def panel(ax,state,view,mode,focus=None):
 Q=np.array(D['native_vertices'] if state=='NATIVE' else D['vertices']);P=projection(Q,state,view)
 ax.add_collection(PolyCollection([P[fs] for fs in F],facecolors='#e9eef2',edgecolors='#c2cdd5',linewidths=.3,alpha=.28,zorder=0))
 if mode not in ['diff','guards']:
  ax.add_collection(PolyCollection([P[F[f]] for f in D['graph_faces']],facecolors='#dfe7ed',edgecolors='#97a9b8',linewidths=.3,alpha=.6,zorder=1))
 if mode=='hard':
  for ids,color,label in [(T,C['THUMB'],'THUMB hard'),(I,C['INDEX'],'INDEX hard')]:
   q=sorted(ids);ax.scatter(P[q,0],P[q,1],s=12,color=color,label=label,zorder=4)
 elif mode=='neutral':
  for ids,color,size in [(N,C['neutral'],8),(set(D['band']),'#6c8d88',16),(W,C['web'],28)]:
   q=sorted(ids);ax.scatter(P[q,0],P[q,1],s=size,color=color,zorder=4)
 elif mode=='graph':
  ax.add_collection(LineCollection([P[E[e]] for e in D['graph_edges']],colors='#54718b',linewidths=.5,zorder=3))
  for ids,col in [(T,C['THUMB']),(I,C['INDEX']),(W,C['web'])]:
   q=sorted(ids);ax.scatter(P[q,0],P[q,1],s=9,color=col,zorder=4)
 elif mode=='diff':
  q=sorted(GV);ax.scatter(P[q,0],P[q,1],s=7,color='#91a5b5',zorder=2)
  ax.add_collection(LineCollection([P[E[e]] for e in D['removed_edges']],colors=C['removed'],linewidths=3,zorder=5))
  q=D['removed_vertices'];ax.scatter(P[q,0],P[q,1],s=90,marker='*',color=C['removed'],zorder=6)
  for v in q:ax.annotate('removed v'+str(v),P[v],xytext=(12,18),textcoords='offset points',arrowprops={'arrowstyle':'-','color':C['removed']},fontsize=9,color=C['removed'])
 elif mode=='guards':
  for fs,col in [(D['guard_faces'],'#ebd8d9')]:ax.add_collection(PolyCollection([P[F[f]] for f in fs],facecolors=col,edgecolors='#9b6977',linewidths=1,zorder=3))
  for ids,col in [(D['cap'],C['boundary']),(D['thumb_nail'],'#299d9b')]:
   ax.scatter(P[ids,0],P[ids,1],s=16,color=col,zorder=4)
  for j,v in enumerate([304,298,1454]):ax.annotate('v'+str(v),P[v],xytext=(18,14+j*12),textcoords='offset points',arrowprops={'arrowstyle':'-','color':'#526879'},fontsize=9)
 for e in D['boundary_edges']:
  ax.plot(*P[E[e]].T,color=C['boundary'],lw=2.6,zorder=6)
 if mode in ['hard','graph']:
  for v in [284,233]:ax.annotate('tip v'+str(v),P[v],xytext=(8,10),textcoords='offset points',fontsize=9,color='#183b54')
 ids=sorted(focus or GV);p=P[ids];lo=p.min(0);hi=p.max(0);pad=np.maximum((hi-lo)*.13,4);ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.set_axis_off();ax.set_title(state+' / '+view,fontsize=12,color='#254457')
def render(name,title,subtitle,modes,states=None,views=None,focus=None):
 fig,axes=plt.subplots(1,2,figsize=(13,8),facecolor='#f8fafc');fig.suptitle(title,fontsize=19,color='#20384c',x=.04,ha='left',y=.97);fig.text(.04,.918,subtitle,fontsize=10,color='#5c7286')
 for j,ax in enumerate(axes):panel(ax,(states or ['RSSF','RSSF'])[j],(views or ['DORSAL','PALMAR'])[j],modes[j],focus[j] if focus else None)
 legend=[Line2D([0],[0],marker='o',linestyle='',color=C['THUMB'],label='THUMB hard 57'),Line2D([0],[0],marker='o',linestyle='',color=C['INDEX'],label='INDEX hard 145'),Line2D([0],[0],marker='o',linestyle='',color=C['web'],label='FIRST_WEB21: context only'),Line2D([0],[0],color=C['boundary'],lw=2,label='Frozen P04/P05 stop')]
 fig.legend(handles=legend,ncol=4,loc='lower center',bbox_to_anchor=(.5,.025),frameon=False,fontsize=9);fig.text(.04,.015,'Solver workspace / neutral engineering support; no anatomical ownership assigned. No R3 solve performed.',fontsize=9,color='#5c7286');fig.subplots_adjust(top=.875,bottom=.09,wspace=.04);fig.savefig(R/name,dpi=150);plt.close(fig)
render('HARD_SOURCE_MAP.png','Authority-backed hard sources','Unique unions rebuilt from sources. THUMB cap37 + nail; INDEX resolved ingredients. No ambiguous THUMB tube pins.',['hard','hard'])
render('NEUTRAL_INTERFACE_CONTEXT.png','Neutral interface / frozen context','760 unpinned workspace vertices; FIRST_WEB21 hard pins = 0. 47-vertex conservative strip remains engineering context.',['neutral','neutral'],states=['NATIVE','RSSF'],views=['DORSAL','DORSAL'])
render('ENGINEERING_GRAPH_DOMAIN.png','Face-supported engineering graph','962 vertices / 1881 edges / 920 complete faces. One connected component; all sources reachable.',['graph','graph'])
render('GRAPH_CLEANUP_DIFF.png','G3_K2 baseline -> cleaned graph','Deterministic face support removes v3049 and wire (1891,3049). Counts are recomputed, never preserved by exception.',['diff','diff'],views=['DORSAL','DORSAL'],focus=[GV,set(D['removed_vertices'])|set(E[D['removed_edges'][0]])|{v for f in F if 1891 in f for v in f}])
guard=set(D['cap'])|set(D['thumb_nail'])|{v for f in D['guard_faces'] for v in F[f]}
render('DISTAL_CAP_NAIL_GUARDS.png','Frozen distal guards / prior engineering evidence','Do not propagate neutral strip into face1177/nail v304 or face1227/cap v298,v1454. No new distal Human freeze.',['guards','guards'],focus=[guard,guard])
# The approved boundary closeup is reused as historical geometry context only.
p=OUT.parents[1]/'audits/proximal_partial_circumference_semantic_boundary_authority_r1/renders/OPTION_B_CLOSEUP.png'
(R/'FROZEN_P04_P05_BOUNDARY.png').write_bytes(p.read_bytes())
print('Six scientific review PNGs generated.')
