from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.almacen_servicio import AlmacenServicio
from src.reabastecimiento.domain.almacen import MercaderiaUbicada, Ubicacion

bp = Blueprint("reabastecimiento_almacen", __name__, url_prefix="/api/almacenes")


def _serializar_ubicacion(u: Ubicacion) -> dict:
    return {"codigo": u.codigo, "pasillo": u.pasillo, "estante": u.estante, "nivel": u.nivel}


def _serializar_mercaderia(m: MercaderiaUbicada) -> dict:
    return {
        "id": m.id, "sku": m.sku, "ubicacionCodigo": m.ubicacion_codigo,
        "cantidad": m.cantidad, "fechaUbicacion": m.fecha_ubicacion,
    }


@bp.post("/ubicaciones")
def registrar_ubicacion():
    d = request.get_json(silent=True) or {}
    u = AlmacenServicio().registrar_ubicacion(
        codigo=d.get("codigo", ""),
        pasillo=d.get("pasillo", ""),
        estante=d.get("estante", ""),
        nivel=d.get("nivel", ""),
    )
    return jsonify(_serializar_ubicacion(u)), 201


@bp.get("/ubicaciones")
def listar_ubicaciones():
    return jsonify([_serializar_ubicacion(u) for u in AlmacenServicio().listar_ubicaciones()]), 200


@bp.get("/ubicaciones/<codigo>")
def consultar_ubicacion(codigo: str):
    return jsonify(_serializar_ubicacion(AlmacenServicio().consultar_ubicacion(codigo))), 200


@bp.post("/mercaderia")
def ubicar_mercaderia():
    d = request.get_json(silent=True) or {}
    m = AlmacenServicio().ubicar_mercaderia(
        sku=d.get("sku", ""),
        ubicacion_codigo=d.get("ubicacionCodigo", ""),
        cantidad=int(d.get("cantidad", 0)),
    )
    return jsonify(_serializar_mercaderia(m)), 201


@bp.get("/mercaderia/<sku>")
def consultar_por_sku(sku: str):
    return jsonify([_serializar_mercaderia(m) for m in AlmacenServicio().consultar_por_sku(sku)]), 200


@bp.put("/inventario")
def actualizar_inventario_cd():
    d = request.get_json(silent=True) or {}
    r = AlmacenServicio().actualizar_inventario_cd(
        sku=d.get("sku", ""),
        ubicacion_codigo=d.get("ubicacionCodigo", ""),
        cantidad=int(d.get("cantidad", 0)),
    )
    return jsonify(r), 200
