"""Controlador REST del servicio de Almacén (Reabastecimiento)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.almacen_servicio import AlmacenServicio
from src.reabastecimiento.domain.ubicacion import Ubicacion

bp = Blueprint("reabastecimiento_almacen", __name__, url_prefix="/api/almacenes")


def _serializar(ubicacion: Ubicacion) -> dict:
    return {
        "codigo": ubicacion.codigo,
        "zona": ubicacion.zona,
        "sku": ubicacion.sku,
        "cantidad": ubicacion.cantidad,
        "stock": ubicacion.cantidad,
    }


@bp.post("/ubicaciones")
def registrar_ubicacion():
    datos = request.get_json(silent=True) or {}
    ubicacion = AlmacenServicio().registrar_ubicacion(
        codigo=datos.get("codigo", ""),
        zona=datos.get("zona", ""),
        sku=datos.get("sku", ""),
        cantidad=int(datos.get("cantidad", 0)),
    )
    return jsonify(_serializar(ubicacion)), 201


@bp.post("/mercaderia")
def ubicar_mercaderia():
    datos = request.get_json(silent=True) or {}
    ubicacion = AlmacenServicio().ubicar_mercaderia(
        codigo=datos.get("codigo", ""),
        zona=datos.get("zona", ""),
        sku=datos.get("sku", ""),
        cantidad=int(datos.get("cantidad", 0)),
    )
    return jsonify(_serializar(ubicacion)), 200


@bp.get("/ubicaciones/<sku>")
def consultar_ubicacion(sku: str):
    ubicacion = AlmacenServicio().consultar_ubicacion(sku)
    return jsonify(_serializar(ubicacion)), 200


@bp.put("/inventario")
def actualizar_inventario_cd():
    datos = request.get_json(silent=True) or {}
    ubicacion = AlmacenServicio().actualizar_inventario(
        sku=datos.get("sku", ""),
        stock=int(datos.get("stock", 0)),
    )
    return jsonify(_serializar(ubicacion)), 200
