"""STUB — Servicio de Almacén (Reabastecimiento). Responsable: Integrante 5a.

Endpoints a implementar (Práctica 4 §5.1):
    POST /api/almacenes/ubicaciones       → registrar ubicación
    POST /api/almacenes/mercaderia        → ubicar mercadería
    GET  /api/almacenes/ubicaciones/<sku> → consultar ubicación
    PUT  /api/almacenes/inventario        → actualizar inventario en CD
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_almacen", __name__, url_prefix="/api/almacenes")

_SVC = "Almacén"
_INT = "Integrante 5"


@bp.post("/ubicaciones")
def registrar_ubicacion():
    return no_implementado(_SVC, _INT)


@bp.post("/mercaderia")
def ubicar_mercaderia():
    return no_implementado(_SVC, _INT)


@bp.get("/ubicaciones/<sku>")
def consultar_ubicacion(sku: str):
    return no_implementado(_SVC, _INT)


@bp.put("/inventario")
def actualizar_inventario_cd():
    return no_implementado(_SVC, _INT)
