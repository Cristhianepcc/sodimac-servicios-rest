"""Controlador REST del proceso `ventas` (Servicio Web).

Expone el `bp` (Blueprint) que el application factory autoregistra.
Endpoints de referencia:
    POST /api/ventas/carrito        → crear carrito/cotización
    GET  /api/ventas/carrito/<id>   → consultar carrito
    GET  /api/ventas/carrito        → listar carritos
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.ventas.application.carrito_servicio import CarritoServicio
from src.ventas.domain.modelo import Carrito

bp = Blueprint("ventas_carrito", __name__, url_prefix="/api/ventas")

_servicio = CarritoServicio


def _serializar(carrito: Carrito) -> dict:
    return {
        "id": carrito.id,
        "cliente": carrito.cliente,
        "estado": carrito.estado.value,
        "items": [
            {
                "sku": i.sku,
                "cantidad": i.cantidad,
                "precioUnitario": i.precio_unitario,
                "subtotal": i.subtotal,
            }
            for i in carrito.items
        ],
        "total": carrito.total,
    }


@bp.post("/carrito")
def crear_carrito():
    datos = request.get_json(silent=True) or {}
    carrito = _servicio().crear(
        cliente=datos.get("cliente", ""),
        items=datos.get("items", []),
    )
    return jsonify(_serializar(carrito)), 201


@bp.get("/carrito/<carrito_id>")
def obtener_carrito(carrito_id: str):
    carrito = _servicio().obtener(carrito_id)
    return jsonify(_serializar(carrito)), 200


@bp.get("/carrito")
def listar_carritos():
    carritos = _servicio().listar()
    return jsonify([_serializar(c) for c in carritos]), 200
