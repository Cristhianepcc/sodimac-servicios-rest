"""Controlador REST de Solicitudes de Servicio (referencia de `servicios_cliente`).

    POST /api/solicitudes        → registrar solicitud de servicio
    GET  /api/solicitudes/<id>   → consultar solicitud
    GET  /api/solicitudes        → listar solicitudes
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.servicios_cliente.application.solicitud_servicio import SolicitudAppServicio
from src.servicios_cliente.domain.solicitud import SolicitudServicio

bp = Blueprint("servicios_cliente_solicitud", __name__, url_prefix="/api/solicitudes")


def _serializar(s: SolicitudServicio) -> dict:
    return {
        "id": s.id,
        "cliente": s.cliente,
        "tipoServicio": s.tipo_servicio,
        "direccion": s.direccion,
        "estado": s.estado.value,
    }


@bp.post("")
def crear_solicitud():
    d = request.get_json(silent=True) or {}
    s = SolicitudAppServicio().crear(
        cliente=d.get("cliente", ""),
        tipo_servicio=d.get("tipoServicio", ""),
        direccion=d.get("direccion", ""),
    )
    return jsonify(_serializar(s)), 201


@bp.get("/<solicitud_id>")
def obtener_solicitud(solicitud_id: str):
    return jsonify(_serializar(SolicitudAppServicio().obtener(solicitud_id))), 200


@bp.get("")
def listar_solicitudes():
    return jsonify([_serializar(s) for s in SolicitudAppServicio().listar()]), 200
