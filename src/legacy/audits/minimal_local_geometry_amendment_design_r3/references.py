import sys
sys.dont_write_bytecode=True
from contact_geometry import *
from itertools import combinations
frames=read(OUT/'FROZEN_RIG_FRAME_EXTRACTION_R3.json')['bones']
def unit(a):return a/max(np.linalg.norm(a),1e-15)
def bone_pair_frame(a,b):
 aa=frames[a];bb=frames[b];pa=np.array(aa['head_world_mm']);pb=np.array(bb['head_world_mm']);xx=unit(pb-pa);yy=unit(np.array(aa['tail_world_mm'])-pa+np.array(bb['tail_world_mm'])-pb);yy=unit(yy-xx*(xx@yy));zz=unit(np.cross(xx,yy))
 dorsal=unit(np.array(aa['frame_world'][2])+np.array(bb['frame_world'][2]))
 if zz@dorsal<0:xx=-xx;zz=-zz
 return (pa+pb)*.5,np.column_stack([xx,yy,zz]),float(np.linalg.norm(pb-pa))
def ray_hit(o,d):
 a=V[tri[:,0]];e1=V[tri[:,1]]-a;e2=V[tri[:,2]]-a;h=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.sum(e1*h,axis=1);valid=abs(det)>1e-12;invd=np.where(valid,1/np.where(valid,det,1),0);s=o-a;u=np.sum(s*h,axis=1)*invd;qq=np.cross(s,e1);v=(qq@d)*invd;t=np.sum(e2*qq,axis=1)*invd
 valid&=(u>=0)&(v>=0)&(u+v<=1)&(t>0)&(baseN[owners]@d>.15)
 return [{'point':o+d*t[i],'face_id':int(owners[i]),'triangle_index':int(i),'distance':float(t[i])} for i in np.where(valid)[0]]
targetpair=('MIDDLE_MCP_R','RING_MCP_R');p0,b0,w0=bone_pair_frame(*targetpair);offset=(origin-p0)@b0
evaluated=[];selected=[]
for name,pair in [('INDEX_MIDDLE_DORSAL_ROOT',('INDEX_MCP_R','MIDDLE_MCP_R')),('RING_LITTLE_DORSAL_ROOT',('RING_MCP_R','LITTLE_MCP_R'))]:
 p,bb,width=bone_pair_frame(*pair);scale=width/w0
 for longitudinal in [-4.,0.,4.]:
  prediction=p+(offset*scale+np.array([0,longitudinal,0]))@bb.T;hits=ray_hit(prediction-bb[:,2]*30,bb[:,2]);hits=sorted(hits,key=lambda z:np.linalg.norm(z['point']-prediction))
  if not hits:continue
  hit=hits[0];center=hit['point'];core=set(F[hit['face_id']]);s1=core|{j for i in core for j in adj[i]};s2=s1|{j for i in s1 for j in adj[i]};fs=face_domain(s1);ns=unit(sum((baseN[fi]*baseAreas[fi] for fi in fs if baseN[fi]@bb[:,2]>.15),np.zeros(3)));xx=unit(bb[:,0]-ns*(bb[:,0]@ns));yy=unit(np.cross(ns,xx));chart=np.column_stack([xx,yy,ns]);q=(V-center)@chart
  centraledges={ei for fi in fs for ei in FE[fi] if all(v in s1 for v in E[ei])};folds=[ei for ei in centraledges if baseA[ei]>=90]
  coefs=np.linalg.lstsq(feat(q[sorted(s2-s1)]),q[sorted(s2-s1),2],rcond=None)[0];res=q[:,2]-feat(q)@coefs
  localbow=set(quad_bowties(V))&fs
  prior={'name':name,'bone_pair':list(pair),'longitudinal_offset_mm':longitudinal,'bone_frame':bb.tolist(),'surface_frame':chart.tolist(),'center_world_mm':center.tolist(),'center_face_id':hit['face_id'],'core_vertex_ids':sorted(core),'support_vertex_ids':sorted(s2),'face_ids':sorted(face_domain(s2)),'central_face_ids':sorted(fs),'central_edge_ids':sorted(centraledges),'valley_axis_world':yy.tolist(),'width_proxy_mm':float(np.ptp(q[sorted(s1),0])),'depth_proxy_mm':float(max(0,-min(res[sorted(core)]))),'boundary_slope_coefficients':coefs[1:3].tolist(),'curvature_fit_coefficients':coefs[3:].tolist(),'native_normal_progression':{str(ei):float(baseA[ei]) for ei in sorted(centraledges)},'central_obtuse_edge_ids':sorted(folds),'quad_bowtie_faces':sorted(localbow),'alignment_to_dent':{'method':'Rigid bone pair frames plus uniform joint-spacing similarity scale, unmodified sampled surface','target_pair_frame':b0.tolist(),'reference_pair_frame':bb.tolist(),'uniform_scale_reference_to_target':1/scale,'target_frame_landmark':p0.tolist(),'reference_frame_landmark':p.tolist(),'no_nonrigid_warp':True},'GEOMETRIC_SHAPE_PRIOR':True,'anatomical_authority':False,'screen':'PROVISIONAL_REFERENCE_REQUIRES_PLAIN_SOLID_REVIEW'}
  evaluated.append(prior)
 options=[z for z in evaluated if z['name']==name]
 if options:selected.append(min(options,key=lambda z:(len(z['central_obtuse_edge_ids']),len(z['quad_bowtie_faces']),abs(z['longitudinal_offset_mm']))))
dump('HEALTHY_DORSAL_MCP_REFERENCE_PATCH_AUDIT_R3.json',{'source':L['stages']['STAGE4C_R2_RAW']['input'],'frozen_rig_frames':ref(OUT/'FROZEN_RIG_FRAME_EXTRACTION_R3.json'),'selection_method':'Two neighboring bone-pair valley predictions aligned using same-hand frozen frames and unaffected surface ray landmarks; three deterministic longitudinal samples per pair, ranked without native-ID symmetry. Complete native neighborhoods retained.','reference_candidates':selected,'screened_locations':evaluated,'HEALTHY_REFERENCE_AVAILABLE':'PENDING_RENDER_REVIEW','REFERENCE_PRIOR_UNAVAILABLE':False,'candidate_count':len(selected),'shape_prior_only':True,'no_anatomy_authority':True})
print([(z['name'],z['center_face_id'],z['width_proxy_mm'],z['depth_proxy_mm'],z['central_obtuse_edge_ids']) for z in selected])
