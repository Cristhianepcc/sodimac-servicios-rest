# Calidad de código — análisis SonarQube

Criterio 8 de la rúbrica del proyecto: *"Código presenta Code Smells, Bugs o
Vulnerabilidades cuya severidad máxima es Minor o Info (2 puntos)"*.

## Resultado actual

| Métrica | Valor |
| --- | --- |
| Líneas de código | 2 010 |
| Bugs | **0** |
| Vulnerabilidades | **0** |
| Code smells | **0** |
| Duplicación | **0.0 %** |
| Deuda técnica | **0 min** |
| Fiabilidad · Seguridad · Mantenibilidad | **A · A · A** |

Sin issues abiertos en ninguna severidad (Blocker, Critical, Major, Minor, Info).

## Cómo reproducir el análisis

```bash
# 1) Servidor SonarQube
docker run -d --name sonarqube-tif -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true sonarqube:community

# esperar a que responda UP
curl -s http://localhost:9000/api/system/status

# 2) Cambiar la contraseña por defecto y generar un token en
#    http://localhost:9000  (admin/admin)

# 3) Analizar
docker run --rm --network host \
  -v "$PWD:/usr/src" \
  -v "$HOME/.cache/sonar-scanner/dotsonar:/opt/sonar-scanner/.sonar" \
  -v "$HOME/.cache/sonar-scanner/tmp:/tmp" \
  -e SONAR_HOST_URL="http://localhost:9000" \
  -e SONAR_TOKEN="<token>" \
  sonarsource/sonar-scanner-cli
```

La configuración está en [`sonar-project.properties`](../sonar-project.properties).

> **Los dos montajes de volumen no son opcionales** si la partición raíz del equipo
> está llena: el scanner escribe su caché y sus temporales en la capa de escritura del
> contenedor y falla con `No space left on device` aunque Docker tenga su almacén en
> otra partición.

## Qué se corrigió

El primer análisis dio **6 Critical, 2 Major y 2 Minor** (0.5 puntos según la rúbrica).

| Severidad | Hallazgo | Corrección |
| --- | --- | --- |
| Critical | `"application/json"` duplicado 5 veces | Constante `_JSON` |
| Critical | `"#/components/schemas/Error"` duplicado 3 veces | Constante `_REF_ERROR` |
| Critical | `construir_spec()` con complejidad cognitiva 16 (máx. 15) | Extraídas `_construir_paths()`, `_operacion()`, `_es_documentable()`, `_metodos_de()` |
| Critical | `"all, delete-orphan"` duplicado 4 veces | Constante `_CASCADA_COMPOSICION` |
| Critical | `"rse_iniciativa.codigo"` duplicado 4 veces | Constante `_FK_INICIATIVA` |
| Major | Parámetro `comentario` sin usar en `IniciativaRSE.evaluar()` | **Se persiste** en `comentario_evaluacion` (ver abajo) |
| Major | `pytest.raises(Exception)` demasiado genérico | `FrozenInstanceError` |
| Minor | `except (ValueError, UnicodeDecodeError)` redundante | `UnicodeDecodeError` ya deriva de `ValueError` |
| Minor | Variable local `SessionLocal` fuera de convención | Renombrada a `fabrica_sesion` |

### El caso del `comentario`

No era un parámetro sobrante: viajaba desde el controlador
(`d.get("comentario")`) a través del servicio de aplicación hasta
`IniciativaRSE.evaluar()`, donde **se descartaba en silencio**. La justificación que
escribía el comité al aprobar o rechazar una iniciativa —un campo real del contrato
`teval` del proceso BPM— se perdía en cada evaluación.

La corrección no fue borrar el parámetro sino **persistirlo**: nuevo campo
`comentario_evaluacion` en el agregado, columna en el ORM, mapeo en el repositorio
SQLAlchemy y exposición como `comentarioEvaluacion` en la respuesta REST. Dos pruebas
nuevas cubren el caso aprobado y el rechazado.

## Advertencia sobre el hallazgo de CSRF

Queda un hallazgo marcado como **aceptado** (no corregido en código):

> `src/__init__.py` — *Make sure disabling CSRF protection is safe here* (`python:S4502`)

Es un **falso positivo**. Esta es una API REST sin estado: no emite cookies de sesión ni
usa autenticación basada en cookies, así que no existe la credencial ambiental que un
ataque CSRF explota. Sus clientes son los conectores de Bonita y el worker de eventos,
no un navegador. Añadir `CSRFProtect` rompería esos clientes sin aportar seguridad.

El razonamiento está también como comentario en `src/__init__.py`, junto al código.

> ⚠️ **La marca de "aceptado" vive en el servidor SonarQube, no en el repositorio.** Si
> se analiza el proyecto en una instancia nueva, este hallazgo reaparecerá como 1
> Critical. Hay que volver a revisarlo y aceptarlo, o justificarlo en la sustentación.
> Si en el futuro se añade login por cookie, deja de ser un falso positivo.
