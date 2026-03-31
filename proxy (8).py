#!/usr/bin/env python3
"""
Bonos AR — Servidor de precios en tiempo real
Versión v4: login por Selenium + bridge WebSocket dentro del browser,
replicando el protocolo real detectado en Matriz.
"""
import json
import threading
import time
import sys
import urllib.parse
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("ERROR: py -m pip install selenium webdriver-manager")
    sys.exit(1)

import os
PORT = int(os.environ.get("PORT", 8765))
BASE = "https://matriz.adcap.xoms.com.ar"

TICKERS_TF = [
    "S17A6", "S30A6", "S15Y6", "S29Y6", "T30J6", "S31L6",
    "S31G6", "S30S6", "S30O6", "S30N6", "T15E7", "T30A7", "T31Y7", "T30J7"
]
TICKERS_CER = [
    "X15Y6", "X29Y6", "TZX26", "X31L6", "X30S6", "TZXO6", "X30N6",
    "TZXD6", "TZXM7", "TZXA7", "TZXY7", "TZX27", "TZXD7", "TZX28"
]
ALL = TICKERS_TF + TICKERS_CER
TOPICS = [f"md.bm_MERV_{sym}_24hs" for sym in ALL]
TOPIC_MAP = {f"bm_MERV_{sym}_24hs": sym for sym in ALL}
TOPIC_MAP.update({f"md.bm_MERV_{sym}_24hs": sym for sym in ALL})

prices = {}
status = {
    "connected": False,
    "login_in_progress": False,
    "msg": "Desconectado",
    "last_error": "",
    "last_update": None,
    "ws_url": None,
    "ws_bridge_status": "idle",
}
lock = threading.Lock()
driver_lock = threading.Lock()
browser_driver = None
poller_started = False


def set_status(**kwargs):
    with lock:
        status.update(kwargs)


def snapshot_status():
    with lock:
        return dict(status)


def clear_prices():
    with lock:
        prices.clear()


def get_error_text(driver):
    selectors = [
        (By.CSS_SELECTOR, ".error, .alert-danger, .invalid-feedback, .notification-error, .toast-error, [role='alert']"),
    ]
    keywords = [
        "incorrect", "incorrecto", "inválid", "inval", "credencial",
        "error", "timeout", "timed out", "expir", "bloque", "fall",
        "deneg", "rechaz", "inválido", "inválida"
    ]

    def looks_like_real_error(txt: str) -> bool:
        t = " ".join((txt or "").strip().lower().split())
        if not t:
            return False
        if t in {"usuario", "contraseña", "conectar", "ingresa tu usuario", "ingresa tu contraseña"}:
            return False
        return any(k in t for k in keywords)

    for selector in selectors:
        try:
            nodes = driver.find_elements(*selector)
            for node in nodes:
                txt = (node.text or "").strip()
                if looks_like_real_error(txt):
                    return txt
        except Exception:
            pass

    try:
        body_txt = (driver.find_element(By.TAG_NAME, "body").text or "").strip()
        for line in body_txt.splitlines():
            txt = line.strip()
            if looks_like_real_error(txt):
                return txt
    except Exception:
        pass

    return ""


def ensure_poller():
    global poller_started
    if poller_started:
        return
    poller_started = True
    threading.Thread(target=price_loop, daemon=True).start()


def build_driver():
    print("  Iniciando Chrome en modo headless...")
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,1000")
    opts.add_argument("--disable-extensions")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # En Railway usamos Chrome del sistema; localmente usamos ChromeDriverManager
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.path.exists("/usr/bin/google-chrome"):
        opts.binary_location = "/usr/bin/google-chrome"
        drv = webdriver.Chrome(options=opts)
    else:
        drv = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    drv.set_page_load_timeout(45)
    drv.set_script_timeout(30)
    return drv


def drain_performance_log(driver):
    out = []
    try:
        for entry in driver.get_log("performance"):
            try:
                msg = json.loads(entry["message"])["message"]
                out.append(msg)
            except Exception:
                pass
    except Exception:
        pass
    return out


def randomize_conn_id(url: str) -> str:
    try:
        u = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(u.query, keep_blank_values=True)
        if "conn_id" in qs:
            qs["conn_id"] = [uuid.uuid4().hex + uuid.uuid4().hex]
        new_query = urllib.parse.urlencode(qs, doseq=True)
        return urllib.parse.urlunparse((u.scheme, u.netloc, u.path, u.params, new_query, u.fragment))
    except Exception:
        return url


