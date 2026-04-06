"""
Servidor Railway — solo sirve el dashboard HTML.
Todo el procesamiento de precios ocurre en el proxy_local.py
corriendo en la PC del usuario.
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8080))

with open("/app/index.html", "rb") as f:
    DASHBOARD = f.read()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(DASHBOARD))
            self.end_headers()
            self.wfile.write(DASHBOARD)
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    print(f"Dashboard sirviendo en puerto {PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
