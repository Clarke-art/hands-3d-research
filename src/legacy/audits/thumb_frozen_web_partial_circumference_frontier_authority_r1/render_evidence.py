"""Exact polygon/edge plots, local scope only. No AI images or Blender."""
import sys
sys.dont_write_bytecode=True
from local_data import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
R=OUT/'renders';R.mkdir(exist_ok=True)
ST=read(OUT/'THUMB_PROXIMAL_RING_STACK_R1.json');RS=ST['rings'];SEQ=[r['vertex_sequence'] for r in RS];STACK=set(ST['vertex_set']['vertex_ids']);FS=set(ST['face_ids'])
C=read(OUT/'LOCAL_DIAGNOSTIC_STRIP_SETS.json');F1=C['F1'];F3=C['F3'];SH=set(F3['shared_vertex_ids']);END=read(OUT/'DISTAL_PROXIMAL_TERMINATION_AUDIT.json');localcontext=grow(STACK,2)
ALLLOCAL={fi for v in localcontext for fi in VF[v]};focus=STACK|{v for x in END.values() for h in x['two_face_row_continuation_probe'] for v in h['outward_vertex_ids']}
TC='#1f8a79';SC='#efb257';SEED='#bb4f08';LEFT='#c93269';RIGHT='#3665c3';GRAY='#dce4eb';NAIL='#7965ac'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
def basis(cam):
    z=unit(np.array(cam,float));x=unit(np.cross([0.,0.,1.],z));y=np.cross(z,x);return np.stack([x,y,z],axis=1)
