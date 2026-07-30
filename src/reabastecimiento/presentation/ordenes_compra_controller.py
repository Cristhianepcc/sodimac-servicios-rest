from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.orden_compra_servicio import OrdenCompraServicio
from src.reabastecimiento.domain.orden_compra import OrdenCompra
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_ordenes_compra", __name__, url_prefix="/api/ordenes-compra")
proteger_api_bp(bp, "ALMACENERO")


def _serializar(o: OrdenCompra) -> dict:
    return {
        "id": o.id,
        "proveedorId": o.proveedor_id,
        "fechaEmision": o.fecha_emision,
        "estado": o.estado.value,
        "lineas": [
            {"sku": l.sku, "cantidad": l.cantidad, "precioUnitario": l.precio_unitario, "subtotal": l.subtotal}
            for l in o.lineas
        ],
        "total": o.total,
    }


@bp.post("")
def generar():
    d = request.get_json(silent=True) or {}
    o = OrdenCompraServicio().generar(
        proveedor_id=d.get("proveedorId", ""),
        lineas=d.get("lineas", []),
    )
    return jsonify(_serializar(o)), 201


@bp.get("/<orden_id>")
def consultar(orden_id: str):
    return jsonify(_serializar(OrdenCompraServicio().obtener(orden_id))), 200


@bp.get("")
def listar():
    return jsonify([_serializar(o) for o in OrdenCompraServicio().listar()]), 200


@bp.put("/<orden_id>/autorizar")
def autorizar(orden_id: str):
    return jsonify(_serializar(OrdenCompraServicio().autorizar(orden_id))), 200


@bp.delete("/<orden_id>")
def cancelar(orden_id: str):
    return jsonify(_serializar(OrdenCompraServicio().cancelar(orden_id))), 200


@bp.post("/<orden_id>/enviar")
def enviar(orden_id: str):
    return jsonify(_serializar(OrdenCompraServicio().enviar(orden_id))), 200
