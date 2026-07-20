"""STUB — Servicio de Distribución (Reabastecimiento). Responsable: Integrante 6a.

Endpoints a implementar (Práctica 4 §5.1):
    POST /api/distribucion/pedidos    → generar pedido de reabastecimiento
    POST /api/distribucion/picking    → preparar picking
    POST /api/distribucion/packing    → preparar packing
    POST /api/distribucion/despachos  → programar despacho
    PUT  /api/distribucion/<id>/estado→ actualizar estado de envío
    PUT  /api/distribucion/<id>/llegada→ registrar llegada a tienda
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_distribucion", __name__, url_prefix="/api/distribucion")

_SVC = "Distribución"
_INT = "Integrante 6"


@bp.post("/pedidos")
def generar_pedido():
    return no_implementado(_SVC, _INT)


@bp.post("/picking")
def preparar_picking():
    return no_implementado(_SVC, _INT)


@bp.post("/packing")
def preparar_packing():
    return no_implementado(_SVC, _INT)


@bp.post("/despachos")
def programar_despacho():
    return no_implementado(_SVC, _INT)


@bp.put("/<envio_id>/estado")
def actualizar_estado(envio_id: str):
    return no_implementado(_SVC, _INT)


@bp.put("/<envio_id>/llegada")
def registrar_llegada(envio_id: str):
    return no_implementado(_SVC, _INT)
