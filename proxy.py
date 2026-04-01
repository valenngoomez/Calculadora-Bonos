#!/usr/bin/env python3
"""
Bonos AR — Servidor de precios en tiempo real
Versión v4: login por Selenium + bridge WebSocket dentro del browser,
replicando el protocolo real detectado en Matriz.
"""
import os
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
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("ERROR: py -m pip install selenium webdriver-manager")
    sys.exit(1)

PORT = int(os.environ.get("PORT", 8080))
BASE = "https://matriz.adcap.xoms.com.ar"

DASHBOARD = b'<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Bonos AR</title>\n<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">\n<style>\n:root{\n  --bg:#06090f;--bg2:#0b1120;--bg3:#0f1929;--bg4:#152034;--bg5:#1b2a42;\n  --b1:rgba(255,255,255,.04);--b2:rgba(255,255,255,.09);--b3:rgba(255,255,255,.15);\n  --tw:#fff;--t2:#8899bb;--t3:#3d5070;\n  --blue:#5b9af8;--blueD:rgba(91,154,248,.13);\n  --purple:#a97cf5;--purpD:rgba(169,124,245,.13);\n  --green:#27d98a;--greenD:rgba(39,217,138,.10);\n  --red:#f2564a;--amber:#f5aa24;--amberD:rgba(245,170,36,.10);--teal:#22cfc8;\n  --mono:\'IBM Plex Mono\',monospace;--sans:\'IBM Plex Sans\',system-ui,sans-serif;\n}\n*{box-sizing:border-box;margin:0;padding:0;}\nhtml,body{background:var(--bg);color:var(--tw);font-family:var(--sans);font-size:13px;}\n\nheader{height:46px;background:var(--bg2);border-bottom:1px solid var(--b3);display:flex;align-items:center;padding:0 12px;gap:0;position:sticky;top:0;z-index:100;}\n.logo{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:600;padding-right:12px;border-right:1px solid var(--b2);margin-right:10px;flex-shrink:0;}\n.lring{width:19px;height:19px;border-radius:50%;border:2px solid var(--blue);display:flex;align-items:center;justify-content:center;animation:rp 2.8s ease-in-out infinite;}\n@keyframes rp{0%,100%{box-shadow:0 0 0 0 rgba(91,154,248,.5)}50%{box-shadow:0 0 0 5px rgba(91,154,248,0)}}\n.ldot{width:5px;height:5px;border-radius:50%;background:var(--blue);}\n.macro{display:flex;align-items:center;}\n.mi{display:flex;align-items:baseline;gap:4px;padding:0 9px;border-right:1px solid var(--b1);white-space:nowrap;}\n.ml{font-size:9px;text-transform:uppercase;letter-spacing:.6px;color:var(--t3);font-weight:500;}\n.mv{font-family:var(--mono);font-size:11.5px;font-weight:500;}\n.liq-wrap{display:flex;align-items:center;gap:5px;padding:0 9px;border-right:1px solid var(--b1);flex-shrink:0;}\n.liq-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.6px;color:var(--t3);font-weight:500;}\n.liq-i{width:88px;background:var(--bg4);border:1px solid var(--b2);color:var(--amber);font-family:var(--mono);font-size:11px;padding:2px 5px;border-radius:4px;outline:none;}\n.liq-i:focus{border-color:var(--amber);}\n.hdr-r{margin-left:auto;display:flex;align-items:center;gap:6px;flex-shrink:0;}\n.badge{display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:600;letter-spacing:.5px;}\n.b-live{background:var(--greenD);border:1px solid rgba(39,217,138,.25);color:var(--green);}\n.b-demo{background:var(--amberD);border:1px solid rgba(245,170,36,.3);color:var(--amber);}\n.bdot{width:5px;height:5px;border-radius:50%;background:currentColor;}\n.ts{font-size:10px;color:var(--t3);font-family:var(--mono);}\nselect.isel{background:var(--bg4);border:1px solid var(--b2);color:var(--t2);font-family:var(--sans);font-size:10px;padding:3px 6px;border-radius:4px;outline:none;cursor:pointer;}\n.btn{background:var(--bg4);border:1px solid var(--b2);color:var(--t2);padding:4px 9px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;white-space:nowrap;}\n.btn:hover{color:var(--tw);border-color:var(--blue);}\n.btn-d{border-color:rgba(169,124,245,.3);color:var(--purple);}\n.btn-d:hover{border-color:var(--purple);}\n\n.panel{border-bottom:1px solid var(--b2);}\n.phead{height:36px;background:var(--bg2);border-bottom:1px solid var(--b2);display:flex;align-items:center;padding:0 10px;gap:9px;position:sticky;top:46px;z-index:50;}\n.ptag{font-size:9px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;padding:2px 7px;border-radius:2px;}\n.ptag-tf{background:var(--blueD);color:var(--blue);border:1px solid rgba(91,154,248,.25);}\n.ptag-cer{background:var(--purpD);color:var(--purple);border:1px solid rgba(169,124,245,.25);}\n.ptitle{font-size:11px;font-weight:500;color:var(--t2);}\n.pact{margin-left:auto;display:flex;gap:5px;}\n.tbtn{background:none;border:1px solid var(--b1);color:var(--t3);padding:2px 8px;border-radius:2px;font-family:var(--sans);font-size:10px;cursor:pointer;}\n.tbtn:hover{border-color:var(--b2);color:var(--t2);}\n.tbtn.on{background:var(--bg5);color:var(--tw);border-color:var(--b2);}\n.cer-info{padding:3px 10px;font-size:10px;color:var(--t3);border-bottom:1px solid var(--b1);}\n\n.tw{overflow-x:auto;}\ntable{border-collapse:collapse;white-space:nowrap;} .tw{overflow-x:auto;width:100%;}\nthead th{background:var(--bg3);color:var(--t3);font-size:9px;font-weight:500;letter-spacing:.4px;text-transform:uppercase;padding:4px 5px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--b2);cursor:pointer;user-select:none;}\nthead th:first-child{text-align:left;padding-left:8px;}\nthead th:hover{color:var(--t2);}\n.ton{color:var(--blue)!important;}\n.hb{color:rgba(91,154,248,.6)!important;}\n.hp{color:rgba(169,124,245,.6)!important;}\n.ha{color:rgba(245,170,36,.6)!important;}\n.hs{border-left:1px solid rgba(245,170,36,.2)!important;color:rgba(245,170,36,.6)!important;}\n.hm{color:rgba(245,170,36,.5)!important;font-style:italic;}\ntbody tr{border-bottom:1px solid var(--b1);}\ntbody tr:hover{background:var(--bg3);}\ntd{padding:4px 5px;text-align:right;font-family:var(--mono);font-size:10.5px;white-space:nowrap;color:var(--tw);}\ntd:first-child{text-align:left;padding-left:8px;font-family:var(--sans);}\ntd.sa{border-left:1px solid rgba(245,170,36,.15);}\n.tn{font-size:11px;font-weight:600;}\n.td{font-size:8.5px;color:var(--t3);margin-top:1px;}\n.cg{color:var(--green);}.cr{color:var(--red);}.cb{color:var(--blue);}.ca{color:var(--amber);}.ct{color:var(--teal);}.cp{color:var(--purple);}\n\n/* manual price input */\n.man-inp{width:58px;font-family:var(--mono);font-size:10.5px;padding:1px 4px;border-radius:3px;text-align:right;outline:none;background:transparent;border:1px solid transparent;color:var(--t3);transition:all .15s;}\n.man-inp:focus{border-color:var(--amber);color:var(--amber);background:var(--bg4);}\n.man-inp.filled{background:rgba(245,170,36,.08);border-color:rgba(245,170,36,.4);color:var(--amber);} .man-inp::placeholder{color:var(--t3);font-size:9.5px;}\n\n/* MODAL */\n.mbg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:999;align-items:center;justify-content:center;}\n.mbox{background:var(--bg2);border:1px solid var(--b3);border-radius:8px;width:580px;max-width:96vw;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;}\n.mhead{display:flex;align-items:center;padding:12px 16px;border-bottom:1px solid var(--b2);gap:8px;flex-shrink:0;}\n.mtabs{display:flex;border-bottom:1px solid var(--b2);padding:0 16px;flex-shrink:0;}\n.mtab{background:none;border:none;border-bottom:2px solid transparent;color:var(--t2);padding:8px 14px 7px;font-family:var(--sans);font-size:11px;cursor:pointer;font-weight:500;margin-bottom:-1px;}\n.mtab.on{color:var(--tw);border-bottom-color:var(--purple);}\n.mpane{flex:1;overflow-y:auto;padding:12px 16px;display:flex;flex-direction:column;gap:10px;}\n.mshare{padding:8px 16px;border-top:1px solid var(--b2);display:flex;gap:6px;align-items:center;flex-shrink:0;background:rgba(169,124,245,.04);}\n.mfoot{padding:7px 16px;border-top:1px solid var(--b1);font-size:10px;color:var(--t3);display:flex;align-items:center;gap:10px;flex-shrink:0;}\n.mfoot b{color:var(--purple);font-family:var(--mono);font-weight:400;}\ntextarea.mta{width:100%;height:110px;background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:11px;padding:8px;border-radius:4px;resize:vertical;outline:none;}\ntextarea.mta:focus{border-color:var(--blue);}\n.hint{font-size:10px;color:var(--t3);line-height:1.7;}\n.hint code{background:var(--bg4);padding:1px 4px;border-radius:3px;color:var(--t2);font-family:var(--mono);}\n.brow{display:flex;gap:6px;flex-wrap:wrap;}\n.bg{background:var(--bg4);border:1px solid rgba(39,217,138,.3);color:var(--green);padding:5px 12px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;}\n.bg:hover{background:rgba(39,217,138,.08);}\n.br{background:var(--bg4);border:1px solid rgba(242,86,74,.3);color:var(--red);padding:5px 12px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;}\n.br:hover{background:rgba(242,86,74,.08);}\n.imsg{font-size:10px;color:var(--green);display:none;padding:2px 0;}\n.dtbl{width:100%;border-collapse:collapse;font-size:11px;}\n.dtbl th{background:var(--bg3);color:var(--t3);font-size:9px;font-weight:500;text-transform:uppercase;letter-spacing:.4px;padding:4px 10px;text-align:right;border-bottom:1px solid var(--b2);}\n.dtbl th:first-child{text-align:left;}\n.dtbl td{padding:3px 10px;text-align:right;border-bottom:1px solid var(--b1);color:var(--tw);}\n.dtbl td:first-child{text-align:left;}\n.dtbl tr.act{background:rgba(169,124,245,.08);}\n.dtbl tr.act td{color:var(--purple);}\n.dbtn{background:none;border:none;color:var(--t3);cursor:pointer;font-size:11px;padding:0 2px;}\n.dbtn:hover{color:var(--red);}\n.dempty{text-align:center;padding:20px;color:var(--t3);font-size:11px;}\n</style>\n</head>\n<body>\n\n<header>\n  <div class="logo"><div class="lring"><div class="ldot"></div></div>Bonos AR</div>\n  <div class="macro">\n    <div class="mi"><span class="ml">MEP</span><span class="mv cb" id="v-mep">$1.407</span></div>\n    <div class="mi"><span class="ml">CCL</span><span class="mv ct" id="v-ccl">\xe2\x80\x94</span></div>\n    <div class="mi">\n      <span class="ml">CER</span>\n      <span class="mv cp" id="v-cer" style="cursor:pointer;border-bottom:1px dashed rgba(169,124,245,.4)" title="Click para editar" onclick="editCerHdr()">\xe2\x80\x94</span>\n      <input id="v-cer-inp" type="number" step="0.0001" style="display:none;width:76px;background:var(--bg4);border:1px solid rgba(169,124,245,.5);color:var(--purple);font-family:var(--mono);font-size:11px;padding:2px 5px;border-radius:4px;outline:none;" onblur="commitCerHdr(this)" onkeydown="if(event.key===\'Enter\')this.blur();if(event.key===\'Escape\')cancelCerHdr(this)">\n    </div>\n  </div>\n  <div class="liq-wrap">\n    <span class="liq-lbl">Liquidaci\xc3\xb3n</span>\n    <input class="liq-i" id="liq-i" type="text" placeholder="27/03/2026" maxlength="10" onblur="onLiqBlur(this)" onkeydown="if(event.key===\'Enter\')this.blur()">\n  </div>\n  <div class="hdr-r">\n    <div class="badge b-demo" id="v-badge"><div class="bdot"></div><span id="v-st">DEMO</span></div>\n    <span class="ts" id="v-ts">\xe2\x80\x94</span>\n    <select class="isel" id="isel" onchange="changeInterval()">\n      <option value="5">5 seg</option>\n      <option value="10" selected>10 seg</option>\n      <option value="30">30 seg</option>\n      <option value="60">1 min</option>\n      <option value="180">3 min</option>\n      <option value="0">Manual</option>\n    </select>\n    <button class="btn" onclick="doRefresh()">\xe2\x86\xbb Actualizar</button>\n    <button class="btn btn-d" onclick="openModal()">\xe2\x9a\x99 Datos</button>\n  </div>\n</header>\n\n<div class="panel">\n  <div class="phead">\n    <span class="ptag ptag-tf">TF</span>\n    <span class="ptitle">Tasa Fija \xe2\x80\x94 BONCAP / LECAP</span>\n    <div class="pact">\n      <button class="tbtn on" id="tfb0" onclick="setTFV(0)">Base</button>\n      <button class="tbtn"   id="tfb1" onclick="setTFV(1)">c/ Comisi\xc3\xb3n</button>\n      <button class="tbtn"             onclick="dlTF()">\xe2\x86\x93 CSV</button>\n    </div>\n  </div>\n  <div id="tf-body"></div>\n</div>\n\n<div class="panel">\n  <div class="phead">\n    <span class="ptag ptag-cer">CER</span>\n    <span class="ptitle">Ajustables CER \xe2\x80\x94 BONCER / LECER</span>\n    <div class="pact">\n      <button class="tbtn on" id="cerb0" onclick="setCERV(0)">Base</button>\n      <button class="tbtn"   id="cerb1" onclick="setCERV(1)">c/ Comisi\xc3\xb3n</button>\n      <button class="tbtn"              onclick="dlCER()">\xe2\x86\x93 CSV</button>\n    </div>\n  </div>\n  <div class="cer-info" id="cer-info">CER actual: \xe2\x80\x94</div>\n  <div id="cer-body"></div>\n</div>\n\n<!-- MODAL -->\n<div class="mbg" id="modal">\n  <div class="mbox">\n    <div class="mhead">\n      <span style="font-size:12px;font-weight:600;">Datos de referencia</span>\n      <span style="font-size:10px;color:var(--t3);margin-left:4px;">localStorage del browser</span>\n      <button onclick="closeModal()" style="margin-left:auto;background:none;border:none;color:var(--t2);font-size:16px;cursor:pointer;line-height:1;">\xe2\x9c\x95</button>\n    </div>\n    <div class="mtabs">\n      <button class="mtab on" id="tab-cer" onclick="switchTab(\'cer\')">Serie CER</button>\n      <button class="mtab"    id="tab-hol" onclick="switchTab(\'hol\')">Feriados</button>\n    </div>\n    <div class="mpane" id="pane-cer">\n      <div class="hint">Peg\xc3\xa1 desde Excel (dos columnas: fecha y valor).<br>Formatos: <code>dd/mm/aa</code> <code>dd/mm/aaaa</code> <code>yyyy-mm-dd</code> \xc2\xb7 Separador: tab, coma o punto y coma.</div>\n      <textarea class="mta" id="cer-ta" placeholder="01/01/16&#9;5.0386&#10;12/03/26&#9;721.5850&#10;..."></textarea>\n      <div class="brow">\n        <button class="bg" onclick="importCER()">\xe2\x86\x91 Importar</button>\n        <button class="btn" onclick="exportCER()">\xe2\x86\x93 Exportar CSV</button>\n        <button class="br" onclick="clearCER()">\xe2\x9c\x95 Limpiar todo</button>\n      </div>\n      <div class="imsg" id="cer-msg"></div>\n      <div id="cer-tbl"></div>\n    </div>\n    <div class="mpane" id="pane-hol" style="display:none;">\n      <div class="hint">Peg\xc3\xa1 una columna de fechas desde Excel.<br>Formatos: <code>dd/mm/aa</code> <code>dd/mm/aaaa</code> <code>yyyy-mm-dd</code> \xc2\xb7 Se suman a los del c\xc3\xb3digo (2025-2027 incluidos).</div>\n      <textarea class="mta" id="hol-ta" placeholder="01/01/26&#10;24/03/26&#10;02/04/26&#10;..."></textarea>\n      <div class="brow">\n        <button class="bg" onclick="importHol()">\xe2\x86\x91 Importar</button>\n        <button class="btn" onclick="exportHol()">\xe2\x86\x93 Exportar CSV</button>\n        <button class="br" onclick="clearHol()">\xe2\x9c\x95 Limpiar importados</button>\n      </div>\n      <div class="imsg" id="hol-msg"></div>\n      <div id="hol-tbl"></div>\n    </div>\n    <div class="mshare">\n      <span style="font-size:10px;color:var(--t3);flex:1;">Para compartir con otra persona:</span>\n      <button class="bg" style="font-size:10px;padding:4px 10px;" onclick="exportAll()">\xe2\x86\x93 Exportar configuraci\xc3\xb3n</button>\n      <label class="btn" style="font-size:10px;padding:4px 10px;cursor:pointer;border-color:rgba(39,217,138,.3);color:var(--green);">\xe2\x86\x91 Importar configuraci\xc3\xb3n<input type="file" accept=".json" style="display:none" onchange="importAll(this)"></label>\n    </div>\n    <div class="mfoot">\n      <span id="m-cer-cnt">\xe2\x80\x94</span> \xc2\xb7 Lag: <b id="m-lag">\xe2\x80\x94</b> \xc2\xb7 CER en uso: <b id="m-use">\xe2\x80\x94</b> \xc2\xb7 <span id="m-hol-cnt" style="color:var(--teal)">\xe2\x80\x94</span>\n    </div>\n  </div>\n</div>\n\n<script>\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   HOLIDAYS (base hardcoded + localStorage)\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst HOL = new Set([\n  \'2025-01-01\',\'2025-03-03\',\'2025-03-04\',\'2025-03-24\',\'2025-04-02\',\'2025-04-17\',\n  \'2025-04-18\',\'2025-05-01\',\'2025-05-25\',\'2025-06-20\',\'2025-07-09\',\'2025-08-17\',\n  \'2025-10-12\',\'2025-11-21\',\'2025-12-08\',\'2025-12-25\',\n  \'2026-01-01\',\'2026-02-16\',\'2026-02-17\',\'2026-03-24\',\'2026-04-02\',\'2026-04-03\',\n  \'2026-04-04\',\'2026-05-01\',\'2026-05-25\',\'2026-06-19\',\'2026-06-20\',\'2026-07-09\',\n  \'2026-08-17\',\'2026-10-12\',\'2026-11-20\',\'2026-12-08\',\'2026-12-25\',\n  \'2027-01-01\',\'2027-02-15\',\'2027-02-16\',\'2027-03-24\',\'2027-04-02\',\'2027-06-20\',\n  \'2027-07-09\',\'2027-08-16\',\'2027-10-11\',\'2027-12-08\',\'2027-12-25\',\n]);\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   DATE UTILS\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst D = (y,m,d) => new Date(y, m, d);\nconst iso = d => d.getFullYear()+\'-\'+(\'0\'+(d.getMonth()+1)).slice(-2)+\'-\'+(\'0\'+d.getDate()).slice(-2);\nconst fmt = d => (\'0\'+d.getDate()).slice(-2)+\'/\'+(\'0\'+(d.getMonth()+1)).slice(-2)+\'/\'+d.getFullYear();\nconst isBD = d => d.getDay()!==0 && d.getDay()!==6 && !HOL.has(iso(d));\n\nfunction nextBD(d){\n  const r=D(d.getFullYear(),d.getMonth(),d.getDate()+1);\n  while(!isBD(r)) r.setDate(r.getDate()+1);\n  return r;\n}\nfunction wdBack(d,n){\n  const r=D(d.getFullYear(),d.getMonth(),d.getDate());\n  let c=0; while(c<n){r.setDate(r.getDate()-1);if(isBD(r))c++;} return r;\n}\nfunction dDiff(a,b){\n  return Math.round((D(b.getFullYear(),b.getMonth(),b.getDate())-D(a.getFullYear(),a.getMonth(),a.getDate()))/86400000);\n}\nfunction days360(a,b){\n  let y1=a.getFullYear(),m1=a.getMonth()+1,d1=a.getDate();\n  let y2=b.getFullYear(),m2=b.getMonth()+1,d2=b.getDate();\n  if(d1===31)d1=30; if(d2===31&&d1===30)d2=30;\n  return 360*(y2-y1)+30*(m2-m1)+(d2-d1);\n}\nfunction parseDate(s){\n  s=(s||\'\').trim();\n  if(/^\\d{4}-\\d{2}-\\d{2}$/.test(s)){const[y,m,d]=s.split(\'-\');return D(+y,+m-1,+d);}\n  const m2=s.match(/^(\\d{1,2})[\\/\\-](\\d{1,2})[\\/\\-](\\d{2,4})$/);\n  if(m2){let[,dd,mm,yy]=m2;if(yy.length===2)yy=+yy<50?\'20\'+yy:\'19\'+yy;return D(+yy,+mm-1,+dd);}\n  return null;\n}\nfunction parseIso(s){const d=parseDate(s);return(d&&!isNaN(d))?iso(d):null;}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   LOCALSTORAGE\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst K_CER=\'bar2_cer\', K_HOL=\'bar2_hol\';\nconst lsCer = ()=>{try{return JSON.parse(localStorage.getItem(K_CER)||\'{}\')}catch(e){return{}}};\nconst lsHol = ()=>{try{return new Set(JSON.parse(localStorage.getItem(K_HOL)||\'[]\'))}catch(e){return new Set()}};\nconst savCer = m=>{try{localStorage.setItem(K_CER,JSON.stringify(m))}catch(e){}};\nconst savHol = s=>{try{localStorage.setItem(K_HOL,JSON.stringify([...s].sort()))}catch(e){}};\n\nfunction cerForDate(isoDate){\n  const map=lsCer(),keys=Object.keys(map).sort();\n  let val=null,key=null;\n  for(const k of keys){if(k<=isoDate&&(!key||k>key)){key=k;val=map[k];}}\n  return{val,key};\n}\nfunction mergeHol(){for(const d of lsHol())HOL.add(d);}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   STATE\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nlet LIQ;\nlet CER_VAL = 716.446;\nlet TFV=0, CERV=0;\nlet TF_SK=\'d\', TF_SA=true, CER_SK=\'dc\', CER_SA=true;\nconst TF_MAN={}, CER_MAN={};  // manual prices\n\n// API/demo prices (updated by doRefresh)\nconst TP={TZXM6:212.68,S17A6:108.00,S30A6:123.73,S15Y6:100.69,S29Y6:125.35,T30J6:134.00,\n  S31L6:106.62,S31G6:112.53,S30S6:100.70,S30O6:113.30,S30N6:105.99,T15E7:127.15,\n  T30A7:114.00,T31Y7:107.40,T30J7:108.95};\nconst CP={X15Y6:102.93,X29Y6:110.90,TZX26:360.60,X31L6:105.58,X30S6:99.20,TZXO6:147.30,\n  X30N6:106.59,TZXD6:258.55,TZXM7:189.70,TZXA7:104.75,TZXY7:102.50,TZX27:339.45,\n  TZXD7:237.65,TZX28:301.70};\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   BOND DATA\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst TF_BONDS=[\n  {t:\'TZXM6\',vto:D(2026,2,31),em:\'30/04/2024\',pago:214.536,com:.02},\n  {t:\'S17A6\', vto:D(2026,3,17),em:\'15/12/2025\',pago:110.124,com:.02},\n  {t:\'S30A6\', vto:D(2026,3,30),em:\'30/09/2025\',pago:127.486,com:.02},\n  {t:\'S15Y6\', vto:D(2026,4,15),em:\'16/03/2026\',pago:105.178,com:.02},\n  {t:\'S29Y6\', vto:D(2026,4,29),em:\'30/05/2025\',pago:132.044,com:.02},\n  {t:\'T30J6\', vto:D(2026,5,30),em:\'17/01/2025\',pago:144.896,com:.02},\n  {t:\'S31L6\', vto:D(2026,6,31),em:\'30/01/2026\',pago:117.678,com:.02},\n  {t:\'S31G6\', vto:D(2026,7,31),em:\'31/08/2026\',pago:127.065,com:.02},\n  {t:\'S30S6\', vto:D(2026,8,30),em:\'16/03/2026\',pago:117.536,com:.02},\n  {t:\'S30O6\', vto:D(2026,9,30),em:\'31/10/2025\',pago:135.280,com:.02},\n  {t:\'S30N6\', vto:D(2026,10,30),em:\'15/12/2025\',pago:129.885,com:.02},\n  {t:\'T15E7\', vto:D(2027,0,15), em:\'31/01/2025\',pago:161.104,com:.02},\n  {t:\'T30A7\', vto:D(2027,3,30), em:\'31/10/2025\',pago:157.344,com:.02},\n  {t:\'T31Y7\', vto:D(2027,4,31), em:\'15/12/2025\',pago:151.558,com:.02},\n  {t:\'T30J7\', vto:D(2027,5,30), em:\'16/01/2026\',pago:156.031,com:.02},\n];\nconst CER_BONDS=[\n  {t:\'X15Y6\', vto:D(2026,4,15), em:\'27/02/2026\',cerI:701.614,com:.005},\n  {t:\'X29Y6\', vto:D(2026,4,29), em:\'28/11/2025\',cerI:651.898,com:.005},\n  {t:\'TZX26\', vto:D(2026,5,30), em:\'01/02/2024\',cerI:200.388,com:.005},\n  {t:\'X31L6\', vto:D(2026,6,31), em:\'30/01/2026\',cerI:685.551,com:.005},\n  {t:\'X30S6\', vto:D(2026,8,30), em:\'16/03/2026\',cerI:714.985,com:.005},\n  {t:\'TZXO6\', vto:D(2026,9,30), em:\'31/10/2024\',cerI:480.153,com:.005},\n  {t:\'X30N6\', vto:D(2026,10,30),em:\'15/12/2025\',cerI:659.679,com:.005},\n  {t:\'TZXD6\', vto:D(2026,11,15),em:\'15/03/2024\',cerI:271.048,com:.005},\n  {t:\'TZXM7\', vto:D(2027,2,31), em:\'20/05/2024\',cerI:361.318,com:.005},\n  {t:\'TZXA7\', vto:D(2027,3,30), em:\'28/11/2025\',cerI:651.898,com:.005},\n  {t:\'TZXY7\', vto:D(2027,4,31), em:\'15/12/2025\',cerI:659.679,com:.005},\n  {t:\'TZX27\', vto:D(2027,5,30), em:\'01/02/2024\',cerI:200.388,com:.005},\n  {t:\'TZXD7\', vto:D(2027,11,15),em:\'15/03/2024\',cerI:271.048,com:.005},\n  {t:\'TZX28\', vto:D(2028,5,30), em:\'01/02/2024\',cerI:200.388,com:.005},\n];\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   COMPUTE\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction getMEP(){return parseFloat((document.getElementById(\'v-mep\').textContent||\'\').replace(/\\./g,\'\').replace(\',\',\'.\').replace(/[^\\d.]/g,\'\'))||1407;}\n\nfunction compTF(){\n  const mep=getMEP();\n  return TF_BONDS.map(b=>{\n    const apiP = TP[b.t]||100;\n    const p    = TF_MAN[b.t]!=null ? TF_MAN[b.t] : apiP;\n    const d = dDiff(LIQ, b.vto); if(d<=0) return null;\n    const dur=d/365, r=b.pago/p, ret=r-1;\n    const tna=ret*365/d, tea=Math.pow(r,365/d)-1, tem=Math.pow(tea+1,30/365)-1;\n    const mepBE=mep*(1+ret), tnaCC=tna-b.com;\n    const precCC=Math.round(b.pago/(1+tnaCC*d/365)*1000)/1000;\n    const comDir=precCC/p-1, teaCC=Math.pow(b.pago/precCC,365/d)-1, temCC=Math.pow(teaCC+1,30/365)-1;\n    return{t:b.t,em:b.em,vto:b.vto,pago:b.pago,com:b.com,apiP,p,d,dur,ret,tna,tea,tem,mepBE,tnaCC,precCC,comDir,teaCC,temCC};\n  }).filter(Boolean);\n}\n\nfunction compCER(){\n  return CER_BONDS.map(b=>{\n    const apiP = CP[b.t]||100;\n    const p    = CER_MAN[b.t]!=null ? CER_MAN[b.t] : apiP;\n    const dc=dDiff(LIQ,b.vto); if(dc<=0) return null;\n    const d3=days360(LIQ,b.vto), dur=dc/365;\n    const ratio=100*CER_VAL/b.cerI/p;\n    const tna=(Math.pow(ratio,180/d3)-1)*2, tir=Math.pow(ratio,365/dc)-1;\n    const tnaCC=tna-b.com;\n    const precCC=Math.round(100*CER_VAL/(b.cerI*Math.pow(1+tnaCC/2,d3/180))*1000)/1000;\n    const comDir=precCC/p-1, teaCC=Math.pow(100*CER_VAL/b.cerI/precCC,365/dc)-1;\n    return{t:b.t,em:b.em,vto:b.vto,cerI:b.cerI,com:b.com,apiP,p,dc,d3,dur,tna,tir,tnaCC,precCC,comDir,teaCC};\n  }).filter(Boolean);\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   FORMAT\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst N=(v,d=3)=>v==null||isNaN(v)?\'\xe2\x80\x94\':v.toFixed(d);\nconst P=(v,d=2)=>v==null||isNaN(v)?\'\xe2\x80\x94\':(v*100).toFixed(d)+\'%\';\nconst ARS=v=>\'<span class="ca">$\'+Math.round(v).toLocaleString(\'es-AR\')+\'</span>\'; const ARSN=v=>v==null||isNaN(v)?\'\xe2\x80\x94\':\'<span class="ca">$\'+Math.round(v).toLocaleString(\'es-AR\')+\'</span>\';\nfunction PC(v,d=2,t=0){if(v==null||isNaN(v))return\'<span style="color:var(--t3)">\xe2\x80\x94</span>\';return\'<span class="\'+(v>t?\'cg\':v<t?\'cr\':\'\')+\'"> \'+(v*100).toFixed(d)+\'%</span>\';}\nfunction TnaC(v){const pv=v*100;return\'<span class="\'+(pv>=32?\'cg\':pv>=28?\'ca\':\'cr\')+\'">\'+pv.toFixed(2)+\'%</span>\';}\nfunction TeaC(v){const pv=v*100;return\'<span class="\'+(pv>=35?\'cg\':pv>=30?\'ca\':\'cr\')+\'">\'+pv.toFixed(2)+\'%</span>\';}\nfunction CerC(v){const pv=v*100;return\'<span class="\'+(pv>3?\'cg\':pv>0?\'ca\':pv>-3?\'cb\':\'cr\')+\'">\'+pv.toFixed(2)+\'%</span>\';}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   MANUAL PRICE INPUT CELL\n   Two separate <td>s: API price | Manual input\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction apiCell(apiP){\n  return \'<span style="font-family:var(--mono);font-size:11px;color:var(--t2)">\'+N(apiP,3)+\'</span>\';\n}\nfunction manCell(ns, t, manP){\n  const filled = manP != null;\n  return \'<input class="man-inp\'+(filled?\' filled\':\'\')+\'" id="\'+ns+\'m\'+t+\'"\'+\n    \' type="number" step="0.001"\'+\n    \' placeholder="manual"\'+\n    \' value="\'+(filled?N(manP,3):\'\')+\'"\'+\n    \' onchange="commitMan(\\\'\'+ns+\'\\\',\\\'\'+t+\'\\\',this)"\'+\n    \' title="Vac\xc3\xado = usa precio API \xc2\xb7 Con valor = calcula con ese precio">\';\n}\n\nfunction commitMan(ns,t,inp){\n  const v=parseFloat(inp.value);\n  if(isNaN(v)||v<=0||inp.value.trim()===\'\'){\n    if(ns===\'tf\') delete TF_MAN[t]; else delete CER_MAN[t];\n    inp.value=\'\'; inp.classList.remove(\'filled\');\n  } else {\n    if(ns===\'tf\') TF_MAN[t]=v; else CER_MAN[t]=v;\n    inp.classList.add(\'filled\');\n  }\n  ns===\'tf\' ? renderTF() : renderCER();\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   TABLE BUILDER\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction mkTable(rows, cols, sk, sa, sfn){\n  const sorted=[...rows].sort((a,b)=>{\n    const av=a[sk],bv=b[sk];\n    if(typeof av===\'string\')return sa?av.localeCompare(bv):bv.localeCompare(av);\n    return sa?(av-bv):(bv-av);\n  });\n  const ths=cols.map(c=>{\n    const on=sk===c.k?\' ton\':\'\', arr=sk===c.k?(sa?\' \xe2\x96\xb2\':\' \xe2\x96\xbc\'):\'\';\n    return \'<th class="\'+(c.h||\'\')+on+\'" onclick="\'+sfn+\'(\\\'\'+c.k+\'\\\')">\'+c.l+arr+\'</th>\';\n  }).join(\'\');\n  const trs=sorted.map(r=>\n    \'<tr>\'+cols.map(c=>\'<td class="\'+(c.tc||\'\')+\'">\'+c.f(r)+\'</td>\').join(\'\')+\'</tr>\'\n  ).join(\'\');\n  return \'<div class="tw"><table><thead><tr>\'+ths+\'</tr></thead><tbody>\'+trs+\'</tbody></table></div>\';\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   TF VIEWS\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction tfBase(rows){ return mkTable(rows,[\n  {k:\'t\',    l:\'Bono\',      h:\'\',   f:r=>\'<div class="tn">\'+r.t+\'</div><div class="td">\'+r.em+\'</div>\'},\n  {k:\'apiP\', l:\'P. API\',   h:\'hb\', f:r=>apiCell(r.apiP)},\n  {k:\'p\',    l:\'P. Manual\',h:\'hm\', f:r=>manCell(\'tf\',r.t,TF_MAN[r.t]??null)},\n  {k:\'d\',    l:\'D\xc3\xadas\',      h:\'\',   f:r=>r.d},\n  {k:\'vto\',  l:\'Vto.\',      h:\'\',   f:r=>fmt(r.vto)},\n  {k:\'pago\', l:\'Pago\',      h:\'\',   f:r=>N(r.pago,3)},\n  {k:\'ret\',  l:\'Ret.\',      h:\'\',   f:r=>PC(r.ret)},\n  {k:\'tna\',  l:\'TNA\',       h:\'hb\', f:r=>TnaC(r.tna)},\n  {k:\'tea\',  l:\'TEA\',       h:\'hb\', f:r=>TeaC(r.tea)},\n  {k:\'tem\',  l:\'TEM\',       h:\'\',   f:r=>P(r.tem,3)},\n  {k:\'mepBE\',l:\'MEP BE\',    h:\'ha mepbe\', tc:\'mepbe\', f:r=>\'<span class="ca">\'+Math.round(r.mepBE).toLocaleString(\'es-AR\')+\'</span>\'},\n],TF_SK,TF_SA,\'stf\');}\n\nfunction tfCC(rows){ return mkTable(rows,[\n  {k:\'t\',    l:\'Bono\',       h:\'\',   f:r=>\'<div class="tn">\'+r.t+\'</div><div class="td">\'+r.em+\'</div>\'},\n  {k:\'apiP\', l:\'P. API\',    h:\'hb\', f:r=>apiCell(r.apiP)},\n  {k:\'p\',    l:\'P. Manual\', h:\'hm\', f:r=>manCell(\'tf\',r.t,TF_MAN[r.t]??null)},\n  {k:\'d\',    l:\'D\xc3\xadas\',       h:\'\',   f:r=>r.d},\n  {k:\'com\',  l:\'Com.\',       h:\'hs\', tc:\'sa\',f:r=>\'<span class="ca">\'+P(r.com)+\'</span>\'},\n  {k:\'tnaCC\',l:\'TNA c/Com.\', h:\'ha\', f:r=>\'<span class="ca">\'+P(r.tnaCC)+\'</span>\'},\n  {k:\'precCC\',l:\'P. c/Com.\', h:\'\',   f:r=>N(r.precCC,3)},\n  {k:\'comDir\',l:\'Com. Dir.\', h:\'\',   f:r=>PC(r.comDir,4)},\n  {k:\'teaCC\',l:\'TEA c/Com.\', h:\'ha\', f:r=>TeaC(r.teaCC)},\n  {k:\'temCC\',l:\'TEM c/Com.\', h:\'\',   f:r=>P(r.temCC,3)},\n],TF_SK,TF_SA,\'stf\');}\n\nfunction stf(k){if(TF_SK===k)TF_SA=!TF_SA;else{TF_SK=k;TF_SA=true;}renderTF();}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   CER VIEWS\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction cerBase(rows){ return mkTable(rows,[\n  {k:\'t\',   l:\'Ticker\',      h:\'\',   f:r=>\'<div class="tn">\'+r.t+\'</div><div class="td">\'+r.em+\'</div>\'},\n  {k:\'apiP\',l:\'P. API\',      h:\'hp\', f:r=>apiCell(r.apiP)},\n  {k:\'p\',   l:\'P. Manual\',   h:\'hm\', f:r=>manCell(\'cer\',r.t,CER_MAN[r.t]??null)},\n  {k:\'dc\',  l:\'D\xc3\xadas\',        h:\'\',   f:r=>r.dc},\n  {k:\'vto\', l:\'Vto.\',        h:\'\',   f:r=>fmt(r.vto)},\n  {k:\'cerI\',l:\'CER inic.\',   h:\'\',   f:r=>N(r.cerI,2)},\n  {k:\'tna\', l:\'TNA 180/360\', h:\'hp\', f:r=>CerC(r.tna)},\n  {k:\'tir\', l:\'TIR\',         h:\'hp\', f:r=>CerC(r.tir)},\n],CER_SK,CER_SA,\'scer\');}\n\nfunction cerCC(rows){ return mkTable(rows,[\n  {k:\'t\',    l:\'Ticker\',      h:\'\',   f:r=>\'<div class="tn">\'+r.t+\'</div><div class="td">\'+r.em+\'</div>\'},\n  {k:\'apiP\', l:\'P. API\',     h:\'hp\', f:r=>apiCell(r.apiP)},\n  {k:\'p\',    l:\'P. Manual\',  h:\'hm\', f:r=>manCell(\'cer\',r.t,CER_MAN[r.t]??null)},\n  {k:\'dc\',   l:\'D\xc3\xadas\',        h:\'\',   f:r=>r.dc},\n  {k:\'com\',  l:\'Com.\',        h:\'hs\', tc:\'sa\',f:r=>\'<span class="ca">\'+P(r.com)+\'</span>\'},\n  {k:\'tnaCC\',l:\'TNA c/Com.\',  h:\'ha\', f:r=>\'<span class="ca">\'+P(r.tnaCC,2)+\'</span>\'},\n  {k:\'precCC\',l:\'P. c/Com.\', h:\'\',   f:r=>N(r.precCC,3)},\n  {k:\'comDir\',l:\'Com. Dir.\', h:\'\',   f:r=>PC(r.comDir,4)},\n  {k:\'teaCC\',l:\'TEA c/Com.\', h:\'ha\', f:r=>CerC(r.teaCC)},\n],CER_SK,CER_SA,\'scer\');}\n\nfunction scer(k){if(CER_SK===k)CER_SA=!CER_SA;else{CER_SK=k;CER_SA=true;}renderCER();}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   RENDER\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction renderTF(){ document.getElementById(\'tf-body\').innerHTML = TFV===0?tfBase(compTF()):tfCC(compTF()); }\nfunction renderCER(){ document.getElementById(\'cer-body\').innerHTML = CERV===0?cerBase(compCER()):cerCC(compCER()); }\nfunction setTFV(v){TFV=v;document.getElementById(\'tfb0\').classList.toggle(\'on\',v===0);document.getElementById(\'tfb1\').classList.toggle(\'on\',v===1);renderTF();}\nfunction setCERV(v){CERV=v;document.getElementById(\'cerb0\').classList.toggle(\'on\',v===0);document.getElementById(\'cerb1\').classList.toggle(\'on\',v===1);renderCER();}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   LIQUIDATION DATE\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction setLIQ(d){\n  LIQ=d;\n  document.getElementById(\'liq-i\').value=fmt(d);\n  updateCERFromLS();\n}\nfunction onLiqBlur(inp){\n  const d=parseDate(inp.value);\n  if(!d||isNaN(d)){inp.style.borderColor=\'var(--red)\';return;}\n  inp.style.borderColor=\'\';\n  LIQ=d; inp.value=fmt(d);\n  updateCERFromLS(); renderTF(); renderCER();\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   CER VALUE\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction updateCERFromLS(){\n  if(!LIQ) return;\n  const lag=wdBack(LIQ,10), lagISO=iso(lag);\n  const {val,key}=cerForDate(lagISO);\n  if(val!=null){\n    CER_VAL=val;\n    document.getElementById(\'v-cer\').textContent=val.toFixed(4);\n    document.getElementById(\'cer-info\').innerHTML=\n      \'CER actual: <b style="color:var(--purple);font-family:var(--mono)">\'+val.toFixed(4)+\'</b>\'+\n      \' &nbsp;\xc2\xb7&nbsp; lag: <span style="color:var(--teal);font-family:var(--mono)">\'+lagISO+\'</span>\'+\n      \' &nbsp;\xc2\xb7&nbsp; dato de: <span style="color:var(--teal);font-family:var(--mono)">\'+key+\'</span>\';\n  } else {\n    document.getElementById(\'v-cer\').textContent=CER_VAL.toFixed(4);\n    document.getElementById(\'cer-info\').innerHTML=\n      \'CER actual: <b style="color:var(--purple);font-family:var(--mono)">\'+CER_VAL.toFixed(4)+\'</b>\'+\n      \' &nbsp;\xc2\xb7&nbsp; <span style="color:var(--red)">\xe2\x9a\xa0 sin dato para lag \'+lagISO+\' \xe2\x80\x94 import\xc3\xa1 la serie en \xe2\x9a\x99 Datos</span>\';\n  }\n  renderCER();\n}\n\nfunction editCerHdr(){\n  const sp=document.getElementById(\'v-cer\'),inp=document.getElementById(\'v-cer-inp\');\n  inp.value=CER_VAL.toFixed(4); sp.style.display=\'none\'; inp.style.display=\'inline-block\'; inp.focus(); inp.select();\n}\nfunction cancelCerHdr(inp){document.getElementById(\'v-cer\').style.display=\'\';inp.style.display=\'none\';}\nfunction commitCerHdr(inp){\n  const v=parseFloat(inp.value);\n  if(!isNaN(v)&&v>0){CER_VAL=v;document.getElementById(\'v-cer\').textContent=v.toFixed(4);\n    document.getElementById(\'cer-info\').innerHTML=\'CER actual: <b style="color:var(--purple);font-family:var(--mono)">\'+v.toFixed(4)+\'</b> <span style="color:var(--amber)">(manual)</span>\';\n    renderCER();}\n  cancelCerHdr(inp);\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   MODAL\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction openModal(){document.getElementById(\'modal\').style.display=\'flex\';refreshModal();}\nfunction closeModal(){document.getElementById(\'modal\').style.display=\'none\';}\nfunction switchTab(t){\n  document.getElementById(\'pane-cer\').style.display=t===\'cer\'?\'\':\'none\';\n  document.getElementById(\'pane-hol\').style.display=t===\'hol\'?\'\':\'none\';\n  document.getElementById(\'tab-cer\').classList.toggle(\'on\',t===\'cer\');\n  document.getElementById(\'tab-hol\').classList.toggle(\'on\',t===\'hol\');\n}\nfunction refreshModal(){\n  const map=lsCer(), set=lsHolSet=lsHol();\n  const lag=LIQ?iso(wdBack(LIQ,10)):null;\n  const{val,key}=lag?cerForDate(lag):{val:null,key:null};\n  document.getElementById(\'m-cer-cnt\').textContent=Object.keys(map).length+\' fechas CER\';\n  document.getElementById(\'m-lag\').textContent=lag||\'\xe2\x80\x94\';\n  document.getElementById(\'m-use\').textContent=val!=null?(val.toFixed(4)+\' (\'+key+\')\'):\'sin dato\';\n  document.getElementById(\'m-hol-cnt\').textContent=set.size+\' feriados importados\';\n  refreshCERTbl(); refreshHolTbl();\n}\nfunction showMsg(id,txt){const e=document.getElementById(id);e.textContent=txt;e.style.display=\'block\';setTimeout(()=>e.style.display=\'none\',3000);}\n\n// CER CRUD\nfunction importCER(){\n  const raw=document.getElementById(\'cer-ta\').value.trim();\n  if(!raw){alert(\'Peg\xc3\xa1 datos primero\');return;}\n  const map=lsCer();let ok=0,sk=0;\n  for(const line of raw.split(\'\\n\')){\n    const parts=line.trim().split(/[\\t,;]+/);\n    if(parts.length<2){sk++;continue;}\n    const f=parseIso(parts[0]),v=parseFloat(parts[1].replace(\',\',\'.\'));\n    if(!f||isNaN(v)){sk++;continue;}\n    map[f]=v;ok++;\n  }\n  savCer(map);\n  document.getElementById(\'cer-ta\').value=\'\';\n  showMsg(\'cer-msg\',\'\xe2\x9c\x93 \'+ok+\' fechas importadas\'+(sk?\' (\'+sk+\' ignoradas)\':\'\'));\n  refreshModal(); updateCERFromLS();\n}\nfunction exportCER(){\n  const map=lsCer(),k=Object.keys(map).sort();\n  if(!k.length){alert(\'Sin datos\');return;}\n  dl(\'cer_serie\',\'fecha,valor\\n\'+k.map(x=>x+\',\'+map[x].toFixed(4)).join(\'\\n\'));\n}\nfunction clearCER(){if(!confirm(\'\xc2\xbfBorrar toda la serie CER?\'))return;localStorage.removeItem(K_CER);refreshModal();}\nfunction delCerRow(k){const m=lsCer();delete m[k];savCer(m);refreshModal();updateCERFromLS();}\nfunction refreshCERTbl(){\n  const map=lsCer(),keys=Object.keys(map).sort().reverse();\n  const lag=LIQ?iso(wdBack(LIQ,10)):null;\n  const{key:ak}=lag?cerForDate(lag):{key:null};\n  const wrap=document.getElementById(\'cer-tbl\');\n  if(!keys.length){wrap.innerHTML=\'<div class="dempty">Sin datos guardados.</div>\';return;}\n  wrap.innerHTML=\'<table class="dtbl"><thead><tr><th>Fecha</th><th>Valor CER</th><th></th></tr></thead><tbody>\'+\n    keys.map(k=>\'<tr class="\'+(k===ak?\'act\':\'\')+\'"><td>\'+k+(k===ak?\' \xe2\x97\x84 en uso\':\'\')+\n    \'</td><td>\'+map[k].toFixed(4)+\'</td><td><button class="dbtn" onclick="delCerRow(\\\'\'+k+\'\\\')">\xe2\x9c\x95</button></td></tr>\'\n    ).join(\'\')+\'</tbody></table>\';\n}\n\n// HOL CRUD\nfunction importHol(){\n  const raw=document.getElementById(\'hol-ta\').value.trim();\n  if(!raw){alert(\'Peg\xc3\xa1 fechas primero\');return;}\n  const set=lsHol();let ok=0,sk=0;\n  for(const line of raw.split(\'\\n\')){\n    let found=false;\n    for(const part of line.split(/[\\t,;]+/)){\n      const f=parseIso(part.trim());\n      if(f){set.add(f);HOL.add(f);ok++;found=true;break;}\n    }\n    if(!found&&line.trim())sk++;\n  }\n  savHol(set);\n  document.getElementById(\'hol-ta\').value=\'\';\n  showMsg(\'hol-msg\',\'\xe2\x9c\x93 \'+ok+\' feriados importados\'+(sk?\' (\'+sk+\' ignorados)\':\'\'));\n  refreshModal(); updateCERFromLS(); renderTF(); renderCER();\n}\nfunction exportHol(){\n  const set=lsHol();if(!set.size){alert(\'Sin feriados importados\');return;}\n  dl(\'feriados\',\'fecha\\n\'+[...set].sort().join(\'\\n\'));\n}\nfunction clearHol(){\n  if(!confirm(\'\xc2\xbfBorrar feriados importados?\'))return;\n  localStorage.removeItem(K_HOL);\n  alert(\'Eliminados. Recarg\xc3\xa1 la p\xc3\xa1gina para actualizar el lag.\');\n  refreshModal();\n}\nfunction delHolRow(k){const s=lsHol();s.delete(k);savHol(s);HOL.delete(k);refreshModal();updateCERFromLS();renderCER();}\nfunction refreshHolTbl(){\n  const set=lsHol();\n  const wrap=document.getElementById(\'hol-tbl\');\n  if(!set.size){wrap.innerHTML=\'<div class="dempty">Sin feriados importados. Los del c\xc3\xb3digo (2025-2027) est\xc3\xa1n activos.</div>\';return;}\n  wrap.innerHTML=\'<table class="dtbl"><thead><tr><th>Fecha</th><th></th></tr></thead><tbody>\'+\n    [...set].sort().reverse().map(k=>\'<tr><td>\'+k+\'</td><td><button class="dbtn" onclick="delHolRow(\\\'\'+k+\'\\\')">\xe2\x9c\x95</button></td></tr>\'\n    ).join(\'\')+\'</tbody></table>\';\n}\n\n// EXPORT/IMPORT ALL\nfunction exportAll(){\n  const data={version:2,cer_serie:lsCer(),feriados:[...lsHol()].sort(),exportado:new Date().toISOString()};\n  dl(\'bonos_ar_config\',JSON.stringify(data,null,2));\n  showMsg(\'cer-msg\',\'\xe2\x9c\x93 Exportado: \'+Object.keys(data.cer_serie).length+\' CER + \'+data.feriados.length+\' feriados\');\n}\nfunction importAll(input){\n  const f=input.files[0];if(!f)return;\n  const r=new FileReader();\n  r.onload=e=>{\n    try{\n      const d=JSON.parse(e.target.result);\n      if(d.cer_serie){const m=lsCer();Object.assign(m,d.cer_serie);savCer(m);}\n      if(Array.isArray(d.feriados)){const s=lsHol();for(const x of d.feriados){s.add(x);HOL.add(x);}savHol(s);}\n      refreshModal();updateCERFromLS();renderTF();renderCER();\n      showMsg(\'cer-msg\',\'\xe2\x9c\x93 Importado correctamente\');\n    }catch(err){alert(\'Error: \'+err.message);}\n    input.value=\'\';\n  };\n  r.readAsText(f);\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   CSV DOWNLOAD\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nfunction dl(name,csv){\n  const a=document.createElement(\'a\');\n  a.href=\'data:text/csv;charset=utf-8,%EF%BB%BF\'+encodeURIComponent(csv);\n  a.download=name+\'.csv\'; document.body.appendChild(a); a.click(); document.body.removeChild(a);\n}\nfunction dlTF(){\n  const rows=compTF(),cc=TFV===1;\n  const h=cc?[\'Bono\',\'Precio API\',\'Precio Manual\',\'Dias\',\'Com TNA\',\'TNA c/Com\',\'Precio c/Com\',\'Com Directa\',\'TEA c/Com\',\'TEM c/Com\']:[\'Bono\',\'Precio API\',\'Precio Manual\',\'Dias\',\'Duration\',\'Vto\',\'Pago\',\'Ret Total\',\'TNA\',\'TEA\',\'TEM\',\'MEP BE\'];\n  const f=r=>cc?[r.t,N(r.apiP,3),TF_MAN[r.t]?N(TF_MAN[r.t],3):\'\',r.d,P(r.com),P(r.tnaCC),N(r.precCC,3),P(r.comDir,4),P(r.teaCC),P(r.temCC)]:[r.t,N(r.apiP,3),TF_MAN[r.t]?N(TF_MAN[r.t],3):\'\',r.d,N(r.dur,2),fmt(r.vto),N(r.pago,3),P(r.ret),P(r.tna),P(r.tea),P(r.tem),Math.round(r.mepBE)];\n  dl(\'bonos_tf_\'+iso(LIQ), h.join(\',\')+\'\\n\'+rows.map(r=>f(r).map(v=>\'"\'+v+\'"\').join(\',\')).join(\'\\n\'));\n}\nfunction dlCER(){\n  const rows=compCER(),cc=CERV===1;\n  const h=cc?[\'Ticker\',\'Precio API\',\'Precio Manual\',\'Dias\',\'Com TNA\',\'TNA c/Com\',\'Precio c/Com\',\'Com Directa\',\'TEA c/Com\']:[\'Ticker\',\'Precio API\',\'Precio Manual\',\'Dias\',\'Duration\',\'Vto\',\'CER inicial\',\'TNA (180/360)\',\'TIR\'];\n  const f=r=>cc?[r.t,N(r.apiP,3),CER_MAN[r.t]?N(CER_MAN[r.t],3):\'\',r.dc,P(r.com),P(r.tnaCC,2),N(r.precCC,3),P(r.comDir,4),P(r.teaCC,2)]:[r.t,N(r.apiP,3),CER_MAN[r.t]?N(CER_MAN[r.t],3):\'\',r.dc,N(r.dur,2),fmt(r.vto),N(r.cerI,2),P(r.tna,2),P(r.tir,2)];\n  dl(\'bonos_cer_\'+iso(LIQ), h.join(\',\')+\'\\n\'+rows.map(r=>f(r).map(v=>\'"\'+v+\'"\').join(\',\')).join(\'\\n\'));\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   API REFRESH\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nasync function doRefresh(){\n  document.getElementById(\'v-st\').textContent=\'...\';\n  try{\n    const[rN,rB,rM,rC]=await Promise.allSettled([\n      fetch(\'https://data912.com/live/arg/notes\',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),\n      fetch(\'https://data912.com/live/arg/bonds\', {signal:AbortSignal.timeout(7000)}).then(r=>r.json()),\n      fetch(\'https://dolarapi.com/v1/dolares/bolsa\',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),\n      fetch(\'https://dolarapi.com/v1/dolares/contadoconliqui\',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),\n    ]);\n    for(const res of[rN,rB]){\n      if(res.status===\'fulfilled\'&&Array.isArray(res.value)){\n        for(const i of res.value){\n          const s=(i.symbol||i.ticker||\'\').toUpperCase(), p=i.last_price||i.close||i.bid;\n          if(s&&p){if(s in TP)TP[s]=p;if(s in CP)CP[s]=p;}\n        }\n      }\n    }\n    if(rM.status===\'fulfilled\'&&rM.value?.venta){\n      const m=rM.value,mid=m.compra?(m.compra+m.venta)/2:m.venta;\n      document.getElementById(\'v-mep\').textContent=\'$\'+Math.round(mid).toLocaleString(\'es-AR\');\n      document.getElementById(\'v-mep\').title=\'Compra $\'+m.compra+\' | Venta $\'+m.venta;\n    }\n    if(rC.status===\'fulfilled\'&&rC.value?.venta){\n      const c=rC.value,mid=c.compra?(c.compra+c.venta)/2:c.venta;\n      document.getElementById(\'v-ccl\').textContent=\'$\'+Math.round(mid).toLocaleString(\'es-AR\');\n    }\n    const live=rM.status===\'fulfilled\'&&rM.value?.venta;\n    document.getElementById(\'v-badge\').className=\'badge \'+(live?\'b-live\':\'b-demo\');\n    document.getElementById(\'v-st\').textContent=live?\'EN VIVO\':\'DEMO\';\n  }catch(e){\n    document.getElementById(\'v-badge\').className=\'badge b-demo\';\n    document.getElementById(\'v-st\').textContent=\'DEMO\';\n  }\n  document.getElementById(\'v-ts\').textContent=new Date().toLocaleTimeString(\'es-AR\');\n  renderTF(); renderCER();\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   INTERVAL\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nlet _tmr=null;\nfunction startTimer(s){if(_tmr)clearInterval(_tmr);if(s>0)_tmr=setInterval(doRefresh,s*1000);}\nfunction changeInterval(){startTimer(parseInt(document.getElementById(\'isel\').value));}\n\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   PRIMARY / MATRIZ API\n   Servidor local: http://localhost:8765\n   Correr: py proxy_fixed.py\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\nconst PROXY = \'\';\nlet WS_ACTIVE = false;\nlet PRIMARY_FAILS = 0;\n\nfunction sleep(ms){ return new Promise(r => setTimeout(r, ms)); }\n\nasync function getProxyStatus(){\n  const r = await fetch(PROXY+\'/status\', {signal:AbortSignal.timeout(5000)});\n  if(!r.ok) throw new Error(\'No se pudo consultar el estado del proxy\');\n  return await r.json();\n}\n\n// \xe2\x94\x80\xe2\x94\x80 LOGIN \xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\nasync function waitForPrimaryConnection(timeoutMs=90000){\n  const err = document.getElementById(\'login-err\');\n  const started = Date.now();\n\n  while(Date.now() - started < timeoutMs){\n    const st = await getProxyStatus();\n\n    if(st.connected){\n      return st;\n    }\n\n    if(st.last_error && !st.login_in_progress){\n      throw new Error(st.last_error);\n    }\n\n    err.textContent = st.msg || \'Conectando...\';\n    err.style.display = \'\';\n\n    await sleep(1000);\n  }\n\n  throw new Error(\'Timeout esperando conexi\xc3\xb3n con Matriz.\');\n}\n\nasync function doLogin(){\n  const user = document.getElementById(\'login-user\').value.trim();\n  const pass = document.getElementById(\'login-pass\').value;\n  const err  = document.getElementById(\'login-err\');\n  const btn  = document.querySelector(\'#login-modal button\');\n\n  if(!user||!pass){\n    err.textContent=\'Complet\xc3\xa1 usuario y contrase\xc3\xb1a.\';\n    err.style.display=\'\';\n    return;\n  }\n\n  err.style.display=\'none\';\n  btn.textContent=\'Conectando...\';\n  btn.disabled=true;\n\n  try{\n    const r = await fetch(PROXY+\'/login\', {\n      method:\'POST\',\n      headers:{\'Content-Type\':\'application/json\'},\n      body: JSON.stringify({user, password:pass}),\n      signal: AbortSignal.timeout(10000),\n    });\n\n    const data = await r.json();\n    if(!data.ok) throw new Error(data.msg || \'No se pudo iniciar el login\');\n\n    err.textContent=\'Conectando con Matriz...\';\n    err.style.display=\'\';\n\n    await waitForPrimaryConnection(90000);\n\n    WS_ACTIVE = true;\n    PRIMARY_FAILS = 0;\n    document.getElementById(\'login-modal\').style.display=\'none\';\n    document.getElementById(\'v-badge\').className=\'badge b-live\';\n    document.getElementById(\'v-st\').textContent=\'Primary RT\';\n\n    startTimer(parseInt(document.getElementById(\'isel\').value)||10);\n    await fetchPrimaryPrices();\n  }catch(e){\n    const msg = (e.message.includes(\'fetch\') || e.message.includes(\'Failed\') || e.message.includes(\'NetworkError\'))\n      ? \'\xc2\xbfEst\xc3\xa1 corriendo proxy_fixed.py? Abr\xc3\xad una terminal y ejecut\xc3\xa1: py proxy_fixed.py\'\n      : e.message;\n\n    err.textContent = msg;\n    err.style.display = \'\';\n    WS_ACTIVE = false;\n  }\n\n  btn.textContent=\'Conectar\';\n  btn.disabled=false;\n}\n\nfunction skipLogin(){\n  document.getElementById(\'login-modal\').style.display=\'none\';\n  renderTF();\n  renderCER();\n  doRefresh();\n  startTimer(180);\n}\n\n// \xe2\x94\x80\xe2\x94\x80 FETCH PRICES FROM LOCAL SERVER \xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\nasync function fetchPrimaryPrices(){\n  if(!WS_ACTIVE) return false;\n\n  try{\n    const r = await fetch(PROXY+\'/prices\', {signal:AbortSignal.timeout(8000)});\n    if(!r.ok) throw new Error(\'El proxy respondi\xc3\xb3 con error\');\n\n    const data = await r.json();\n    const px = data.prices || {};\n    let updated = 0;\n\n    for(const [sym, md] of Object.entries(px)){\n      const price = md.last || md.ask || md.bid || md.close;\n      if(price != null){\n        if(sym in TP) TP[sym] = price;\n        if(sym in CP) CP[sym] = price;\n        updated++;\n      }\n    }\n\n    PRIMARY_FAILS = 0;\n\n    if(updated > 0){\n      renderTF();\n      renderCER();\n    }\n\n    document.getElementById(\'v-ts\').textContent = new Date().toLocaleTimeString(\'es-AR\');\n    document.getElementById(\'v-st\').textContent = data.status?.connected ? \'Primary RT\' : (data.status?.msg || \'Primary\');\n    document.getElementById(\'v-badge\').className = data.status?.connected ? \'badge b-live\' : \'badge b-demo\';\n\n    return true;\n  }catch(e){\n    PRIMARY_FAILS++;\n\n    if(PRIMARY_FAILS >= 3){\n      WS_ACTIVE = false;\n      document.getElementById(\'v-badge\').className = \'badge b-demo\';\n      document.getElementById(\'v-st\').textContent = \'Sin conexi\xc3\xb3n\';\n      document.getElementById(\'login-modal\').style.display = \'flex\';\n      document.getElementById(\'login-err\').textContent = \'Se perdi\xc3\xb3 la conexi\xc3\xb3n con proxy_fixed.py\';\n      document.getElementById(\'login-err\').style.display = \'\';\n    }\n\n    return false;\n  }\n}\n\n// \xe2\x94\x80\xe2\x94\x80 OVERRIDE doRefresh \xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\nconst _origRefresh = doRefresh;\nasync function doRefresh(){\n  if(WS_ACTIVE){\n    await fetchPrimaryPrices();\n    try{\n      const[rM,rC]=await Promise.allSettled([\n        fetch(\'https://dolarapi.com/v1/dolares/bolsa\',{signal:AbortSignal.timeout(5000)}).then(r=>r.json()),\n        fetch(\'https://dolarapi.com/v1/dolares/contadoconliqui\',{signal:AbortSignal.timeout(5000)}).then(r=>r.json()),\n      ]);\n      if(rM.status===\'fulfilled\'&&rM.value?.venta){\n        const m=rM.value,mid=m.compra?(m.compra+m.venta)/2:m.venta;\n        document.getElementById(\'v-mep\').textContent=\'$\'+Math.round(mid).toLocaleString(\'es-AR\');\n      }\n      if(rC.status===\'fulfilled\'&&rC.value?.venta){\n        const c=rC.value,mid=c.compra?(c.compra+c.venta)/2:c.venta;\n        document.getElementById(\'v-ccl\').textContent=\'$\'+Math.round(mid).toLocaleString(\'es-AR\');\n      }\n    }catch(e){}\n  } else {\n    await _origRefresh();\n  }\n}\n\n/* \xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\n   INIT\n\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90 */\n(async function(){\n  mergeHol();\n  const n=new Date();\n  setLIQ(nextBD(D(n.getFullYear(),n.getMonth(),n.getDate())));\n  renderTF();\n  renderCER();\n\n  try{\n    const st = await getProxyStatus();\n    if(st.connected){\n      WS_ACTIVE = true;\n      PRIMARY_FAILS = 0;\n      document.getElementById(\'login-modal\').style.display = \'none\';\n      document.getElementById(\'v-badge\').className = \'badge b-live\';\n      document.getElementById(\'v-st\').textContent = \'Primary RT\';\n      startTimer(parseInt(document.getElementById(\'isel\').value)||10);\n      await fetchPrimaryPrices();\n      return;\n    }\n  }catch(e){}\n\n  // Login modal queda visible por defecto\n})();\n</script>\n\n<!-- LOGIN MODAL -->\n<div class="mbg" id="login-modal" style="display:flex;">\n  <div class="mbox" style="width:360px;max-width:96vw;">\n    <div class="mhead">\n      <span style="font-size:13px;font-weight:600;">Acceso Matriz Adcap</span>\n    </div>\n    <div class="mpane" style="gap:12px;">\n      <div class="hint">Ingres\xc3\xa1 tus credenciales de <b style="color:var(--tw)">matriz.adcap.xoms.com.ar</b><br>Las credenciales no se guardan.</div>\n      <div style="display:flex;flex-direction:column;gap:8px;">\n        <div style="display:flex;flex-direction:column;gap:4px;">\n          <label style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.5px;">Usuario</label>\n          <input id="login-user" type="text" autocomplete="username"\n            style="background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:4px;outline:none;"\n            onkeydown="if(event.key===\'Enter\')document.getElementById(\'login-pass\').focus()">\n        </div>\n        <div style="display:flex;flex-direction:column;gap:4px;">\n          <label style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.5px;">Contrase\xc3\xb1a</label>\n          <input id="login-pass" type="password" autocomplete="current-password"\n            style="background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:4px;outline:none;"\n            onkeydown="if(event.key===\'Enter\')doLogin()">\n        </div>\n      </div>\n      <div id="login-err" style="font-size:10px;color:var(--red);display:none;"></div>\n      <button onclick="doLogin()" style="background:var(--blue);border:none;color:#fff;font-family:var(--sans);font-size:12px;font-weight:600;padding:8px;border-radius:4px;cursor:pointer;width:100%;">Conectar</button>\n      <div style="font-size:10px;color:var(--t3);text-align:center;">\n        Necesit\xc3\xa1s correr <code style="background:var(--bg4);padding:1px 5px;border-radius:3px;color:var(--t2);">proxy.py</code> en tu PC\n        &nbsp;\xc2\xb7&nbsp; <button onclick="skipLogin()" style="background:none;border:none;color:var(--t3);font-size:10px;cursor:pointer;text-decoration:underline;">Continuar sin login (demo)</button>\n      </div>\n    </div>\n  </div>\n</div>\n\n</body>\n</html>\n'



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
    # Sin --headless: usamos Xvfb como display virtual en Railway
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1280,800")
    # Reducir consumo de memoria para Railway (evita tab crashed)
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--disable-background-timer-throttling")
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-ipc-flooding-protection")
    opts.add_argument("--disable-hang-monitor")
    opts.add_argument("--disable-prompt-on-repost")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-translate")
    opts.add_argument("--metrics-recording-only")
    opts.add_argument("--no-first-run")
    opts.add_argument("--safebrowsing-disable-auto-update")
    opts.add_argument("--js-flags=--max-old-space-size=256")
    # --single-process removido: causa invalid session id en Railway
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # En Railway el chromedriver está en /usr/local/bin/chromedriver (instalado por Dockerfile).
    # En Windows local no existe ese path, así que lo usamos solo si existe.
    chromedriver_path = "/usr/local/bin/chromedriver"
    chrome_bin = "/opt/chrome-linux64/chrome"
    if os.path.exists(chromedriver_path):
        if os.path.exists(chrome_bin):
            opts.binary_location = chrome_bin
        svc = Service(chromedriver_path)
        drv = webdriver.Chrome(service=svc, options=opts)
    else:
        # Local Windows: Selenium manager resuelve automáticamente
        drv = webdriver.Chrome(options=opts)

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


