#!/usr/bin/env bash
# Levanta TODA la demo del proyecto y verifica cada pieza antes de continuar.
#
#   ./scripts/demo_up.sh
#
# Arranca, en orden: RabbitMQ + MailHog (repo BPM), PostgreSQL, la API REST y el
# worker de eventos. Si algo no queda operativo, se detiene y dice exactamente
# qué falló, en vez de dejar la demo a medias.
#
# Para apagar todo:  ./scripts/demo_down.sh
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_BPM="${REPO_BPM:-$AQUI/../../lab6}"
LOGS="$AQUI/.demo-logs"
mkdir -p "$LOGS"

verde()  { printf '  \033[32m✓\033[0m %s\n' "$1"; }
rojo()   { printf '  \033[31m✗\033[0m %s\n' "$1"; }
info()   { printf '\n\033[1m%s\033[0m\n' "$1"; }

fallar() {
    rojo "$1"
    echo
    echo "  La demo NO está lista. Corrige lo anterior y vuelve a ejecutar."
    exit 1
}

esperar() {  # esperar <descripcion> <segundos> <comando...>
    local desc="$1" limite="$2"; shift 2
    for ((i = 0; i < limite; i++)); do
        if "$@" >/dev/null 2>&1; then verde "$desc"; return 0; fi
        sleep 1
    done
    rojo "$desc (tras ${limite}s)"
    return 1
}

# ---------------------------------------------------------------- 1. broker
info "1/5  RabbitMQ y servidor de correo"

[ -f "$REPO_BPM/docker-compose.yml" ] || fallar \
    "No encuentro el repo BPM en '$REPO_BPM'. Indícalo con REPO_BPM=/ruta/a/laboratorio_6"

(cd "$REPO_BPM" && docker compose up -d >/dev/null 2>&1) || fallar "No pude levantar RabbitMQ/MailHog"

esperar "RabbitMQ operativo (:15672)" 45 \
    curl -sf -u guest:guest http://localhost:15672/api/overview || fallar "RabbitMQ no responde"
esperar "Servidor de correo operativo (:8025)" 30 \
    curl -sf http://localhost:8025/api/v2/messages || fallar "MailHog no responde"

for cola in rse.convocatorias rse.postulaciones rse.notificaciones; do
    if curl -sf -u guest:guest "http://localhost:15672/api/queues/%2f/$cola" >/dev/null 2>&1; then
        verde "Cola '$cola' declarada"
    else
        rojo "Falta la cola '$cola'"
    fi
done

# ------------------------------------------------------------ 2. postgresql
info "2/5  PostgreSQL"

(cd "$AQUI" && docker compose up -d >/dev/null 2>&1) || fallar \
    "No pude levantar PostgreSQL. ¿Puerto ocupado? Revisa 'docker compose logs postgres'"

esperar "PostgreSQL aceptando conexiones (:5433)" 45 \
    docker exec sodimac_postgres pg_isready -U sodimac -d reabastecimiento \
    || fallar "PostgreSQL no arrancó"

# -------------------------------------------------------------------- 3. API
info "3/5  API REST"

export REPO_BACKEND=sqlalchemy
export EVENTOS_BACKEND=rabbitmq
export DEBUG=false

PY="$AQUI/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

if curl -sf http://localhost:5000/health >/dev/null 2>&1; then
    verde "Ya había una API escuchando en :5000"
else
    (cd "$AQUI" && nohup "$PY" run.py > "$LOGS/api.log" 2>&1 &)
    esperar "API arrancada (:5000)" 30 curl -sf http://localhost:5000/health \
        || fallar "La API no arrancó — mira $LOGS/api.log"
fi

BACKEND=$(curl -s http://localhost:5000/health | grep -o '"backend": *"[^"]*"' | cut -d'"' -f4)
if [ "$BACKEND" = "sqlalchemy" ]; then
    verde "Backend de persistencia: sqlalchemy"
else
    rojo "Backend de la API: '$BACKEND' (se esperaba 'sqlalchemy')"
    fallar "Con el backend en memoria la API NO verá lo que sincronice el worker. Párala y vuelve a lanzar este script."
fi

# ----------------------------------------------------------------- 4. worker
info "4/5  Worker de eventos"

if pgrep -f "$AQUI/worker.py" >/dev/null 2>&1 || pgrep -f "python.*worker\.py" >/dev/null 2>&1; then
    verde "Ya había un worker en marcha"
else
    (cd "$AQUI" && nohup "$PY" worker.py > "$LOGS/worker.log" 2>&1 &)
    esperar "Worker suscrito a las colas" 25 \
        grep -q "Suscrito a la cola" "$LOGS/worker.log" \
        || fallar "El worker no se suscribió — mira $LOGS/worker.log"
fi

# ------------------------------------------------------- 5. prueba de humo
info "5/5  Prueba de extremo a extremo"

CODIGO="RSE-DEMO-$(date +%H%M%S)"
PAYLOAD=$(printf '{"codigo":"%s","nombre":"Reciclaje de mermas en tiendas","tipo":"RECICLAJE","presupuestoAprobado":15000.0,"requisitos":"Certificacion ISO 14001"}' "$CODIGO")
SOBRE=$(python3 -c "import json,sys; print(json.dumps({'routing_key':'rse.convocatorias','payload':sys.argv[1],'payload_encoding':'string','properties':{'content_type':'application/json','delivery_mode':2}}))" "$PAYLOAD")

curl -sf -u guest:guest -H 'content-type: application/json' \
    -XPOST "http://localhost:15672/api/exchanges/%2f/amq.default/publish" \
    -d "$SOBRE" >/dev/null 2>&1 \
    && verde "Convocatoria publicada en la cola (como hace el conector de Bonita)" \
    || fallar "No pude publicar en RabbitMQ"

sleep 3

if curl -sf "http://localhost:5000/api/iniciativas/$CODIGO" >/dev/null 2>&1; then
    verde "El worker la sincronizó y la API la sirve — integración COMPLETA"
else
    fallar "La API no encuentra '$CODIGO'. El worker no la procesó; mira $LOGS/worker.log"
fi

# ------------------------------------------------------------------ resumen
info "Todo listo"
cat <<EOF
  Bandeja de correo   http://localhost:8025
  Colas RabbitMQ      http://localhost:15672     (guest / guest)
  Swagger de la API   http://localhost:5000/docs
  Logs                $LOGS/

  Datos de demo:      ./scripts/seed_demo.sh
  Apagar todo:        ./scripts/demo_down.sh
EOF
