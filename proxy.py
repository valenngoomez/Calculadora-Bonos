#!/usr/bin/env python3
"""
Bonos AR — Servidor de precios
Se conecta a Matriz con credenciales del entorno.
Sin Selenium, sin Chrome.
"""
import os, json, threading, time, ssl, re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError

PORT     = int(os.environ.get("PORT", 8080))
BASE     = "https://matriz.adcap.xoms.com.ar"
MX_USER  = os.environ.get("MATRIZ_USER", "")
MX_PASS  = os.environ.get("MATRIZ_PASS", "")

TICKERS_TF  = ["TZXM6","S17A6","S30A6","S15Y6","S29Y6","T30J6","S31L6",
                "S31G6","S30S6","S30O6","S30N6","T15E7","T30A7","T31Y7","T30J7"]
TICKERS_CER = ["X15Y6","X29Y6","TZX26","X31L6","X30S6","TZXO6","X30N6",
                "TZXD6","TZXM7","TZXA7","TZXY7","TZX27","TZXD7","TZX28"]
ALL = TICKERS_TF + TICKERS_CER

prices  = {}
status  = {"connected": False, "msg": "Iniciando...", "ts": ""}
lock    = threading.Lock()
SESSION_COOKIE = None

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

# Read dashboard HTML (served at /)
DASHBOARD_HTML = b""
try:
    with open("index.html", "rb") as f:
        DASHBOARD_HTML = f.read()
    print(f"Dashboard HTML cargado: {len(DASHBOARD_HTML)} bytes")
except Exception as e:
    print(f"Warning: no se pudo leer index.html: {e}")

def make_req(url, method="GET", body=None, extra_headers={}):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": BASE,
        "Referer": BASE + "/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    if SESSION_COOKIE:
        headers["Cookie"] = SESSION_COOKIE
    headers.update(extra_headers)
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, method=method, headers=headers)
    return urlopen(req, timeout=10, context=CTX)

def get_csrf():
    try:
        req = Request(BASE + "/login", headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        })
        with urlopen(req, timeout=10, context=CTX) as r:
            html = r.read().decode(errors="ignore")
            for pattern in [
                r'"csrfToken"\s*:\s*"([^"]+)"',
                r'name=["\']_csrf["\'] value=["\']([^"\']+)',
                r'_csrf["\']:\s*["\']([^"\']+)',
            ]:
                m = re.search(pattern, html)
                if m:
                    return m.group(1)
    except Exception as e:
        print(f"CSRF error: {e}")
    return ""

def do_login():
    global SESSION_COOKIE
    if not MX_USER or not MX_PASS:
        with lock:
            status["msg"] = "Error: MATRIZ_USER y MATRIZ_PASS no configurados"
        print("ERROR: configurá MATRIZ_USER y MATRIZ_PASS en Railway Variables")
        return False
    print(f"Intentando login como {MX_USER}...")
    csrf = get_csrf()
    print(f"CSRF: {'encontrado' if csrf else 'no encontrado'}")
    try:
        req = Request(
            BASE + "/auth/login",
            data=json.dumps({"username": MX_USER, "password": MX_PASS}).encode(),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": BASE,
                "Referer": BASE + "/login",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "X-Csrf-Token": csrf,
            }
        )
        with urlopen(req, timeout=15, context=CTX) as r:
            set_cookie = r.headers.get("Set-Cookie", "")
            print(f"Login response: HTTP {r.status}")
            print(f"Set-Cookie: {set_cookie[:100]}")
            m = re.search(r'_mtz_web_key=([^;]+)', set_cookie)
            if m:
                SESSION_COOKIE = "_mtz_web_key=" + m.group(1)
                with lock:
                    status["connected"] = True
                    status["msg"] = "Conectado"
                print("Login exitoso!")
                return True
            else:
                print(f"No cookie en respuesta. Body: {r.read()[:200]}")
    except HTTPError as e:
        body = e.read().decode(errors="ignore")
        print(f"Login HTTP {e.code}: {body[:300]}")
        with lock:
            status["msg"] = f"Error login HTTP {e.code}"
    except Exception as e:
        print(f"Login error: {e}")
        with lock:
            status["msg"] = f"Error: {e}"
    return False

def fetch_price(sym):
    global SESSION_COOKIE
    try:
        url = f"{BASE}/rest/marketdata/get?marketId=BYMA&symbol={sym}&entries=LA,OF,BI,CL"
        with make_req(url) as r:
            if r.status == 401:
                SESSION_COOKIE = None
                return
            data = json.loads(r.read())
            md = data.get("marketData", {})
            p = {}
            if md.get("LA"): p["last"]  = md["LA"].get("price")
            if md.get("OF"): p["ask"]   = md["OF"].get("price")
            if md.get("BI"): p["bid"]   = md["BI"].get("price")
            if md.get("CL"): p["close"] = md["CL"].get("price")
            if any(v for v in p.values()):
                with lock:
                    prices[sym] = p
                    prices[sym]["ts"] = time.strftime("%H:%M:%S")
    except Exception:
        pass

def price_loop():
    global SESSION_COOKIE
    while True:
        if not SESSION_COOKIE:
            if not do_login():
                time.sleep(30)
                continue
        for sym in ALL:
            fetch_price(sym)
            time.sleep(0.15)
        with lock:
            status["ts"] = time.strftime("%H:%M:%S")
            status["msg"] = f"Actualizado {status['ts']}"
        time.sleep(5)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(DASHBOARD_HTML))
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML)
        elif self.path == "/prices":
            with lock:
                self._json(200, {"prices": dict(prices), "status": dict(status)})
        elif self.path == "/status":
            with lock:
                self._json(200, dict(status))
        else:
            self.send_response(404); self.end_headers()

    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code); self.cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers(); self.wfile.write(body)

if __name__ == "__main__":
    print(f"Bonos AR iniciando en puerto {PORT}...")
    threading.Thread(target=price_loop, daemon=True).start()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Servidor listo en http://0.0.0.0:{PORT}")
    srv.serve_forever()