def find_ws_url(driver, timeout=10):
    deadline = time.time() + timeout
    seen = []
    while time.time() < deadline:
        logs = drain_performance_log(driver)
        for msg in logs:
            if msg.get("method") == "Network.webSocketCreated":
                params = msg.get("params", {})
                url = params.get("url")
                if url and "/ws?" in url:
                    return url
            # fallback in case driver only logs handshake request
            if msg.get("method") == "Network.webSocketWillSendHandshakeRequest":
                params = msg.get("params", {})
                req = params.get("request", {})
                url = req.get("url")
                if url and "/ws?" in url:
                    return url
            seen.append(msg)
        time.sleep(0.5)
    return None


def js_open_bridge(driver, ws_url, topics):
    js = r"""
const wsUrl = arguments[0];
const topics = arguments[1];
const done = arguments[arguments.length - 1];
(function(){
  let finished = false;
  const finish = (obj) => { if (!finished) { finished = true; done(obj); } };
  try {
    if (window.__bonos_bridge && window.__bonos_bridge.ws && window.__bonos_bridge.ws.readyState === 1) {
      finish({ok:true, reused:true, status: window.__bonos_bridge.status || 'open'});
      return;
    }
    if (window.__bonos_bridge && window.__bonos_bridge.ws) {
      try { window.__bonos_bridge.ws.close(); } catch (e) {}
    }
    const bridge = window.__bonos_bridge = {
      messages: [],
      status: 'opening',
      lastError: null,
      lastMessageAt: null,
      sentAt: null,
      wsUrl: wsUrl
    };
    const ws = new WebSocket(wsUrl);
    bridge.ws = ws;
    bridge.pingTimer = null;

    ws.onopen = function() {
      bridge.status = 'open';
      bridge.sentAt = Date.now();
      try {
        ws.send(JSON.stringify({_req:'S', topicType:'md', topics: topics, replace:true}));
      } catch (e) {
        bridge.lastError = 'error suscribiendo: ' + String(e);
      }
      bridge.pingTimer = setInterval(() => {
        try {
          if (ws.readyState === 1) ws.send('ping');
        } catch (e) {}
      }, 15000);
      finish({ok:true, status:'open'});
    };

    ws.onmessage = function(ev) {
      bridge.lastMessageAt = Date.now();
      bridge.messages.push(ev.data);
      if (bridge.messages.length > 1000) {
        bridge.messages.splice(0, bridge.messages.length - 1000);
      }
    };

    ws.onerror = function(ev) {
      bridge.lastError = 'ws error';
    };

    ws.onclose = function(ev) {
      bridge.status = 'closed';
      if (bridge.pingTimer) clearInterval(bridge.pingTimer);
    };

    setTimeout(() => {
      if (bridge.status !== 'open') {
        finish({ok:false, status:bridge.status, error: bridge.lastError || 'timeout abriendo websocket bridge'});
      }
    }, 8000);
  } catch (e) {
    finish({ok:false, error:String(e)});
  }
})();
"""
    return driver.execute_async_script(js, ws_url, topics)


def js_bridge_state(driver):
    js = r"""
const b = window.__bonos_bridge;
if (!b) return null;
return {
  status: b.status,
  lastError: b.lastError,
  wsUrl: b.wsUrl,
  lastMessageAt: b.lastMessageAt,
  readyState: b.ws ? b.ws.readyState : null,
  queue: b.messages ? b.messages.length : 0,
};
"""
    return driver.execute_script(js)


def js_take_messages(driver):
    js = r"""
const b = window.__bonos_bridge;
if (!b || !b.messages) return [];
const out = b.messages.slice();
b.messages.length = 0;
return out;
"""
    return driver.execute_script(js)


def to_num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None


