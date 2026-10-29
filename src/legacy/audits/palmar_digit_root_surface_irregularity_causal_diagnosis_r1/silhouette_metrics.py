import sys
sys.dont_write_bytecode=True
from common import *
import numpy as np, math
from PIL import Image
G=read(OUT/'DIAGNOSTIC_RENDER_GEOMETRY_R1.json');roi=G['roi'];boxes=roi['pixel_rectangles_xyxy'];window=np.zeros((1100,1600),dtype=bool)
for x0,y0,x1,y1 in boxes:window[y0:y1+1,x0:x1+1]=True
def boundary(label):
 a=np.array(Image.open(OUT/f'renders/{label}__MATCHED_CANDIDATE__SILHOUETTE.png'))[:,:,:3];mask=a.min(2)>210
 interior=mask.copy()
 for axis in [0,1]:
  for shift in [-1,1]:interior&=np.roll(mask,shift,axis)
 return mask&~interior
base=boundary('CURRENT_R2_RAW');bp=np.argwhere(base&window);result={}
for label in ['CURRENT_R2_RAW','CURRENT_R2_ZERO','IDX_MCP_30']:
 qp=np.argwhere(boundary(label)&window)
 if len(bp) and len(qp):
  dist=np.sqrt(((bp[:,None,:]-qp[None,:,:])**2).sum(2));haus=max(float(dist.min(1).max()),float(dist.min(0).max()))
 else:haus=None
 result[label]={'RAW_contour_sample_count_in_ROI_pixel_windows':len(bp),'state_contour_sample_count_in_ROI_pixel_windows':len(qp),'symmetric_Hausdorff_pixels':haus,'symmetric_Hausdorff_mm':None if haus is None else haus*G['camera_source']['camera']['orthographic_width_m']*1000/1600,'scope':'actual whole-mesh rendered silhouette boundary clipped to visual ROI windows; not patch wire boundary','raster_limit':'1600x1100 pixel resolution; silhouette center-line extracted with bright mask; not anatomy/product gate'}
d=read(OUT/'PALMAR_IRREGULARITY_SILHOUETTE_DIAGNOSTIC_R1.json');d['actual_rendered_ROI_silhouette_deviation']=result;dump('PALMAR_IRREGULARITY_SILHOUETTE_DIAGNOSTIC_R1.json',d)
m=read(OUT/'PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json')
for label,row in m['states'].items():
 row['local_curvature_proxy_per_shared_edge_rad_per_mm']={str(x['edge_id']):math.radians(x['dihedral_degrees'])/row['edge_length_mm'][str(x['edge_id'])] for x in row['adjacent_face_dihedral'] if str(x['edge_id']) in row['edge_length_mm']}
 if label in result:row['actual_ROI_rendered_silhouette_deviation']=result[label]
dump('PALMAR_IRREGULARITY_GEOMETRY_METRICS_R1.json',m)
print('Actual silhouette measurement',result,flush=True)
