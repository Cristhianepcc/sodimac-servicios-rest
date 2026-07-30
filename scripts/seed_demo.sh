#!/usr/bin/env bash
# Carga datos de demostracion en la API para no teclear nada en vivo.
#
#   ./scripts/seed_demo.sh
#
# Deja una iniciativa aprobada, con dos KPIs (uno cumplido y otro rezagado) y una
# evidencia, de modo que el endpoint de cumplimiento devuelva un resultado con
# contenido y el gateway "Metas cumplidas?" tenga algo que decidir.
set -uo pipefail
API="${API:-http://localhost:5000}"

curl -sf "$API/health" >/dev/null 2>&1 || {
    echo "La API no responde en $API. Ejecuta antes ./scripts/demo_up.sh"; exit 1; }

echo "Creando iniciativa..."
COD=$(curl -s -XPOST "$API/api/iniciativas" -H 'content-type: application/json' \
  -d '{"nombre":"Reciclaje de mermas en tiendas","tipo":"RECICLAJE","descripcion":"Recojo y valorizacion de mermas organicas en tiendas de Arequipa","requierePresupuesto":true,"presupuestoSolicitado":15000}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["codigo"])')
echo "  $COD"

echo "Aprobando en el comite..."
curl -s -XPOST "$API/api/iniciativas/$COD/evaluacion" -H 'content-type: application/json' \
  -d '{"aprobada":true,"presupuestoAprobado":15000,"comentario":"Aprobada por alineacion con la meta de residuos cero."}' -o /dev/null

echo "Registrando KPIs..."
curl -s -XPOST "$API/api/iniciativas/$COD/indicadores" -H 'content-type: application/json' \
  -d '{"nombre":"Merma valorizada","unidad":"t","valorLineaBase":0,"valorActual":95,"meta":100}' -o /dev/null
curl -s -XPOST "$API/api/iniciativas/$COD/indicadores" -H 'content-type: application/json' \
  -d '{"nombre":"Tiendas adheridas","unidad":"u","valorLineaBase":0,"valorActual":30,"meta":100}' -o /dev/null

echo "Registrando evidencia..."
curl -s -XPOST "$API/api/iniciativas/$COD/evidencias" -H 'content-type: application/json' \
  -d '{"descripcion":"Primer mes de operacion en 30 tiendas","porcentajeAvance":45}' -o /dev/null

echo
echo "Cumplimiento (lo que consulta el conector REST de Bonita):"
curl -s "$API/api/iniciativas/$COD/cumplimiento?tolerancia=0.9" | python3 -m json.tool | sed 's/^/  /'
echo
echo "Para la demo usa el codigo: $COD"
