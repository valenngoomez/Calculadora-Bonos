import os
PORT = int(os.environ.get("PORT", 8765))

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bonos AR</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#06090f;--bg2:#0b1120;--bg3:#0f1929;--bg4:#152034;--bg5:#1b2a42;
  --b1:rgba(255,255,255,.04);--b2:rgba(255,255,255,.09);--b3:rgba(255,255,255,.15);
  --tw:#fff;--t2:#8899bb;--t3:#3d5070;
  --blue:#5b9af8;--blueD:rgba(91,154,248,.13);
  --purple:#a97cf5;--purpD:rgba(169,124,245,.13);
  --green:#27d98a;--greenD:rgba(39,217,138,.10);
  --red:#f2564a;--amber:#f5aa24;--amberD:rgba(245,170,36,.10);--teal:#22cfc8;
  --mono:'IBM Plex Mono',monospace;--sans:'IBM Plex Sans',system-ui,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{background:var(--bg);color:var(--tw);font-family:var(--sans);font-size:13px;}

header{height:46px;background:var(--bg2);border-bottom:1px solid var(--b3);display:flex;align-items:center;padding:0 12px;gap:0;position:sticky;top:0;z-index:100;}
.logo{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:600;padding-right:12px;border-right:1px solid var(--b2);margin-right:10px;flex-shrink:0;}
.lring{width:19px;height:19px;border-radius:50%;border:2px solid var(--blue);display:flex;align-items:center;justify-content:center;animation:rp 2.8s ease-in-out infinite;}
@keyframes rp{0%,100%{box-shadow:0 0 0 0 rgba(91,154,248,.5)}50%{box-shadow:0 0 0 5px rgba(91,154,248,0)}}
.ldot{width:5px;height:5px;border-radius:50%;background:var(--blue);}
.macro{display:flex;align-items:center;}
.mi{display:flex;align-items:baseline;gap:4px;padding:0 9px;border-right:1px solid var(--b1);white-space:nowrap;}
.ml{font-size:9px;text-transform:uppercase;letter-spacing:.6px;color:var(--t3);font-weight:500;}
.mv{font-family:var(--mono);font-size:11.5px;font-weight:500;}
.liq-wrap{display:flex;align-items:center;gap:5px;padding:0 9px;border-right:1px solid var(--b1);flex-shrink:0;}
.liq-lbl{font-size:9px;text-transform:uppercase;letter-spacing:.6px;color:var(--t3);font-weight:500;}
.liq-i{width:88px;background:var(--bg4);border:1px solid var(--b2);color:var(--amber);font-family:var(--mono);font-size:11px;padding:2px 5px;border-radius:4px;outline:none;}
.liq-i:focus{border-color:var(--amber);}
.hdr-r{margin-left:auto;display:flex;align-items:center;gap:6px;flex-shrink:0;}
.badge{display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:600;letter-spacing:.5px;}
.b-live{background:var(--greenD);border:1px solid rgba(39,217,138,.25);color:var(--green);}
.b-demo{background:var(--amberD);border:1px solid rgba(245,170,36,.3);color:var(--amber);}
.bdot{width:5px;height:5px;border-radius:50%;background:currentColor;}
.ts{font-size:10px;color:var(--t3);font-family:var(--mono);}
select.isel{background:var(--bg4);border:1px solid var(--b2);color:var(--t2);font-family:var(--sans);font-size:10px;padding:3px 6px;border-radius:4px;outline:none;cursor:pointer;}
.btn{background:var(--bg4);border:1px solid var(--b2);color:var(--t2);padding:4px 9px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;white-space:nowrap;}
.btn:hover{color:var(--tw);border-color:var(--blue);}
.btn-d{border-color:rgba(169,124,245,.3);color:var(--purple);}
.btn-d:hover{border-color:var(--purple);}

.panel{border-bottom:1px solid var(--b2);}
.phead{height:36px;background:var(--bg2);border-bottom:1px solid var(--b2);display:flex;align-items:center;padding:0 10px;gap:9px;position:sticky;top:46px;z-index:50;}
.ptag{font-size:9px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;padding:2px 7px;border-radius:2px;}
.ptag-tf{background:var(--blueD);color:var(--blue);border:1px solid rgba(91,154,248,.25);}
.ptag-cer{background:var(--purpD);color:var(--purple);border:1px solid rgba(169,124,245,.25);}
.ptitle{font-size:11px;font-weight:500;color:var(--t2);}
.pact{margin-left:auto;display:flex;gap:5px;}
.tbtn{background:none;border:1px solid var(--b1);color:var(--t3);padding:2px 8px;border-radius:2px;font-family:var(--sans);font-size:10px;cursor:pointer;}
.tbtn:hover{border-color:var(--b2);color:var(--t2);}
.tbtn.on{background:var(--bg5);color:var(--tw);border-color:var(--b2);}
.cer-info{padding:3px 10px;font-size:10px;color:var(--t3);border-bottom:1px solid var(--b1);}

.tw{overflow-x:auto;}
table{border-collapse:collapse;white-space:nowrap;} .tw{overflow-x:auto;width:100%;}
thead th{background:var(--bg3);color:var(--t3);font-size:9px;font-weight:500;letter-spacing:.4px;text-transform:uppercase;padding:4px 5px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--b2);cursor:pointer;user-select:none;}
thead th:first-child{text-align:left;padding-left:8px;}
thead th:hover{color:var(--t2);}
.ton{color:var(--blue)!important;}
.hb{color:rgba(91,154,248,.6)!important;}
.hp{color:rgba(169,124,245,.6)!important;}
.ha{color:rgba(245,170,36,.6)!important;}
.hs{border-left:1px solid rgba(245,170,36,.2)!important;color:rgba(245,170,36,.6)!important;}
.hm{color:rgba(245,170,36,.5)!important;font-style:italic;}
tbody tr{border-bottom:1px solid var(--b1);}
tbody tr:hover{background:var(--bg3);}
td{padding:4px 5px;text-align:right;font-family:var(--mono);font-size:10.5px;white-space:nowrap;color:var(--tw);}
td:first-child{text-align:left;padding-left:8px;font-family:var(--sans);}
td.sa{border-left:1px solid rgba(245,170,36,.15);}
.tn{font-size:11px;font-weight:600;}
.td{font-size:8.5px;color:var(--t3);margin-top:1px;}
.cg{color:var(--green);}.cr{color:var(--red);}.cb{color:var(--blue);}.ca{color:var(--amber);}.ct{color:var(--teal);}.cp{color:var(--purple);}

/* manual price input */
.man-inp{width:58px;font-family:var(--mono);font-size:10.5px;padding:1px 4px;border-radius:3px;text-align:right;outline:none;background:transparent;border:1px solid transparent;color:var(--t3);transition:all .15s;}
.man-inp:focus{border-color:var(--amber);color:var(--amber);background:var(--bg4);}
.man-inp.filled{background:rgba(245,170,36,.08);border-color:rgba(245,170,36,.4);color:var(--amber);} .man-inp::placeholder{color:var(--t3);font-size:9.5px;}

