from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.recepcion_servicio import InspeccionServicio, RecepcionServicio
from src.reabastecimiento.domain.recepcion import Inspeccion, Recepcion

bp = Blueprint("reabastecimiento_recepcion", __name__, url_prefix="/api")


def _serializar_recepcion(r: Recepcion) -> dict:
    return {
        "id": r.id,
        "ordenCompraId": r.orden_compra_id,
        "fechaLlegada": r.fecha_llegada,
        "estado": r.estado.value,
        "items": [{"sku": i.sku, "cantidadRecibida": i.cantidad_recibida} for i in r.items],
    }


def _serializar_inspeccion(i: Inspeccion) -> dict:
    return {
        "id": i.id,
        "recepcionId": i.recepcion_id,
        "fecha": i.fecha,
        "resultado": i.resultado.value,
        "observaciones": i.observaciones,
    }


@bp.post("/recepciones")
def registrar_recepcion():
    d = request.get_json(silent=True) or {}
    r = RecepcionServicio().registrar(
        orden_compra_id=d.get("ordenCompraId", ""),
        items=d.get("items", []),
    )
    return jsonify(_serializar_recepcion(r)), 201


@bp.get("/recepciones")
def listar_recepciones():
    return jsonify([_serializar_recepcion(r) for r in RecepcionServicio().listar()]), 200


@bp.get("/recepciones/<recepcion_id>")
def consultar_recepcion(recepcion_id: str):
    return jsonify(_serializar_recepcion(RecepcionServicio().obtener(recepcion_id))), 200


@bp.put("/recepciones/<recepcion_id>/confirmar")
def confirmar_recepcion(recepcion_id: str):
    return jsonify(_serializar_recepcion(RecepcionServicio().confirmar(recepcion_id))), 200


@bp.post("/inspecciones")
def inspeccionar():
    d = request.get_json(silent=True) or {}
    i = InspeccionServicio().crear(recepcion_id=d.get("recepcionId", ""))
    return jsonify(_serializar_inspeccion(i)), 201


@bp.get("/inspecciones/<inspeccion_id>")
def consultar_inspeccion(inspeccion_id: str):
    return jsonify(_serializar_inspeccion(InspeccionServicio().obtener(inspeccion_id))), 200


@bp.get("/inspecciones")
def listar_inspecciones():
    recepcion_id = request.args.get("recepcionId", "")
    if recepcion_id:
        return jsonify([_serializar_inspeccion(i) for i in InspeccionServicio().listar_por_recepcion(recepcion_id)]), 200
    return jsonify([]), 200


@bp.put("/inspecciones/<inspeccion_id>/validar")
def validar(inspeccion_id: str):
    d = request.get_json(silent=True) or {}
    i = InspeccionServicio().validar(inspeccion_id, d.get("observaciones", ""))
    return jsonify(_serializar_inspeccion(i)), 200


@bp.put("/inspecciones/<inspeccion_id>/rechazar")
def rechazar(inspeccion_id: str):
    d = request.get_json(silent=True) or {}
    i = InspeccionServicio().rechazar(inspeccion_id, d.get("observaciones", ""))
    return jsonify(_serializar_inspeccion(i)), 200
