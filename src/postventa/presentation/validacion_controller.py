"""Controlador REST de validaciones de reclamos."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.postventa.application.validacion_servicio import ValidacionServicio
from src.postventa.presentation.serializadores import serializar_reclamo

bp = Blueprint("postventa_validacion", __name__, url_prefix="/api/validaciones")


@bp.post("/verificar")
def verificar_validacion():
    d = request.get_json(silent=True) or {}
    r = ValidacionServicio().verificar(
        reclamo_id=d.get("reclamoId", ""),
        cumple_garantia=d.get("cumpleGarantia"),
        motivo=d.get("motivoValidacion", d.get("motivo", "")),
    )
    return jsonify(serializar_reclamo(r)), 201