/* MODAL */
.mbg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.78);z-index:999;align-items:center;justify-content:center;}
.mbox{background:var(--bg2);border:1px solid var(--b3);border-radius:8px;width:580px;max-width:96vw;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;}
.mhead{display:flex;align-items:center;padding:12px 16px;border-bottom:1px solid var(--b2);gap:8px;flex-shrink:0;}
.mtabs{display:flex;border-bottom:1px solid var(--b2);padding:0 16px;flex-shrink:0;}
.mtab{background:none;border:none;border-bottom:2px solid transparent;color:var(--t2);padding:8px 14px 7px;font-family:var(--sans);font-size:11px;cursor:pointer;font-weight:500;margin-bottom:-1px;}
.mtab.on{color:var(--tw);border-bottom-color:var(--purple);}
.mpane{flex:1;overflow-y:auto;padding:12px 16px;display:flex;flex-direction:column;gap:10px;}
.mshare{padding:8px 16px;border-top:1px solid var(--b2);display:flex;gap:6px;align-items:center;flex-shrink:0;background:rgba(169,124,245,.04);}
.mfoot{padding:7px 16px;border-top:1px solid var(--b1);font-size:10px;color:var(--t3);display:flex;align-items:center;gap:10px;flex-shrink:0;}
.mfoot b{color:var(--purple);font-family:var(--mono);font-weight:400;}
textarea.mta{width:100%;height:110px;background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:11px;padding:8px;border-radius:4px;resize:vertical;outline:none;}
textarea.mta:focus{border-color:var(--blue);}
.hint{font-size:10px;color:var(--t3);line-height:1.7;}
.hint code{background:var(--bg4);padding:1px 4px;border-radius:3px;color:var(--t2);font-family:var(--mono);}
.brow{display:flex;gap:6px;flex-wrap:wrap;}
.bg{background:var(--bg4);border:1px solid rgba(39,217,138,.3);color:var(--green);padding:5px 12px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;}
.bg:hover{background:rgba(39,217,138,.08);}
.br{background:var(--bg4);border:1px solid rgba(242,86,74,.3);color:var(--red);padding:5px 12px;border-radius:4px;font-family:var(--sans);font-size:11px;cursor:pointer;}
.br:hover{background:rgba(242,86,74,.08);}
.imsg{font-size:10px;color:var(--green);display:none;padding:2px 0;}
.dtbl{width:100%;border-collapse:collapse;font-size:11px;}
.dtbl th{background:var(--bg3);color:var(--t3);font-size:9px;font-weight:500;text-transform:uppercase;letter-spacing:.4px;padding:4px 10px;text-align:right;border-bottom:1px solid var(--b2);}
.dtbl th:first-child{text-align:left;}
.dtbl td{padding:3px 10px;text-align:right;border-bottom:1px solid var(--b1);color:var(--tw);}
.dtbl td:first-child{text-align:left;}
.dtbl tr.act{background:rgba(169,124,245,.08);}
.dtbl tr.act td{color:var(--purple);}
.dbtn{background:none;border:none;color:var(--t3);cursor:pointer;font-size:11px;padding:0 2px;}
.dbtn:hover{color:var(--red);}
.dempty{text-align:center;padding:20px;color:var(--t3);font-size:11px;}
</style>
</head>
<body>

<header>
  <div class="logo"><div class="lring"><div class="ldot"></div></div>Bonos AR</div>
  <div class="macro">
    <div class="mi"><span class="ml">MEP</span><span class="mv cb" id="v-mep">$1.407</span></div>
    <div class="mi"><span class="ml">CCL</span><span class="mv ct" id="v-ccl">—</span></div>
    <div class="mi">
      <span class="ml">CER</span>
      <span class="mv cp" id="v-cer" style="cursor:pointer;border-bottom:1px dashed rgba(169,124,245,.4)" title="Click para editar" onclick="editCerHdr()">—</span>
      <input id="v-cer-inp" type="number" step="0.0001" style="display:none;width:76px;background:var(--bg4);border:1px solid rgba(169,124,245,.5);color:var(--purple);font-family:var(--mono);font-size:11px;padding:2px 5px;border-radius:4px;outline:none;" onblur="commitCerHdr(this)" onkeydown="if(event.key==='Enter')this.blur();if(event.key==='Escape')cancelCerHdr(this)">
    </div>
  </div>
  <div class="liq-wrap">
    <span class="liq-lbl">Liquidación</span>
    <input class="liq-i" id="liq-i" type="text" placeholder="27/03/2026" maxlength="10" onblur="onLiqBlur(this)" onkeydown="if(event.key==='Enter')this.blur()">
  </div>
  <div class="hdr-r">
    <div class="badge b-demo" id="v-badge"><div class="bdot"></div><span id="v-st">DEMO</span></div>
    <span class="ts" id="v-ts">—</span>
    <select class="isel" id="isel" onchange="changeInterval()">
      <option value="5">5 seg</option>
      <option value="10" selected>10 seg</option>
      <option value="30">30 seg</option>
      <option value="60">1 min</option>
      <option value="180">3 min</option>
      <option value="0">Manual</option>
    </select>
    <button class="btn" onclick="doRefresh()">↻ Actualizar</button>
    <button class="btn btn-d" onclick="openModal()">⚙ Datos</button>
  </div>
</header>

<div class="panel">
  <div class="phead">
    <span class="ptag ptag-tf">TF</span>
    <span class="ptitle">Tasa Fija — BONCAP / LECAP</span>
    <div class="pact">
      <button class="tbtn on" id="tfb0" onclick="setTFV(0)">Base</button>
      <button class="tbtn"   id="tfb1" onclick="setTFV(1)">c/ Comisión</button>
      <button class="tbtn"             onclick="dlTF()">↓ CSV</button>
    </div>
  </div>
  <div id="tf-body"></div>
</div>

<div class="panel">
  <div class="phead">
    <span class="ptag ptag-cer">CER</span>
    <span class="ptitle">Ajustables CER — BONCER / LECER</span>
    <div class="pact">
      <button class="tbtn on" id="cerb0" onclick="setCERV(0)">Base</button>
      <button class="tbtn"   id="cerb1" onclick="setCERV(1)">c/ Comisión</button>
      <button class="tbtn"              onclick="dlCER()">↓ CSV</button>
    </div>
  </div>
  <div class="cer-info" id="cer-info">CER actual: —</div>
  <div id="cer-body"></div>
</div>

<!-- MODAL -->
<div class="mbg" id="modal">
  <div class="mbox">
    <div class="mhead">
      <span style="font-size:12px;font-weight:600;">Datos de referencia</span>
      <span style="font-size:10px;color:var(--t3);margin-left:4px;">localStorage del browser</span>
      <button onclick="closeModal()" style="margin-left:auto;background:none;border:none;color:var(--t2);font-size:16px;cursor:pointer;line-height:1;">✕</button>
    </div>
    <div class="mtabs">
      <button class="mtab on" id="tab-cer" onclick="switchTab('cer')">Serie CER</button>
      <button class="mtab"    id="tab-hol" onclick="switchTab('hol')">Feriados</button>
    </div>
    <div class="mpane" id="pane-cer">
      <div class="hint">Pegá desde Excel (dos columnas: fecha y valor).<br>Formatos: <code>dd/mm/aa</code> <code>dd/mm/aaaa</code> <code>yyyy-mm-dd</code> · Separador: tab, coma o punto y coma.</div>
      <textarea class="mta" id="cer-ta" placeholder="01/01/16&#9;5.0386&#10;12/03/26&#9;721.5850&#10;..."></textarea>
      <div class="brow">
        <button class="bg" onclick="importCER()">↑ Importar</button>
        <button class="btn" onclick="exportCER()">↓ Exportar CSV</button>
        <button class="br" onclick="clearCER()">✕ Limpiar todo</button>
      </div>
      <div class="imsg" id="cer-msg"></div>
      <div id="cer-tbl"></div>
    </div>
    <div class="mpane" id="pane-hol" style="display:none;">
      <div class="hint">Pegá una columna de fechas desde Excel.<br>Formatos: <code>dd/mm/aa</code> <code>dd/mm/aaaa</code> <code>yyyy-mm-dd</code> · Se suman a los del código (2025-2027 incluidos).</div>
      <textarea class="mta" id="hol-ta" placeholder="01/01/26&#10;24/03/26&#10;02/04/26&#10;..."></textarea>
      <div class="brow">
        <button class="bg" onclick="importHol()">↑ Importar</button>
        <button class="btn" onclick="exportHol()">↓ Exportar CSV</button>
        <button class="br" onclick="clearHol()">✕ Limpiar importados</button>
      </div>
      <div class="imsg" id="hol-msg"></div>
      <div id="hol-tbl"></div>
    </div>
    <div class="mshare">
      <span style="font-size:10px;color:var(--t3);flex:1;">Para compartir con otra persona:</span>
      <button class="bg" style="font-size:10px;padding:4px 10px;" onclick="exportAll()">↓ Exportar configuración</button>
      <label class="btn" style="font-size:10px;padding:4px 10px;cursor:pointer;border-color:rgba(39,217,138,.3);color:var(--green);">↑ Importar configuración<input type="file" accept=".json" style="display:none" onchange="importAll(this)"></label>
    </div>
    <div class="mfoot">
      <span id="m-cer-cnt">—</span> · Lag: <b id="m-lag">—</b> · CER en uso: <b id="m-use">—</b> · <span id="m-hol-cnt" style="color:var(--teal)">—</span>
    </div>
  </div>
