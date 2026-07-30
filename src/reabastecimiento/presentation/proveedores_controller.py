"""Controlador REST del servicio de Proveedores (Reabastecimiento).

    POST /api/proveedores              → registrar proveedor
    GET  /api/proveedores              → listar proveedores
    GET  /api/proveedores/<id>         → consultar proveedor
    POST /api/proveedores/<id>/evaluar → evaluar proveedor
    PUT  /api/proveedores/<id>/aprobar → aprobar proveedor
    PUT  /api/proveedores/<id>/rechazar→ rechazar proveedor
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.proveedor_servicio import ProveedorServicio
from src.reabastecimiento.domain.proveedor import Proveedor
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_proveedores", __name__, url_prefix="/api/proveedores")
proteger_api_bp(bp, "ALMACENERO")


def _serializar(p: Proveedor) -> dict:
    return {
        "id": p.id,
        "nombre": p.nombre,
        "ruc": p.ruc,
        "puntaje": p.puntaje,
        "estado": p.estado.value,
    }


@bp.post("")
def registrar():
    d = request.get_json(silent=True) or {}
    p = ProveedorServicio().registrar(
        nombre=d.get("nombre", ""),
        ruc=d.get("ruc", ""),
    )
    return jsonify(_serializar(p)), 201


@bp.get("")
def listar():
    proveedores = ProveedorServicio().listar()
    return jsonify([_serializar(p) for p in proveedores]), 200


@bp.get("/<proveedor_id>")
def consultar(proveedor_id: str):
    return jsonify(_serializar(ProveedorServicio().obtener(proveedor_id))), 200


@bp.post("/<proveedor_id>/evaluar")
def evaluar(proveedor_id: str):
    d = request.get_json(silent=True) or {}
    p = ProveedorServicio().evaluar(proveedor_id, int(d.get("puntaje", 0)))
    return jsonify(_serializar(p)), 200


@bp.put("/<proveedor_id>/aprobar")
def aprobar(proveedor_id: str):
    p = ProveedorServicio().aprobar(proveedor_id)
    return jsonify(_serializar(p)), 200


@bp.put("/<proveedor_id>/rechazar")
def rechazar(proveedor_id: str):
    p = ProveedorServicio().rechazar(proveedor_id)
    return jsonify(_serializar(p)), 200
