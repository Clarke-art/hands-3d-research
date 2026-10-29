import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D
OUT=Path(__file__).resolve().parent;R=OUT/'renders';R.mkdir(exist_ok=True)
D=json.loads((OUT/'REVIEW_VIEW_DATA.json').read_text(encoding='utf8'));F=D['faces'];E=D['edges']
BC={'A':'#2470b5','B':'#b76a16','C':'#8c4ab4'};RC={'P02':'#c9e6df','P03':'#d9e8f4','P04':'#eee4cb','P05':'#e7dcef','P06':'#d7dce5'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
focus=[f for fs in D['row_faces'].values() for f in fs]
def unit(v):return v/np.linalg.norm(v)
def view_basis(s,v):
    f=D['frames'][s];up=np.array(f['distal_axis']);n=np.array(f['dorsal_axis_from_approved_nail']);r=np.array(f['radial_axis_away_from_frozen_web'])
    look={'DORSAL':n,'PALMAR':-n,'RADIAL':r,'ULNAR':-r}[v];right=unit(np.cross(up,look));return np.array([right,up,look])
def mesh(ax,s,v,option=None,rows=None,context=False):
    Q=np.array(D['vertices'][s]);centre=Q[sorted({x for f in focus for x in F[f]})].mean(0);B=view_basis(s,v);P=(Q-centre)@B.T*1000
    fs=range(len(F)) if context else D['local_context_faces']
    hi={f:RC[row] for row,faces in D['row_faces'].items() for f in faces}
    if context:
        for f in D['frozen_surface_strip_faces']:hi[f]='#b8ddd1'
        for f in D['cap37_faces']:hi[f]='#b9a4d5'
        for f in D['thumb_nail_faces']:hi[f]='#67b7c6'
    if rows:hi={f:c for f,c in hi.items() if f in {f for row in rows for f in D['row_faces'][row]}}
    sort=sorted(fs,key=lambda f:(f in hi,float(P[F[f],2].mean())))
    ax.add_collection(PolyCollection([P[F[f],:2] for f in sort],facecolors=[hi.get(f,'#edf0f3') for f in sort],edgecolors='#9ba5b1',linewidth=.45,alpha=.85))
    choices=[q for q in D['boundaries'] if option is None or q['option']==option]
    for q in choices:
        for e in q['boundary_edges']:
            xy=P[E[e['edge_id']],:2];ax.plot(xy[:,0],xy[:,1],c=BC[q['option']],lw=2.3,zorder=6)
            if not context:
                xy=xy.mean(0);ax.annotate(q['option']+' e'+str(e['edge_id']),xy,xytext=(.02,.96-(ord(q['option'])-65)*.11-(0 if e['lane'].startswith('LEFT') else .05)),textcoords='axes fraction',fontsize=7,color=BC[q['option']],arrowprops={'arrowstyle':'-','color':BC[q['option']],'lw':.6},bbox={'facecolor':'white','edgecolor':'none','alpha':.9},zorder=10)
    for i,(row,faces) in enumerate(D['row_faces'].items()):
        if rows and row not in rows:continue
        pos=P[sorted({x for f in faces for x in F[f]})].mean(0)
        if not context:ax.annotate(row+' '+ '/'.join(map(str,faces)),pos[:2],xytext=(.98,.95-i*.11),textcoords='axes fraction',ha='right',fontsize=7,bbox={'facecolor':'white','edgecolor':'none','alpha':.9},arrowprops={'arrowstyle':'-','color':'#556273','lw':.5},zorder=10)
    if context:
        for seed in D['frozen_first_web_seeds']:
            ax.scatter(*P[seed,:2],s=30,c='#086f65',edgecolors='white',zorder=8);ax.annotate('v'+str(seed),P[seed,:2],xytext=(4,3),textcoords='offset points',fontsize=6)
        for label,faces in [('thumb nail',D['thumb_nail_faces']),('cap37 frozen',D['cap37_faces'])]:
            vs=sorted({x for f in faces for x in F[f]});p=P[vs].mean(0);ax.annotate(label,p[:2],xytext=(10,8),textcoords='offset points',fontsize=7,bbox={'facecolor':'white','edgecolor':'none','alpha':.9},arrowprops={'arrowstyle':'-','color':'#566373'})
        if s=='RSSF':
            chain=np.array(D['frames'][s]['corrected_chain_world_m']);cp=(chain-centre)@B.T*1000;ax.plot(cp[:,0],cp[:,1],'--',color='#364858',lw=1)
            for i,label in enumerate(['CMC approved','MCP approved']):ax.scatter(*cp[i,:2],s=28,marker='X',c='#364858',zorder=8);ax.annotate(label,cp[i,:2],xytext=(4,-9),textcoords='offset points',fontsize=7)
        else:ax.text(.02,.02,'Native MCP/CMC registration not approved.\nApproved joint markers shown in RSSF companion.',transform=ax.transAxes,fontsize=7,bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
    fitfaces=focus if not rows else [f for row in rows for f in D['row_faces'][row]]
    ids=sorted({x for f in fitfaces for x in F[f]})
    if context:ids=sorted(set(ids)|set(D['cap37_vertex_ids'])|set(D['frozen_first_web_seeds'])|{x for f in D['thumb_nail_faces'] for x in F[f]})
    box=P[ids,:2];lo=box.min(0);hi=box.max(0);pad=np.maximum((hi-lo)*(.28 if context else .55),3)
    if context and s=='RSSF':lo=np.minimum(lo,cp[:2,:2].min(0));hi=np.maximum(hi,cp[:2,:2].max(0))
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.grid(alpha=.1)
    ax.set_title(s+' | '+v+' reference side',loc='left',fontweight='bold');ax.set_xlabel('Projected reference distance (mm)');ax.set_ylabel('Approved distal-axis reference (mm)')
def finish(fig,name,title,subtitle):
    fig.suptitle(title,x=.035,y=.98,ha='left',fontsize=17,fontweight='bold');fig.text(.035,.929,subtitle,fontsize=10)
    fig.text(.035,.045,'MACHINE EVIDENCE EXHAUSTED | A/B/C unresolved | Human anatomical adjudication required.',fontsize=11,color='#713e69',fontweight='bold')
    fig.text(.035,.018,'Sides use thumb-local nail / frozen-web references, not a whole-palm normal. Stable original IDs; no production changes.',fontsize=9)
    fig.subplots_adjust(left=.07,right=.97,top=.87,bottom=.14,wspace=.25,hspace=.35);fig.savefig(R/name,dpi=160);plt.close(fig)
def pair(name,title,option=None,rows=None,context=False):
    fig,axs=plt.subplots(2,2,figsize=(15,11),facecolor='#f8fafc')
    for i,s in enumerate(['NATIVE','RSSF']):
        for k,v in enumerate(['DORSAL','ULNAR']):mesh(axs[i,k],s,v,option,rows,context)
    finish(fig,name,title,'Blue A e1375/e1374 | amber B e4666/e4668 | purple C e1376/e1377. Colours identify options only.')
pair('THREE_CANDIDATE_BOUNDARIES_OVERVIEW.png','Three fixed boundary alternatives | equal presentation')
for opt in 'ABC':
    q=next(x for x in D['boundaries'] if x['option']==opt)
    pair('OPTION_'+opt+'_CLOSEUP.png','Option '+opt+' | '+q['stop'],option=opt,rows=q['row_pair'])
pair('P02_EARLY_SIDE_CONTROL.png','P02 early-side control | digit-web dominance unproved',rows=['P02'])
pair('P06_LATE_SIDE_CONTROL.png','P06 late-side control | positive broader role unproved',rows=['P06'])
for s in ['NATIVE','RSSF']:
    fig,axs=plt.subplots(2,2,figsize=(15,11),facecolor='#f8fafc')
    for ax,v in zip(axs.flat,['PALMAR','DORSAL','RADIAL','ULNAR']):mesh(ax,s,v)
    finish(fig,s+'_FOUR_REFERENCE_VIEWS.png',s+' | four anatomical reference sides','Palmar/dorsal = opposite/toward thumb nail. Radial/ulnar = away/toward the frozen first-web context.')
pair('FROZEN_LANDMARK_CONTEXT.png','Frozen nail / cap37 / web seeds and approved joint context',context=True)
print('Rendered',len(list(R.glob('*.png'))),'exact-data review images')
