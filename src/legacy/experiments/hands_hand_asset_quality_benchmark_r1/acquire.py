from pathlib import Path
import urllib.request, json, hashlib, re, sys
sys.dont_write_bytecode=True
ROOT=Path(r'<HANDS_ROOT>')
OUT=ROOT/'experiments/hands_hand_asset_quality_benchmark_r1'
E=OUT/'sources'; E.mkdir(exist_ok=True)
urls={
 'innerscene':'https://www.innerscene.com/tools/library/3d-parts/posable-anatomical-right-hand-f6098b4f',
 'library_terms':'https://www.innerscene.com/tools/library/terms',
 'makehuman_license':'https://static.makehumancommunity.org/about/license.html',
 'mpfb_license':'https://raw.githubusercontent.com/makehumancommunity/mpfb2/master/LICENSE.md',
 'mpfb_assets_license':'https://raw.githubusercontent.com/makehumancommunity/mpfb2/master/LICENSE.ASSETS.md',
 'cc0':'https://creativecommons.org/publicdomain/zero/1.0/legalcode.en',
 'blendswap':'https://blendswap.com/blend/22269',
 'blendswap_download':'https://blendswap.com/blend/22269/download',
 'blender_official':'https://www.blender.org/download/demo-files/'
}
rows=[]
for name,url in urls.items():
 p=E/(name+'.html' if not name.startswith('mpfb') else name+'.md')
 try:
  if p.exists(): data=p.read_bytes(); final=url; typ='CACHED_LOCAL'
  else:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r: data=r.read();final=r.url;typ=r.headers.get('Content-Type')
   p.write_bytes(data)
  rows.append(dict(name=name,url=url,final_url=final,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content_type=typ))
  if name=='innerscene':
   s=data.decode('utf8'); print('LINKS',[(a,b) for a,b in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>',s,re.S) if 'Download' in b or '.glb' in a],flush=True)
  print('FETCH',name,len(data),flush=True)
 except Exception as e: rows.append(dict(name=name,url=url,error=str(e)));print('ERROR',name,str(e),flush=True)
(OUT/'SOURCE_FETCH_RECEIPT.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
