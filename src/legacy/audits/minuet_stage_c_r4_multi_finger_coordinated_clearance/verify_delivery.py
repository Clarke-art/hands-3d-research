from pathlib import Path
import json,re,urllib.request,hashlib
P=Path(__file__).resolve().parent
page=(P/'DIAGNOSTIC_REVIEW.html').read_text(encoding='utf8');links=re.findall(r'(?:href|src)="([^"]+)"',page)
assert all((P/link).is_file() for link in links)
assert not list(P.glob('*.blend')) and not list(P.glob('*.mp4'))
policy=json.loads((P/'PREFLIGHT_POLICY_RECORD.json').read_text(encoding='utf8'))
assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in policy['script_sha256'].items())
url='http://127.0.0.1:53518/'+P.name+'/DIAGNOSTIC_REVIEW.html'
res=urllib.request.urlopen(url);assert res.status==200
f=P/'FINAL_DELIVERY_VERIFICATION.json';d=json.loads(f.read_text(encoding='utf8'));d.update(relative_links_checked=len(links),HTTP_status=res.status,review_url=url,policy_script_hashes_unchanged=True)
f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
print('VERIFIED',len(links),'links; HTTP 200; no new Blend/video; policy unchanged')