</div>

<script>
/* ═══════════════════════════════════════════
   HOLIDAYS (base hardcoded + localStorage)
═══════════════════════════════════════════ */
const HOL = new Set([
  '2025-01-01','2025-03-03','2025-03-04','2025-03-24','2025-04-02','2025-04-17',
  '2025-04-18','2025-05-01','2025-05-25','2025-06-20','2025-07-09','2025-08-17',
  '2025-10-12','2025-11-21','2025-12-08','2025-12-25',
  '2026-01-01','2026-02-16','2026-02-17','2026-03-24','2026-04-02','2026-04-03',
  '2026-04-04','2026-05-01','2026-05-25','2026-06-19','2026-06-20','2026-07-09',
  '2026-08-17','2026-10-12','2026-11-20','2026-12-08','2026-12-25',
  '2027-01-01','2027-02-15','2027-02-16','2027-03-24','2027-04-02','2027-06-20',
  '2027-07-09','2027-08-16','2027-10-11','2027-12-08','2027-12-25',
]);

/* ═══════════════════════════════════════════
   DATE UTILS
═══════════════════════════════════════════ */
const D = (y,m,d) => new Date(y, m, d);
const iso = d => d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);
const fmt = d => ('0'+d.getDate()).slice(-2)+'/'+('0'+(d.getMonth()+1)).slice(-2)+'/'+d.getFullYear();
const isBD = d => d.getDay()!==0 && d.getDay()!==6 && !HOL.has(iso(d));

function nextBD(d){
  const r=D(d.getFullYear(),d.getMonth(),d.getDate()+1);
  while(!isBD(r)) r.setDate(r.getDate()+1);
  return r;
}
function wdBack(d,n){
  const r=D(d.getFullYear(),d.getMonth(),d.getDate());
  let c=0; while(c<n){r.setDate(r.getDate()-1);if(isBD(r))c++;} return r;
}
function dDiff(a,b){
  return Math.round((D(b.getFullYear(),b.getMonth(),b.getDate())-D(a.getFullYear(),a.getMonth(),a.getDate()))/86400000);
}
function days360(a,b){
  let y1=a.getFullYear(),m1=a.getMonth()+1,d1=a.getDate();
  let y2=b.getFullYear(),m2=b.getMonth()+1,d2=b.getDate();
  if(d1===31)d1=30; if(d2===31&&d1===30)d2=30;
  return 360*(y2-y1)+30*(m2-m1)+(d2-d1);
}
function parseDate(s){
  s=(s||'').trim();
  if(/^\\d{4}-\\d{2}-\\d{2}$/.test(s)){const[y,m,d]=s.split('-');return D(+y,+m-1,+d);}
  const m2=s.match(/^(\\d{1,2})[\\/\\-](\\d{1,2})[\\/\\-](\\d{2,4})$/);
  if(m2){let[,dd,mm,yy]=m2;if(yy.length===2)yy=+yy<50?'20'+yy:'19'+yy;return D(+yy,+mm-1,+dd);}
  return null;
}
function parseIso(s){const d=parseDate(s);return(d&&!isNaN(d))?iso(d):null;}

/* ═══════════════════════════════════════════
   LOCALSTORAGE
═══════════════════════════════════════════ */
const K_CER='bar2_cer', K_HOL='bar2_hol';
const lsCer = ()=>{try{return JSON.parse(localStorage.getItem(K_CER)||'{}')}catch(e){return{}}};
const lsHol = ()=>{try{return new Set(JSON.parse(localStorage.getItem(K_HOL)||'[]'))}catch(e){return new Set()}};
const savCer = m=>{try{localStorage.setItem(K_CER,JSON.stringify(m))}catch(e){}};
const savHol = s=>{try{localStorage.setItem(K_HOL,JSON.stringify([...s].sort()))}catch(e){}};

function cerForDate(isoDate){
  const map=lsCer(),keys=Object.keys(map).sort();
  let val=null,key=null;
  for(const k of keys){if(k<=isoDate&&(!key||k>key)){key=k;val=map[k];}}
  return{val,key};
}
function mergeHol(){for(const d of lsHol())HOL.add(d);}

/* ═══════════════════════════════════════════
   STATE
═══════════════════════════════════════════ */
let LIQ;
let CER_VAL = 716.446;
let TFV=0, CERV=0;
let TF_SK='d', TF_SA=true, CER_SK='dc', CER_SA=true;
const TF_MAN={}, CER_MAN={};  // manual prices

// API/demo prices (updated by doRefresh)
const TP={TZXM6:212.68,S17A6:108.00,S30A6:123.73,S15Y6:100.69,S29Y6:125.35,T30J6:134.00,
  S31L6:106.62,S31G6:112.53,S30S6:100.70,S30O6:113.30,S30N6:105.99,T15E7:127.15,
  T30A7:114.00,T31Y7:107.40,T30J7:108.95};
const CP={X15Y6:102.93,X29Y6:110.90,TZX26:360.60,X31L6:105.58,X30S6:99.20,TZXO6:147.30,
  X30N6:106.59,TZXD6:258.55,TZXM7:189.70,TZXA7:104.75,TZXY7:102.50,TZX27:339.45,
  TZXD7:237.65,TZX28:301.70};

