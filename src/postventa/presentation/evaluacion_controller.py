"""Controlador REST de evaluaciones de reclamos."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.postventa.application.evaluacion_servicio import EvaluacionServicio
from src.postventa.presentation.serializadores import serializar_pagina, serializar_reclamo

bp = Blueprint("postventa_evaluacion", __name__, url_prefix="/api/evaluaciones")


@bp.get("")
def listar_evaluaciones():
    pagina = EvaluacionServicio().listar(
        page=request.args.get("page", 1),
        size=request.args.get("size", 20),
    )
    return jsonify(serializar_pagina(pagina)), 200


@bp.post("")
def registrar_evaluacion():
    d = request.get_json(silent=True) or {}
    r = EvaluacionServicio().registrar(
        reclamo_id=d.get("reclamoId", ""),
        diagnostico=d.get("diagnostico", ""),
        procede=d.get("procede"),
    )
    return jsonify(serializar_reclamo(r)), 201
