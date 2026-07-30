"""Controlador REST de notificaciones simuladas."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.postventa.application.notificacion_servicio import NotificacionServicio
from src.postventa.presentation.serializadores import serializar_reclamo

bp = Blueprint("postventa_notificacion", __name__, url_prefix="/api/notificaciones")


@bp.post("")
def enviar_notificacion():
    d = request.get_json(silent=True) or {}
    reclamo = NotificacionServicio().enviar(
        reclamo_id=d.get("reclamoId", ""),
        mensaje=d.get("mensajeCliente", d.get("mensaje", "")),
    )
    return jsonify(serializar_reclamo(reclamo)), 201
