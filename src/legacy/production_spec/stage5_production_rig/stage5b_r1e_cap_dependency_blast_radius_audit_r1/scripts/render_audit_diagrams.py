from pathlib import Path
import json, textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

O=Path(__file__).resolve().parents[1]
def j(n): return json.loads((O/n).read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'savefig.facecolor':'#f7f9fc'})
INK='#15283c';GREEN='#24855a';RED='#c93649';AMBER='#c38819';BLUE='#316dae';PURPLE='#8250a0'
def box(ax,x,y,label,w=1.14,h=.65,color='#e5ebf3',size=10):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.035,rounding_size=0.06',facecolor=color,edgecolor='#627489',linewidth=1,zorder=3))
    ax.text(x,y,label,ha='center',va='center',fontsize=size,color=INK,zorder=4)
def arrow(ax,a,b,color=BLUE,rad=0,alpha=.65,lw=1.15,shrink=35):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,connectionstyle=f'arc3,rad={rad}',color=color,alpha=alpha,linewidth=lw,shrinkA=shrink,shrinkB=shrink,zorder=1))
def save(fig,n):
    fig.savefig(O/'renders'/n,dpi=160,bbox_inches='tight');plt.close(fig)

G=j('CAP_DEPENDENCY_DAG.json')
pos={'UPSTREAM':(0,5),'OLD_CAP9':(1.55,5),'R2A_CAP_RIG':(3.05,6.25),'R1_SKIN':(4.65,7.55),'R1A_MASKS':(3.05,3.4),'R1A_SKIN':(6.2,7.55),'R1B_SKIN':(7.75,7.55),'R2_OWNERSHIP':(4.65,3.4),'THUMB_STRONG_R3':(4.65,5),'R3_LABELS':(6.2,5),'R3_BOUNDARY':(7.75,5),'R1C_SKIN':(9.35,8.1),'R1D_SKIN':(9.35,6.85),'R1E_SKIN':(9.35,4.8),'STAGE6A':(11,8.1),'STAGE6B':(12.55,6.85),'CAP_VALIDATORS':(9.35,2.6),'STRICT_BOUNDS':(11,3.7),'ENDPOINT_REVIEWS':(12.55,3.7),'EDGE5879':(11,5.65),'MANUAL_REVIEWS':(3.05,1.15),'NEW_CAP37':(4.65,1.15),'STATUS_REPORTS':(14.1,5)}
labels={'UPSTREAM':'Stage4 frozen\ngeometry / nail','OLD_CAP9':'OLD CAP9\n9 native INDEX','R2A_CAP_RIG':'R2A TIP / IP tail\nlocal frames','R1_SKIN':'R1 skin\nlive bind bones','R1A_MASKS':'R1A ownership\nfirst-web masks','R1A_SKIN':'R1A skin\nexplicit cap write','R1B_SKIN':'R1B skin\nprotected carry-over','R2_OWNERSHIP':'R2 ownership\ncap-centroid seed','THUMB_STRONG_R3':'R3 strong anchors\nCAP + live tube','R3_LABELS':'R3 labels\nfields / cut / closure','R3_BOUNDARY':'R3 cut / sheet\nambiguous / gates','R1C_SKIN':'R1C skin\nR2 repair','R1D_SKIN':'R1D skin\ndistal continuity','R1E_SKIN':'R1E skin\nR3 transition','STAGE6A':'Stage6A\nfull qualification','STAGE6B':'Stage6B\nfull qualification','CAP_VALIDATORS':'Cap fixtures\nsemantic validators','STRICT_BOUNDS':'Old strict bounds\nendpoint meaning','ENDPOINT_REVIEWS':'Endpoint reviews\nrecommendations','EDGE5879':'edge5879\npartly cap-derived','MANUAL_REVIEWS':'Human correction\nreview chain','NEW_CAP37':'NEW CAP37\nfrozen 37 / 25','STATUS_REPORTS':'Status / reports\nreuse qualification'}
ec={'DIRECT_INPUT':BLUE,'DERIVED_LABEL':PURPLE,'WEIGHT_AUTHORITY':AMBER,'VALIDATION_ONLY':'#65919c','REPORTING_REFERENCE':'#99a4b2','HUMAN_APPROVAL':GREEN}
fig,ax=plt.subplots(figsize=(25,13));fig.patch.set_facecolor('#f7f9fc');ax.set_facecolor('#f7f9fc')
for k,e in enumerate(G['edges']):
    a,b=pos[e['from']],pos[e['to']]
    rad=0 if abs(a[1]-b[1])<.1 else (.06 if k%2 else -.06)
    if e['from']=='OLD_CAP9' and e['to'] in ['STRICT_BOUNDS','CAP_VALIDATORS']:rad=.15
    arrow(ax,a,b,ec[e['edge_type']],rad=rad,alpha=.55,shrink=48)
