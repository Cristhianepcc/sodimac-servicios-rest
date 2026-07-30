from __future__ import annotations

from flask import Blueprint, jsonify, request

from src.reabastecimiento.application.auditoria_servicio import AuditoriaServicio, MovimientoStockServicio
from src.reabastecimiento.domain.auditoria import Auditoria, MovimientoStock
from src.shared.auth import proteger_api_bp

bp = Blueprint("reabastecimiento_auditoria", __name__, url_prefix="/api/auditorias")
proteger_api_bp(bp, "ALMACENERO")


def _serializar_auditoria(a: Auditoria) -> dict:
    return {
        "id": a.id, "sku": a.sku, "tipo": a.tipo.value, "fecha": a.fecha,
        "estado": a.estado.value, "observaciones": a.observaciones,
    }


def _serializar_movimiento(m: MovimientoStock) -> dict:
    return {
        "id": m.id, "sku": m.sku, "tipo": m.tipo.value, "cantidad": m.cantidad,
        "motivo": m.motivo, "fecha": m.fecha, "usuario": m.usuario,
    }


@bp.post("")
def crear_auditoria():
    d = request.get_json(silent=True) or {}
    a = AuditoriaServicio().crear(sku=d.get("sku", ""), tipo=d.get("tipo", ""))
    return jsonify(_serializar_auditoria(a)), 201


@bp.get("")
def listar_auditorias():
    return jsonify([_serializar_auditoria(a) for a in AuditoriaServicio().listar()]), 200


@bp.get("/<auditoria_id>")
def consultar_auditoria(auditoria_id: str):
    return jsonify(_serializar_auditoria(AuditoriaServicio().obtener(auditoria_id))), 200


@bp.put("/<auditoria_id>/completar")
def completar_auditoria(auditoria_id: str):
    d = request.get_json(silent=True) or {}
    a = AuditoriaServicio().completar(auditoria_id, d.get("observaciones", ""))
    return jsonify(_serializar_auditoria(a)), 200


@bp.post("/movimientos")
def registrar_movimiento():
    d = request.get_json(silent=True) or {}
    m = MovimientoStockServicio().registrar(
        sku=d.get("sku", ""), tipo=d.get("tipo", ""), cantidad=int(d.get("cantidad", 0)),
        motivo=d.get("motivo", ""), usuario=d.get("usuario", ""),
    )
    return jsonify(_serializar_movimiento(m)), 201


@bp.get("/movimientos")
def listar_movimientos():
    sku = request.args.get("sku", "")
    if sku:
        return jsonify([_serializar_movimiento(m) for m in MovimientoStockServicio().historial(sku)]), 200
    return jsonify([_serializar_movimiento(m) for m in MovimientoStockServicio().listar_todos()]), 200


@bp.get("/<sku>")
def consultar_historial(sku: str):
    return jsonify([_serializar_movimiento(m) for m in MovimientoStockServicio().historial(sku)]), 200


@bp.get("/<auditoria_id>/archivo")
def generar_archivo(auditoria_id: str):
    a = AuditoriaServicio().obtener(auditoria_id)
    return jsonify({
        "auditoria": _serializar_auditoria(a),
        "mensaje": f"Archivo generado para auditoría {auditoria_id}",
        "formato": "CSV",
    }), 200
