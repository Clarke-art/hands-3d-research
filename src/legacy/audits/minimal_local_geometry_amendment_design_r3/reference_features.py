import sys
sys.dont_write_bytecode=True
from geometry import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def native_sections(v,fs,center,frame):
 q=(v-center)@frame;out=[]
 for angle in [0,60,120]:
  a=math.radians(angle);axis=np.array([math.cos(a),math.sin(a)]);cut=np.array([-axis[1],axis[0]]);segments=[]
  for fi in fs:
   for k in range(1,len(F[fi])-1):
    t=q[[F[fi][0],F[fi][k],F[fi][k+1]]];side=t[:,:2]@cut;pts=[]
    for i,j in [(0,1),(1,2),(2,0)]:
     if side[i]*side[j]<0:pts.append(t[i]+(t[j]-t[i])*side[i]/(side[i]-side[j]))
     elif abs(side[i])<1e-9:pts.append(t[i])
    if len(pts)>=2:
     p1,p2=max(((a,b) for a in pts for b in pts),key=lambda ab:np.linalg.norm(ab[0]-ab[1]));segments.append({'face_id':fi,'profile_mm':[[float(p[:2]@axis),float(p[2])] for p in [p1,p2]]})
  out.append({'angle_deg':angle,'segments':segments})
 return out

def hull2(points):
 pts=sorted(set(map(tuple,points)))
 def cr(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];up=[]
 for p in pts:
  while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(up)>=2 and cr(up[-2],up[-1],p)<=0:up.pop()
  up.append(p)
 return [list(p) for p in lo[:-1]+up[:-1]]

if __name__=='__main__':
 data=read(OUT/'HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json');(OUT/'renders').mkdir(exist_ok=True)
 for r in data['reference_candidates']:
  center=np.array(r['center_world_mm']);frame=np.array(r['surface_frame']);r['display_context_face_ids']=r['face_ids'];r['display_context_projected_bowtie_face_ids']=sorted(set(r['face_ids'])&baseBow);r['healthy_prior_face_ids']=[fi for fi in r['central_face_ids'] if fi not in baseBow and baseN[fi]@frame[:,2]>.1];r['healthy_prior_vertex_ids']=sorted({i for fi in r['healthy_prior_face_ids'] for i in F[fi]});r['shape_prior_context_policy']='Only the healthy outward central native patch is a solve prior; outer context shown for location is never transferred. Context bowtie flags are disclosed.';r['cross_section_family']=native_sections(V,r['healthy_prior_face_ids'],center,frame);q=(V[r['healthy_prior_vertex_ids']]-center)@frame
  r['silhouette']={'native_patch_tangent_projected_convex_envelope_mm':hull2(q[:,:2]),'native_patch_side_projected_convex_envelope_mm':hull2(q[:,[0,2]]),'description':'Actual patch projection; correspondence is geometric only.'}
  r['boundary_landmarks']=[{'vertex_id':i,'world_mm':V[i].tolist()} for i in sorted(set(r['support_vertex_ids'])-set(r['core_vertex_ids']))];r['screen']='ACCEPTED_LOCAL_GEOMETRIC_SHAPE_PRIOR_AFTER_PLAIN_SOLID_REVIEW';r['review_observation']='Native dorsal root transition has gradual polygon normal progression and no core opposing fold. Reference2 is a shallower shoulder/valley transition; its zero quadratic residual depth is not a copied target depth.'
 data['HEALTHY_REFERENCE_AVAILABLE']=True;data['selection_method']='Neighboring frozen bone-pair predictions; prefer the closest longitudinal correspondence among zero-obtuse, zero-bowtie patches. No optimization for minimum valley depth.';data['REFERENCE_REGION']=[r['name']+':face'+str(r['center_face_id']) for r in data['reference_candidates']];data['alignment_limitation']='Bone-pair frames and unchanged sampled surrounding landmarks determine rigid/similarity alignment. Native surface normal refinement only rotates the chart. No vertex correspondence, mirror anatomy claim, or nonrigid warp.'
 dump('HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json',data)
 family={'TARGET_FAMILY_COUNT':2,'DESIGN_PRIORS':True,'ANATOMICAL_AUTHORITY':False,'A':{'name':'Conservative notch-only surrounding native continuation','valley_retention':'Core normal coordinates weakly guided (0.3 strength); original surface outside support fixed. Core tangent continuation from actual native neighboring positions.','normal_progression':'Explicit central opposing fold hinge target60deg; all originally acute incident edges retain bounded baseline-relative normal progression.','objective_terms':['position displacement','length-normalized first displacement gradient','native graph second displacement bending','soft core surrounding-surface continuation','fixed exterior transition decay']},'B':{'name':'Same-hand reference-guided normalized progression','reference_region':data['REFERENCE_REGION'][0],'soft_depth_slope_prior':'Actual reference native triangles sampled in aligned tangent coordinates; affine trend removed, current surrounding dorsal arch trend retained. Small (0.35) soft height attraction. Absolute depth/width not imposed.','normal_progression':'Central crease target from reference95th-percentile native normal progression with 30deg lower design cap; full local baseline-relative edge constraints retained.','objective_terms':['all A terms','soft reference native profile','reference normal progression']},'C':{'tested':False,'reason':'Allowed only if A/B structurally feasible but visually insufficient. No mechanical third candidate.'},'thresholds_are_anatomy':False,'core_shape_guide_is_R1_or_R2_failed_coordinates':False,'abstract_quadratic_is_primary_target':False,'depth_proxy_only':'Old fixed-reference quadratic depth is reported solely as a diagnostic, never imposed as hard surface target.'}
 dump('REFERENCE_GUIDED_TARGET_FAMILY_R3.json',family)
 fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
 for j,ax in enumerate(axes):
  for r,color in zip(data['reference_candidates'],['#206a7c','#925339']):
   ax.add_collection(LineCollection([s['profile_mm'] for s in r['cross_section_family'][j]['segments']],colors=color,label=r['name']))
  ax.autoscale();ax.set_aspect('equal',adjustable='box');ax.set(title=f'{[0,60,120][j]} degrees',xlabel='Native section distance (mm)',ylabel='Reference local height (mm)');ax.grid(alpha=.2)
 axes[0].legend(fontsize=7);fig.suptitle('Unwarped same-hand reference patches: native section family');fig.savefig(OUT/'renders/REFERENCE_NATIVE_SECTIONS.png',dpi=150);plt.close(fig)
