"""Local review only. HTTP byte ranges let the in-app browser seek the small MP4s."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def send_head(self):
  self.remaining=None;path=Path(self.translate_path(self.path))
  if not path.is_file():return super().send_head()
  size=path.stat().st_size;start,end=0,size-1;range_header=self.headers.get('Range')
  if range_header:
   match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header)
   if not match:self.send_error(416);return None
   first,last=match.groups()
   if first:start=int(first);end=min(int(last),size-1) if last else size-1
   elif last:start=max(0,size-int(last))
   if start>end or start>=size:self.send_error(416);return None
  stream=path.open('rb');stream.seek(start);self.remaining=end-start+1
  self.send_response(206 if range_header else 200);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(self.remaining));self.send_header('Cache-Control','no-cache')
  if range_header:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers();return stream
 def copyfile(self,source,outputfile):
  if self.remaining is None:return super().copyfile(source,outputfile)
  remaining=self.remaining
  while remaining:
   chunk=source.read(min(65536,remaining))
   if not chunk:break
   outputfile.write(chunk);remaining-=len(chunk)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8777),Handler).serve_forever()