def draw(ax,P,cam,mode):
    B=basis(cam);Q=P@B*1000;order=sorted(ALLLOCAL,key=lambda fi:float(Q[F[fi],2].mean()));poly=[];colors=[]
    for fi in order:
        color=GRAY
        if fi in FS:color='#d6e9e4'
        if fi in F3['shared_face_ids'] and mode!='rings':color=SC
        if fi in NAILF['thumb']:color=NAIL
        if fi in src('cap_authority')['face_ids']:color='#58b4a3'
        if mode=='ends' and fi in {f for x in END.values() for h in x['two_face_row_continuation_probe'] for f in h['face_ids']}:color='#e8d4f3'
        poly.append(Q[F[fi],:2]);colors.append(color)
    ax.add_collection(PolyCollection(poly,facecolors=colors,edgecolors='#909fab',linewidth=.45))
    def lines(es,color,width=1,ls='-'):
        ax.add_collection(LineCollection([Q[E[e],:2] for e in es],colors=color,linewidths=width,linestyles=ls,zorder=7))
    for r in RS:lines(r['edge_sequence'],TC,.8)
    if mode in ['frontier','roles','seeds','ends','complement']:
        lines(F3['left_frontier_edge_ids'],LEFT,2.8);lines(F3['right_frontier_edge_ids'],RIGHT,2.8)
        lines(F3['distal_cut_edge_ids']+F3['proximal_cut_edge_ids'],'#2d3443',2,'--')
    ax.scatter(Q[sorted(SEEDS),0],Q[sorted(SEEDS),1],c=SEED,s=42,edgecolors='white',linewidth=.7,zorder=10)
    if mode in ['seeds','rings']:
        for v,off in zip(sorted(SEEDS),[(-60,18),(35,32),(-60,-30),(35,-10)]):
            ax.annotate('v'+str(v),Q[v,:2],xytext=off,textcoords='offset points',fontsize=8,color='#753306',arrowprops={'arrowstyle':'-','color':'#753306'},bbox={'facecolor':'white','alpha':.88,'edgecolor':'none','pad':2},zorder=15)
    if mode=='rings':
        for r in RS:
            v=r['vertex_sequence'][0];ax.annotate(r['ring_id'],Q[v,:2],xytext=(-25,0),textcoords='offset points',fontsize=8,color=TC,bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'},zorder=10)
    if mode=='ends':
        for j,title in [(0,'R00: crop, not approved stop'),(8,'R08: strip continues')]:
            x=Q[SEQ[j][5],:2];ax.annotate(title,x,xytext=(20,25 if j==0 else -30),textcoords='offset points',fontsize=8,arrowprops={'arrowstyle':'->','color':'#514461'},bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'},zorder=20)
        v=304;ax.scatter(*Q[v,:2],marker='s',c=NAIL,s=60,edgecolors='white',zorder=15);ax.annotate('nail v304',Q[v,:2],xytext=(-55,45),textcoords='offset points',color=NAIL,fontsize=8,arrowprops={'arrowstyle':'-','color':NAIL},zorder=20)
    qq=Q[sorted(focus),:2];lo=qq.min(0);hi=qq.max(0);pad=np.maximum((hi-lo)*.12,4);ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.grid(alpha=.12);ax.set_xlabel('Projected world distance (mm)');ax.set_ylabel('Projected world distance (mm)')
def two(name,title,sub,mode='roles',view=(.2,1,.12),footer=''):
    fig,ax=plt.subplots(1,2,figsize=(14,8),facecolor='#f7f9fc')
    for a,P,state in zip(ax,[N,V],['NATIVE / original topology','RSSF / frozen repose']):draw(a,P,view,mode);a.set_title(state,loc='left',fontweight='bold')
    fig.suptitle(title,fontsize=17,fontweight='bold',x=.05,ha='left',y=.98);fig.text(.05,.924,sub,fontsize=10)
    legend=[Line2D([0],[0],color=SEED,marker='o',lw=0,label='Frozen shared seeds'),Line2D([0],[0],color=SC,lw=6,label='F3 strip hypothesis'),Line2D([0],[0],color=LEFT,lw=3,label='Left chain / column4'),Line2D([0],[0],color=RIGHT,lw=3,label='Right chain / column6'),Line2D([0],[0],color=TC,lw=2,label='Original complete rings')]
    fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.085),ncol=5,frameon=False,fontsize=8)
    fig.text(.05,.042,'FAIL CLOSED — DIAGNOSTIC STRIP ONLY; DISTAL / PROXIMAL TERMINATIONS UNRESOLVED',fontsize=10,color='#b72843',fontweight='bold')
    fig.text(.05,.016,footer or 'Exact mesh polygons and edge IDs. Markers/lines are x-ray overlays. No new FIRST_WEB membership, solver-role extension or exclusive complement approved.',fontsize=8)
    fig.subplots_adjust(left=.06,right=.98,bottom=.17,top=.86,wspace=.2);fig.savefig(R/name,dpi=150);plt.close(fig)
two('THUMB_RING_STACK_OVERVIEW.png','Thumb proximal ring stack / 9 x16 vertices','Eight deterministic16-quad annuli; longitudinal arc ordering uses the corrected live chain.',mode='rings')
two('FROZEN_WEB_SEEDS_ON_RINGS.png','Frozen shared seeds / exact ring columns','R00:1399 /2774 /1396 at columns4 /5 /6. R01:1402 at column5. No angular matching.',mode='seeds')
for name,view in [('DORSAL',(0,1,0)),('PALMAR',(0,-1,0)),('RADIAL',(1,0,0)),('ULNAR',(-1,0,0))]:
    two('PARTIAL_SHARED_SECTOR_'+name+'.png','Partial shared sector hypothesis / '+name,'F3 maps the seed-supported columns through all9rings. These roles are not approved; the remaining arc stays unresolved.',view=view)
