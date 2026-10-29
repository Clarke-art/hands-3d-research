"""Scientific projections of immutable mesh arrays; no raster image editing or Blender."""
import sys
sys.dont_write_bytecode=True
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
from matplotlib.lines import Line2D
OUTR=OUT/'renders';OUTR.mkdir(exist_ok=True)
S=read(OUT/'STATIC_SUMMARY.json');T=set(S['thumb_diag_ids']);I=set(S['index_diag_ids']);O=set(S['outside_landmark_ids']);D=T|I|WEB
G3=set(read(PREV/'PROXIMAL_COUPLED_DOMAIN_CANDIDATE_AUDIT.json')['candidates']['G3_K2']['membership']['vertex_ids'])
BR={d:read(OUT/(d.upper()+'_BRANCH_CONTINUITY_AUDIT.json')) for d in ['thumb','index']}
TR=BR['thumb']['true_topological_rings']['rings'];IR=BR['index']['true_topological_rings']['unique_maximal_core']
COL={'thumb':'#158272','index':'#2764b0','web':'#df8b19','outside':'#485362','unknown':'#e2e7ed','thumb_diag':'#c3e2dc','index_diag':'#c6d9f2','extra':'#ae8bc1','bad':'#bd2940'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
def basis(camera):
    camera=unit(np.array(camera,float));up=np.array([0.,0.,1.]);right=unit(np.cross(up,camera));up=unit(np.cross(camera,right));return np.stack([right,up,camera],axis=1)
def panel(ax,coords,view,focus,mode='roles',digit=None):
    P=basis(view);Q=coords@P*1000;ff=[];colors=[];order=sorted(range(len(F)),key=lambda fi:float(Q[F[fi],2].mean()))
    for fi in order:
        vs=set(F[fi]);c=COL['unknown']
        if mode in ['roles','shared','thumb','index','sample','anchor']:
            if vs<=T:c=COL['thumb_diag']
            elif vs<=I:c=COL['index_diag']
            if vs<=CAP|NAILS['thumb']:c=COL['thumb']
            elif vs<=INDEX_SOURCES:c=COL['index']
            elif vs<=O:c=COL['outside']
        elif mode=='compare':
            if vs<=G3:c=COL['extra']
            if vs<=D:c='#d6e8dc'
        ff.append(Q[F[fi],:2]);colors.append(c)
    ax.add_collection(PolyCollection(ff,facecolors=colors,edgecolors='#a5aeba',linewidth=.25))
    def pts(ids,color,size=13,marker='o',edge='white'):
        ids=sorted(ids)
        if ids:ax.scatter(Q[ids,0],Q[ids,1],c=color,s=size,marker=marker,edgecolors=edge,linewidth=.45,zorder=10)
    pts(WEB,COL['web'],19)
    if mode=='roles':
        pts(CAP|NAILS['thumb'],COL['thumb'],9);pts(INDEX_SOURCES,COL['index'],7);pts(O,COL['outside'],6)
    def lines(eids,color,width=1.4,style='-'):
        ax.add_collection(LineCollection([Q[E[e],:2] for e in eids],colors=color,linewidths=width,linestyles=style,zorder=8))
    if mode in ['roles','shared']:
        lines(surface_audit(T)['boundary_edge_ids'],COL['thumb'],1.5,'--');lines(IR['edge_ids'],COL['index'],1.6,'--')
    if mode=='thumb':
        for r in TR:lines(r['edge_ids'],COL['thumb'],1.1)
        lines(TR[0]['edge_ids'],COL['bad'],2.5);pts({1396,1399,1402,2774},COL['web'],48)
        for v,off in zip([1396,1399,1402,2774],[(-55,25),(30,45),(-55,-45),(35,-10)]):
            ax.annotate('v'+str(v),Q[v,:2],xytext=off,textcoords='offset points',fontsize=8,color='#733d00',arrowprops={'arrowstyle':'-','color':'#733d00'},bbox={'facecolor':'white','alpha':.82,'edgecolor':'none','pad':2},zorder=15)
    if mode=='index':
        for r in BR['index']['true_topological_rings']['rings']:
            if r['eligible_structural_core']:lines(r['edge_ids'],COL['index'],.7)
        lines(IR['edge_ids'],COL['bad'],2.5);pts({TIPS['index']},COL['index'],85,'*')
    if mode=='shared':
        a=surface_audit(D);lines(a['wire_only_edge_ids'],COL['bad'],2.2);pts(a['non_face_supported_vertices'],COL['bad'],25,'x',None)
    if mode in ['sample','anchor']:
        if coords is V:
            chain=CHAINS['thumb'];pq=chain@P*1000
            ax.plot(pq[:,0],pq[:,1],'-o',color='#7938a1',lw=2,ms=4,zorder=14)
            for i,l in enumerate(['CMC','MCP','IP','TIP']):ax.annotate(l,pq[i,:2],xytext=(6,6),textcoords='offset points',fontsize=8,color='#612785',zorder=16)
        pts(CAP,'#c4a324',18);pts(NAILS['thumb'],'#5641a7',16)
        # Potential band context is not a selected sample. Draw no tube membership.
        if mode=='sample':
            s=PROJ['thumb'][0];k=PROJ['thumb'][3];ids={v for r in TR for v in r['core_including_ring']['vertex_ids'] if k[1]<=s[v]<=k[2]}-(CAP|NAILS['thumb']|WEB)
            pts(ids,'#8a929b',7)
    if mode=='compare':
        pts(G3-D,'#8b5ca1',7);pts({3049},COL['bad'],75,'*');lines([EF[tuple(sorted((1891,3049)))]],COL['bad'],2.2)
        ax.annotate('unsupported v3049',Q[3049,:2],xytext=(15,-22),textcoords='offset points',fontsize=8,color=COL['bad'],arrowprops={'arrowstyle':'-','color':COL['bad']},bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'},zorder=15)
    lo=Q[sorted(focus),:2].min(0);hi=Q[sorted(focus),:2].max(0);pad=np.maximum((hi-lo)*.09,3)
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal');ax.set_xlabel('Projected world distance (mm)');ax.set_ylabel('Projected world distance (mm)');ax.grid(alpha=.1)
    return Q
def render(name,title,subtitle,mode='roles',focus=None,view=(0,1,0),footer=''):
    if focus is None:focus=set(range(NV))
    fig,axs=plt.subplots(1,2,figsize=(14,8),facecolor='#f7f9fc')
    for ax,coords,state in zip(axs,[N,V],['NATIVE / stable vertex IDs','RSSF / frozen Stage4C_R2']):
        panel(ax,coords,view,focus,mode);ax.set_title(state,loc='left',fontweight='bold')
    fig.suptitle(title,fontsize=17,fontweight='bold',x=.05,ha='left',y=.98)
    fig.text(.05,.925,subtitle,fontsize=10,color='#394657')
    items=[Line2D([0],[0],color=COL['thumb'],marker='o',lw=0,label='Retained thumb landmarks'),Line2D([0],[0],color=COL['index'],marker='o',lw=0,label='Retained INDEX ingredients'),Line2D([0],[0],color=COL['web'],marker='o',lw=0,label='Frozen FIRST_WEB_21 / shared'),Line2D([0],[0],color='#97adb8',lw=5,label='Pale fill / diagnostic core only'),Line2D([0],[0],color='#c3cbd6',lw=5,label='Grey / unassigned context')]
    if mode=='compare':items=[Line2D([0],[0],color=COL['extra'],lw=5,label='G3_K2 comparison'),Line2D([0],[0],color='#91b7a0',lw=5,label='Core + web diagnostic'),Line2D([0],[0],color=COL['bad'],marker='*',lw=0,label='Unsupported spur')]
    fig.legend(handles=items,loc='lower center',bbox_to_anchor=(.5,.083),ncol=len(items),fontsize=8,frameon=False)
    fig.text(.05,.04,'FAIL CLOSED — NO FINAL ROLE MAP / GRAPH / SAMPLE / TUBE ANCHORS',fontsize=11,color=COL['bad'],fontweight='bold')
    fig.text(.05,.014,footer or 'Surface polygons are exact frozen geometry. Markers and boundary lines are x-ray evidence overlays; pale cores are not anatomical authority.',fontsize=8,color='#465363')
    fig.subplots_adjust(left=.06,right=.98,bottom=.17,top=.87,wspace=.2)
    fig.savefig(OUTR/name,dpi=150);plt.close(fig)

for label,view in [('DORSAL',(0,1,0)),('PALMAR',(0,-1,0)),('RADIAL',(1,0,0)),('ULNAR',(-1,0,0))]:
    render('PROXIMAL_ROLE_MAP_'+label+'.png','Proximal role evidence / '+label,'Partial known memberships: thumb57 / index145 / shared21 / outside landmarks128. Remaining3065 are unassigned.',view=view)
tf={v for r in TR for v in r['core_including_ring']['vertex_ids']}|{1396,1399,1402,2774}
render('THUMB_EXCLUSIVE_RING_EXTENT.png','Thumb ring extent / frozen shared intersection','Nine complete original edge loops enclose the thumb anchors; every distal region contains frozen web points.',mode='thumb',focus=tf,view=(.25,1,.15),footer='Red = most distal complete loop found. It already includes shared v1396/v1399/v2774; proximal loops also include v1402. No exclusive ring chosen.')
render('INDEX_EXCLUSIVE_RING_EXTENT.png','Index ring extent / structural candidate','Unique maximal marker-free closed-ring core:329 vertices. This is structural evidence, not a finalized four-role map.',mode='index',focus=I,view=(.2,1,.1),footer='Red ring =16 vertices; corrected INDEX arc0.000–2.433 mm. All145 retained INDEX source ingredients are inside; frozen web overlap0.')
render('FIRST_WEB_SHARED_NEUTRAL_CONTEXT.png','Frozen first-web / shared-neutral context','Orange membership is fixed. Its extent along the thumb tube is a partial circumference, not an axial ring boundary.',mode='thumb',focus=WEB|T|I,view=(.35,1,.1))
render('MINIMAL_SHARED_SUPPORT_GRAPH.png','Minimal shared support / not established','Diagnostic cores + frozen web:471 vertices /903 edges /4 components. Red wires lack complete face support.',mode='shared',focus=D,view=(.3,1,.1),footer='No support was added to make this graph connected. Incidence around web is measured separately; it is not automatically classified as shared.')
render('THUMB_TUBE_SAMPLE_POPULATION.png','Thumb radius sample population / blocked','MCP–IP band is shown for context only. Grey band dots are NOT selected samples; cap, nail and web are exclusions.',mode='sample',focus=tf|WEB,view=(.3,1,.1),footer='No sample IDs, sample statistic or radius were generated. Exclusive sector boundary must be established first.')
render('THUMB_TUBE_ANCHOR_CANDIDATE.png','Thumb tube anchors / blocked','Corrected live chain and retained cap/nail are shown. No radius envelope or new tube hard pins have been generated.',mode='anchor',focus=tf|WEB,view=(.3,1,.1),footer='First-web hard pins=0. Native INDEX/shared conflicts for a future tube are unknown, not reported as zero for a nonexistent set.')
render('G3K2_VS_PROPOSED_DOMAIN.png','G3_K2 vs limited diagnostic evidence','No final proposed domain. G3_K2 has492 additional vertices versus diagnostic cores+web; this is not an anatomical excess verdict.',mode='compare',focus=G3,view=(.25,1,.1),footer='G3_K2:963 vertices/1882 edges; unsupported v3049 and wire(1891,3049). Connectivity alone did not authorize its extent.')
dump('VISUAL_EVIDENCE_MANIFEST.json',{'status':'GENERATED_STATIC_EVIDENCE','role':'Diagnostic evidence only; no Human approval page because no unique final candidate','files':[{'path':str(p.relative_to(OUT)),'sha256':sha(p)} for p in sorted(OUTR.glob('*.png'))],'view_directions':'Canonical world +Y dorsal/-Y palmar/+X radial/-X ulnar; oblique additional diagnostic views identified by scripts','plot_source':'Frozen polygon coordinates and original edge IDs; no mesh changes','image_generation_AI_used':False})
print('Generated',len(list(OUTR.glob('*.png'))),'scientific evidence PNGs.')
