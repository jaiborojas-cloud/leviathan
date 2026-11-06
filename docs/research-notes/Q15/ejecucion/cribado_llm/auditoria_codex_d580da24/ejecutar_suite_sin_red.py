"""Run the unchanged upstream suite with HTTP simulated in memory, no sockets."""
import io, runpy, urllib.request, urllib.error, http.server
from pathlib import Path
class Server:
    def __init__(self, address, handler):
        self.server_port=43210
        self.handler=handler
        global active
        active=self
    def serve_forever(self): pass
http.server.HTTPServer=Server
http.server.BaseHTTPRequestHandler.send_response=lambda self, code: setattr(self,'status',code)
http.server.BaseHTTPRequestHandler.end_headers=lambda self: None
class Response(io.BytesIO): pass
def transport(req, **kwargs):
    url=req.full_url
    if url=='http://127.0.0.1:9/api/chat':
        raise urllib.error.URLError(ConnectionRefusedError('synthetic refusal'))
    if url!='http://127.0.0.1:43210/api/chat':
        raise AssertionError('External network forbidden: '+url)
    h=object.__new__(active.handler)
    h.headers={'Content-Length':str(len(req.data))}
    h.rfile=io.BytesIO(req.data); h.wfile=io.BytesIO()
    h.do_POST()
    if h.status>=400:
        raise urllib.error.HTTPError(url,h.status,'synthetic HTTP failure',None,None)
    return Response(h.wfile.getvalue())
urllib.request.urlopen=transport
runpy.run_path(str(Path(__file__).with_name('pruebas_sinteticas.py')),run_name='__main__')
