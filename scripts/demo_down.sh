#!/usr/bin/env bash
# Apaga todo lo que levanta demo_up.sh.
#
#   ./scripts/demo_down.sh            # para procesos y contenedores
#   ./scripts/demo_down.sh --datos    # ademas borra el volumen de PostgreSQL
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_BPM="${REPO_BPM:-$AQUI/../../lab6}"

echo "Deteniendo worker y API..."
# Se matan por el puerto y por patron amplio: segun como se lanzaran, la linea
# de comandos puede ser absoluta ("/ruta/run.py") o relativa ("./venv/bin/python
# run.py"), y un patron con ruta absoluta no captura el segundo caso.
for patron in "[p]ython.*worker\.py" "[p]ython.*run\.py"; do
    pkill -f "$patron" 2>/dev/null
done
# Ultimo recurso: lo que siga escuchando en el puerto de la API.
PID_API=$(ss -lntp "sport = :5000" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
[ -n "${PID_API:-}" ] && kill "$PID_API" 2>/dev/null
sleep 2

echo "Deteniendo PostgreSQL..."
if [ "${1:-}" = "--datos" ]; then
    (cd "$AQUI" && docker compose down -v >/dev/null 2>&1)
    echo "  volumen de datos eliminado"
else
    (cd "$AQUI" && docker compose down >/dev/null 2>&1)
fi

echo "Deteniendo RabbitMQ y el servidor de correo..."
[ -f "$REPO_BPM/docker-compose.yml" ] && (cd "$REPO_BPM" && docker compose down >/dev/null 2>&1)

echo "Listo."
