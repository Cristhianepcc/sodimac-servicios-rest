#!/usr/bin/env bash
# Demo narrada para la sustentación: recorre el ciclo completo de un reclamo de
# postventa y la integración BPM <-> servicios por RabbitMQ, paso a paso.
#
#   ./scripts/demo_presentacion.sh              # avanza pulsando Enter
#   ./scripts/demo_presentacion.sh --auto       # avanza solo, 3 s por paso
#
# Requiere que ./scripts/demo_up.sh haya terminado en 5/5.
set -uo pipefail

API="${API:-http://localhost:5000}"
RABBIT="${RABBIT:-http://localhost:15672}"
AUTO=0
[ "${1:-}" = "--auto" ] && AUTO=1

# ---------------------------------------------------------------- estilo
B=$'\033[1m'; D=$'\033[2m'; N=$'\033[0m'
AZ=$'\033[38;5;33m'; VE=$'\033[38;5;35m'; AM=$'\033[38;5;178m'; RO=$'\033[38;5;167m'; MO=$'\033[38;5;98m'

titulo() {
    clear
    printf '\n%s%s  %s%s\n' "$B" "$AZ" "$1" "$N"
    printf '%s  %s%s\n\n' "$D" "$(printf '─%.0s' $(seq 1 68))" "$N"
}
narra()  { printf '  %s%s%s\n' "$AM" "$1" "$N"; }
paso()   { printf '\n  %s▸ %s%s\n' "$B" "$1" "$N"; }
cmd()    { printf '  %s$ %s%s\n' "$D" "$1" "$N"; }
ok()     { printf '  %s✓%s %s\n' "$VE" "$N" "$1"; }
err()    { printf '  %s✗%s %s\n' "$RO" "$N" "$1"; }

pausa() {
    if [ "$AUTO" = "1" ]; then sleep 3; else
        printf '\n  %s· Enter para continuar ·%s' "$D" "$N"; read -r _
    fi
}

json() { python3 -m json.tool 2>/dev/null | sed 's/^/    /' || cat; }

# ---------------------------------------------------------------- checks
curl -sf "$API/health" >/dev/null 2>&1 || {
    err "La API no responde en $API"
    echo "     Ejecuta antes: ./scripts/demo_up.sh"; exit 1; }

# ═══════════════════════════════════════════════════════════════ 0
titulo "Sodimac — Aplicación BPM · demostración"
narra "Vamos a recorrer dos cosas:"
echo
echo "    1. El ciclo de vida de un reclamo de postventa a través de la API,"
echo "       con sus tres roles y dónde se validan las reglas de negocio."
echo
echo "    2. La integración entre el proceso BPM de Bonita y los servicios web"
echo "       a través del broker de mensajes."
echo
paso "Estado de la plataforma"
cmd "curl -s $API/health"
curl -s "$API/health" | json
BACKEND=$(curl -s "$API/health" | grep -o '"backend": *"[^"]*"' | cut -d'"' -f4)
[ "$BACKEND" = "sqlalchemy" ] && ok "Persistencia compartida entre la API y el worker" \
                              || err "backend='$BACKEND' — la API y el worker NO comparten estado"
pausa

# ═══════════════════════════════════════════════════════════════ 1
titulo "1/6  El cliente registra un reclamo"
narra "El frontend web no tiene lógica: hace exactamente esta llamada."
echo
paso "POST /api/reclamos   ·   rol CLIENTE"
cmd "curl -X POST $API/api/reclamos -d '{...}'"
RESP=$(curl -s -XPOST "$API/api/reclamos" -H 'content-type: application/json' -d '{
  "cliente":"Ana Quispe","dni":"70123456","email":"ana.quispe@correo.pe",
  "telefono":"958123456","producto":"Taladro percutor 750W",
  "motivo":"El equipo se detiene tras cinco minutos de uso"}')