/* ═══════════════════════════════════════════
   BOND DATA
═══════════════════════════════════════════ */
const TF_BONDS=[
  {t:'TZXM6',vto:D(2026,2,31),em:'30/04/2024',pago:214.536,com:.02},
  {t:'S17A6', vto:D(2026,3,17),em:'15/12/2025',pago:110.124,com:.02},
  {t:'S30A6', vto:D(2026,3,30),em:'30/09/2025',pago:127.486,com:.02},
  {t:'S15Y6', vto:D(2026,4,15),em:'16/03/2026',pago:105.178,com:.02},
  {t:'S29Y6', vto:D(2026,4,29),em:'30/05/2025',pago:132.044,com:.02},
  {t:'T30J6', vto:D(2026,5,30),em:'17/01/2025',pago:144.896,com:.02},
  {t:'S31L6', vto:D(2026,6,31),em:'30/01/2026',pago:117.678,com:.02},
  {t:'S31G6', vto:D(2026,7,31),em:'31/08/2026',pago:127.065,com:.02},
  {t:'S30S6', vto:D(2026,8,30),em:'16/03/2026',pago:117.536,com:.02},
  {t:'S30O6', vto:D(2026,9,30),em:'31/10/2025',pago:135.280,com:.02},
  {t:'S30N6', vto:D(2026,10,30),em:'15/12/2025',pago:129.885,com:.02},
  {t:'T15E7', vto:D(2027,0,15), em:'31/01/2025',pago:161.104,com:.02},
  {t:'T30A7', vto:D(2027,3,30), em:'31/10/2025',pago:157.344,com:.02},
  {t:'T31Y7', vto:D(2027,4,31), em:'15/12/2025',pago:151.558,com:.02},
  {t:'T30J7', vto:D(2027,5,30), em:'16/01/2026',pago:156.031,com:.02},
];
const CER_BONDS=[
  {t:'X15Y6', vto:D(2026,4,15), em:'27/02/2026',cerI:701.614,com:.005},
  {t:'X29Y6', vto:D(2026,4,29), em:'28/11/2025',cerI:651.898,com:.005},
  {t:'TZX26', vto:D(2026,5,30), em:'01/02/2024',cerI:200.388,com:.005},
  {t:'X31L6', vto:D(2026,6,31), em:'30/01/2026',cerI:685.551,com:.005},
  {t:'X30S6', vto:D(2026,8,30), em:'16/03/2026',cerI:714.985,com:.005},
  {t:'TZXO6', vto:D(2026,9,30), em:'31/10/2024',cerI:480.153,com:.005},
  {t:'X30N6', vto:D(2026,10,30),em:'15/12/2025',cerI:659.679,com:.005},
  {t:'TZXD6', vto:D(2026,11,15),em:'15/03/2024',cerI:271.048,com:.005},
  {t:'TZXM7', vto:D(2027,2,31), em:'20/05/2024',cerI:361.318,com:.005},
  {t:'TZXA7', vto:D(2027,3,30), em:'28/11/2025',cerI:651.898,com:.005},
  {t:'TZXY7', vto:D(2027,4,31), em:'15/12/2025',cerI:659.679,com:.005},
  {t:'TZX27', vto:D(2027,5,30), em:'01/02/2024',cerI:200.388,com:.005},
  {t:'TZXD7', vto:D(2027,11,15),em:'15/03/2024',cerI:271.048,com:.005},
  {t:'TZX28', vto:D(2028,5,30), em:'01/02/2024',cerI:200.388,com:.005},
];

/* ═══════════════════════════════════════════
   COMPUTE
═══════════════════════════════════════════ */
function getMEP(){return parseFloat((document.getElementById('v-mep').textContent||'').replace(/\\./g,'').replace(',','.').replace(/[^\\d.]/g,''))||1407;}

function compTF(){
  const mep=getMEP();
  return TF_BONDS.map(b=>{
    const apiP = TP[b.t]||100;
    const p    = TF_MAN[b.t]!=null ? TF_MAN[b.t] : apiP;
    const d = dDiff(LIQ, b.vto); if(d<=0) return null;
    const dur=d/365, r=b.pago/p, ret=r-1;
    const tna=ret*365/d, tea=Math.pow(r,365/d)-1, tem=Math.pow(tea+1,30/365)-1;
    const mepBE=mep*(1+ret), tnaCC=tna-b.com;
    const precCC=Math.round(b.pago/(1+tnaCC*d/365)*1000)/1000;
    const comDir=precCC/p-1, teaCC=Math.pow(b.pago/precCC,365/d)-1, temCC=Math.pow(teaCC+1,30/365)-1;
    return{t:b.t,em:b.em,vto:b.vto,pago:b.pago,com:b.com,apiP,p,d,dur,ret,tna,tea,tem,mepBE,tnaCC,precCC,comDir,teaCC,temCC};
  }).filter(Boolean);
}

function compCER(){
  return CER_BONDS.map(b=>{
    const apiP = CP[b.t]||100;
    const p    = CER_MAN[b.t]!=null ? CER_MAN[b.t] : apiP;
    const dc=dDiff(LIQ,b.vto); if(dc<=0) return null;
    const d3=days360(LIQ,b.vto), dur=dc/365;
    const ratio=100*CER_VAL/b.cerI/p;
    const tna=(Math.pow(ratio,180/d3)-1)*2, tir=Math.pow(ratio,365/dc)-1;
    const tnaCC=tna-b.com;
    const precCC=Math.round(100*CER_VAL/(b.cerI*Math.pow(1+tnaCC/2,d3/180))*1000)/1000;
    const comDir=precCC/p-1, teaCC=Math.pow(100*CER_VAL/b.cerI/precCC,365/dc)-1;
    return{t:b.t,em:b.em,vto:b.vto,cerI:b.cerI,com:b.com,apiP,p,dc,d3,dur,tna,tir,tnaCC,precCC,comDir,teaCC};
  }).filter(Boolean);
}

/* ═══════════════════════════════════════════
   FORMAT
═══════════════════════════════════════════ */
const N=(v,d=3)=>v==null||isNaN(v)?'—':v.toFixed(d);
const P=(v,d=2)=>v==null||isNaN(v)?'—':(v*100).toFixed(d)+'%';
const ARS=v=>'<span class="ca">$'+Math.round(v).toLocaleString('es-AR')+'</span>'; const ARSN=v=>v==null||isNaN(v)?'—':'<span class="ca">$'+Math.round(v).toLocaleString('es-AR')+'</span>';
function PC(v,d=2,t=0){if(v==null||isNaN(v))return'<span style="color:var(--t3)">—</span>';return'<span class="'+(v>t?'cg':v<t?'cr':'')+'"> '+(v*100).toFixed(d)+'%</span>';}
function TnaC(v){const pv=v*100;return'<span class="'+(pv>=32?'cg':pv>=28?'ca':'cr')+'">'+pv.toFixed(2)+'%</span>';}
function TeaC(v){const pv=v*100;return'<span class="'+(pv>=35?'cg':pv>=30?'ca':'cr')+'">'+pv.toFixed(2)+'%</span>';}
function CerC(v){const pv=v*100;return'<span class="'+(pv>3?'cg':pv>0?'ca':pv>-3?'cb':'cr')+'">'+pv.toFixed(2)+'%</span>';}

/* ═══════════════════════════════════════════
   MANUAL PRICE INPUT CELL
   Two separate <td>s: API price | Manual input
═══════════════════════════════════════════ */
function apiCell(apiP){
  return '<span style="font-family:var(--mono);font-size:11px;color:var(--t2)">'+N(apiP,3)+'</span>';
}
function manCell(ns, t, manP){
  const filled = manP != null;
  return '<input class="man-inp'+(filled?' filled':'')+'" id="'+ns+'m'+t+'"'+
    ' type="number" step="0.001"'+
    ' placeholder="manual"'+
    ' value="'+(filled?N(manP,3):'')+'"'+
    ' onchange="commitMan(\\''+ns+'\\',\\''+t+'\\',this)"'+
    ' title="Vacío = usa precio API · Con valor = calcula con ese precio">';
}

function commitMan(ns,t,inp){
  const v=parseFloat(inp.value);
  if(isNaN(v)||v<=0||inp.value.trim()===''){
    if(ns==='tf') delete TF_MAN[t]; else delete CER_MAN[t];
    inp.value=''; inp.classList.remove('filled');
  } else {
    if(ns==='tf') TF_MAN[t]=v; else CER_MAN[t]=v;
    inp.classList.add('filled');
  }
  ns==='tf' ? renderTF() : renderCER();
}

