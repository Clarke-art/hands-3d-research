// Local-only audit review; no product hosting or publishing.
const http=require('http'),fs=require('fs'),path=require('path');
const root=__dirname,old=path.resolve(root,'../minuet_target_key_hand_position_planning_r1'),port=8871;
const mime={'.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8','.md':'text/plain; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.mp4':'video/mp4','.blend':'application/octet-stream'};
http.createServer((req,res)=>{try{
 const url=new URL(req.url,'http://127.0.0.1');let rel=decodeURIComponent(url.pathname).replace(/^\/+/,''),base=root;
 if(rel.startsWith('before/')){base=old;rel=rel.slice(7)}
 const file=path.resolve(base,rel||'HUMAN_REVIEW.html');if(file!==base&&!file.startsWith(base+path.sep)){res.writeHead(403).end();return}
 const stat=fs.statSync(file);if(!stat.isFile()){res.writeHead(404).end();return}
 const headers={'Content-Type':mime[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};let start=0,end=stat.size-1,status=200;
 if(req.headers.range){const match=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);if(!match){res.writeHead(416).end();return}if(match[1]){start=Number(match[1]);if(match[2])end=Number(match[2])}else{start=Math.max(0,stat.size-Number(match[2]))}end=Math.min(end,stat.size-1);if(start>end||start>=stat.size){res.writeHead(416).end();return}status=206;headers['Content-Range']=`bytes ${start}-${end}/${stat.size}`}
 headers['Content-Length']=end-start+1;res.writeHead(status,headers);if(req.method==='HEAD'){res.end();return}fs.createReadStream(file,{start,end}).pipe(res);
 }catch(e){res.writeHead(404).end('Not found')}}).listen(port,'127.0.0.1',()=>console.log('http://127.0.0.1:'+port+'/HUMAN_REVIEW.html'));
