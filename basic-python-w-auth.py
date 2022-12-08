import http.server
import cgi
import base64
import json
from urllib.parse import urlparse, parse_qs
#from bs4 import BeautifulSoup

class CustomServerHandler(http.server.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/xml')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        key = self.server.get_auth_key()

        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            #self.send_response(200)
            #self.send_header('Content-type', 'text/html')
            #self.end_headers()

            getvars = self._parse_GET()

            response = self.path # just display the path if this is not a page meant for the demo

            base_path = urlparse(self.path).path
            if base_path == '/path1':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open("vs-sample-sitemap-html.html", "r") as f:
                    data = f.read()
                response = data
            elif base_path == '/path2':
                self.send_response(200)
                self.send_header('Content-type', 'application/xml')
                self.end_headers()
                with open("vs-sample-sitemap.xml", "r") as f:
                    data = f.read()
                #print(data) you know... debugging.
                response = data

            self.wfile.write(bytes(response, 'utf-8'))
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def _parse_GET(self):
        getvars = parse_qs(urlparse(self.path).query)

        return getvars


class CustomHTTPServer(http.server.HTTPServer):
    key = ''

    def __init__(self, address, handlerClass=CustomServerHandler):
        super().__init__(address, handlerClass)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


if __name__ == '__main__':
    server = CustomHTTPServer(('', 8888))
    server.set_auth('demo', 'demo')
    server.serve_forever()
