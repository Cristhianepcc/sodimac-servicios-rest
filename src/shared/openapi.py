"""Documentación OpenAPI 3 + Swagger UI de la API.

La especificación se **deriva del `url_map` de Flask**, no de un archivo YAML
mantenido a mano: con 5 bounded contexts y decenas de operaciones, un documento
paralelo se desincroniza al primer merge. Aquí la fuente de verdad es el código.

Cada operación se enriquece con:
  - `tags`   → el bounded context (proceso de negocio) del blueprint,
  - `summary`→ la primera línea del docstring de la vista,
  - parámetros de ruta inferidos de los convertidores de la regla.

Endpoints publicados:
    GET /openapi.json  → especificación cruda (formato estándar OpenAPI 3.0.3)
    GET /docs          → Swagger UI
"""
from __future__ import annotations

import re
from typing import Any

from flask import Flask, jsonify, render_template_string

#: Blueprint (prefijo) → proceso de negocio al que pertenece.
CONTEXTOS = {
    "ventas": "Venta y Atención al Cliente (Omnicanal)",
    "reabastecimiento": "Cadena de Suministro y Reabastecimiento",
    "servicios_cliente": "Servicios al Cliente (Instalaciones)",
    "postventa": "Postventa y Experiencia",
    "rse": "RSE y Sostenibilidad",
}

#: Convertidores de Flask → tipos de OpenAPI.
_TIPOS = {
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "string": {"type": "string"},
    "path": {"type": "string"},
    "uuid": {"type": "string", "format": "uuid"},
    "default": {"type": "string"},
}

_JSON = "application/json"
_REF_ERROR = "#/components/schemas/Error"
_ESQUEMA_OBJETO = {"type": "object"}

_METODOS = ("get", "post", "put", "patch", "delete")
_RUTAS_EXCLUIDAS = {"/openapi.json", "/docs"}

_PARAM = re.compile(r"<(?:(?P<conv>[a-zA-Z_]+)(?:\([^)]*\))?:)?(?P<nombre>[a-zA-Z_][\w]*)>")


def _a_ruta_openapi(regla: str) -> str:
    """`/api/iniciativas/<codigo>` → `/api/iniciativas/{codigo}`."""
    return _PARAM.sub(lambda m: "{" + m.group("nombre") + "}", regla)


def _parametros(regla) -> list[dict[str, Any]]:
    params = []
    for m in _PARAM.finditer(regla.rule):
        nombre = m.group("nombre")
        conv = m.group("conv") or "default"
        params.append(
            {
                "name": nombre,
                "in": "path",
                "required": True,
                "schema": _TIPOS.get(conv, _TIPOS["default"]),
                "description": f"Identificador '{nombre}' del recurso.",
            }
        )
    return params


def _contexto_de(regla) -> str:
    """Deduce el proceso de negocio a partir del nombre del blueprint."""
    endpoint = regla.endpoint or ""
    prefijo = endpoint.split(".")[0]
    for clave, etiqueta in CONTEXTOS.items():
        if prefijo.startswith(clave):
            return etiqueta
    return "General"


def _resumen(vista) -> str:
    """Primera línea del docstring; si no hay, humaniza el nombre de la vista.

    El fallback evita que la documentación quede muda cuando un integrante
    añade un endpoint sin docstring, que es lo habitual en un equipo grande.
    """
    if vista is None:
        return ""

    doc = (vista.__doc__ or "").strip()
    if doc:
        return doc.splitlines()[0].strip()

    nombre = getattr(vista, "__name__", "").strip("_")
    if not nombre:
        return ""
    return nombre.replace("_", " ").capitalize()


def _respuestas(metodo: str, tiene_params: bool) -> dict[str, Any]:
    exito = "201" if metodo == "post" else "200"
    resp: dict[str, Any] = {
        exito: {
            "description": "Operación exitosa.",
            "content": {_JSON: {"schema": _ESQUEMA_OBJETO}},
        },
        "400": {"$ref": "#/components/responses/ErrorDominio"},
    }
    if tiene_params:
        resp["404"] = {"$ref": "#/components/responses/NoEncontrado"}
    if metodo in ("post", "put", "patch"):
        resp["409"] = {"$ref": "#/components/responses/Conflicto"}
    return resp