/* ═══════════════════════════════════════════
   TABLE BUILDER
═══════════════════════════════════════════ */
function mkTable(rows, cols, sk, sa, sfn){
  const sorted=[...rows].sort((a,b)=>{
    const av=a[sk],bv=b[sk];
    if(typeof av==='string')return sa?av.localeCompare(bv):bv.localeCompare(av);
    return sa?(av-bv):(bv-av);
  });
  const ths=cols.map(c=>{
    const on=sk===c.k?' ton':'', arr=sk===c.k?(sa?' ▲':' ▼'):'';
    return '<th class="'+(c.h||'')+on+'" onclick="'+sfn+'(\\''+c.k+'\\')">'+c.l+arr+'</th>';
  }).join('');
  const trs=sorted.map(r=>
    '<tr>'+cols.map(c=>'<td class="'+(c.tc||'')+'">'+c.f(r)+'</td>').join('')+'</tr>'
  ).join('');
  return '<div class="tw"><table><thead><tr>'+ths+'</tr></thead><tbody>'+trs+'</tbody></table></div>';
}

/* ═══════════════════════════════════════════
   TF VIEWS
═══════════════════════════════════════════ */
function tfBase(rows){ return mkTable(rows,[
  {k:'t',    l:'Bono',      h:'',   f:r=>'<div class="tn">'+r.t+'</div><div class="td">'+r.em+'</div>'},
  {k:'apiP', l:'P. API',   h:'hb', f:r=>apiCell(r.apiP)},
  {k:'p',    l:'P. Manual',h:'hm', f:r=>manCell('tf',r.t,TF_MAN[r.t]??null)},
  {k:'d',    l:'Días',      h:'',   f:r=>r.d},
  {k:'vto',  l:'Vto.',      h:'',   f:r=>fmt(r.vto)},
  {k:'pago', l:'Pago',      h:'',   f:r=>N(r.pago,3)},
  {k:'ret',  l:'Ret.',      h:'',   f:r=>PC(r.ret)},
  {k:'tna',  l:'TNA',       h:'hb', f:r=>TnaC(r.tna)},
  {k:'tea',  l:'TEA',       h:'hb', f:r=>TeaC(r.tea)},
  {k:'tem',  l:'TEM',       h:'',   f:r=>P(r.tem,3)},
  {k:'mepBE',l:'MEP BE',    h:'ha mepbe', tc:'mepbe', f:r=>'<span class="ca">'+Math.round(r.mepBE).toLocaleString('es-AR')+'</span>'},
],TF_SK,TF_SA,'stf');}

function tfCC(rows){ return mkTable(rows,[
  {k:'t',    l:'Bono',       h:'',   f:r=>'<div class="tn">'+r.t+'</div><div class="td">'+r.em+'</div>'},
  {k:'apiP', l:'P. API',    h:'hb', f:r=>apiCell(r.apiP)},
  {k:'p',    l:'P. Manual', h:'hm', f:r=>manCell('tf',r.t,TF_MAN[r.t]??null)},
  {k:'d',    l:'Días',       h:'',   f:r=>r.d},
  {k:'com',  l:'Com.',       h:'hs', tc:'sa',f:r=>'<span class="ca">'+P(r.com)+'</span>'},
  {k:'tnaCC',l:'TNA c/Com.', h:'ha', f:r=>'<span class="ca">'+P(r.tnaCC)+'</span>'},
  {k:'precCC',l:'P. c/Com.', h:'',   f:r=>N(r.precCC,3)},
  {k:'comDir',l:'Com. Dir.', h:'',   f:r=>PC(r.comDir,4)},
  {k:'teaCC',l:'TEA c/Com.', h:'ha', f:r=>TeaC(r.teaCC)},
  {k:'temCC',l:'TEM c/Com.', h:'',   f:r=>P(r.temCC,3)},
],TF_SK,TF_SA,'stf');}

function stf(k){if(TF_SK===k)TF_SA=!TF_SA;else{TF_SK=k;TF_SA=true;}renderTF();}

/* ═══════════════════════════════════════════
   CER VIEWS
═══════════════════════════════════════════ */
function cerBase(rows){ return mkTable(rows,[
  {k:'t',   l:'Ticker',      h:'',   f:r=>'<div class="tn">'+r.t+'</div><div class="td">'+r.em+'</div>'},
  {k:'apiP',l:'P. API',      h:'hp', f:r=>apiCell(r.apiP)},
  {k:'p',   l:'P. Manual',   h:'hm', f:r=>manCell('cer',r.t,CER_MAN[r.t]??null)},
  {k:'dc',  l:'Días',        h:'',   f:r=>r.dc},
  {k:'vto', l:'Vto.',        h:'',   f:r=>fmt(r.vto)},
  {k:'cerI',l:'CER inic.',   h:'',   f:r=>N(r.cerI,2)},
  {k:'tna', l:'TNA 180/360', h:'hp', f:r=>CerC(r.tna)},
  {k:'tir', l:'TIR',         h:'hp', f:r=>CerC(r.tir)},
],CER_SK,CER_SA,'scer');}

function cerCC(rows){ return mkTable(rows,[
  {k:'t',    l:'Ticker',      h:'',   f:r=>'<div class="tn">'+r.t+'</div><div class="td">'+r.em+'</div>'},
  {k:'apiP', l:'P. API',     h:'hp', f:r=>apiCell(r.apiP)},
  {k:'p',    l:'P. Manual',  h:'hm', f:r=>manCell('cer',r.t,CER_MAN[r.t]??null)},
  {k:'dc',   l:'Días',        h:'',   f:r=>r.dc},
  {k:'com',  l:'Com.',        h:'hs', tc:'sa',f:r=>'<span class="ca">'+P(r.com)+'</span>'},
  {k:'tnaCC',l:'TNA c/Com.',  h:'ha', f:r=>'<span class="ca">'+P(r.tnaCC,2)+'</span>'},
  {k:'precCC',l:'P. c/Com.', h:'',   f:r=>N(r.precCC,3)},
  {k:'comDir',l:'Com. Dir.', h:'',   f:r=>PC(r.comDir,4)},
  {k:'teaCC',l:'TEA c/Com.', h:'ha', f:r=>CerC(r.teaCC)},
],CER_SK,CER_SA,'scer');}

function scer(k){if(CER_SK===k)CER_SA=!CER_SA;else{CER_SK=k;CER_SA=true;}renderCER();}

/* ═══════════════════════════════════════════
   RENDER
═══════════════════════════════════════════ */
function renderTF(){ document.getElementById('tf-body').innerHTML = TFV===0?tfBase(compTF()):tfCC(compTF()); }
function renderCER(){ document.getElementById('cer-body').innerHTML = CERV===0?cerBase(compCER()):cerCC(compCER()); }
function setTFV(v){TFV=v;document.getElementById('tfb0').classList.toggle('on',v===0);document.getElementById('tfb1').classList.toggle('on',v===1);renderTF();}
function setCERV(v){CERV=v;document.getElementById('cerb0').classList.toggle('on',v===0);document.getElementById('cerb1').classList.toggle('on',v===1);renderCER();}

/* ═══════════════════════════════════════════
   LIQUIDATION DATE
═══════════════════════════════════════════ */
function setLIQ(d){
  LIQ=d;
  document.getElementById('liq-i').value=fmt(d);
  updateCERFromLS();
}
function onLiqBlur(inp){
  const d=parseDate(inp.value);
  if(!d||isNaN(d)){inp.style.borderColor='var(--red)';return;}
  inp.style.borderColor='';
  LIQ=d; inp.value=fmt(d);
  updateCERFromLS(); renderTF(); renderCER();
}

