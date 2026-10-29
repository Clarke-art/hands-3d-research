// Local, read-only audit page and baseline media. No deployment.
const http=require('http'),fs=require('fs'),path=require('path');
const root=path.dirname(__dirname),prefix=path.basename(__dirname),port=8874;
const mime={'.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8','.md':'text/plain; charset=utf-8','.txt':'text/plain; charset=utf-8','.jpg':'image/jpeg','.png':'image/png','.mp4':'video/mp4'};
http.createServer((req,res)=>{
  try{
    const url=new URL(req.url,'http://127.0.0.1');
    if(url.pathname==='/'){res.writeHead(302,{Location:`/${prefix}/HUMAN_REVIEW.html`}).end();return;}
    const file=path.resolve(root,decodeURIComponent(url.pathname).replace(/^\/+/,''));
    if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
    const stat=fs.statSync(file);if(!stat.isFile()){res.writeHead(404).end();return;}
    let start=0,end=stat.size-1,status=200;
    const headers={'Content-Type':mime[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
    if(req.headers.range){const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!m){res.writeHead(416).end();return;}start=Number(m[1]);if(m[2])end=Number(m[2]);end=Math.min(end,stat.size-1);if(start>end||start>=stat.size){res.writeHead(416).end();return;}status=206;headers['Content-Range']=`bytes ${start}-${end}/${stat.size}`;}
    headers['Content-Length']=end-start+1;res.writeHead(status,headers);if(req.method==='HEAD'){res.end();return;}fs.createReadStream(file,{start,end}).pipe(res);
  }catch(e){res.writeHead(404).end('Not found');}
}).listen(port,'127.0.0.1',()=>console.log(`http://127.0.0.1:${port}/${prefix}/HUMAN_REVIEW.html`));
