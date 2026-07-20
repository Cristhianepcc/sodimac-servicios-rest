"""STUB — Servicio de Órdenes de Compra (Reabastecimiento). Responsable: Integrante 3.

Endpoints a implementar (Práctica 4 §5.1):
    POST   /api/ordenes-compra                → generar orden de compra
    GET    /api/ordenes-compra/<id>           → consultar orden
    PUT    /api/ordenes-compra/<id>/autorizar → autorizar orden
    DELETE /api/ordenes-compra/<id>           → cancelar orden
    POST   /api/ordenes-compra/<id>/enviar    → enviar orden al proveedor
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_ordenes_compra", __name__, url_prefix="/api/ordenes-compra")

_SVC = "Órdenes de Compra"
_INT = "Integrante 3"


@bp.post("")
def generar():
    return no_implementado(_SVC, _INT)


@bp.get("/<orden_id>")
def consultar(orden_id: str):
    return no_implementado(_SVC, _INT)


@bp.put("/<orden_id>/autorizar")
def autorizar(orden_id: str):
    return no_implementado(_SVC, _INT)


@bp.delete("/<orden_id>")
def cancelar(orden_id: str):
    return no_implementado(_SVC, _INT)


@bp.post("/<orden_id>/enviar")
def enviar(orden_id: str):
    return no_implementado(_SVC, _INT)
