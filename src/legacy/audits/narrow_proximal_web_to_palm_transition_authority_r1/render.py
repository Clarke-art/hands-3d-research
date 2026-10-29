"""Exact-data scientific plots, restricted to the fixed local patch."""
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
OUT=Path(__file__).resolve().parent; R=OUT/'renders';R.mkdir(exist_ok=True)
P=json.loads((OUT/'PROXIMAL_TRANSITION_LOCAL_PATCH_R1.json').read_text(encoding='utf8'))
S=P['states']; C={'P02':'#3b9b83','P03':'#e5bd53','P04':'#ef9354','P05':'#c76485','P06':'#8a79c6'}
SC={'NATIVE':'#218a78','RSSF':'#466cc1'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def finish(fig,name,title,subtitle):
    fig.suptitle(title,x=.04,y=.98,ha='left',fontsize=18,fontweight='bold')
    fig.text(.04,.929,subtitle,fontsize=10)
    fig.text(.04,.045,'FAIL CLOSED | geometric transition supported; unique anatomical role boundary unproved.',color='#a63048',fontsize=11,fontweight='bold')
    fig.text(.04,.018,'Frozen stable IDs | P02-P06 and direct incident faces only | no radius, ownership, solver, production or blend writes',fontsize=9)
    fig.subplots_adjust(left=.08,right=.97,bottom=.14,top=.87,wspace=.3,hspace=.35)
    fig.savefig(R/name,dpi=160);plt.close(fig)
def basis(state):
    rows=S[state]['rows'];axis=np.array(rows[0]['thumb_chain_relation']['axis_vector']); t=np.array(rows[0]['frame']['transverse'])
    x=t-axis*(t@axis);x=x/np.linalg.norm(x);z=np.cross(x,axis)
    origin=np.array(rows[2]['centre_world_m']);return origin,np.array([x,axis,z])
def mesh(ax,state,selected=None,side=False,vertexlabels=False,frames=False,landmarks=False,normalarrows=False):
    d=S[state];origin,B=basis(state);Q={int(v):(np.array(p)-origin)@B.T*1000 for v,p in d['vertex_positions_world_m'].items()}
    dims=[2,1] if side else [0,1];selected=set(selected or P['row_ids'])
    highlights={f:C[r['row_id']] for r in d['rows'] if r['row_id'] in selected for f in r['face_ids']}
    context=P['direct_incident_face_ids']; faceinfo=P['topology']['faces']
    order=sorted(context,key=lambda f:(f in highlights,np.mean([Q[v][0 if side else 2] for v in faceinfo[str(f)]['vertex_ids']])))
    polys=[[Q[v][dims] for v in faceinfo[str(f)]['vertex_ids']] for f in order]
    ax.add_collection(PolyCollection(polys,facecolors=[highlights.get(f,'#e5e9ee') for f in order],edgecolors='#8994a2',linewidth=.65,alpha=.88))
    for r in d['rows']:
        if r['row_id'] not in selected:continue
        ct=(np.array(r['centre_world_m'])-origin)@B.T*1000
        if side and not landmarks:
            ax.text(*ct[dims],r['row_id']+'\n'+ '/'.join(map(str,r['face_ids'])),ha='center',va='center',fontsize=8,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none','pad':1},zorder=8)
        elif not side:
            labelids=[x for x in d['rows'] if x['row_id'] in selected];j=next(i for i,x in enumerate(labelids) if x['row_id']==r['row_id'])
            ax.annotate(r['row_id']+' '+ '/'.join(map(str,r['face_ids'])),ct[dims],xytext=(.96,.9-j*.15),textcoords='axes fraction',ha='right',fontsize=8,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none','pad':1},arrowprops={'arrowstyle':'-','color':'#536475','lw':.7},zorder=10)
        for kind,ls in [('incoming','--'),('outgoing','-')]:
            vs=r['frontiers'][kind]['ordered_vertex_ids']; vv=np.array([Q[v][dims] for v in vs]);ax.plot(vv[:,0],vv[:,1],ls,c='#314759',lw=1)
        if frames or normalarrows:
            keys=['longitudinal','transverse','surface_normal'] if frames else ['surface_normal']
            for key,col in zip(keys,['#265cda','#09806a','#c23c59'] if frames else ['#c23c59']):
                v=np.array(r['frame'][key])@B.T*2.8;ax.arrow(*ct[dims],*v[dims],color=col,width=.035,head_width=.28,length_includes_head=True,zorder=6)
    focused={v for r in d['rows'] if r['row_id'] in selected for v in r['vertex_ids']}
    if vertexlabels and side:
        for v in sorted(focused):
            ax.scatter(*Q[v][dims],s=13,c='#263748',zorder=8)
            ax.annotate(str(v),Q[v][dims],xytext=(3,3),textcoords='offset points',fontsize=7,zorder=9)
    box=np.array([Q[v][dims] for v in focused]);lo=box.min(0);hi=box.max(0);pad=np.maximum((hi-lo)*.35,2)
    if landmarks:
        chain=np.array(d['rows'][0]['thumb_chain_relation']['chain_points_world_m']);X=(chain[:2]-origin)@B.T*1000
        ax.plot(X[:,dims[0]],X[:,dims[1]],'--',color='#344960',lw=1.2)
        for i,label in enumerate(['CMC structural reference','MCP structural reference']):
            ax.scatter(*X[i,dims],marker='X',c='#344960',s=45,zorder=9);ax.annotate(label,X[i,dims],xytext=(5,6),textcoords='offset points',fontsize=8)
        box=np.vstack([box,X[:,dims]]);lo=box.min(0);hi=box.max(0);pad=np.maximum((hi-lo)*.2,3)
        centrex=(lo[0]+hi[0])/2; width=(hi[1]-lo[1]+2*pad[1])*.9
        lo[0]=centrex-width/2;hi[0]=centrex+width/2;pad[0]=0
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.grid(alpha=.16)
    ax.set_xlabel('Local '+('depth' if side else 'transverse')+' (mm)');ax.set_ylabel('Own-state CMC-MCP axis projection (mm)')
    ax.set_title(state+' | '+('orthogonal side projection' if side else 'local transverse projection'),loc='left',fontsize=11,fontweight='bold')
def meshpair(name,title,subtitle,selected=None,vertexlabels=False,landmarks=False):
    fig,axs=plt.subplots(2,2,figsize=(15,11),facecolor='#f8f9fc')
    for row,state in enumerate(S):
        for col in range(2):mesh(axs[row,col],state,selected,side=bool(col),vertexlabels=vertexlabels,landmarks=landmarks)
    finish(fig,name,title,subtitle)
meshpair('P02_P06_TRANSITION_OVERVIEW.png','P02-P06 transition | ten original quads','Green P02 / gold P03 / orange P04 / rose P05 / purple P06. Grey: direct incident neighbourhood only.')
meshpair('P03_P05_TRANSITION_CLOSEUP.png','P03-P05 | same face and vertex IDs','Labels expose the actual incident patch. State-specific camera bases have the same structural meaning.',selected=['P03','P04','P05'],vertexlabels=True)
for state in S:
    fig,axs=plt.subplots(1,2,figsize=(15,9),facecolor='#f8f9fc')
    for col,ax in enumerate(axs):mesh(ax,state,side=bool(col),frames=True)
    axs[0].legend(handles=[Line2D([0],[0],color=c,label=n) for n,c in [('L longitudinal','#265cda'),('T transverse','#09806a'),('N normal','#c23c59')]],fontsize=9)
    finish(fig,'ROW_LOCAL_FRAMES_'+state+'.png',state+' row frames | continuous rotation','Arrows are unit frame vectors drawn at equal 2.8 mm scale; projection shortening is expected.')

def line(ax,key,kind='frame',title='',ylabel=''):
    for state,d in S.items():
        rr=d['rows']; y=[r[kind][key] for r in rr]
        ax.plot(range(2,7),y,'-o',label=state,c=SC[state])
    ax.set_xticks(range(2,7),P['row_ids']);ax.set_title(title,loc='left',fontsize=11);ax.set_ylabel(ylabel);ax.grid(alpha=.18);ax.legend(fontsize=8)
    ax.axvspan(2.9,5.1,alpha=.06,color='#c36d28')

fig,axs=plt.subplots(2,2,figsize=(15,10),facecolor='#f8f9fc')
for state,d in S.items():
    rr=d['rows'];x=range(2,7)
    for ax,key,title in [(axs[0,0],'chord_width_mm','Outgoing frontier chord (mm)'),(axs[0,1],'partial_arc_width_mm','Outgoing two-edge arc (mm)'),(axs[1,0],'arc_chord_ratio','Arc / chord ratio')]:
        ax.plot(x,[r['frontiers']['outgoing'][key] for r in rr],'-o',label=state,c=SC[state]);ax.set_title(title,loc='left');ax.set_xticks(x,P['row_ids']);ax.grid(alpha=.18);ax.legend()
    axs[1,1].plot(range(3,7),[r['outgoing_width_relative_change_from_previous']*100 for r in rr[1:]],'-o',label=state,c=SC[state])
axs[1,1].set_title('Chord change from preceding row (%)',loc='left');axs[1,1].set_xticks(range(3,7),P['row_ids'][1:]);axs[1,1].grid(alpha=.18);axs[1,1].legend()
finish(fig,'FRONTIER_SEPARATION_PROFILE.png','Frontier separation | gradual widening, no role cutoff','Maximum sampled chord at P05 in both states. A geometric maximum does not prove a web/palm semantic edge.')

fig,axs=plt.subplots(2,3,figsize=(17,10),facecolor='#f8f9fc')
for ax,key,kind,title in [(axs[0,0],'normal_dot_chain_radial','frame','N dot own-state radial'),(axs[0,1],'normal_dot_thumb_axis','frame','N dot thumb axis'),(axs[0,2],'normal_dot_circumferential','frame','N dot circumference tangent'),(axs[1,0],'inherited_web_facing_dot','surface_cues','Inherited web-context dot'),(axs[1,1],'inherited_proximal_palm_proxy_dot','surface_cues','Inherited proximal direction proxy'),(axs[1,2],'normal_dot_local_flank_normal','surface_cues','N dot local flank mean N')]:line(ax,key,kind,title)
axs[0,0].axhline(0,color='#777',ls='--',lw=.8)
finish(fig,'NORMAL_FIELD_TRANSITION.png','Normal field | geometry support, semantic ambiguity','Radial sign changes at P05 on row average; flank alignment is already high at P02. Proxies do not label palm/thenar.')

fig,axs=plt.subplots(2,2,figsize=(15,10),facecolor='#f8f9fc')
line(axs[0,0],'transverse_dot_circumferential',title='T dot own-state circumferential tangent')
line(axs[0,1],'transverse_dot_thumb_axis',title='T dot own-state thumb axis')
for state,ax in zip(S,axs[1]):
    for lane,col in enumerate(['#8e5eb6','#be6636']):
        yy=[r['lanes'][lane]['normal_dot_own_face_centroid_radial'] for r in S[state]['rows']]
        ax.plot(range(2,7),yy,'-o',c=col,label='face column '+str(4+lane))
    ax.axhline(0,c='#777',ls='--',lw=.8);ax.set_xticks(range(2,7),P['row_ids']);ax.grid(alpha=.18);ax.legend(fontsize=8);ax.set_title(state+' | per-face N dot own-centroid radial',loc='left')
finish(fig,'PARTIAL_CIRCUMFERENCE_VALIDITY.png','Partial-circumference audit | loss not uniquely certified','P05 is mixed by face in BOTH states; RSSF retains T/circ correspondence. No angle or dot cutoff defines semantics.')
fig,axs=plt.subplots(2,2,figsize=(15,11),facecolor='#f8f9fc')
for i,state in enumerate(S):
    mesh(axs[i,0],state,side=True,landmarks=True)
    mesh(axs[i,1],state,side=True)
    axs[i,0].set_title(state+' | CMC-MCP reference overview',loc='left',fontsize=11,fontweight='bold')
    axs[i,1].set_title(state+' | enlarged local patch',loc='left',fontsize=11,fontweight='bold')
finish(fig,'MCP_CMC_LOCAL_CONTEXT.png','MCP / CMC | structural references and local enlargement','All row centres reference CMC-MCP segment0. Grey geometry stays within the direct incident patch.')
for row in ['P02','P06']:
    meshpair(row+'_NEGATIVE_CONTROL.png',row+' negative control | required semantic proof fails','FAIL = control role is not certified. It does not assign the opposite anatomical role.',selected=[row],vertexlabels=True)
print('Rendered',len(list(R.glob('*.png'))),'exact-data PNGs')
