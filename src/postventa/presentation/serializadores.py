"""Serializadores HTTP del modulo postventa."""
from __future__ import annotations

from src.postventa.domain.reclamo import Reclamo


def serializar_reclamo(r: Reclamo) -> dict:
    return {
        "id": r.id,
        "cliente": r.cliente,
        "dni": r.dni,
        "email": r.email,
        "telefono": r.telefono,
        "producto": r.producto,
        "motivo": r.motivo,
        "estado": r.estado.value,
        "cumpleGarantia": r.cumple_garantia,
        "motivoValidacion": r.motivo_validacion,
        "diagnostico": r.diagnostico,
        "procedeEvaluacion": r.procede_evaluacion,
        "tipoSolucion": r.tipo_solucion,
        "mensajeCliente": r.mensaje_cliente,
        "fechaCierre": r.fecha_cierre.isoformat() if r.fecha_cierre else None,
        "fechaNotificacion": r.fecha_notificacion.isoformat() if r.fecha_notificacion else None,
    }


def serializar_pagina(pagina: dict) -> dict:
    return {
        "page": pagina["page"],
        "size": pagina["size"],
        "total": pagina["total"],
        "items": [serializar_reclamo(r) for r in pagina["items"]],
    }
