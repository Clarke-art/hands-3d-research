import sys
sys.dont_write_bytecode=True
import urllib.request,urllib.parse,json
from pathlib import Path
AUD=Path(__file__).resolve().parents[1]
titles=['Male Right Hand - Kolkata 2011-04-19 2333.JPG','Male Right Hand - Kolkata 2011-04-19 2334.JPG','Male Right Hand - Kolkata 2011-04-19 2335.JPG','Hand male 2.jpg','Hand female 5.jpg']
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AnatomicalReferenceReview/1.0 (local educational research)'}),timeout=30) as r:return r.read()
url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(dict(action='query',format='json',prop='imageinfo',iiprop='url|extmetadata',titles='|'.join('File:'+n for n in titles)))
data=json.loads(get(url));(AUD/'_tmp/additional_source_metadata.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for n,page in enumerate(data['query']['pages'].values()):
    if 'imageinfo' not in page:continue
    info=page['imageinfo'][0];name=page['title'][5:];path=AUD/'references'/name
    if not path.exists():path.write_bytes(get(info['url']))
    print(name,info['url'],flush=True)
