"""Mapeo ORM de Solicitud de Servicio → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class SolicitudServicioORM(Base):
    __tablename__ = "servicios_cliente_solicitud"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_servicio: Mapped[str] = mapped_column(String(80), nullable=False)
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADA")
