from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import json,os
P=Path(__file__).resolve().parent
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P.parent)))
url=f'http://127.0.0.1:{server.server_port}/{P.name}/DIAGNOSTIC_REVIEW.html'
(P/'review_server_state.json').write_text(json.dumps(dict(pid=os.getpid(),url=url)),encoding='utf8')
server.serve_forever()