def parse_md_line(line):
    if not isinstance(line, str) or not line.startswith("M:"):
        return None
    parts = line.split("|")
    if len(parts) < 16:
        return None
    topic = parts[0][2:]
    sym = TOPIC_MAP.get(topic)
    if not sym:
        return None

    # Formato inferido desde los frames del WebSocket:
    # M:topic|secId|bidSize|bid|ask|askSize|last|lastTs||turnover|nominalVol|low|high|open||close|closeDate|||prevClose|prevCloseDate
    # Ejemplo: bm_MERV_T30J6_24hs -> bid=135.65 ask=135.7 last=135.7 close=135.7 prevClose=136.25
    payload = {
        "security_id": parts[1] if len(parts) > 1 else None,
        "bid_size": to_num(parts[2]) if len(parts) > 2 else None,
        "bid": to_num(parts[3]) if len(parts) > 3 else None,
        "ask": to_num(parts[4]) if len(parts) > 4 else None,
        "ask_size": to_num(parts[5]) if len(parts) > 5 else None,
        "last": to_num(parts[6]) if len(parts) > 6 else None,
        "last_ts": parts[7] if len(parts) > 7 else None,
        "turnover": to_num(parts[9]) if len(parts) > 9 else None,
        "nominal_volume": to_num(parts[10]) if len(parts) > 10 else None,
        "low": to_num(parts[11]) if len(parts) > 11 else None,
        "high": to_num(parts[12]) if len(parts) > 12 else None,
        "open": to_num(parts[13]) if len(parts) > 13 else None,
        "close": to_num(parts[15]) if len(parts) > 15 else None,
        "close_date": parts[16] if len(parts) > 16 else None,
        "prev_close": to_num(parts[19]) if len(parts) > 19 else None,
        "prev_close_date": parts[20] if len(parts) > 20 else None,
    }

    # si no hay close del día, usar previo
    if payload["close"] is None and payload["prev_close"] is not None:
        payload["close"] = payload["prev_close"]
    payload["ts"] = time.strftime("%H:%M:%S")
    return sym, payload


def process_ws_message(msg):
    count = 0
    if msg is None:
        return count
    if isinstance(msg, str):
        s = msg.strip()
        if not s or s == "ping" or s.startswith("X:"):
            return 0
        if s.startswith("["):
            try:
                arr = json.loads(s)
            except Exception:
                return 0
            for item in arr:
                parsed = parse_md_line(item)
                if parsed:
                    sym, payload = parsed
                    with lock:
                        prices[sym] = payload
                    count += 1
            return count
        parsed = parse_md_line(s)
        if parsed:
            sym, payload = parsed
            with lock:
                prices[sym] = payload
            return 1
    return 0


def ensure_bridge(driver):
    st = js_bridge_state(driver)
    if st and st.get("status") == "open":
        return True

    ws_url = snapshot_status().get("ws_url")
    if not ws_url:
        ws_url = find_ws_url(driver, timeout=8)
        if not ws_url:
            set_status(msg="No pude detectar el WebSocket de Matriz", last_error="No se encontró /ws en performance log")
            return False
        # intento con conn_id nuevo para no depender del socket original de la app
        ws_url = randomize_conn_id(ws_url)
        set_status(ws_url=ws_url)
        print(f"  WebSocket detectado: {ws_url[:160]}")

    res = js_open_bridge(driver, ws_url, TOPICS)
    print(f"  Bridge WS: {res}")
    if not res or not res.get("ok"):
        set_status(msg="No pude abrir el bridge WebSocket", last_error=(res or {}).get("error", "error desconocido"), ws_bridge_status="error")
        return False

    set_status(ws_bridge_status="open", msg="Conectado")
    return True