/* ═══════════════════════════════════════════
   CER VALUE
═══════════════════════════════════════════ */
function updateCERFromLS(){
  if(!LIQ) return;
  const lag=wdBack(LIQ,10), lagISO=iso(lag);
  const {val,key}=cerForDate(lagISO);
  if(val!=null){
    CER_VAL=val;
    document.getElementById('v-cer').textContent=val.toFixed(4);
    document.getElementById('cer-info').innerHTML=
      'CER actual: <b style="color:var(--purple);font-family:var(--mono)">'+val.toFixed(4)+'</b>'+
      ' &nbsp;·&nbsp; lag: <span style="color:var(--teal);font-family:var(--mono)">'+lagISO+'</span>'+
      ' &nbsp;·&nbsp; dato de: <span style="color:var(--teal);font-family:var(--mono)">'+key+'</span>';
  } else {
    document.getElementById('v-cer').textContent=CER_VAL.toFixed(4);
    document.getElementById('cer-info').innerHTML=
      'CER actual: <b style="color:var(--purple);font-family:var(--mono)">'+CER_VAL.toFixed(4)+'</b>'+
      ' &nbsp;·&nbsp; <span style="color:var(--red)">⚠ sin dato para lag '+lagISO+' — importá la serie en ⚙ Datos</span>';
  }
  renderCER();
}

function editCerHdr(){
  const sp=document.getElementById('v-cer'),inp=document.getElementById('v-cer-inp');
  inp.value=CER_VAL.toFixed(4); sp.style.display='none'; inp.style.display='inline-block'; inp.focus(); inp.select();
}
function cancelCerHdr(inp){document.getElementById('v-cer').style.display='';inp.style.display='none';}
function commitCerHdr(inp){
  const v=parseFloat(inp.value);
  if(!isNaN(v)&&v>0){CER_VAL=v;document.getElementById('v-cer').textContent=v.toFixed(4);
    document.getElementById('cer-info').innerHTML='CER actual: <b style="color:var(--purple);font-family:var(--mono)">'+v.toFixed(4)+'</b> <span style="color:var(--amber)">(manual)</span>';
    renderCER();}
  cancelCerHdr(inp);
}

/* ═══════════════════════════════════════════
   MODAL
═══════════════════════════════════════════ */
function openModal(){document.getElementById('modal').style.display='flex';refreshModal();}
function closeModal(){document.getElementById('modal').style.display='none';}
function switchTab(t){
  document.getElementById('pane-cer').style.display=t==='cer'?'':'none';
  document.getElementById('pane-hol').style.display=t==='hol'?'':'none';
  document.getElementById('tab-cer').classList.toggle('on',t==='cer');
  document.getElementById('tab-hol').classList.toggle('on',t==='hol');
}
function refreshModal(){
  const map=lsCer(), set=lsHolSet=lsHol();
  const lag=LIQ?iso(wdBack(LIQ,10)):null;
  const{val,key}=lag?cerForDate(lag):{val:null,key:null};
  document.getElementById('m-cer-cnt').textContent=Object.keys(map).length+' fechas CER';
  document.getElementById('m-lag').textContent=lag||'—';
  document.getElementById('m-use').textContent=val!=null?(val.toFixed(4)+' ('+key+')'):'sin dato';
  document.getElementById('m-hol-cnt').textContent=set.size+' feriados importados';
  refreshCERTbl(); refreshHolTbl();
}
function showMsg(id,txt){const e=document.getElementById(id);e.textContent=txt;e.style.display='block';setTimeout(()=>e.style.display='none',3000);}

// CER CRUD
function importCER(){
  const raw=document.getElementById('cer-ta').value.trim();
  if(!raw){alert('Pegá datos primero');return;}
  const map=lsCer();let ok=0,sk=0;
  for(const line of raw.split('\\n')){
    const parts=line.trim().split(/[\\t,;]+/);
    if(parts.length<2){sk++;continue;}
    const f=parseIso(parts[0]),v=parseFloat(parts[1].replace(',','.'));
    if(!f||isNaN(v)){sk++;continue;}
    map[f]=v;ok++;
  }
  savCer(map);
  document.getElementById('cer-ta').value='';
  showMsg('cer-msg','✓ '+ok+' fechas importadas'+(sk?' ('+sk+' ignoradas)':''));
  refreshModal(); updateCERFromLS();
}
function exportCER(){
  const map=lsCer(),k=Object.keys(map).sort();
  if(!k.length){alert('Sin datos');return;}
  dl('cer_serie','fecha,valor\\n'+k.map(x=>x+','+map[x].toFixed(4)).join('\\n'));
}
function clearCER(){if(!confirm('¿Borrar toda la serie CER?'))return;localStorage.removeItem(K_CER);refreshModal();}
function delCerRow(k){const m=lsCer();delete m[k];savCer(m);refreshModal();updateCERFromLS();}
function refreshCERTbl(){
  const map=lsCer(),keys=Object.keys(map).sort().reverse();
  const lag=LIQ?iso(wdBack(LIQ,10)):null;
  const{key:ak}=lag?cerForDate(lag):{key:null};
  const wrap=document.getElementById('cer-tbl');
  if(!keys.length){wrap.innerHTML='<div class="dempty">Sin datos guardados.</div>';return;}
  wrap.innerHTML='<table class="dtbl"><thead><tr><th>Fecha</th><th>Valor CER</th><th></th></tr></thead><tbody>'+
    keys.map(k=>'<tr class="'+(k===ak?'act':'')+'"><td>'+k+(k===ak?' ◄ en uso':'')+
    '</td><td>'+map[k].toFixed(4)+'</td><td><button class="dbtn" onclick="delCerRow(\\''+k+'\\')">✕</button></td></tr>'
    ).join('')+'</tbody></table>';
}

// HOL CRUD
function importHol(){
  const raw=document.getElementById('hol-ta').value.trim();
  if(!raw){alert('Pegá fechas primero');return;}
  const set=lsHol();let ok=0,sk=0;
  for(const line of raw.split('\\n')){
    let found=false;
    for(const part of line.split(/[\\t,;]+/)){
      const f=parseIso(part.trim());
      if(f){set.add(f);HOL.add(f);ok++;found=true;break;}
    }
    if(!found&&line.trim())sk++;
  }
  savHol(set);
  document.getElementById('hol-ta').value='';
  showMsg('hol-msg','✓ '+ok+' feriados importados'+(sk?' ('+sk+' ignorados)':''));
  refreshModal(); updateCERFromLS(); renderTF(); renderCER();
}
function exportHol(){
  const set=lsHol();if(!set.size){alert('Sin feriados importados');return;}
  dl('feriados','fecha\\n'+[...set].sort().join('\\n'));
}
function clearHol(){
  if(!confirm('¿Borrar feriados importados?'))return;
  localStorage.removeItem(K_HOL);
  alert('Eliminados. Recargá la página para actualizar el lag.');
  refreshModal();
}
function delHolRow(k){const s=lsHol();s.delete(k);savHol(s);HOL.delete(k);refreshModal();updateCERFromLS();renderCER();}
function refreshHolTbl(){
  const set=lsHol();
  const wrap=document.getElementById('hol-tbl');
  if(!set.size){wrap.innerHTML='<div class="dempty">Sin feriados importados. Los del código (2025-2027) están activos.</div>';return;}
  wrap.innerHTML='<table class="dtbl"><thead><tr><th>Fecha</th><th></th></tr></thead><tbody>'+
    [...set].sort().reverse().map(k=>'<tr><td>'+k+'</td><td><button class="dbtn" onclick="delHolRow(\\''+k+'\\')">✕</button></td></tr>'
    ).join('')+'</tbody></table>';
}