for n in G['nodes']:
    color='#e5ebf3'
    if n['id']=='OLD_CAP9':color='#f9dbe1'
    elif n['id'] in ['UPSTREAM','NEW_CAP37']:color='#dbeee3'
    elif n['id'] in ['R2A_CAP_RIG','THUMB_STRONG_R3','R3_LABELS','R3_BOUNDARY']:color='#f5e8cd'
    box(ax,*pos[n['id']],labels[n['id']],w=1.30,h=.72,size=10)
ax.set_xlim(-.95,15);ax.set_ylim(.3,9.35);ax.axis('off')
ax.text(-.85,9.06,'CAP DEPENDENCY PROVENANCE DAG',fontsize=23,fontweight='bold',color=INK)
ax.text(-.85,8.65,f"{len(G['nodes'])} component nodes / {len(G['edges'])} source-backed edges | historical provenance, not counterfactual outcomes",fontsize=13,color='#4c6177')
handles=[Patch(color=v,label=k.replace('_',' '))for k,v in ec.items()]
ax.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,-.08),ncol=3,frameon=False,fontsize=11)
fig.text(.025,.018,'Complete edge evidence and artifact hashes: CAP_DEPENDENCY_DAG.json. Corrective Human review retains old cap as audit target, never as native anatomical truth.',fontsize=11,color=INK)
save(fig,'CAP_DEPENDENCY_DAG.png')

A=j('R3_OLD_CAP9_INFLUENCE_RADIUS_AUDIT.json')
fig=plt.figure(figsize=(16,10));gs=fig.add_gridspec(2,2,height_ratios=[1.1,1.3],hspace=.38,wspace=.27)
ax=fig.add_subplot(gs[0,:]);ax.set_xlim(-.9,7.7);ax.set_ylim(-.9,1.3);ax.axis('off')
path=[('OLD CAP9\nall native INDEX',RED),('CAP union +\nlive tube anchors',AMBER),('dT field +\nINF source pins',BLUE),('coupled mincut\nconnectivity closure',PURPLE),('labels / boundary\nsheet / gates',BLUE)]
for i,(t,c) in enumerate(path):
    x=1.65*i;box(ax,x,0,t,w=1.42,h=.82,color='#e5ebf3',size=11)
    if i:arrow(ax,(x-1.65,0),(x,0),c,alpha=1,shrink=65)
