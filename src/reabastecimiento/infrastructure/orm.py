"""Mapeo ORM del servicio de Inventario → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.db import Base


class ProductoInventarioORM(Base):
    __tablename__ = "reabastecimiento_producto"

    sku: Mapped[str] = mapped_column(String(40), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ProveedorORM(Base):
    __tablename__ = "reabastecimiento_proveedor"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    ruc: Mapped[str] = mapped_column(String(11), nullable=False)
    puntaje: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADO")
