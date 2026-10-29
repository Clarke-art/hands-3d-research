const http=require('http'),fs=require('fs'),path=require('path');const root=__dirname;
const types={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.wav':'audio/wav','.png':'image/png','.jpg':'image/jpeg','.json':'application/json','.md':'text/plain; charset=utf-8'};
http.createServer((req,res)=>{
 let file;try{const p=decodeURIComponent(new URL(req.url,'http://localhost').pathname);file=path.resolve(root,'.'+(p==='/'?'/review.html':p));if(!file.startsWith(root+path.sep))throw Error();}catch{res.writeHead(403).end();return;}
 fs.stat(file,(err,stat)=>{if(err||!stat.isFile()){res.writeHead(404).end();return;}let start=0,end=stat.size-1,status=200;const range=req.headers.range;
 if(range){const m=/^bytes=(\d*)-(\d*)$/.exec(range);if(!m){res.writeHead(416).end();return;}start=m[1]?Number(m[1]):Math.max(0,stat.size-Number(m[2]));end=m[2]&&m[1]?Math.min(Number(m[2]),end):end;if(start>end||start>=stat.size){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`}).end();return;}status=206;res.setHeader('Content-Range',`bytes ${start}-${end}/${stat.size}`);}
 res.writeHead(status,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Content-Length':end-start+1,'Cache-Control':'no-cache'});if(req.method==='HEAD'){res.end();return;}fs.createReadStream(file,{start,end}).pipe(res);
 });
}).listen(8789,'127.0.0.1',()=>console.log('Review: http://127.0.0.1:8789/review.html'));
