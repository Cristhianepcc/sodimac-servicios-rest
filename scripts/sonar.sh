#!/usr/bin/env sh
# Análisis de calidad con SonarQube: levanta el servidor si hace falta, lo
# configura la primera vez, analiza el proyecto y muestra el resultado.
#
#   ./scripts/sonar.sh              # levanta (si hace falta) + analiza + informe
#   ./scripts/sonar.sh --informe    # solo el informe, sin volver a analizar
#   ./scripts/sonar.sh --detalle    # informe + lista de hallazgos abiertos
#   ./scripts/sonar.sh --parar      # detiene el servidor (libera ~2.5 GB de RAM)
#
# La contraseña y el token se guardan en .sonar-credenciales (ignorado por git).
set -u

RAIZ=$(cd "$(dirname "$0")/.." && pwd)
CRED="$RAIZ/.sonar-credenciales"
CACHE="${SONAR_CACHE:-$HOME/.cache/sonar-scanner}"
HOST="${SONAR_HOST_URL:-http://localhost:9000}"
CONTENEDOR=sonarqube-tif
PROYECTO=sodimac-servicios-rest

# Contraseña de admin: se puede fijar por entorno la primera vez.
PASS_NUEVA="${SONAR_PASSWORD:-Sonar#Tif2026}"

V=$(printf '\033[32m'); R=$(printf '\033[31m'); A=$(printf '\033[33m')
B=$(printf '\033[1m');  D=$(printf '\033[2m');  N=$(printf '\033[0m')

ok()   { printf '  %s✓%s %s\n' "$V" "$N" "$1"; }
mal()  { printf '  %s✗%s %s\n' "$R" "$N" "$1"; }
info() { printf '  %s%s%s\n' "$D" "$1" "$N"; }
tit()  { printf '\n%s%s%s\n' "$B" "$1" "$N"; }
morir(){ mal "$1"; exit 1; }

# ─────────────────────────────────────────────────── parar
if [ "${1:-}" = "--parar" ]; then
    docker stop "$CONTENEDOR" >/dev/null 2>&1 \
        && ok "SonarQube detenido (revive con: docker start $CONTENEDOR)" \
        || info "No estaba corriendo"
    exit 0
fi

command -v docker >/dev/null 2>&1 || morir "Docker no está disponible"

# ─────────────────────────────────────────────────── servidor
arrancar_servidor() {
    tit "Servidor SonarQube"
    if curl -sf "$HOST/api/system/status" 2>/dev/null | grep -q '"UP"'; then
        ok "Ya estaba operativo en $HOST"
        return 0
    fi

    if docker ps -a --format '{{.Names}}' | grep -qx "$CONTENEDOR"; then
        info "Arrancando contenedor existente..."
        docker start "$CONTENEDOR" >/dev/null 2>&1
    else
        info "Creando el contenedor (la primera vez descarga la imagen)..."
        docker run -d --name "$CONTENEDOR" -p 9000:9000 \
            -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
            sonarqube:community >/dev/null 2>&1 \
            || morir "No pude crear el contenedor"
    fi

    printf '  esperando'
    i=0
    while [ "$i" -lt 60 ]; do
        if curl -sf "$HOST/api/system/status" 2>/dev/null | grep -q '"UP"'; then
            printf '\n'; ok "Operativo tras $((i * 3))s"; return 0
        fi
        printf '.'; sleep 3; i=$((i + 1))
    done
    printf '\n'
    morir "No arrancó en 180s — revisa: docker logs $CONTENEDOR"
}

# ─────────────────────────────────────────────────── credenciales
preparar_credenciales() {
    tit "Credenciales"
    if [ -f "$CRED" ]; then
        # shellcheck disable=SC1090
        . "$CRED"
        if curl -s -u "admin:$SONAR_PASS" "$HOST/api/authentication/validate" \
             2>/dev/null | grep -q '"valid":true'; then
            ok "Reutilizando las guardadas en .sonar-credenciales"
            return 0
        fi
        info "Las guardadas ya no sirven; regenerando"
    fi

    # Primer arranque: SonarQube obliga a cambiar admin/admin
    if curl -s -u admin:admin "$HOST/api/authentication/validate" \
         2>/dev/null | grep -q '"valid":true'; then
        curl -s -u admin:admin -X POST "$HOST/api/users/change_password" \
            -d "login=admin&previousPassword=admin&password=$PASS_NUEVA" >/dev/null 2>&1
        SONAR_PASS="$PASS_NUEVA"
        ok "Contraseña por defecto cambiada"
    else
        SONAR_PASS="$PASS_NUEVA"
    fi

    SONAR_TOKEN=$(curl -s -u "admin:$SONAR_PASS" -X POST \
        "$HOST/api/user_tokens/generate" -d "name=tif-$(date +%s)" \
        | python3 -c 'import json,sys; print(json.load(sys.stdin).get("token",""))' 2>/dev/null)

    [ -n "$SONAR_TOKEN" ] || morir "No pude generar el token — ¿la contraseña de admin es otra? Usa SONAR_PASSWORD=..."

    umask 077
    printf 'SONAR_PASS=%s\nSONAR_TOKEN=%s\n' "$SONAR_PASS" "$SONAR_TOKEN" > "$CRED"
    ok "Token generado y guardado en .sonar-credenciales"
}

