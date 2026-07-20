"""Mapeo ORM de Reclamo → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class ReclamoORM(Base):
    __tablename__ = "postventa_reclamo"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    producto: Mapped[str] = mapped_column(String(120), nullable=False)
    motivo: Mapped[str] = mapped_column(String(300), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADO")
