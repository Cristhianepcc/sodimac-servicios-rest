"""Controlador REST de Reclamos (referencia de `postventa`).

    POST /api/reclamos        → registrar reclamo
    GET  /api/reclamos/<id>   → consultar reclamo
    GET  /api/reclamos        → listar reclamos
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.postventa.application.reclamo_servicio import ReclamoServicio
from src.postventa.domain.reclamo import Reclamo

bp = Blueprint("postventa_reclamo", __name__, url_prefix="/api/reclamos")


def _serializar(r: Reclamo) -> dict:
    return {
        "id": r.id,
        "cliente": r.cliente,
        "producto": r.producto,
        "motivo": r.motivo,
        "estado": r.estado.value,
    }


@bp.post("")
def crear_reclamo():
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().crear(
        cliente=d.get("cliente", ""),
        producto=d.get("producto", ""),
        motivo=d.get("motivo", ""),
    )
    return jsonify(_serializar(r)), 201


@bp.get("/<reclamo_id>")
def obtener_reclamo(reclamo_id: str):
    return jsonify(_serializar(ReclamoServicio().obtener(reclamo_id))), 200


@bp.get("")
def listar_reclamos():
    return jsonify([_serializar(r) for r in ReclamoServicio().listar()]), 200
