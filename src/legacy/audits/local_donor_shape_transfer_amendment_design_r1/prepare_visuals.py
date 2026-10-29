import sys,math
sys.dont_write_bytecode=True
from common import *
import numpy as np
C=read(OUT/'FORMAL_DONOR_TRANSFER_COORDINATES_R1.json');G=read(PRIOR/'REVIEW_GEOMETRY.json');smoke=read(OUT/'TEMP_BIND_SMOKE_COORDINATES_R1.json');R=read(DIAG/'DORSAL_MCP_DENT_ROI_R1.json');F=C['faces']
stages={'CURRENT_STAGE4C_R2':G['stages']['STAGE4C_R2'],'OFFICIAL_L1_DONOR':G['stages']['OFFICIAL_L1'],'TEMPORARY_FEASIBILITY_PROBE':G['stages']['TRANSFER_PROBE'],'FORMAL_AMENDMENT_CANDIDATE':{**G['stages']['STAGE4C_R2'],'world_mm':C['candidate_world_mm']},'ANCESTRY_DONOR_TARGET':{**G['stages']['STAGE4C_R2'],'world_mm':C['unrounded_ancestry_target_world_mm']}}
for cid,points in smoke['states']['FORMAL_CANDIDATE'].items():stages['TEMP_'+cid]={**stages['FORMAL_AMENDMENT_CANDIDATE'],'world_mm':points}
origin=np.array(G['frame']['origin_world_mm']);x=np.array(G['frame']['x']);y=np.array(G['frame']['y']);n=np.array(G['frame']['outward'])
def sections(v,faces,fs):
 result={}
 for ang in [0,60,120]:
  d=x*math.cos(math.radians(ang))+y*math.sin(math.radians(ang));pn=np.cross(n,d);segs=[]
  for fi in fs:
   p=faces[fi]
   for k in range(1,len(p)-1):
    tri=[p[0],p[k],p[k+1]];pts=[]
    for a,b in zip(tri,tri[1:]+tri[:1]):
     da=(v[a]-origin)@pn;db=(v[b]-origin)@pn
     if abs(da)<1e-8:pts.append(v[a])
     if da*db<0:pts.append(v[a]+(v[b]-v[a])*da/(da-db))
    if len(pts)>=2:segs.append({'face_id':fi,'world_mm':[pts[0].tolist(),pts[1].tolist()],'profile_mm':[[float((p-origin)@d),float((p-origin)@n)] for p in pts[:2]]})
  result[str(ang)]={'plane_origin_mm':origin.tolist(),'plane_normal_world':pn.tolist(),'tangent_direction_world':d.tolist(),'native_triangle_plane_intersections':segs}
 return result
for label,s in stages.items():s['sections']=sections(np.array(s['world_mm']),s['faces'],s['roi_faces'])
dump('FORMAL_MATCHED_REVIEW_GEOMETRY_R1.json',{'stages':stages,'frame':G['frame'],'camera':G['camera'],'same_camera_registration_as_frozen_feasibility':True,'forensic_colors_required_for_primary_review':False})
dump('FORMAL_NATIVE_SECTION_COMPARISON_R1.json',{'stages':{k:s['sections'] for k,s in stages.items()},'meaning':'Actual native triangle-plane section segments with each native face ID; common physical planes at0/60/120 degrees. Official donor rigidly registered as frozen prior review. Ancestry target uses current topology and frozenRSSF only on authorized54points.','nearest_surface_projection_used':False})
print('Four-column plain-solid and bind/smoke review geometry prepared')
