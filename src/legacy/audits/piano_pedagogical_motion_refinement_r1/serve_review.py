"""Local-only static review server with MP4 byte ranges. No asset writes."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(ROOT),**kw)
 def send_head(self):
  p=Path(self.translate_path(self.path));self.remaining=None
  if not p.is_file():return super().send_head()
  f=p.open('rb');size=p.stat().st_size;start,end=0,size-1
  rang=self.headers.get('Range');m=re.fullmatch(r'bytes=(\d*)-(\d*)',rang or '')
  if m:
   if m[1]:start=int(m[1]);end=min(int(m[2]),end) if m[2] else end
   elif m[2]:start=max(0,size-int(m[2]))
   if start>end or start>=size:
    f.close();self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
  self.send_response(206 if m else 200);self.send_header('Content-Type',self.guess_type(str(p)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if m:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers();f.seek(start);self.remaining=end-start+1;return f
 def copyfile(self,source,out):
  if self.remaining is None:return super().copyfile(source,out)
  left=self.remaining
  try:
   while left:
    data=source.read(min(left,1024*1024))
    if not data:break
    out.write(data);left-=len(data)
  except (ConnectionResetError,BrokenPipeError):pass
if __name__=='__main__':
 print('http://127.0.0.1:8770/audits/piano_pedagogical_motion_refinement_r1/HUMAN_REVIEW.html',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8770),Handler).serve_forever()
