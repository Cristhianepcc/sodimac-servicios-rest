"""STUB — Servicio de Proveedores (Reabastecimiento). Responsable: Integrante 2.

Endpoints a implementar (Práctica 4 §5.1):
    GET  /api/proveedores              → listar proveedores
    GET  /api/proveedores/<id>         → consultar proveedor
    POST /api/proveedores/<id>/evaluar → evaluar proveedor
    PUT  /api/proveedores/<id>/aprobar → aprobar proveedor
    PUT  /api/proveedores/<id>/rechazar→ rechazar proveedor

Reemplazar los `no_implementado(...)` por la implementación real siguiendo el
patrón del servicio de referencia `inventario` (dominio → aplicación → infra).
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_proveedores", __name__, url_prefix="/api/proveedores")

_SVC = "Proveedores"
_INT = "Integrante 2"


@bp.get("")
def listar():
    return no_implementado(_SVC, _INT)


@bp.get("/<proveedor_id>")
def consultar(proveedor_id: str):
    return no_implementado(_SVC, _INT)


@bp.post("/<proveedor_id>/evaluar")
def evaluar(proveedor_id: str):
    return no_implementado(_SVC, _INT)


@bp.put("/<proveedor_id>/aprobar")
def aprobar(proveedor_id: str):
    return no_implementado(_SVC, _INT)


@bp.put("/<proveedor_id>/rechazar")
def rechazar(proveedor_id: str):
    return no_implementado(_SVC, _INT)
