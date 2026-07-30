"""Servicio de Órdenes de Compra (Reabastecimiento)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.ordenes_compra_servicio import OrdenCompraServicio

bp = Blueprint("reabastecimiento_ordenes_compra", __name__, url_prefix="/api/ordenes-compra")

_servicio = OrdenCompraServicio


def _serializar_linea(linea: dict) -> dict:
    return {
        "sku": linea["sku"],
        "cantidad": linea["cantidad"],
        "precioUnitario": linea["precio_unitario"],
        "subtotal": linea["cantidad"] * linea["precio_unitario"],
    }


def _serializar(orden) -> dict:
    return {
        "id": orden.id,
        "proveedorId": orden.proveedor_id,
        "estado": orden.estado.value,
        "total": orden.total,
        "lineas": [_serializar_linea({
            "sku": linea.sku,
            "cantidad": linea.cantidad,
            "precio_unitario": linea.precio_unitario,
        }) for linea in orden.lineas],
    }


@bp.post("")
def generar():
    datos = request.get_json(silent=True) or {}
    lineas = [
        {
            "sku": item.get("sku", ""),
            "cantidad": int(item.get("cantidad", 0)),
            "precio_unitario": float(item.get("precioUnitario", item.get("precio_unitario", 0))),
        }
        for item in datos.get("lineas", [])
    ]
    orden = _servicio().crear_orden_compra(
        proveedor_id=datos.get("proveedorId", ""),
        lineas=lineas,
    )
    return jsonify(_serializar(orden)), 201


@bp.get("/<orden_id>")
def consultar(orden_id: str):
    orden = _servicio().obtener_orden_compra(orden_id)
    return jsonify(_serializar(orden)), 200


@bp.put("/<orden_id>/autorizar")
def autorizar(orden_id: str):
    orden = _servicio().autorizar_orden_compra(orden_id)
    return jsonify(_serializar(orden)), 200


@bp.delete("/<orden_id>")
def cancelar(orden_id: str):
    orden = _servicio().cancelar_orden_compra(orden_id)
    return jsonify(_serializar(orden)), 200


@bp.post("/<orden_id>/enviar")
def enviar(orden_id: str):
    orden = _servicio().enviar_orden_compra(orden_id)
    return jsonify(_serializar(orden)), 200
