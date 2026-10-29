from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,os
P=Path(__file__).resolve().parent
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)))
(P/'review_server_state.json').write_text(json.dumps(dict(pid=os.getpid(),port=server.server_port,url=f'http://127.0.0.1:{server.server_port}/HUMAN_REVIEW.html')),encoding='utf8')
server.serve_forever()