// EXPORT/IMPORT ALL
function exportAll(){
  const data={version:2,cer_serie:lsCer(),feriados:[...lsHol()].sort(),exportado:new Date().toISOString()};
  dl('bonos_ar_config',JSON.stringify(data,null,2));
  showMsg('cer-msg','✓ Exportado: '+Object.keys(data.cer_serie).length+' CER + '+data.feriados.length+' feriados');
}
function importAll(input){
  const f=input.files[0];if(!f)return;
  const r=new FileReader();
  r.onload=e=>{
    try{
      const d=JSON.parse(e.target.result);
      if(d.cer_serie){const m=lsCer();Object.assign(m,d.cer_serie);savCer(m);}
      if(Array.isArray(d.feriados)){const s=lsHol();for(const x of d.feriados){s.add(x);HOL.add(x);}savHol(s);}
      refreshModal();updateCERFromLS();renderTF();renderCER();
      showMsg('cer-msg','✓ Importado correctamente');
    }catch(err){alert('Error: '+err.message);}
    input.value='';
  };
  r.readAsText(f);
}

/* ═══════════════════════════════════════════
   CSV DOWNLOAD
═══════════════════════════════════════════ */
function dl(name,csv){
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,%EF%BB%BF'+encodeURIComponent(csv);
  a.download=name+'.csv'; document.body.appendChild(a); a.click(); document.body.removeChild(a);
}
function dlTF(){
  const rows=compTF(),cc=TFV===1;
  const h=cc?['Bono','Precio API','Precio Manual','Dias','Com TNA','TNA c/Com','Precio c/Com','Com Directa','TEA c/Com','TEM c/Com']:['Bono','Precio API','Precio Manual','Dias','Duration','Vto','Pago','Ret Total','TNA','TEA','TEM','MEP BE'];
  const f=r=>cc?[r.t,N(r.apiP,3),TF_MAN[r.t]?N(TF_MAN[r.t],3):'',r.d,P(r.com),P(r.tnaCC),N(r.precCC,3),P(r.comDir,4),P(r.teaCC),P(r.temCC)]:[r.t,N(r.apiP,3),TF_MAN[r.t]?N(TF_MAN[r.t],3):'',r.d,N(r.dur,2),fmt(r.vto),N(r.pago,3),P(r.ret),P(r.tna),P(r.tea),P(r.tem),Math.round(r.mepBE)];
  dl('bonos_tf_'+iso(LIQ), h.join(',')+'\\n'+rows.map(r=>f(r).map(v=>'"'+v+'"').join(',')).join('\\n'));
}
function dlCER(){
  const rows=compCER(),cc=CERV===1;
  const h=cc?['Ticker','Precio API','Precio Manual','Dias','Com TNA','TNA c/Com','Precio c/Com','Com Directa','TEA c/Com']:['Ticker','Precio API','Precio Manual','Dias','Duration','Vto','CER inicial','TNA (180/360)','TIR'];
  const f=r=>cc?[r.t,N(r.apiP,3),CER_MAN[r.t]?N(CER_MAN[r.t],3):'',r.dc,P(r.com),P(r.tnaCC,2),N(r.precCC,3),P(r.comDir,4),P(r.teaCC,2)]:[r.t,N(r.apiP,3),CER_MAN[r.t]?N(CER_MAN[r.t],3):'',r.dc,N(r.dur,2),fmt(r.vto),N(r.cerI,2),P(r.tna,2),P(r.tir,2)];
  dl('bonos_cer_'+iso(LIQ), h.join(',')+'\\n'+rows.map(r=>f(r).map(v=>'"'+v+'"').join(',')).join('\\n'));
}

/* ═══════════════════════════════════════════
   API REFRESH
═══════════════════════════════════════════ */
async function doRefresh(){
  document.getElementById('v-st').textContent='...';
  try{
    const[rN,rB,rM,rC]=await Promise.allSettled([
      fetch('https://data912.com/live/arg/notes',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),
      fetch('https://data912.com/live/arg/bonds', {signal:AbortSignal.timeout(7000)}).then(r=>r.json()),
      fetch('https://dolarapi.com/v1/dolares/bolsa',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),
      fetch('https://dolarapi.com/v1/dolares/contadoconliqui',{signal:AbortSignal.timeout(7000)}).then(r=>r.json()),
    ]);
    for(const res of[rN,rB]){
      if(res.status==='fulfilled'&&Array.isArray(res.value)){
        for(const i of res.value){
          const s=(i.symbol||i.ticker||'').toUpperCase(), p=i.last_price||i.close||i.bid;
          if(s&&p){if(s in TP)TP[s]=p;if(s in CP)CP[s]=p;}
        }
      }
    }
    if(rM.status==='fulfilled'&&rM.value?.venta){
      const m=rM.value,mid=m.compra?(m.compra+m.venta)/2:m.venta;
      document.getElementById('v-mep').textContent='$'+Math.round(mid).toLocaleString('es-AR');
      document.getElementById('v-mep').title='Compra $'+m.compra+' | Venta $'+m.venta;
    }
    if(rC.status==='fulfilled'&&rC.value?.venta){
      const c=rC.value,mid=c.compra?(c.compra+c.venta)/2:c.venta;
      document.getElementById('v-ccl').textContent='$'+Math.round(mid).toLocaleString('es-AR');
    }
    const live=rM.status==='fulfilled'&&rM.value?.venta;
    document.getElementById('v-badge').className='badge '+(live?'b-live':'b-demo');
    document.getElementById('v-st').textContent=live?'EN VIVO':'DEMO';
  }catch(e){
    document.getElementById('v-badge').className='badge b-demo';
    document.getElementById('v-st').textContent='DEMO';
  }
  document.getElementById('v-ts').textContent=new Date().toLocaleTimeString('es-AR');
  renderTF(); renderCER();
}

/* ═══════════════════════════════════════════
   INTERVAL
═══════════════════════════════════════════ */
let _tmr=null;
function startTimer(s){if(_tmr)clearInterval(_tmr);if(s>0)_tmr=setInterval(doRefresh,s*1000);}
function changeInterval(){startTimer(parseInt(document.getElementById('isel').value));}


/* ═══════════════════════════════════════════
   PRIMARY / MATRIZ API
   Servidor local: http://localhost:8765
   Correr: py proxy_fixed.py
═══════════════════════════════════════════ */
const PROXY = 'http://localhost:8765';
let WS_ACTIVE = false;
let PRIMARY_FAILS = 0;

function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

async function getProxyStatus(){
  const r = await fetch(PROXY+'/status', {signal:AbortSignal.timeout(5000)});
  if(!r.ok) throw new Error('No se pudo consultar el estado del proxy');
  return await r.json();
}

// ── LOGIN ────────────────────────────────────────
async function waitForPrimaryConnection(timeoutMs=90000){
  const err = document.getElementById('login-err');
  const started = Date.now();

  while(Date.now() - started < timeoutMs){
    const st = await getProxyStatus();

    if(st.connected){
      return st;
    }

    if(st.last_error && !st.login_in_progress){
      throw new Error(st.last_error);
    }

    err.textContent = st.msg || 'Conectando...';
    err.style.display = '';

    await sleep(1000);
  }

  throw new Error('Timeout esperando conexión con Matriz.');
}

