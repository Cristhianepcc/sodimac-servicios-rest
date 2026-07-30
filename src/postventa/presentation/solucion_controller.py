"""Controlador REST de soluciones de reclamos."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.postventa.application.solucion_servicio import SolucionServicio
from src.postventa.presentation.serializadores import serializar_pagina, serializar_reclamo

bp = Blueprint("postventa_solucion", __name__, url_prefix="/api/soluciones")


@bp.get("")
def listar_soluciones():
    pagina = SolucionServicio().listar(
        page=request.args.get("page", 1),
        size=request.args.get("size", 20),
    )
    return jsonify(serializar_pagina(pagina)), 200


@bp.post("")
def registrar_solucion():
    d = request.get_json(silent=True) or {}
    r = SolucionServicio().registrar(
        reclamo_id=d.get("reclamoId", ""),
        tipo_solucion=d.get("tipoSolucion", ""),
    )
    return jsonify(serializar_reclamo(r)), 201