def do_login(username, password):
    global browser_driver

    set_status(
        connected=False,
        login_in_progress=True,
        msg="Abriendo Matriz...",
        last_error="",
        ws_url=None,
        ws_bridge_status="idle",
    )
    clear_prices()

    driver = build_driver()

    try:
        print("  Abriendo pagina de login...")
        driver.get(BASE + "/login")
        set_status(msg="Cargando login...")
        time.sleep(3)

        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"  Inputs encontrados: {len(inputs)}")
        for i, inp in enumerate(inputs):
            print(
                f"    [{i}] type={inp.get_attribute('type')} "
                f"name={inp.get_attribute('name')} "
                f"id={inp.get_attribute('id')} "
                f"placeholder={inp.get_attribute('placeholder')}"
            )

        user_input = None
        pass_input = None

        for selector in [
            (By.NAME, "username"),
            (By.NAME, "user"),
            (By.ID, "username"),
            (By.ID, "user"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
        ]:
            try:
                user_input = driver.find_element(*selector)
                print(f"  Campo usuario encontrado con: {selector}")
                break
            except Exception:
                pass

        for selector in [
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
        ]:
            try:
                pass_input = driver.find_element(*selector)
                print(f"  Campo password encontrado con: {selector}")
                break
            except Exception:
                pass

        if not user_input or not pass_input:
            driver.save_screenshot("login_debug.png")
            raise Exception("No se encontraron los campos de usuario/password")

        set_status(msg="Completando credenciales...")
        user_input.clear()
        user_input.send_keys(username)
        pass_input.clear()
        pass_input.send_keys(password)

        btn = None
        for selector in [
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "button.btn-primary"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//button[contains(text(),'Ingresar') or contains(text(),'Conectar') or contains(text(),'Login')]"),
            (By.TAG_NAME, "button"),
        ]:
            try:
                btn = driver.find_element(*selector)
                print(f"  Boton encontrado con: {selector}")
                break
            except Exception:
                pass

        if not btn:
            raise Exception("No se encontró el botón de submit")

        print("  Haciendo click en Ingresar...")
        set_status(msg="Enviando login...")
        btn.click()

        print("  Esperando redireccion...")
        set_status(msg="Esperando redirección...")

        redirected = False
        deadline = time.time() + 35
        while time.time() < deadline:
            if "/login" not in driver.current_url:
                redirected = True
                break
            err_txt = get_error_text(driver)
            if err_txt:
                raise Exception(err_txt)
            time.sleep(0.4)

        if not redirected:
            err_txt = get_error_text(driver)
            if err_txt:
                raise Exception(err_txt)
            raise Exception("Timeout esperando redirección luego del login")

        print(f"  Redirigido a: {driver.current_url}")
        time.sleep(4)

        with driver_lock:
            old = browser_driver
            browser_driver = driver
        if old is not None:
            try:
                old.quit()
            except Exception:
                pass

        if not ensure_bridge(driver):
            raise Exception(snapshot_status().get("last_error") or "No se pudo iniciar el bridge de websocket")

        set_status(
            connected=True,
            login_in_progress=False,
            msg="Conectado",
            last_error="",
        )
        print("  Login exitoso — iniciando polling desde WebSocket...")
        ensure_poller()
        return True

    except Exception as e:
        try:
            driver.save_screenshot("login_error.png")
        except Exception:
            pass
        try:
            driver.quit()
        except Exception:
            pass
        set_status(
            connected=False,
            login_in_progress=False,
            msg="Error de login",
            last_error=str(e),
        )
        raise


def login_worker(username, password):
    try:
        do_login(username, password)
    except Exception as e:
        print(f"  ERROR login: {e}")


def price_loop():
    while True:
        snap = snapshot_status()
        if not snap["connected"]:
            time.sleep(1)
            continue

        with driver_lock:
            drv = browser_driver
        if drv is None:
            time.sleep(1)
            continue

        try:
            if not ensure_bridge(drv):
                time.sleep(2)
                continue

            msgs = js_take_messages(drv)
            updated = 0
            for msg in msgs:
                updated += process_ws_message(msg)

            bridge_state = js_bridge_state(drv) or {}
            set_status(ws_bridge_status=bridge_state.get("status", "unknown"))

            if updated:
                set_status(
                    msg=f"Actualizado {time.strftime('%H:%M:%S')}",
                    last_update=time.strftime("%H:%M:%S"),
                    last_error="",
                )
            else:
                set_status(msg="Conectado, esperando ticks...")

        except Exception as e:
            print(f"[WS] ERROR: {e}")
            set_status(msg="Error leyendo WebSocket", last_error=str(e))

        time.sleep(1)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/prices":
            with lock:
                self._json(200, {"prices": dict(prices), "status": dict(status)})
        elif self.path == "/status":
            with lock:
                self._json(200, dict(status))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/login":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        user = (body.get("user") or "").strip()
        password = body.get("password") or ""

        if not user or not password:
            self._json(400, {"ok": False, "msg": "Falta usuario o contraseña"})
            return

        snap = snapshot_status()
        if snap["login_in_progress"]:
            self._json(202, {"ok": True, "started": False, "msg": "Login ya en progreso"})
            return

        threading.Thread(target=login_worker, args=(user, password), daemon=True).start()
        self._json(202, {"ok": True, "started": True, "msg": "Login iniciado"})

    def _json(self, code, data):
        body = json.dumps(data).encode("utf-8")
        try:
            self.send_response(code)
            self.cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError):
            pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"""
  ╔══════════════════════════════════════════╗
  ║   Bonos AR — Servidor de Precios         ║
  ║   Local: http://localhost:{PORT}            ║
  ║   Dejá esta ventana abierta              ║
  ╚══════════════════════════════════════════╝
""")
    ensure_poller()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
        with driver_lock:
            drv = browser_driver
        if drv is not None:
            try:
                drv.quit()
            except Exception:
                pass
