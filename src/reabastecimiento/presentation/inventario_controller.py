"""Controlador REST del servicio de Inventario (referencia de `reabastecimiento`).

    POST /api/inventario              → registrar producto
    GET  /api/inventario/bajo-stock   → listar productos con bajo stock
    GET  /api/inventario/<sku>        → consultar stock
    PUT  /api/inventario/<sku>        → actualizar stock
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.inventario_servicio import InventarioServicio
from src.reabastecimiento.domain.inventario import ProductoInventario
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_inventario", __name__, url_prefix="/api/inventario")
proteger_api_bp(bp, "ALMACENERO")


def _serializar(p: ProductoInventario) -> dict:
    return {
        "sku": p.sku,
        "nombre": p.nombre,
        "stock": p.stock,
        "stockMinimo": p.stock_minimo,
        "bajoStock": p.bajo_stock,
    }


@bp.post("")
def registrar_producto():
    d = request.get_json(silent=True) or {}
    p = InventarioServicio().registrar_producto(
        sku=d.get("sku", ""),
        nombre=d.get("nombre", ""),
        stock=int(d.get("stock", 0)),
        stock_minimo=int(d.get("stockMinimo", 0)),
    )
    return jsonify(_serializar(p)), 201


@bp.get("/bajo-stock")
def listar_bajo_stock():
    productos = InventarioServicio().listar_bajo_stock()
    return jsonify([_serializar(p) for p in productos]), 200


@bp.get("/<sku>")
def consultar_stock(sku: str):
    return jsonify(_serializar(InventarioServicio().consultar_stock(sku))), 200


@bp.put("/<sku>")
def actualizar_stock(sku: str):
    d = request.get_json(silent=True) or {}
    p = InventarioServicio().actualizar_stock(sku, int(d.get("stock", 0)))
    return jsonify(_serializar(p)), 200