ax.text(-.65,1.05,'OLD CAP9 TO R3: OBSERVED ROLES AND PROPAGATION',fontsize=19,fontweight='bold',color=INK)
ax.text(-.65,-.73,'Also: old cap representative → R2A live rig; old cap centroid → R2 seed / R3 graph domain.',fontsize=12,color=INK)
ax=fig.add_subplot(gs[1,0]);ids=[r['vertex_id']for r in A['vertices']];hs=[r['graph_distance_to_R3_boundary_hops']for r in A['vertices']]
ax.barh([str(i)for i in ids],hs,color=RED,alpha=.85);ax.invert_yaxis();ax.set_xlim(0,5);ax.set_xticks(range(6));ax.set_xlabel('Mesh-edge hops to historical R3 boundary');ax.set_title('All 9: THUMB_STRONG, final R3 = THUMB',loc='left',color=INK)
for i,h in enumerate(hs):ax.text(h+.08,i,str(h),va='center',color=INK)
ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
ax=fig.add_subplot(gs[1,1]);ax.axis('off')
facts=[('0 effective pins removed','Replacing explicit CAP alone leaves all nine\nwrong pins supplied by the live tube.'),('6 additional cap37 pins','285, 297, 339, 1378, 1450, 1452\n31 / 37 were already strong; all 37 labeled THUMB.'),('No old9 incident final cut edge','Old9 are retained source / closure anchors.\nObserved 1 / 2 rings are not a causal radius.'),('FULL RECOMPUTE required','Reconcile rig / seed / anchor authority first.\nNew boundary or sheet change = UNRESOLVED.')]
for k,(head,body)in enumerate(facts):
    y=.98-k*.24;ax.text(0,y,head,fontsize=14,fontweight='bold',color=AMBER if k<2 else BLUE,va='top');ax.text(0,y-.072,body,fontsize=11.5,color=INK,va='top',linespacing=1.4)
fig.text(.035,.022,'Static saved-graph analysis only. No R3 distance-field, mincut, closure or counterfactual recompute ran. Historical 34 changed labels are not attributed to cap9.',fontsize=10.5,color=INK)
save(fig,'OLD_CAP9_TO_R3_PROPAGATION.png')

D=j('_STATIC_AUDIT_DATA.json');V=np.array(D['vertex_positions_world_mm']);scope=D['cap_dependent_review_region_ids'];ind=D['cap_independent_ids'];old=D['old_cap9_ids'];new=D['new_cap37_ids']
fig,axes=plt.subplots(1,3,figsize=(17,11),gridspec_kw={'width_ratios':[1.2,1.2,1]})
for ax,xcol,title in zip(axes[:2],[0,1],['Historical X / Z projection','Historical Y / Z projection']):
    ax.scatter(V[ind,xcol],V[ind,2],s=2,color='#9ba8b5',alpha=.65,label=f'{len(ind)} independent vectors')
    ax.scatter(V[scope,xcol],V[scope,2],s=3,color=AMBER,alpha=.7,label=f'{len(scope)} review envelope')
    ax.scatter(V[new,xcol],V[new,2],s=28,color=GREEN,edgecolors='white',linewidths=.3,label='Current frozen cap37',zorder=6)
    ax.scatter(V[old,xcol],V[old,2],s=38,color=RED,edgecolors='white',linewidths=.4,label='Old cap9, native INDEX',zorder=7)
    for v in [151,2189,284]:ax.annotate(str(v),(V[v,xcol],V[v,2]),xytext=(9,0),textcoords='offset points',fontsize=9,color=INK,zorder=8)
    ax.set_aspect('equal');ax.set_title(title,loc='left',fontsize=13,color=INK);ax.set_xlabel(('X'if xcol==0 else'Y')+' world mm');ax.set_ylabel('Z world mm');ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15)
axes[0].legend(loc='lower left',fontsize=9,framealpha=.95)
ax=axes[2];ax.axis('off')
texts=[('1485: conservative dependency envelope','Stored write / repair masks + R2 domain,\nold9 / cap37 and actual THUMB carriers.\nNot a claim that all 1485 vectors are wrong.'),('1931: independent vector entries','Outside those domains, no THUMB driver,\nnot old / new cap. Reusable with byte\nand regression checks after future rebuild.'),('9: confirmed contaminated anatomy','Old9 all belong to native INDEX surface.\nR1A first explicit cap-driven write;\nR1 already uses cap-derived bind bones.'),('Keep frozen historical R1B','Future R1B / C / D / E counterparts need\nrebuild; historical files and numeric\nFAIL evidence remain intact.')]
for k,(head,body)in enumerate(texts):
    y=.95-k*.235;ax.text(0,y,head,fontsize=13,fontweight='bold',color=AMBER if k==0 else GREEN if k==1 else RED if k==2 else BLUE,va='top');ax.text(0,y-.057,body,fontsize=11,color=INK,va='top',linespacing=1.5)