def find_ws_url(driver, timeout=30):
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
        last_log = 0
        while time.time() < deadline:
            cur = driver.current_url
            if "/login" not in cur:
                redirected = True
                break
            if time.time() - last_log > 5:
                print(f"  [login] URL actual: {cur}")
                last_log = time.time()
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
        time.sleep(8)

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

    def do_OPTIONS(self):
        self.send_response(200)
        self.cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(DASHBOARD)))
            self.end_headers()
            self.wfile.write(DASHBOARD)
        elif self.path == "/prices":
            with lock:
                self._json(200, {"prices": dict(prices), "status": dict(status)})
        elif self.path == "/status":
            with lock:
                self._json(200, dict(status))

        elif self.path == "/debug":
            with driver_lock:
                drv = browser_driver
            if drv is None:
                self._json(200, {"error": "no driver", "status": dict(status)})
                return
            try:
                import base64, tempfile
                url = drv.current_url
                tmp = tempfile.mktemp(suffix=".png")
                drv.save_screenshot(tmp)
                with open(tmp, "rb") as imgf:
                    img_b64 = base64.b64encode(imgf.read()).decode()
                import os as _os; _os.unlink(tmp)
                self._json(200, {"url": url, "screenshot_b64": img_b64, "html": drv.page_source[:2000]})
            except Exception as e:
                self._json(200, {"error": str(e)})

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
