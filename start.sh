#!/bin/bash
set -e

echo "[start.sh] Iniciando Xvfb en :99..."
Xvfb :99 -screen 0 1280x800x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

# Esperar a que Xvfb esté realmente listo
echo "[start.sh] Esperando que Xvfb esté listo..."
for i in $(seq 1 20); do
    if xdpyinfo -display :99 >/dev/null 2>&1; then
        echo "[start.sh] Xvfb listo (intento $i)"
        break
    fi
    sleep 0.5
done

# Verificar
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "[start.sh] Display :99 confirmado OK"
else
    echo "[start.sh] ADVERTENCIA: Xvfb no responde, Chrome usara --headless"
fi

echo "[start.sh] Iniciando proxy.py..."
exec python3 -u /app/proxy.py