two('LEFT_RIGHT_FRONTIER_CHAINS.png','Left / right frontier chains / exact topology','Each chain has8 original longitudinal edges. Columns4 and6 are deterministic; full authority is blocked by stop rules.',mode='frontier')
two('DISTAL_PROXIMAL_TERMINATION.png','Endpoint tests / neither crop is an authority stop','Two actual face rows examined beyond each end. Purple context continues; distal one side encounters fixed nail.',mode='ends')
two('THUMB_EXCLUSIVE_COMPLEMENT_ARC.png','Complement arc / connectivity evidence only','117 remaining stack vertices stay connected to cap37/nail after removing F3. Connectivity does not prove exclusive anatomy.',mode='complement',footer='No THUMB_EXCLUSIVE complement membership is emitted. Pale green is a connectivity diagnostic, not a binary complement assignment.')

# Ring unwrap and angle trajectories make the longitudinal ambiguity directly reviewable.
L=read(OUT/'THUMB_SHARED_SECTOR_LONGITUDINAL_CONTINUITY_AUDIT.json');fig,axs=plt.subplots(1,3,figsize=(16,8),facecolor='#f7f9fc',gridspec_kw={'width_ratios':[1.4,1,1]})
ax=axs[0]
for j in range(9):
    for c in range(16):
        color=SC if c in [4,5,6] else '#e1e8ee';ax.add_patch(Rectangle((c-.45,j-.42),.9,.84,facecolor=color,edgecolor='white'));v=SEQ[j][c]
        if v in SEEDS:ax.scatter(c,j,s=75,c=SEED,edgecolors='white',zorder=5);ax.annotate(str(v),(c,j),xytext=(0,-14),textcoords='offset points',ha='center',fontsize=7,zorder=6)
ax.plot([4]*9,range(9),c=LEFT,lw=2);ax.plot([6]*9,range(9),c=RIGHT,lw=2);ax.set_xlim(-1,16);ax.set_ylim(8.8,-.8);ax.set_xticks(range(16));ax.set_yticks(range(9),[r['ring_id'] for r in RS]);ax.set_xlabel('Topology column / cyclic order');ax.set_title('Same IDs in both geometry states',loc='left',fontweight='bold');ax.grid(alpha=.12)
for state,color in [('NATIVE',TC),('RSSF',RIGHT)]:
    rr=L['states'][state]['rings'];ang=[r['topology_strip_descriptor']['centroid_angle_deg'] for r in rr];wid=[r['topology_strip_descriptor']['angular_width_deg'] for r in rr];axis=[r['axial_mean_mm'] for r in RS]
    axs[1].plot(ang,axis,'-o',color=color,label=state);axs[2].plot(wid,axis,'-o',color=color,label=state)
axs[1].set_xlabel('Sector centroid angle (deg)');axs[2].set_xlabel('Sector width (deg)')
for ax in axs[1:]:ax.set_ylabel('Corrected chain arc (mm)');ax.grid(alpha=.2);ax.legend();ax.set_title('Descriptor only / no angular cutoff',fontsize=10,loc='left')
fig.suptitle('Native vs RSSF / exact topology, changing geometric descriptors',x=.04,ha='left',fontsize=17,fontweight='bold',y=.97)
fig.text(.04,.91,'F1 ends after the first2rings; F3 persists through9. No approved termination follows from either diagram.',fontsize=11)
fig.text(.04,.045,'FAIL CLOSED — same column mapping does not resolve longitudinal stopping authority.',color='#b72843',fontweight='bold',fontsize=11)
fig.subplots_adjust(left=.05,right=.98,bottom=.14,top=.83,wspace=.28);fig.savefig(R/'NATIVE_VS_RSSF_SECTOR_STABILITY.png',dpi=150);plt.close(fig)
dump('VISUAL_EVIDENCE_MANIFEST.json',{'status':'GENERATED_DIAGNOSTIC_ONLY','files':[{'path':str(p.relative_to(OUT)),'sha256':sha(p)} for p in sorted(R.glob('*.png'))],'render_method':'Matplotlib exact frozen polygons/edges plus topological unwrap','membership_applied':False,'Human_review_page_generated':False})
print('Rendered',len(list(R.glob('*.png'))),'local evidence PNGs.')
