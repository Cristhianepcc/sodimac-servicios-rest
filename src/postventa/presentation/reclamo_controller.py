"""Controlador REST de Reclamos (referencia de `postventa`).

    POST /api/reclamos        → registrar reclamo
    GET  /api/reclamos/<id>   → consultar reclamo
    GET  /api/reclamos        → listar reclamos
"""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request

from src.postventa.application.reclamo_servicio import NO_CAMBIO, ReclamoServicio
from src.postventa.presentation.serializadores import serializar_pagina, serializar_reclamo

bp = Blueprint("postventa_reclamo", __name__, url_prefix="/api/reclamos")


def _campo(d: dict, nombre: str):
    return d[nombre] if nombre in d else NO_CAMBIO


def _fecha(d: dict, nombre: str):
    if nombre not in d:
        return NO_CAMBIO
    if d[nombre] is None:
        return None
    return datetime.fromisoformat(d[nombre])


@bp.post("")
def crear_reclamo():
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().crear(
        cliente=d.get("cliente", ""),
        dni=d.get("dni", ""),
        email=d.get("email", ""),
        telefono=d.get("telefono", ""),
        producto=d.get("producto", ""),
        motivo=d.get("motivo", ""),
    )
    return jsonify(serializar_reclamo(r)), 201


@bp.get("/<reclamo_id>")
def obtener_reclamo(reclamo_id: str):
    return jsonify(serializar_reclamo(ReclamoServicio().obtener(reclamo_id))), 200


@bp.get("")
def listar_reclamos():
    pagina = ReclamoServicio().listar_abiertos(
        page=request.args.get("page", 1),
        size=request.args.get("size", 20),
    )
    return jsonify(serializar_pagina(pagina)), 200


@bp.put("/<reclamo_id>")
def actualizar_reclamo(reclamo_id: str):
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().actualizar(
        reclamo_id=reclamo_id,
        cliente=_campo(d, "cliente"),
        dni=_campo(d, "dni"),
        email=_campo(d, "email"),
        telefono=_campo(d, "telefono"),
        producto=_campo(d, "producto"),
        motivo=_campo(d, "motivo"),
        estado=_campo(d, "estado"),
        cumple_garantia=_campo(d, "cumpleGarantia"),
        motivo_validacion=_campo(d, "motivoValidacion"),
        diagnostico=_campo(d, "diagnostico"),
        procede_evaluacion=_campo(d, "procedeEvaluacion"),
        tipo_solucion=_campo(d, "tipoSolucion"),
        mensaje_cliente=_campo(d, "mensajeCliente"),
        fecha_cierre=_fecha(d, "fechaCierre"),
        fecha_notificacion=_fecha(d, "fechaNotificacion"),
    )
    return jsonify(serializar_reclamo(r)), 200


@bp.patch("/<reclamo_id>/garantia")
def actualizar_garantia(reclamo_id: str):
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().actualizar_garantia(
        reclamo_id=reclamo_id,
        cumple_garantia=d.get("cumpleGarantia"),
        motivo_validacion=d.get("motivoValidacion", ""),
    )
    return jsonify(serializar_reclamo(r)), 200


@bp.patch("/<reclamo_id>/evaluacion")
def actualizar_evaluacion(reclamo_id: str):
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().actualizar_evaluacion(
        reclamo_id=reclamo_id,
        diagnostico=d.get("diagnostico", ""),
        procede=d.get("procede"),
    )
    return jsonify(serializar_reclamo(r)), 200


@bp.patch("/<reclamo_id>/solucion")
def registrar_solucion(reclamo_id: str):
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().registrar_solucion(
        reclamo_id=reclamo_id,
        tipo_solucion=d.get("tipoSolucion", ""),
    )
    return jsonify(serializar_reclamo(r)), 200


@bp.post("/<reclamo_id>/notificacion")
def registrar_notificacion(reclamo_id: str):
    d = request.get_json(silent=True) or {}
    r = ReclamoServicio().registrar_notificacion(
        reclamo_id=reclamo_id,
        mensaje_cliente=d.get("mensajeCliente", ""),
    )
    return jsonify(serializar_reclamo(r)), 201
