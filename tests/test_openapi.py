"""Pruebas de la documentación OpenAPI 3.

Protegen el entregable: que la especificación exista, sea estructuralmente
válida y cubra **todas** las rutas de la API (no solo las de un integrante).
"""
from __future__ import annotations

import json
import re

import pytest

from src import create_app
from src.shared.openapi import CONTEXTOS, construir_spec

METODOS_HTTP = {"get", "post", "put", "patch", "delete"}


@pytest.fixture(scope="module")
def app():
    return create_app()


@pytest.fixture(scope="module")
def spec(app) -> dict:
    return construir_spec(app)


@pytest.fixture(scope="module")
def operaciones(spec) -> list[tuple[str, str, dict]]:
    return [
        (ruta, metodo, op)
        for ruta, item in spec["paths"].items()
        for metodo, op in item.items()
    ]


def test_version_y_metadatos(spec):
    assert spec["openapi"] == "3.0.3"
    assert spec["info"]["title"]
    assert spec["info"]["version"]


def test_hay_operaciones_documentadas(operaciones):
    assert len(operaciones) > 40


def test_cubre_todas_las_rutas_de_flask(app, spec):
    """Ninguna ruta registrada puede quedar fuera de la especificación."""
    esperadas = {
        re.sub(r"<(?:[a-zA-Z_]+(?:\([^)]*\))?:)?([a-zA-Z_]\w*)>", r"{\1}", r.rule)
        for r in app.url_map.iter_rules()
        if r.endpoint != "static"
    } - {"/openapi.json", "/docs"}

    assert esperadas == set(spec["paths"]), (
        f"faltan en la spec: {esperadas - set(spec['paths'])}"
    )


def test_toda_operacion_tiene_resumen_y_etiqueta(operaciones):
    for ruta, metodo, op in operaciones:
        assert op.get("summary"), f"{metodo.upper()} {ruta} sin summary"
        assert op.get("tags"), f"{metodo.upper()} {ruta} sin tag"


def test_las_etiquetas_son_bounded_contexts(operaciones):
    validas = set(CONTEXTOS.values()) | {"General"}
    for ruta, metodo, op in operaciones:
        assert op["tags"][0] in validas, f"{metodo.upper()} {ruta}: tag desconocido"


def test_operation_ids_unicos(operaciones):
    ids = [op["operationId"] for _, _, op in operaciones]
    assert len(ids) == len(set(ids))


def test_parametros_de_ruta_declarados(operaciones):
    """Cada `{param}` de la ruta debe estar declarado como parámetro."""
    for ruta, metodo, op in operaciones:
        en_ruta = set(re.findall(r"\{(\w+)\}", ruta))
        declarados = {
            p["name"] for p in op.get("parameters", []) if p["in"] == "path"
        }
        assert en_ruta == declarados, f"{metodo.upper()} {ruta}: {en_ruta} vs {declarados}"


def test_metodos_de_escritura_declaran_cuerpo(operaciones):
    for ruta, metodo, op in operaciones:
        if metodo in ("post", "put", "patch"):
            assert "requestBody" in op, f"{metodo.upper()} {ruta} sin requestBody"


def test_no_hay_referencias_rotas(spec):
    componentes = spec["components"]
    for seccion, nombre in re.findall(
        r'"\$ref":\s*"#/components/(\w+)/(\w+)"', json.dumps(spec)
    ):
        assert nombre in componentes.get(seccion, {}), f"$ref roto: {seccion}/{nombre}"


# --- Endpoints publicados ---

def test_openapi_json_se_sirve(app):
    respuesta = app.test_client().get("/openapi.json")
    assert respuesta.status_code == 200
    assert respuesta.get_json()["openapi"] == "3.0.3"


def test_swagger_ui_se_sirve(app):
    respuesta = app.test_client().get("/docs")
    assert respuesta.status_code == 200
    assert b"swagger-ui" in respuesta.data


def test_la_spec_no_se_documenta_a_si_misma(spec):
    assert "/openapi.json" not in spec["paths"]
    assert "/docs" not in spec["paths"]