async function doLogin(){
  const user = document.getElementById('login-user').value.trim();
  const pass = document.getElementById('login-pass').value;
  const err  = document.getElementById('login-err');
  const btn  = document.querySelector('#login-modal button');

  if(!user||!pass){
    err.textContent='Completá usuario y contraseña.';
    err.style.display='';
    return;
  }

  err.style.display='none';
  btn.textContent='Conectando...';
  btn.disabled=true;

  try{
    const r = await fetch(PROXY+'/login', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({user, password:pass}),
      signal: AbortSignal.timeout(10000),
    });

    const data = await r.json();
    if(!data.ok) throw new Error(data.msg || 'No se pudo iniciar el login');

    err.textContent='Conectando con Matriz...';
    err.style.display='';

    await waitForPrimaryConnection(90000);

    WS_ACTIVE = true;
    PRIMARY_FAILS = 0;
    document.getElementById('login-modal').style.display='none';
    document.getElementById('v-badge').className='badge b-live';
    document.getElementById('v-st').textContent='Primary RT';

    startTimer(parseInt(document.getElementById('isel').value)||10);
    await fetchPrimaryPrices();
  }catch(e){
    const msg = (e.message.includes('fetch') || e.message.includes('Failed') || e.message.includes('NetworkError'))
      ? '¿Está corriendo proxy_fixed.py? Abrí una terminal y ejecutá: py proxy_fixed.py'
      : e.message;

    err.textContent = msg;
    err.style.display = '';
    WS_ACTIVE = false;
  }

  btn.textContent='Conectar';
  btn.disabled=false;
}

function skipLogin(){
  document.getElementById('login-modal').style.display='none';
  renderTF();
  renderCER();
  doRefresh();
  startTimer(180);
}

// ── FETCH PRICES FROM LOCAL SERVER ───────────────
async function fetchPrimaryPrices(){
  if(!WS_ACTIVE) return false;

  try{
    const r = await fetch(PROXY+'/prices', {signal:AbortSignal.timeout(8000)});
    if(!r.ok) throw new Error('El proxy respondió con error');

    const data = await r.json();
    const px = data.prices || {};
    let updated = 0;

    for(const [sym, md] of Object.entries(px)){
      const price = md.last || md.ask || md.bid || md.close;
      if(price != null){
        if(sym in TP) TP[sym] = price;
        if(sym in CP) CP[sym] = price;
        updated++;
      }
    }

    PRIMARY_FAILS = 0;

    if(updated > 0){
      renderTF();
      renderCER();
    }

    document.getElementById('v-ts').textContent = new Date().toLocaleTimeString('es-AR');
    document.getElementById('v-st').textContent = data.status?.connected ? 'Primary RT' : (data.status?.msg || 'Primary');
    document.getElementById('v-badge').className = data.status?.connected ? 'badge b-live' : 'badge b-demo';

    return true;
  }catch(e){
    PRIMARY_FAILS++;

    if(PRIMARY_FAILS >= 3){
      WS_ACTIVE = false;
      document.getElementById('v-badge').className = 'badge b-demo';
      document.getElementById('v-st').textContent = 'Sin conexión';
      document.getElementById('login-modal').style.display = 'flex';
      document.getElementById('login-err').textContent = 'Se perdió la conexión con proxy_fixed.py';
      document.getElementById('login-err').style.display = '';
    }

    return false;
  }
}

// ── OVERRIDE doRefresh ───────────────────────────
const _origRefresh = doRefresh;
async function doRefresh(){
  if(WS_ACTIVE){
    await fetchPrimaryPrices();
    try{
      const[rM,rC]=await Promise.allSettled([
        fetch('https://dolarapi.com/v1/dolares/bolsa',{signal:AbortSignal.timeout(5000)}).then(r=>r.json()),
        fetch('https://dolarapi.com/v1/dolares/contadoconliqui',{signal:AbortSignal.timeout(5000)}).then(r=>r.json()),
      ]);
      if(rM.status==='fulfilled'&&rM.value?.venta){
        const m=rM.value,mid=m.compra?(m.compra+m.venta)/2:m.venta;
        document.getElementById('v-mep').textContent='$'+Math.round(mid).toLocaleString('es-AR');
      }
      if(rC.status==='fulfilled'&&rC.value?.venta){
        const c=rC.value,mid=c.compra?(c.compra+c.venta)/2:c.venta;
        document.getElementById('v-ccl').textContent='$'+Math.round(mid).toLocaleString('es-AR');
      }
    }catch(e){}
  } else {
    await _origRefresh();
  }
}

/* ═══════════════════════════════════════════
   INIT
═══════════════════════════════════════════ */
(async function(){
  mergeHol();
  const n=new Date();
  setLIQ(nextBD(D(n.getFullYear(),n.getMonth(),n.getDate())));
  renderTF();
  renderCER();

  try{
    const st = await getProxyStatus();
    if(st.connected){
      WS_ACTIVE = true;
      PRIMARY_FAILS = 0;
      document.getElementById('login-modal').style.display = 'none';
      document.getElementById('v-badge').className = 'badge b-live';
      document.getElementById('v-st').textContent = 'Primary RT';
      startTimer(parseInt(document.getElementById('isel').value)||10);
      await fetchPrimaryPrices();
      return;
    }
  }catch(e){}

  // Login modal queda visible por defecto
})();
</script>

<!-- LOGIN MODAL -->
<div class="mbg" id="login-modal" style="display:flex;">
  <div class="mbox" style="width:360px;max-width:96vw;">
    <div class="mhead">
      <span style="font-size:13px;font-weight:600;">Acceso Matriz Adcap</span>
    </div>
    <div class="mpane" style="gap:12px;">
      <div class="hint">Ingresá tus credenciales de <b style="color:var(--tw)">matriz.adcap.xoms.com.ar</b><br>Las credenciales no se guardan.</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.5px;">Usuario</label>
          <input id="login-user" type="text" autocomplete="username"
            style="background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:4px;outline:none;"
            onkeydown="if(event.key==='Enter')document.getElementById('login-pass').focus()">
        </div>
        <div style="display:flex;flex-direction:column;gap:4px;">
          <label style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.5px;">Contraseña</label>
          <input id="login-pass" type="password" autocomplete="current-password"
            style="background:var(--bg3);border:1px solid var(--b2);color:var(--tw);font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:4px;outline:none;"
            onkeydown="if(event.key==='Enter')doLogin()">
        </div>
      </div>
      <div id="login-err" style="font-size:10px;color:var(--red);display:none;"></div>
      <button onclick="doLogin()" style="background:var(--blue);border:none;color:#fff;font-family:var(--sans);font-size:12px;font-weight:600;padding:8px;border-radius:4px;cursor:pointer;width:100%;">Conectar</button>
      <div style="font-size:10px;color:var(--t3);text-align:center;">
        Necesitás correr <code style="background:var(--bg4);padding:1px 5px;border-radius:3px;color:var(--t2);">proxy.py</code> en tu PC
        &nbsp;·&nbsp; <button onclick="skipLogin()" style="background:none;border:none;color:var(--t3);font-size:10px;cursor:pointer;text-decoration:underline;">Continuar sin login (demo)</button>
      </div>
    </div>
  </div>
</div>

</body>
</html>
"""

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
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("ERROR: pip3 install selenium")
    import sys; sys.exit(1)

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
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1400,1000")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    # Use system Chrome + ChromeDriver (pre-installed in Docker)
    for chrome in ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]:
        if os.path.exists(chrome):
            opts.binary_location = chrome
            break
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
        if self.path in ("/", "/index.html"):
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/prices":
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