fig.suptitle('CAP-DEPENDENT STAGE5B REGIONS',fontsize=21,fontweight='bold',color=INK,y=.985)
fig.text(.025,.022,'Positions are existing RSSF / R1B snapshot coordinates, not native anatomy adjudication or a new cap selection. No weights / geometry were generated.',fontsize=11,color=INK)
fig.subplots_adjust(top=.92,bottom=.08,wspace=.32)
save(fig,'CAP_DEPENDENT_STAGE5B_REGIONS.png')

seq=j('CAP_CORRECTION_RECOVERY_SEQUENCE_R1.json')
fig,ax=plt.subplots(figsize=(19,15));ax.set_xlim(-2.5,8.4);ax.set_ylim(-.9,10.1);ax.axis('off')
sp={1:(1.6,8.8),2:(1.6,7.7),3:(1.6,6.6),4:(1.6,5.5),5:(1.6,4.4),6:(1.6,3.3),7:(6.1,2.2),8:(1.6,2.2),9:(1.6,.9)}
sn={1:'1  Targeted thumb kinematic authority review\nR2A TIP / IP-tail / local frames',2:'2  Reconcile R2 / R3 input authority\ncentroid seed, live anchors, wrapper semantics',3:'3  Full coupled R3 recompute + authority review\nfields, mincut, closure, boundary and gates',4:'4  Reconcile cap skin-driver / weight authority\nno automatic THUMB_IP_R = 1 inheritance',5:'5  Approved local rig slots + new skin build\nclean baseline + proven independent weights',6:'6  Static fixtures + targeted deformation\nold9, cap37, first-web, collar, edge5879',7:'7  New true-cap bounds\nonly after dependency reconciliation',8:'8  Full Stage6A requalification\nnew harness and region regression',9:'9  Full Stage6B requalification\nnew contact / opposition / SI qualification'}
for a,b in [(1,2),(2,3),(3,4),(4,5),(5,6),(6,8),(8,9)]:
    x,y=sp[a];u,v=sp[b];arrow(ax,(x,y-.43),(u,v+.43),color=BLUE,alpha=1,shrink=1)
arrow(ax,(3.89,3.3),(6.1,2.63),color=BLUE,alpha=1,shrink=1)
arrow(ax,(6.1,1.77),(3.89,.9),color=BLUE,alpha=1,shrink=1)
for s in seq['steps']:
    x,y=sp[s['step']]
    box(ax,x,y,sn[s['step']],w=4.5 if s['step']!=7 else 3.4,h=.78,color='#dbeee3'if s['step']==1 else'#e5ebf3',size=11)
    ax.text(x-2.22 if s['step']!=7 else x-1.68,y+.48,s['tier'],fontsize=9,color=PURPLE)
ax.text(-2.25,9.87,'CAP CORRECTION RECOVERY SEQUENCE',fontsize=20,fontweight='bold',color=INK)
ax.text(-2.25,9.47,'PLANNED ONLY | no remediation, rebuild, R3 solve, Stage6 or strict-bound recompute executed',fontsize=11,color=RED)
ax.text(-2.25,-.1,'NEXT: CAP_DERIVED_THUMB_KINEMATIC_AUTHORITY_REVALIDATION_R1',fontsize=12,fontweight='bold',color=GREEN)
ax.text(-2.25,-.5,'Membership approval does not approve bone endpoints or cap driver values. Preserve all frozen files. STOP after this audit.',fontsize=10.5,color=INK)
save(fig,'CAP_CORRECTION_RECOVERY_SEQUENCE.png')
print(json.dumps({'PNG_count':4,'diagram_sources':'new read-only audit JSONs','production_mutations':0}))
