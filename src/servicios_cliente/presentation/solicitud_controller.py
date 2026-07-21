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
        "tecnico": s.tecnico,
        "fecha": s.fecha,
        "evidenciaDescripcion": s.evidencia_descripcion,
        "evidenciaFotoUrl": s.evidencia_foto_url,
        "conformidadAprobado": s.conformidad_aprobado,
        "conformidadObservacion": s.conformidad_observacion,
        "comprobante": s.comprobante,
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


@bp.post("/<solicitud_id>/programacion")
def programar_solicitud(solicitud_id: str):
    d = request.get_json(silent=True) or {}
    s = SolicitudAppServicio().programar(
        solicitud_id=solicitud_id,
        tecnico=d.get("tecnico", ""),
        fecha=d.get("fecha", ""),
    )
    return jsonify(_serializar(s)), 200


@bp.post("/<solicitud_id>/ejecucion")
def registrar_ejecucion(solicitud_id: str):
    d = request.get_json(silent=True) or {}
    s = SolicitudAppServicio().ejecutar(
        solicitud_id=solicitud_id,
        descripcion=d.get("descripcion", ""),
        foto_url=d.get("fotoUrl", ""),
    )
    return jsonify(_serializar(s)), 200


@bp.post("/<solicitud_id>/conformidad")
def evaluar_conformidad(solicitud_id: str):
    d = request.get_json(silent=True) or {}
    s = SolicitudAppServicio().dar_conformidad(
        solicitud_id=solicitud_id,
        aprobado=d.get("aprobado", False),
        observacion=d.get("observacion", ""),
    )
    return jsonify(_serializar(s)), 200


@bp.post("/<solicitud_id>/facturacion")
def generar_comprobante(solicitud_id: str):
    d = request.get_json(silent=True) or {}
    s = SolicitudAppServicio().facturar(
        solicitud_id=solicitud_id,
        comprobante=d.get("comprobante", ""),
    )
    return jsonify(_serializar(s)), 200

