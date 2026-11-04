# The GAS downloads on talmonlab (talmonlab.bgu.ac.il/downloads/): the files of
# this branch's files/ directory, each served as a download with its type; and
# / , what there is (name, bytes, date), as JSON.
#
# Usage: python serve.py PORT
import json, os, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
TYPES = {'.apk': 'application/vnd.android.package-archive', '.zip': 'application/zip',
         '.exe': 'application/vnd.microsoft.portable-executable', '.json': 'application/json'}

class H(BaseHTTPRequestHandler):
    def _files(self):
        return sorted(f for f in os.listdir(HERE) if not f.startswith('.'))

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        name = self.path.split('?')[0].lstrip('/')
        if name == '':
            out = json.dumps([{'name': f, 'bytes': os.path.getsize(os.path.join(HERE, f)),
                               'date': time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(os.path.join(HERE, f))))}
                              for f in self._files()]).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(out)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            if body: self.wfile.write(out)
            return
        if name not in self._files():
            self.send_error(404)
            return
        path = os.path.join(HERE, name)
        self.send_response(200)
        self.send_header('Content-Type', TYPES.get(os.path.splitext(name)[1], 'application/octet-stream'))
        self.send_header('Content-Length', str(os.path.getsize(path)))
        self.send_header('Content-Disposition', f'attachment; filename="{name}"')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        if body:
            with open(path, 'rb') as f:
                while chunk := f.read(1 << 20):
                    self.wfile.write(chunk)

    def log_message(self, *a):
        pass

ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
