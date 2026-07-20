"""STUB — Recepción y Control de Calidad (Reabastecimiento). Responsable: Integrante 4a.

Endpoints a implementar (Práctica 4 §5.1):
    POST /api/recepciones               → registrar llegada de mercadería
    PUT  /api/recepciones/<id>/confirmar→ confirmar recepción
    POST /api/inspecciones              → inspeccionar mercadería
    PUT  /api/inspecciones/<id>/validar → validar conformidad
    PUT  /api/inspecciones/<id>/rechazar→ registrar rechazo
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_recepcion", __name__, url_prefix="/api")

_SVC = "Recepción y Control de Calidad"
_INT = "Integrante 4"


@bp.post("/recepciones")
def registrar_recepcion():
    return no_implementado(_SVC, _INT)


@bp.put("/recepciones/<recepcion_id>/confirmar")
def confirmar_recepcion(recepcion_id: str):
    return no_implementado(_SVC, _INT)


@bp.post("/inspecciones")
def inspeccionar():
    return no_implementado(_SVC, _INT)


@bp.put("/inspecciones/<inspeccion_id>/validar")
def validar(inspeccion_id: str):
    return no_implementado(_SVC, _INT)


@bp.put("/inspecciones/<inspeccion_id>/rechazar")
def rechazar(inspeccion_id: str):
    return no_implementado(_SVC, _INT)