def _operacion(regla, vista, metodo: str, params: list[dict[str, Any]]) -> dict[str, Any]:
    """Arma el objeto Operation de OpenAPI para un método de una ruta."""
    operacion: dict[str, Any] = {
        "tags": [_contexto_de(regla)],
        "operationId": f"{metodo}_{regla.endpoint}".replace(".", "_"),
        "responses": _respuestas(metodo, bool(params)),
    }
    if resumen := _resumen(vista):
        operacion["summary"] = resumen
    if params:
        operacion["parameters"] = params
    if metodo in ("post", "put", "patch"):
        operacion["requestBody"] = {
            "required": True,
            "content": {_JSON: {"schema": _ESQUEMA_OBJETO}},
        }
    return operacion


def _es_documentable(regla, ruta: str) -> bool:
    return regla.endpoint != "static" and ruta not in _RUTAS_EXCLUIDAS


def _metodos_de(regla) -> list[str]:
    return sorted(
        m.lower() for m in (regla.methods or set()) if m.lower() in _METODOS
    )


def _construir_paths(app: Flask) -> dict[str, dict[str, Any]]:
    """Recorre el url_map y produce el objeto `paths` de la especificación."""
    paths: dict[str, dict[str, Any]] = {}

    for regla in app.url_map.iter_rules():
        ruta = _a_ruta_openapi(regla.rule)
        if not _es_documentable(regla, ruta):
            continue

        vista = app.view_functions.get(regla.endpoint)
        params = _parametros(regla)

        for metodo in _metodos_de(regla):
            paths.setdefault(ruta, {})[metodo] = _operacion(regla, vista, metodo, params)

    return paths


def construir_spec(app: Flask) -> dict[str, Any]:
    """Genera el documento OpenAPI 3.0.3 a partir de las rutas registradas."""
    paths = _construir_paths(app)

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Sodimac — Servicios Web del Negocio",
            "version": "1.0.0",
            "description": (
                "Servicios REST que dan soporte a las tareas automáticas de los "
                "procesos de negocio modelados en Bonita (BPMN). Arquitectura por "
                "capas con Domain-driven Design; integración asíncrona con los "
                "procesos vía RabbitMQ.\n\n"
                "**Colas de integración:** `rse.convocatorias` y `rse.postulaciones` "
                "(entrada, publicadas por Bonita) y `rse.notificaciones` (salida, "
                "consumida por Bonita)."
            ),
        },
        "servers": [{"url": "/", "description": "Servidor local"}],
        "tags": [
            {"name": etiqueta, "description": f"Servicios del proceso «{etiqueta}»."}
            for etiqueta in CONTEXTOS.values()
        ],
        "paths": dict(sorted(paths.items())),
        "components": {
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {"error": {"type": "string"}},
                    "required": ["error"],
                },
                "EventoIntegracion": {
                    "type": "object",
                    "description": "Sobre de los mensajes intercambiados con Bonita.",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "tipo": {"type": "string", "example": "rse.postulacion.aceptada"},
                        "ocurridoEn": {"type": "string", "format": "date-time"},
                        "origen": {"type": "string", "example": "sodimac-api"},
                        "datos": {"type": "object"},
                    },
                    "required": ["id", "tipo", "ocurridoEn", "datos"],
                },
            },
            "responses": {
                "ErrorDominio": {
                    "description": "Violación de una regla de negocio.",
                    "content": {
                        _JSON: {"schema": {"$ref": _REF_ERROR}}
                    },
                },
                "NoEncontrado": {
                    "description": "El recurso solicitado no existe.",
                    "content": {
                        _JSON: {"schema": {"$ref": _REF_ERROR}}
                    },
                },
                "Conflicto": {
                    "description": "Conflicto de estado del recurso.",
                    "content": {
                        _JSON: {"schema": {"$ref": _REF_ERROR}}
                    },
                },
            },
        },
    }


_SWAGGER_UI = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sodimac — Servicios Web | Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => SwaggerUIBundle({
      url: "{{ url_spec }}",
      dom_id: "#swagger-ui",
      docExpansion: "list",
      defaultModelsExpandDepth: 1
    });
  </script>
</body>
</html>"""


def registrar_openapi(app: Flask) -> None:
    """Publica `/openapi.json` y la interfaz Swagger en `/docs`."""

    @app.get("/openapi.json")
    def openapi_json():
        """Especificación OpenAPI 3.0.3 de la API."""
        return jsonify(construir_spec(app))

    @app.get("/docs")
    def swagger_ui():
        """Interfaz Swagger UI para explorar y probar la API."""
        return render_template_string(_SWAGGER_UI, url_spec="/openapi.json")
