from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.distribucion_servicio import DistribucionServicio
from src.reabastecimiento.domain.distribucion import Envio, PedidoDistribucion
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_distribucion", __name__, url_prefix="/api/distribucion")
proteger_api_bp(bp, "ALMACENERO")


def _serializar_pedido(p: PedidoDistribucion) -> dict:
    return {
        "id": p.id,
        "tiendaDestino": p.tienda_destino,
        "fechaSolicitud": p.fecha_solicitud,
        "estado": p.estado.value,
        "items": [{"sku": i.sku, "cantidad": i.cantidad} for i in p.items],
    }


def _serializar_envio(e: Envio) -> dict:
    return {
        "id": e.id,
        "pedidoId": e.pedido_id,
        "transportista": e.transportista,
        "fechaDespacho": e.fecha_despacho,
        "estado": e.estado.value,
    }


@bp.post("/pedidos")
def generar_pedido():
    d = request.get_json(silent=True) or {}
    p = DistribucionServicio().generar_pedido(
        tienda_destino=d.get("tiendaDestino", ""),
        items=d.get("items", []),
    )
    return jsonify(_serializar_pedido(p)), 201


@bp.get("/pedidos")
def listar_pedidos():
    return jsonify([_serializar_pedido(p) for p in DistribucionServicio().listar_pedidos()]), 200


@bp.get("/pedidos/<pedido_id>")
def consultar_pedido(pedido_id: str):
    return jsonify(_serializar_pedido(DistribucionServicio().obtener_pedido(pedido_id))), 200


@bp.post("/picking")
def preparar_picking():
    d = request.get_json(silent=True) or {}
    p = DistribucionServicio().iniciar_picking(pedido_id=d.get("pedidoId", ""))
    return jsonify(_serializar_pedido(p)), 200


@bp.post("/packing")
def preparar_packing():
    d = request.get_json(silent=True) or {}
    p = DistribucionServicio().completar_packing(pedido_id=d.get("pedidoId", ""))
    return jsonify(_serializar_pedido(p)), 200


@bp.post("/despachos")
def programar_despacho():
    d = request.get_json(silent=True) or {}
    e = DistribucionServicio().programar_despacho(
        pedido_id=d.get("pedidoId", ""),
        transportista=d.get("transportista", ""),
    )
    return jsonify(_serializar_envio(e)), 201


@bp.put("/<envio_id>/estado")
def actualizar_estado(envio_id: str):
    d = request.get_json(silent=True) or {}
    e = DistribucionServicio().actualizar_estado_envio(
        envio_id=envio_id, nuevo_estado=d.get("estado", ""),
    )
    return jsonify(_serializar_envio(e)), 200


@bp.put("/<envio_id>/llegada")
def registrar_llegada(envio_id: str):
    e = DistribucionServicio().registrar_llegada(envio_id)
    return jsonify(_serializar_envio(e)), 200
