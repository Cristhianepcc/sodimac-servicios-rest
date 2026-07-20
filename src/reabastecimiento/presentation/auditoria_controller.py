"""STUB — Servicio de Auditoría (Reabastecimiento). Responsable: Integrante 4b.

Endpoints a implementar (Práctica 4 §5.1):
    POST /api/auditorias              → crear auditoría
    POST /api/auditorias/movimientos  → registrar movimiento de stock
    GET  /api/auditorias/<id>/archivo → generar archivo de auditoría
    GET  /api/auditorias/<sku>        → consultar historial de movimientos
"""
from __future__ import annotations

from flask import Blueprint

from src.shared.stub import no_implementado

bp = Blueprint("reabastecimiento_auditoria", __name__, url_prefix="/api/auditorias")

_SVC = "Auditoría"
_INT = "Integrante 4"


@bp.post("")
def crear_auditoria():
    return no_implementado(_SVC, _INT)


@bp.post("/movimientos")
def registrar_movimiento():
    return no_implementado(_SVC, _INT)


@bp.get("/<auditoria_id>/archivo")
def generar_archivo(auditoria_id: str):
    return no_implementado(_SVC, _INT)


@bp.get("/<sku>")
def consultar_historial(sku: str):
    return no_implementado(_SVC, _INT)
