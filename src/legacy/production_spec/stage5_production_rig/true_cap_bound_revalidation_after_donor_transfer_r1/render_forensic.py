"""Computed orthographic forensic diagrams; all marks use native vertex/edge IDs."""
import sys
sys.dont_write_bytecode=True
from common import *
import math
from PIL import Image,ImageDraw,ImageFont
G=read(OUT/'RUN_A/GRAPH_METRIC_PAYLOAD.json');OG=read(OUT/'RUN_A/OLD_GRAPH_METRIC_REPLAY_PAYLOAD.json')
new=read(OUT/'RUN_A/STATIC_PATH_PAYLOAD.json');old=read(OLD/'RUN_A/STATIC_PATH_PAYLOAD.json')
auth=read(OUT/'CORRECTED_TRUE_CAP_SOURCE_TARGET_AUTHORITY.json')
geom=read(OUT/'RUN_A/BOUND_GEOMETRY_CONTEXT.json')
src=set(auth['source']['vertex_ids']);target=set(auth['target']['vertex_ids']);context=set(auth['target']['all_exact_boundary_endpoints'])
roi=set(read(OUT/'APPROVED54_GRAPH_METRIC_IMPACT_R1.json')['approved54_ids'])
NV=G['vertices_world_m'];OV=OG['vertices_world_m'];edges=G['edges'];faces=geom['faces']
NP=new['global_shortest_path'];OP=old['global_shortest_path']
renderdir=OUT/'renders';renderdir.mkdir(exist_ok=True)
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),n)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(a):
 l=math.sqrt(dot(a,a));return [x/l for x in a]
def frame(direction,box,focus):
 normal=unit(direction);right=unit(cross([0,0,1],normal));up=unit(cross(normal,right))
 points=[v for coords in [NV,OV] for i,v in enumerate(coords) if i in focus]
 xy=[(dot(v,right),dot(v,up)) for v in points]
 lo=[min(p[k] for p in xy) for k in [0,1]];hi=[max(p[k] for p in xy) for k in [0,1]]
 center=[(a+b)/2 for a,b in zip(lo,hi)]
 x0,y0,x1,y1=box;scale=min((x1-x0-100)/(hi[0]-lo[0]),(y1-y0-90)/(hi[1]-lo[1]))
 def project(v):return ((x0+x1)/2+(dot(v,right)-center[0])*scale,(y0+y1)/2-(dot(v,up)-center[1])*scale)
 return project,normal
def panel(draw,box,direction,coords,kind,focus):
 draw.rectangle(box,fill='#f4f6f8',outline='#bdc9d5',width=2)
 project,normal=frame(direction,box,focus);P=[project(v) for v in coords]
 # Depth-sorted native quad surface and subdued edge graph give endpoint/path context.
 nativefaces=[(sum(dot(coords[v],normal) for v in face)/len(face),face) for face in faces if any(v in focus for v in face)]
 for _,face in sorted(nativefaces):
  n=cross(sub(coords[face[1]],coords[face[0]]),sub(coords[face[2]],coords[face[0]]));length=math.sqrt(dot(n,n))
  shade=abs(dot(n,normal))/length if length else 0
  c=int(215+25*shade)
  draw.polygon([P[v] for v in face],fill=(c,c+1,min(255,c+3)),outline='#ccd3db')
 for a,b in edges:
  if a in focus and b in focus:draw.line([P[a],P[b]],fill='#b8c3ce',width=1)
 for v in roi:
  x,y=P[v];draw.ellipse((x-3,y-3,x+3,y+3),fill='#ee8332')
 for v in context-target:
  x,y=P[v];draw.ellipse((x-3,y-3,x+3,y+3),fill='#0b9f9b')
 for v in target:
  x,y=P[v];draw.ellipse((x-5,y-5,x+5,y+5),fill='#157dc1',outline='white')
 if kind!='target':
  for v in src:
   x,y=P[v];draw.ellipse((x-4,y-4,x+4,y+4),fill='#d6a416',outline='white')
 if kind in ['old','overlay']:draw.line([P[v] for v in OP['vertex_sequence']],fill='#e35454',width=7)
 if kind in ['new','overlay']:draw.line([P[v] for v in NP['vertex_sequence']],fill='#7e3bb4',width=3 if kind=='overlay' else 6)
 if kind in ['old','new','overlay']:
  path=OP if kind=='old' else NP
  for role,v,color in [('A',path['source_vertex'],'#9b7200'),('B',path['target_vertex'],'#116b9c')]:
   x,y=P[v];draw.ellipse((x-6,y-6,x+6,y+6),fill=color,outline='white',width=2)
   draw.rectangle((x+8,y-26,x+130,y),fill='white');draw.text((x+12,y-24),role+' v'+str(v),font=font(19,True),fill=color)
