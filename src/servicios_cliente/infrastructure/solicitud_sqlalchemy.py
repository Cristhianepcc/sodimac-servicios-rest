"""Repositorio SQLAlchemy de Solicitud de Servicio (PostgreSQL)."""
from __future__ import annotations

from src.servicios_cliente.domain.solicitud import (
    EstadoSolicitud,
    ISolicitudRepositorio,
    SolicitudServicio,
)
from src.shared.db import get_session

from .orm import SolicitudServicioORM


def _a_dominio(row: SolicitudServicioORM) -> SolicitudServicio:
    return SolicitudServicio(
        id=row.id,
        cliente=row.cliente,
        tipo_servicio=row.tipo_servicio,
        direccion=row.direccion,
        estado=EstadoSolicitud(row.estado),
        tecnico=row.tecnico,
        fecha=row.fecha,
        evidencia_descripcion=row.evidencia_descripcion,
        evidencia_foto_url=row.evidencia_foto_url,
        conformidad_aprobado=row.conformidad_aprobado,
        conformidad_observacion=row.conformidad_observacion,
        comprobante=row.comprobante,
    )


class SolicitudRepositorioSQLAlchemy(ISolicitudRepositorio):
    def adicionar(self, solicitud: SolicitudServicio) -> None:
        with get_session() as s:
            orm_obj = SolicitudServicioORM(
                id=solicitud.id,
                cliente=solicitud.cliente,
                tipo_servicio=solicitud.tipo_servicio,
                direccion=solicitud.direccion,
                estado=solicitud.estado.value,
                tecnico=solicitud.tecnico,
                fecha=solicitud.fecha,
                evidencia_descripcion=solicitud.evidencia_descripcion,
                evidencia_foto_url=solicitud.evidencia_foto_url,
                conformidad_aprobado=solicitud.conformidad_aprobado,
                conformidad_observacion=solicitud.conformidad_observacion,
                comprobante=solicitud.comprobante,
            )
            s.merge(orm_obj)
            s.commit()


    def buscar(self, solicitud_id: str) -> SolicitudServicio | None:
        with get_session() as s:
            row = s.get(SolicitudServicioORM, solicitud_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[SolicitudServicio]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(SolicitudServicioORM).all()]
