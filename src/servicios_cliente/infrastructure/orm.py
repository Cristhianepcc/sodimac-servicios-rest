"""Mapeo ORM de Solicitud de Servicio → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class SolicitudServicioORM(Base):
    __tablename__ = "servicios_cliente_solicitud"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo_servicio: Mapped[str] = mapped_column(String(80), nullable=False)
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADA")
    tecnico: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fecha: Mapped[str | None] = mapped_column(String(20), nullable=True)
    evidencia_descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    evidencia_foto_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    conformidad_aprobado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    conformidad_observacion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    comprobante: Mapped[str | None] = mapped_column(String(50), nullable=True)

