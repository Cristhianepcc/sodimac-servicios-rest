"""Mapeo ORM de Reclamo → PostgreSQL."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class ReclamoORM(Base):
    __tablename__ = "postventa_reclamo"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    producto: Mapped[str] = mapped_column(String(120), nullable=False)
    motivo: Mapped[str] = mapped_column(String(300), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADO")

    cumple_garantia: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    motivo_validacion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    diagnostico: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    procede_evaluacion: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tipo_solucion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mensaje_cliente: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_notificacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)