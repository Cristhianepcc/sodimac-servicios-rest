"""Mapeo ORM de Iniciativa RSE → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class IniciativaRSEORM(Base):
    __tablename__ = "rse_iniciativa"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    requiere_presupuesto: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    presupuesto_solicitado: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="FORMULADA")