# ─────────────────────────────────────────────────── análisis
analizar() {
    tit "Análisis"
    [ -f "$RAIZ/sonar-project.properties" ] \
        || morir "Falta sonar-project.properties en $RAIZ"

    # Los dos montajes NO son opcionales: el scanner escribe su caché y sus
    # temporales en la capa del contenedor, y si la partición raíz está llena
    # falla con "No space left on device" aunque Docker viva en otra partición.
    mkdir -p "$CACHE/dotsonar" "$CACHE/tmp"
    chmod -R 777 "$CACHE" 2>/dev/null

    info "Analizando $PROYECTO ..."
    salida=$(docker run --rm --network host \
        -v "$RAIZ:/usr/src" \
        -v "$CACHE/dotsonar:/opt/sonar-scanner/.sonar" \
        -v "$CACHE/tmp:/tmp" \
        -e SONAR_HOST_URL="$HOST" \
        -e SONAR_TOKEN="$SONAR_TOKEN" \
        sonarsource/sonar-scanner-cli 2>&1)

    if printf '%s' "$salida" | grep -q "EXECUTION SUCCESS"; then
        ok "Análisis completado"
    else
        printf '%s\n' "$salida" | tail -20
        morir "El análisis falló"
    fi
    info "Esperando a que el servidor procese el informe..."
    sleep 10
}

# ─────────────────────────────────────────────────── informe
informe() {
    tit "Resultado"
    curl -s -u "admin:$SONAR_PASS" \
        "$HOST/api/measures/component?component=$PROYECTO&metricKeys=ncloc,bugs,vulnerabilities,code_smells,duplicated_lines_density,sqale_index,reliability_rating,security_rating,sqale_rating" \
        | python3 -c "
import json,sys
d=json.load(sys.stdin)
m={x['metric']:x.get('value') for x in d['component']['measures']}
r={'1.0':'A','2.0':'B','3.0':'C','4.0':'D','5.0':'E'}
print(f\"  Líneas de código   {m.get('ncloc','?')}\")
print(f\"  Bugs               {m.get('bugs','?')}\")
print(f\"  Vulnerabilidades   {m.get('vulnerabilities','?')}\")
print(f\"  Code smells        {m.get('code_smells','?')}\")
print(f\"  Duplicación        {m.get('duplicated_lines_density','?')} %\")
print(f\"  Deuda técnica      {m.get('sqale_index','?')} min\")
print()
print(f\"  Fiabilidad {r.get(m.get('reliability_rating'),'?')}  ·  \"
      f\"Seguridad {r.get(m.get('security_rating'),'?')}  ·  \"
      f\"Mantenibilidad {r.get(m.get('sqale_rating'),'?')}\")
" 2>/dev/null || mal "No pude leer las métricas"

    printf '\n  %sSeveridades (sin resolver)%s\n' "$B" "$N"
    maxima="ninguna"
    for sev in BLOCKER CRITICAL MAJOR MINOR INFO; do
        n=$(curl -s -u "admin:$SONAR_PASS" \
            "$HOST/api/issues/search?components=$PROYECTO&severities=$sev&resolved=false" \
            | python3 -c 'import json,sys; print(json.load(sys.stdin)["total"])' 2>/dev/null)
        n=${n:-0}
        [ "$n" -gt 0 ] && [ "$maxima" = "ninguna" ] && maxima="$sev"
        if [ "$n" -gt 0 ]; then
            printf '    %s%-9s %s%s\n' "$A" "$sev" "$n" "$N"
        else
            printf '    %-9s %s\n' "$sev" "$n"
        fi
    done

    printf '\n'
    case "$maxima" in
        ninguna|MINOR|INFO) ok "Severidad máxima: $maxima — cumple el criterio de calidad" ;;
        MAJOR)              mal "Severidad máxima: MAJOR" ;;
        *)                  mal "Severidad máxima: $maxima" ;;
    esac
    info "Panel: $HOST/dashboard?id=$PROYECTO"
}

detalle() {
    printf '\n  %sHallazgos abiertos%s\n' "$B" "$N"
    curl -s -u "admin:$SONAR_PASS" \
        "$HOST/api/issues/search?components=$PROYECTO&resolved=false&ps=30" \
        | python3 -c "
import json,sys
orden={'BLOCKER':0,'CRITICAL':1,'MAJOR':2,'MINOR':3,'INFO':4}
xs=json.load(sys.stdin)['issues']
if not xs: print('    (ninguno)')
for i in sorted(xs, key=lambda x: orden.get(x['severity'],9)):
    print(f\"    [{i['severity']:<8}] {i['component'].split(':',1)[-1]}:{i.get('line','-')}\")
    print(f\"               {i['message'][:78]}\")
" 2>/dev/null
}

# ─────────────────────────────────────────────────── principal
arrancar_servidor
preparar_credenciales
[ "${1:-}" = "--informe" ] || [ "${1:-}" = "--detalle" ] || analizar
informe
[ "${1:-}" = "--detalle" ] && detalle
printf '\n  %sPara liberar memoria al terminar: ./scripts/sonar.sh --parar%s\n\n' "$D" "$N"
