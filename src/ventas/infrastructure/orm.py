"""Mapeo ORM (SQLAlchemy) del agregado Carrito → PostgreSQL.

Tablas separadas del modelo de dominio: el dominio son dataclasses puras; aquí
se define la representación de persistencia y se traduce en el repositorio.
"""
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.db import Base


class CarritoORM(Base):
    __tablename__ = "ventas_carrito"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ABIERTO")

    items: Mapped[list["ItemCarritoORM"]] = relationship(
        back_populates="carrito", cascade="all, delete-orphan", lazy="selectin"
    )


class ItemCarritoORM(Base):
    __tablename__ = "ventas_item_carrito"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carrito_id: Mapped[str] = mapped_column(ForeignKey("ventas_carrito.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    carrito: Mapped["CarritoORM"] = relationship(back_populates="items")