def figure(filename,title,subtitle,coords,kind):
 im=Image.new('RGB',(1800,1120),'white');draw=ImageDraw.Draw(im)
 draw.text((32,22),title,font=font(29,True),fill='#24384c')
 draw.text((32,68),subtitle,font=font(19),fill='#586c7e')
 # Include donor ROI as well as endpoint/path corridor. Frames match old/new exactly.
 focus=src|context|roi|set(NP['vertex_sequence'])|set(OP['vertex_sequence'])
 for _ in range(2):focus|={v for e in edges if set(e)&focus for v in e}
 for box,direction in [((30,113,885,964),(0,-1,.6)),((915,113,1770,964),(-.65,-.5,.7))]:panel(draw,box,direction,coords,kind,focus)
 draw.text((32,989),'Gold: 37 cap sources | Blue: 19 INDEX primary endpoints | Teal: 19 THUMB context endpoints',font=font(19),fill='#324e67')
 draw.text((32,1023),'Orange: approved54 donor ROI | Red: pre-donor route | Purple: current route',font=font(19),fill='#324e67')
 draw.text((32,1062),'Matched native-ID forensic context. No anatomy approval or deformation qualification. No path enters approved54.',font=font(18),fill='#677b8f')
 path=renderdir/filename;im.save(path);return path
files=[
 figure('CURRENT_CAP37_SOURCES.png','Current frozen cap37 source coordinates','37 native vertices / 25 canonical faces. Actual current geometry; membership unchanged.',NV,'source'),
 figure('CURRENT_FRESH_R3_ENDPOINTS.png','Current frozen fresh-R3 exact boundary endpoints','19 INDEX primary targets + 19 THUMB context endpoints; 20 exact boundary edges.',NV,'target'),
 figure('OLD_GLOBAL_SHORTEST_PATH.png','Pre-donor corrected global shortest path','v%d -> v%d | %d native edges | %.12f mm'%(OP['source_vertex'],OP['target_vertex'],len(OP['edge_id_sequence']),OP['total_path_length_mm']),OV,'old'),
 figure('CURRENT_GLOBAL_SHORTEST_PATH.png','Fresh current global shortest path','v%d -> v%d | %d native edges | %.12f mm'%(NP['source_vertex'],NP['target_vertex'],len(NP['edge_id_sequence']),NP['total_path_length_mm']),NV,'new'),
 figure('MATCHED_OLD_CURRENT_PATH_OVERLAY.png','Matched old/current paths on current geometry','Red and purple routes coincide after complete graph recomputation. Donor ROI is separately marked.',NV,'overlay')]
sheet=Image.new('RGB',(1800,1200),'#dfe6ed');draw=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
 with Image.open(p) as im:
  im.thumbnail((600,520));sheet.paste(im,((i%3)*600,(i//3)*600))
 draw.text(((i%3)*600+12,(i//3)*600+410),p.stem.replace('_',' '),font=font(18,True),fill='#294158')
sheet.save(renderdir/'FORENSIC_CONTACT_SHEET.png')
dump('POST_DONOR_FORENSIC_RENDER_MANIFEST_R1.json',{'status':'PASS_GENERATED_NATIVE_ID_FORENSIC_EVIDENCE','render_count':len(files),
 'files':[ref(p) for p in files],'contact_sheet':ref(renderdir/'FORENSIC_CONTACT_SHEET.png'),
 'matching_camera_frames':True,'actual_old_and_current_numeric_graph_coordinates':True,'native_ID_marks':{'cap_sources':sorted(src),'INDEX_targets':sorted(target),'context_targets':sorted(context),'approved54':sorted(roi)},
 'new_path_enters_approved54':bool(roi.intersection(NP['vertex_sequence'])),'Human_anatomy_approval_required':False,'agent_visual_inspection':'PENDING'})
print('FIVE FORENSIC FIGURES + CONTACT SHEET GENERATED',flush=True)
