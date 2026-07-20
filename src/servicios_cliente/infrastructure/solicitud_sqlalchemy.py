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
    )


class SolicitudRepositorioSQLAlchemy(ISolicitudRepositorio):
    def adicionar(self, solicitud: SolicitudServicio) -> None:
        with get_session() as s:
            s.add(
                SolicitudServicioORM(
                    id=solicitud.id,
                    cliente=solicitud.cliente,
                    tipo_servicio=solicitud.tipo_servicio,
                    direccion=solicitud.direccion,
                    estado=solicitud.estado.value,
                )
            )
            s.commit()

    def buscar(self, solicitud_id: str) -> SolicitudServicio | None:
        with get_session() as s:
            row = s.get(SolicitudServicioORM, solicitud_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[SolicitudServicio]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(SolicitudServicioORM).all()]
