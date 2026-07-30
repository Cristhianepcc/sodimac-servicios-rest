from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.almacen_servicio import AlmacenServicio
from src.reabastecimiento.domain.almacen import MercaderiaUbicada, Ubicacion
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_almacen", __name__, url_prefix="/api/almacenes")
proteger_api_bp(bp, "ALMACENERO")


def _serializar_ubicacion(u: Ubicacion) -> dict:
    return {"codigo": u.codigo, "pasillo": u.pasillo, "estante": u.estante, "nivel": u.nivel}


def _serializar_mercaderia(m: MercaderiaUbicada) -> dict:
    return {
        "id": m.id, "sku": m.sku, "ubicacionCodigo": m.ubicacion_codigo,
        "cantidad": m.cantidad, "fechaUbicacion": m.fecha_ubicacion,
    }


def _normalizar_payload_ubicacion(d: dict) -> dict:
    cantidad = d.get("cantidad", 0)
    if cantidad is None:
        cantidad = 0
    cantidad = int(cantidad)
    return {
        "codigo": d.get("codigo", ""),
        "pasillo": d.get("pasillo") or d.get("zona", ""),
        "estante": d.get("estante") or d.get("sku", ""),
        "nivel": d.get("nivel") or str(cantidad),
        "zona": d.get("zona") or d.get("pasillo", ""),
        "sku": d.get("sku", ""),
        "cantidad": cantidad,
    }


@bp.post("/ubicaciones")
def registrar_ubicacion():
    d = request.get_json(silent=True) or {}
    payload = _normalizar_payload_ubicacion(d)
    u = AlmacenServicio().registrar_ubicacion(
        codigo=payload["codigo"],
        pasillo=payload["pasillo"],
        estante=payload["estante"],
        nivel=payload["nivel"],
        sku=payload["sku"],
        cantidad=payload["cantidad"],
    )
    response = _serializar_ubicacion(u)
    response.update({"zona": payload["zona"], "sku": payload["sku"], "cantidad": payload["cantidad"]})
    return jsonify(response), 201


@bp.get("/ubicaciones")
def listar_ubicaciones():
    return jsonify([_serializar_ubicacion(u) for u in AlmacenServicio().listar_ubicaciones()]), 200


@bp.get("/ubicaciones/<codigo>")
def consultar_ubicacion(codigo: str):
    return jsonify(_serializar_ubicacion(AlmacenServicio().consultar_ubicacion_o_sku(codigo))), 200


@bp.post("/mercaderia")
def ubicar_mercaderia():
    d = request.get_json(silent=True) or {}
    m = AlmacenServicio().ubicar_mercaderia(
        sku=d.get("sku", ""),
        ubicacion_codigo=d.get("ubicacionCodigo", ""),
        cantidad=int(d.get("cantidad", 0)),
    )
    return jsonify(_serializar_mercaderia(m)), 201


@bp.get("/mercaderia")
def listar_mercaderia():
    return jsonify([_serializar_mercaderia(m) for m in AlmacenServicio().listar_toda_mercaderia()]), 200


@bp.get("/mercaderia/<sku>")
def consultar_por_sku(sku: str):
    return jsonify([_serializar_mercaderia(m) for m in AlmacenServicio().consultar_por_sku(sku)]), 200


@bp.put("/inventario")
def actualizar_inventario_cd():
    d = request.get_json(silent=True) or {}
    sku = d.get("sku", "")
    ubicacion_codigo = d.get("ubicacionCodigo") or d.get("codigo", "")
    stock = d.get("stock", d.get("cantidad", 0))
    AlmacenServicio().actualizar_inventario_cd(
        sku=sku,
        ubicacion_codigo=ubicacion_codigo,
        cantidad=int(stock),
    )
    return jsonify({"sku": sku, "stock": int(stock), "ubicacionCodigo": ubicacion_codigo}), 200
