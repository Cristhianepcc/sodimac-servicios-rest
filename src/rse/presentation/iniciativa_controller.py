"""Controlador REST de Iniciativas RSE (referencia de `rse`).

    POST /api/iniciativas          → formular iniciativa RSE
    GET  /api/iniciativas/<codigo> → consultar iniciativa
    GET  /api/iniciativas          → listar iniciativas
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.rse.application.iniciativa_servicio import IniciativaServicio
from src.rse.domain.iniciativa import IniciativaRSE

bp = Blueprint("rse_iniciativa", __name__, url_prefix="/api/iniciativas")


def _serializar(i: IniciativaRSE) -> dict:
    return {
        "codigo": i.codigo,
        "nombre": i.nombre,
        "tipo": i.tipo.value,
        "descripcion": i.descripcion,
        "requierePresupuesto": i.requiere_presupuesto,
        "presupuestoSolicitado": i.presupuesto_solicitado,
        "estado": i.estado.value,
    }


@bp.post("")
def crear_iniciativa():
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().crear(
        nombre=d.get("nombre", ""),
        tipo=d.get("tipo", ""),
        descripcion=d.get("descripcion", ""),
        requiere_presupuesto=bool(d.get("requierePresupuesto", False)),
        presupuesto_solicitado=float(d.get("presupuestoSolicitado", 0.0)),
    )
    return jsonify(_serializar(i)), 201


@bp.get("/<codigo>")
def obtener_iniciativa(codigo: str):
    return jsonify(_serializar(IniciativaServicio().obtener(codigo))), 200


@bp.get("")
def listar_iniciativas():
    return jsonify([_serializar(i) for i in IniciativaServicio().listar()]), 200
