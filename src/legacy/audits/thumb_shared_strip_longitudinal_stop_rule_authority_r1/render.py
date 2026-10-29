import sys
sys.dont_write_bytecode=True
from data import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
T=read(OUT/'RAW_LOCAL_COLUMN_TRACES.json');D=read(OUT/'DISTAL_NON_NAIL_LONGITUDINAL_PROFILE.json');P=read(OUT/'PROXIMAL_SHARED_STRIP_LONGITUDINAL_PROFILE.json')
R=OUT/'renders';R.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
COL={'NATIVE':'#178375','RSSF':'#365ecc'};SAFE='#eeb758';BLOCK='#cc4260';CTX='#dce5ec'
def finish(fig,name,title,sub):
    fig.suptitle(title,x=.05,y=.98,ha='left',fontsize=18,fontweight='bold');fig.text(.05,.919,sub,fontsize=10)
    fig.text(.05,.037,'FAIL CLOSED: proximal semantic stop and lateral role authority remain unresolved.',color='#b32d48',fontsize=11,fontweight='bold')
    fig.text(.05,.012,'Exact frozen mesh evidence. Distal stop proposals do not approve new shared membership. No production or solver changes.',fontsize=8)
    fig.subplots_adjust(left=.07,right=.97,top=.85,bottom=.13,wspace=.30,hspace=.38);fig.savefig(R/name,dpi=160);plt.close(fig)