echo "$RESP" | json
RID=$(echo "$RESP" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("id",""))' 2>/dev/null)
[ -n "$RID" ] && ok "Reclamo $RID creado en estado REGISTRADO" || err "No se pudo crear el reclamo"
pausa

# ═══════════════════════════════════════════════════════════════ 2
titulo "2/6  Postventa consulta y valida"
narra "Otro rol, otra vista: postventa ve todos los reclamos, no solo los suyos."
echo
paso "GET /api/reclamos   ·   rol POSTVENTA"
cmd "curl -s $API/api/reclamos"
curl -s "$API/api/reclamos" | python3 -c "
import json,sys
d=json.load(sys.stdin)
items = d.get('items', d) if isinstance(d, dict) else d
print(f\"    {d.get('total', len(items))} reclamo(s) · respuesta paginada\")
print()
for r in items[-4:]:
    print(f\"      {r['id']}  {r['cliente']:<16} {r['estado']}\")" 2>/dev/null
pausa

# ═══════════════════════════════════════════════════════════════ 3
titulo "3/6  Las reglas viven en el dominio, no en la pantalla"
narra "El formulario web no valida nada: quien valida es la fábrica del dominio."
echo
paso "Intentamos crear un reclamo incompleto"
cmd "curl -X POST $API/api/reclamos -d '{\"cliente\":\"\"}'"
CODE=$(curl -s -o /tmp/_r.json -w '%{http_code}' -XPOST "$API/api/reclamos" \
  -H 'content-type: application/json' -d '{"cliente":"","dni":"","email":""}')
cat /tmp/_r.json 2>/dev/null | json
echo
if [ "$CODE" = "400" ]; then
    ok "HTTP $CODE — ReclamoFabrica rechaza la creación"
    narra "Esta regla no está en el formulario ni en el controlador: está en la"
    narra "capa de dominio, así que se cumple llegue por HTTP, por el frontend"
    narra "web o por un conector de Bonita."
else
    printf '  HTTP %s\n' "$CODE"
fi
pausa

titulo "3b/6  Invariantes dentro del agregado"
narra "En el contexto de RSE el agregado sí encapsula reglas de negocio."
echo
paso "Creamos una iniciativa y la aprobamos con presupuesto cero"
cmd "POST /api/iniciativas  →  POST /{codigo}/evaluacion"
COD_INI=$(curl -s -XPOST "$API/api/iniciativas" -H 'content-type: application/json' \
  -d '{"nombre":"Reciclaje de mermas","tipo":"RECICLAJE","requierePresupuesto":true,"presupuestoSolicitado":15000}' \
  | python3 -c 'import json,sys;print(json.load(sys.stdin).get("codigo",""))' 2>/dev/null)
printf '    iniciativa creada: %s\n\n' "$COD_INI"
CODE=$(curl -s -o /tmp/_i.json -w '%{http_code}' -XPOST "$API/api/iniciativas/$COD_INI/evaluacion" \
  -H 'content-type: application/json' -d '{"aprobada":true,"presupuestoAprobado":0}')
cat /tmp/_i.json 2>/dev/null | json
echo
if [ "$CODE" = "400" ]; then
    ok "HTTP $CODE — la invariante está en IniciativaRSE.evaluar()"
    narra "«Una iniciativa aprobada requiere presupuesto mayor que cero.»"
    narra "El agregado protege su propia consistencia."
else
    printf '  HTTP %s\n' "$CODE"
fi
pausa

# ═══════════════════════════════════════════════════════════════ 4
titulo "4/6  La documentación se deriva del código"
narra "No hay ningún YAML mantenido a mano: la especificación sale del url_map."
echo
paso "GET /openapi.json"
cmd "curl -s $API/openapi.json | jq '.paths | length'"
curl -s "$API/openapi.json" | python3 -c "
import json,sys
from collections import Counter
s=json.load(sys.stdin)
ops=[(r,m,o) for r,p in s['paths'].items() for m,o in p.items()]
print(f'    OpenAPI {s[\"openapi\"]}  ·  {len(s[\"paths\"])} rutas  ·  {len(ops)} operaciones')
print()
for tag,n in Counter(o['tags'][0] for _,_,o in ops).most_common():
    print(f'      {n:>3}  {tag}')" 2>/dev/null
echo
ok "Hay pruebas que fallan si alguien añade un endpoint sin documentar"
pausa

# ═══════════════════════════════════════════════════════════════ 5
titulo "5/6  Bonita publica en el broker"
narra "Esto es exactamente lo que hace el conector REST del proceso BPM:"
narra "un POST a la Management API de RabbitMQ."
echo
COD="RSE-DEMO-$(date +%H%M%S)"
paso "El proceso publica una convocatoria en rse.convocatorias"
cmd "POST $RABBIT/api/exchanges/%2f/amq.default/publish"
PAYLOAD=$(printf '{"codigo":"%s","nombre":"Reciclaje de mermas en tiendas","tipo":"RECICLAJE","presupuestoAprobado":15000.0,"requisitos":"Certificacion ISO 14001"}' "$COD")
SOBRE=$(python3 -c "import json,sys;print(json.dumps({'routing_key':'rse.convocatorias','payload':sys.argv[1],'payload_encoding':'string','properties':{'content_type':'application/json','delivery_mode':2}}))" "$PAYLOAD")
curl -s -u guest:guest -H 'content-type: application/json' \
  -XPOST "$RABBIT/api/exchanges/%2f/amq.default/publish" -d "$SOBRE" | json
ok "Mensaje encolado — Bonita ya puede seguir con su flujo"
echo
narra "Fíjense en que el proceso NO espera al servicio. Si estuviera caído,"
narra "el mensaje esperaría en la cola. Eso es el desacople temporal."
pausa

# ═══════════════════════════════════════════════════════════════ 6
titulo "6/6  El worker consume y el dominio responde"
narra "Un proceso distinto —worker.py— escucha la cola por AMQP nativo."
echo
paso "Esperando a que el worker procese el mensaje..."
sleep 3
cmd "curl -s $API/api/iniciativas/$COD"
if curl -sf "$API/api/iniciativas/$COD" >/dev/null 2>&1; then
    curl -s "$API/api/iniciativas/$COD" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f\"    codigo   : {d['codigo']}\")
print(f\"    nombre   : {d['nombre']}\")
print(f\"    estado   : {d['estado']}\")
print(f\"    aprobada : {d['aprobada']}\")" 2>/dev/null
    echo
    ok "El worker sincronizó la iniciativa y la API ya la sirve"
    narra "El mensaje cruzó: Bonita → HTTP → RabbitMQ → AMQP → worker → dominio."
else
    err "La API no encuentra $COD — revisa que el worker esté corriendo"
fi
echo
paso "Estado de las tres colas"
curl -s -u guest:guest "$RABBIT/api/queues/%2f" | python3 -c "
import json,sys
for q in json.load(sys.stdin):
    if q['name'].startswith('rse.'):
        print(f\"      {q['name']:<22} mensajes={q.get('messages',0)}  consumidores={q.get('consumers',0)}\")" 2>/dev/null
echo
narra "rse.notificaciones tiene 0 consumidores de nuestro lado a propósito:"
narra "de esa cola consume Bonita, para saber el resultado de la tarea automática."
pausa

# ═══════════════════════════════════════════════════════════════ fin
titulo "Resumen"
echo "    ✓  Ciclo de un reclamo con tres roles, y validación de negocio en la"
echo "       capa de dominio: la fábrica y las invariantes del agregado"
echo
echo "    ✓  Documentación OpenAPI derivada del código, no mantenida a mano"
echo
echo "    ✓  Proceso BPM y servicios web integrados por un broker, desacoplados"
echo "       en el tiempo y con entrega garantizada"
echo
printf '  %s%sGracias.%s\n\n' "$B" "$AZ" "$N"
