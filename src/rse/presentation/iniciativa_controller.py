"""Controlador REST de Iniciativas RSE (proceso completo).

    POST /api/iniciativas                              → formular iniciativa RSE
    GET  /api/iniciativas/<codigo>                     → consultar iniciativa
    GET  /api/iniciativas                              → listar iniciativas
    POST /api/iniciativas/<codigo>/evaluacion          → evaluar (comité)
    POST /api/iniciativas/<codigo>/indicadores         → agregar KPI
    POST /api/iniciativas/<codigo>/evidencias          → registrar evidencia
    POST /api/iniciativas/<codigo>/reporte             → generar reporte
    POST /api/iniciativas/<codigo>/reporte/publicacion → aprobar publicación
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
        "presupuestoAprobado": i.presupuesto_aprobado,
        "estado": i.estado.value,
        "aprobada": i.aprobada,
        "indicadores": [
            {
                "nombre": k.nombre,
                "unidad": k.unidad,
                "valorLineaBase": k.valor_linea_base,
                "valorActual": k.valor_actual,
                "meta": k.meta,
            }
            for k in i.indicadores
        ],
        "evidencias": [
            {
                "fecha": e.fecha.isoformat(),
                "descripcion": e.descripcion,
                "porcentajeAvance": e.porcentaje_avance,
                "archivoUrl": e.archivo_url,
            }
            for e in i.evidencias
        ],
        "reporte": None
        if i.reporte is None
        else {
            "codigo": i.reporte.codigo,
            "fechaGeneracion": i.reporte.fecha_generacion.isoformat(),
            "resumen": i.reporte.resumen,
            "urlPublicacion": i.reporte.url_publicacion,
            "aprobadoPublicacion": i.reporte.aprobado_publicacion,
        },
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


@bp.post("/<codigo>/evaluacion")
def evaluar_iniciativa(codigo: str):
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().evaluar(
        codigo=codigo,
        aprobada=bool(d.get("aprobada", False)),
        presupuesto_aprobado=float(d.get("presupuestoAprobado", 0.0)),
        comentario=d.get("comentario", ""),
    )
    return jsonify(_serializar(i)), 200


@bp.post("/<codigo>/indicadores")
def agregar_indicador(codigo: str):
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().agregar_indicador(
        codigo=codigo,
        nombre=d.get("nombre", ""),
        unidad=d.get("unidad", ""),
        valor_linea_base=float(d.get("valorLineaBase", 0.0)),
        valor_actual=float(d.get("valorActual", 0.0)),
        meta=float(d.get("meta", 0.0)),
    )
    return jsonify(_serializar(i)), 201


@bp.post("/<codigo>/evidencias")
def registrar_evidencia(codigo: str):
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().registrar_evidencia(
        codigo=codigo,
        descripcion=d.get("descripcion", ""),
        porcentaje_avance=float(d.get("porcentajeAvance", 0.0)),
        archivo_url=d.get("archivoUrl", ""),
    )
    return jsonify(_serializar(i)), 201


@bp.post("/<codigo>/reporte")
def generar_reporte(codigo: str):
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().generar_reporte(codigo=codigo, resumen=d.get("resumen", ""))
    return jsonify(_serializar(i)), 201


@bp.post("/<codigo>/reporte/publicacion")
def aprobar_publicacion(codigo: str):
    d = request.get_json(silent=True) or {}
    i = IniciativaServicio().aprobar_publicacion(
        codigo=codigo, url_publicacion=d.get("urlPublicacion", "")
    )
    return jsonify(_serializar(i)), 200


@bp.get("/<codigo>/cumplimiento")
def evaluar_cumplimiento(codigo: str):
    """Evaluar el cumplimiento de metas (gateway «¿Metas cumplidas?»)."""
    tolerancia = request.args.get("tolerancia", default=0.9, type=float)
    r = IniciativaServicio().evaluar_metas(codigo, tolerancia=tolerancia)
    return jsonify(
        {
            "codigo": codigo,
            "cumplidas": r.cumplidas,
            "porcentajeGlobal": r.porcentaje_global,
            "indicadoresCumplidos": r.indicadores_cumplidos,
            "indicadoresTotales": r.indicadores_totales,
            "rezagados": list(r.rezagados),
            "requiereAccionesCorrectivas": r.requiere_acciones_correctivas,
        }
    ), 200