def mesh(ax,P,focus,highlights,labels=True,landmarks=False):
    ids={v for fi in focus for v in F[fi]};context={fi for v in ids for fi in VF[v]};Q=np.stack([-P[:,0],P[:,2],P[:,1]],axis=1)*1000
    poly=[];colors=[]
    for fi in sorted(context,key=lambda f:float(Q[F[f],2].mean())):
        color=CTX
        if fi in NAILF['thumb']:color='#8870a9'
        if fi in src('cap_authority')['face_ids']:color='#66aba1'
        if fi in highlights:color=highlights[fi]
        poly.append(Q[F[fi],:2]);colors.append(color)
    ax.add_collection(PolyCollection(poly,facecolors=colors,edgecolors='#8495a4',linewidth=.6))
    for v in SEEDS&ids:ax.scatter(*Q[v,:2],s=35,c='#b85d0e',edgecolors='white',zorder=8)
    if labels:
        for fi in focus:
            if fi in highlights:
                xy=Q[F[fi],:2].mean(0);ax.text(*xy,str(fi),fontsize=8,ha='center',va='center',zorder=10,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none','pad':1.3})
    if landmarks:
        if P is N:
            q=src('native_thumb_anchor_evidence')['native_direction_support'];C=np.array([q['axis_anchor_world_m'],q['joint_world_m']['MCP'],q['joint_world_m']['IP']])
        else:C=CHAIN[:3]
        X=np.stack([-C[:,0],C[:,2]],axis=1)*1000;ax.plot(X[:,0],X[:,1],'--',c='#465267',lw=1)
        for i,n in [(0,'CMC axis'),(1,'MCP')]:ax.scatter(*X[i],marker='x',c='#263448');ax.annotate(n,X[i],xytext=(8,5),textcoords='offset points',fontsize=8)
    box=Q[sorted(ids),:2];lo=box.min(0);hi=box.max(0);pad=np.maximum((hi-lo)*.15,3)
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.xaxis.set_major_locator(MaxNLocator(3));ax.grid(alpha=.13);ax.set_xlabel('Projected world distance (mm)');ax.set_ylabel('Projected world distance (mm)')
def pairmesh(name,title,sub,focus,hi,landmarks=False):
    fig,axs=plt.subplots(1,2,figsize=(14,8),facecolor='#f7f9fc')
    for ax,coords,state in zip(axs,[N,V],['NATIVE','RSSF']):mesh(ax,coords,focus,hi,landmarks=landmarks);ax.set_title(state,loc='left',fontweight='bold')
    finish(fig,name,title,sub)
distfs=[1178,1179,1177,1176,1213,1214,1226,1227]
pairmesh('DISTAL_STOP_OPTIONS_CLOSEUP.png','Distal alternatives / flat cut versus asymmetric taper','Gold: non-nail D01-D04. Red: nail conflict1177 and cap conflict1227. Face IDs are original.',distfs,{f:SAFE for f in [1176,1213,1214,1226]}|{1177:BLOCK,1227:BLOCK})
pairmesh('DISTAL_NAIL_SIDE_HARD_STOP.png','Nail-side hard constraint / LEFT column4','First continuation face1177 contains frozen nail v304. This does not force RIGHT column6 to stop at the same station.',[1177,1178,1179,1176],{1177:BLOCK,1176:SAFE})
pfs=[fi for r in T['proximal']['rows'][:6] for fi in r['face_ids']]
pairmesh('PROXIMAL_R08_CONTINUATION.png','R08 continuation / two exact face columns','P01-P06 remain regular quads. Orange: P03-P05 morphology window; no approved stop row.',pfs,{fi:SAFE for r in T['proximal']['rows'][2:5] for fi in r['face_ids']})
contextfs=set(pfs)|{f for r in P['states']['RSSF'][:3] for f in r['face_ids']}
pairmesh('MCP_TO_PALM_TRANSITION_CONTEXT.png','MCP to broader-interface context / local strip only','Dashed axis is a spatial cue. MCP crossing is not a stop rule. No thenar or palm ownership inferred.',sorted(contextfs),{fi:SAFE for r in T['proximal']['rows'][2:5] for fi in r['face_ids']},True)
fig,axs=plt.subplots(2,2,figsize=(14,9),facecolor='#f7f9fc')
for state,rr in D['states'].items():
    x=np.arange(1,len(rr)+1)
    for ax,key,label in zip(axs.flat,['distance_to_cap37_min_vertex_mm','normal_dot_web_context','normal_turn_from_previous_row_deg','sector_angular_width_deg'],['Minimum cap-vertex distance (mm)','Normal dot web-context direction','Normal turn from preceding row (deg)','Partial-lane width (deg)']):
        ax.plot(x,[r[key] if r[key] is not None else np.nan for r in rr],'-o',label=state,c=COL[state]);ax.set_xticks(x,[r['row_id'] for r in rr]);ax.set_ylabel(label);ax.grid(alpha=.18);ax.axvspan(4.5,5.4,color=BLOCK,alpha=.12);ax.legend(fontsize=8)
finish(fig,'DISTAL_NON_NAIL_TAPER_PROFILE.png','Non-nail longitudinal profile / event versus smooth descriptors','No curvature or angle cutoff. First frozen cap collision occurs at D05, face1227; D04 is the last safe row proposal.')
fig,axs=plt.subplots(2,2,figsize=(14,9),facecolor='#f7f9fc')
for state,allr in P['states'].items():
    rr=allr[:11];x=np.arange(len(rr))
    for ax,key,label in zip(axs.flat,['mean_arc_mm','local_tube_radius_proxy_mm','tangent_dot_thumb_axis','frontier_separation_mm'],['Own-state chain arc (mm)','Local distance-to-axis proxy (mm)','Tangent dot own-state thumb axis','Frontier separation (mm)']):
        ax.plot(x,[r[key] for r in rr],'-o',c=COL[state],label=state);ax.set_xticks(x,[r['row_id'] for r in rr],rotation=30);ax.set_ylabel(label);ax.grid(alpha=.18);ax.axvspan(4.5,7.5,color=SAFE,alpha=.15);ax.legend(fontsize=8)
finish(fig,'PROXIMAL_LONGITUDINAL_PROFILE.png','Proximal morphology / P03-P05 transition band','Native reversal: P03/P04. RSSF reversal: P04/P05. Gradual widening does not uniquely select an anatomical stop.')
fig,axs=plt.subplots(1,2,figsize=(14,8),facecolor='#f7f9fc')
ax=axs[0];ax.axis('off');rows=[['D02 / early2','No event at cut','NO'],['D03 / early1','No event at cut','NO'],['D04 / proposal','Before first cap conflict','YES*'],['D05 / late1','Includes cap298 /1454','NO'],['D06 / late2','Already crossed cap','NO']]
table=ax.table(cellText=rows,colLabels=['Non-nail stop','Evidence','Event rule'],cellLoc='left',colWidths=[.28,.52,.2],loc='center');table.auto_set_font_size(False);table.set_fontsize(9);table.scale(1,2.3)
ax.set_title('Distal event-adjacent controls',loc='left',fontweight='bold');ax.text(0,.13,'* Conditional stop-rule proposal, not shared-role approval.',transform=ax.transAxes,fontsize=9)
ax=axs[1]
for state,rr in P['states'].items():
    local=rr[4:9];ax.plot(range(2,7),[r['tangent_dot_thumb_axis'] for r in local],'-o',label=state,c=COL[state])
ax.set_xticks(range(2,7),['P02','P03','P04','P05','P06']);ax.axhline(0,c='#697587',lw=.8,ls='--');ax.grid(alpha=.18);ax.legend();ax.set_ylabel('Local tangent dot thumb axis');ax.set_title('Proximal controls: all retain surface support',loc='left',fontweight='bold')
finish(fig,'STOP_EVENT_NEGATIVE_CONTROLS.png','Neighbor-row controls / full stop gate FAILS','Distal conflict gives a reproducible forbidden successor. Proximal P02-P06 lacks a unique authority event at any cut.')
fig,axs=plt.subplots(1,2,figsize=(14,8),facecolor='#f7f9fc')
ax=axs[0]
for y,state in enumerate(['NATIVE','RSSF']):
    ax.plot(range(1,6),[y]*5,c=COL[state],lw=3);ax.scatter([1,2,3,4],[y]*4,c=SAFE,s=100,zorder=4);ax.scatter(5,y,c=BLOCK,s=120,marker='X',zorder=4);ax.annotate('cap298 /1454',(5,y),xytext=(-55,24),textcoords='offset points',fontsize=10)
ax.set_yticks([0,1],['NATIVE','RSSF']);ax.set_xticks(range(1,6),['D01','D02','D03','D04','D05']);ax.set_ylim(-.5,1.6);ax.set_title('Same distal conflict row and IDs',loc='left',fontweight='bold');ax.grid(alpha=.15)
ax=axs[1]
for y,state,x in [(0,'NATIVE',4),(1,'RSSF',5)]:ax.plot(range(2,7),[y]*5,c=COL[state]);ax.scatter(x,y,c=COL[state],s=110);ax.annotate('first tangent reversal',(x,y),xytext=(-65,25),textcoords='offset points',fontsize=9)
ax.set_xticks(range(2,7),['P02','P03','P04','P05','P06']);ax.set_yticks([0,1],['NATIVE','RSSF']);ax.set_ylim(-.5,1.6);ax.grid(alpha=.15);ax.set_title('Proximal geometry event shifts one row',loc='left',fontweight='bold')
finish(fig,'NATIVE_RSSF_STOP_STABILITY.png','Native/RSSF stability / distal YES, complete stop NOT ESTABLISHED','The same topology does not make a geometry-derived exact semantic stop invariant. Proximal authority remains open.')
dump('VISUAL_EVIDENCE_MANIFEST.json',{'files':[{'path':str(p.relative_to(OUT)),'sha256':sha(p)} for p in sorted(R.glob('*.png'))],'render_type':'Exact frozen mesh polygons and numerical profiles','final_complete_stop_candidate_render_created':False,'Human_Review_HTML_created':False})
print('Rendered',len(list(R.glob('*.png'))),'scientific evidence images')
