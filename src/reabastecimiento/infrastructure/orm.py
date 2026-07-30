"""Mapeo ORM del servicio de Reabastecimiento → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.db import Base


class ProductoInventarioORM(Base):
    __tablename__ = "reabastecimiento_producto"

    sku: Mapped[str] = mapped_column(String(40), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class OrdenCompraORM(Base):
    __tablename__ = "reabastecimiento_orden_compra"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    proveedor_id: Mapped[str] = mapped_column(String(80), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="BORRADOR")
    lineas: Mapped[list["LineaOCORM"]]
    lineas = relationship(
        "LineaOCORM",
        back_populates="orden",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LineaOCORM(Base):
    __tablename__ = "reabastecimiento_linea_oc"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orden_id: Mapped[str] = mapped_column(ForeignKey("reabastecimiento_orden_compra.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    orden: Mapped[OrdenCompraORM] = relationship(back_populates="lineas")


class UbicacionORM(Base):
    __tablename__ = "reabastecimiento_ubicacion"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    zona: Mapped[str] = mapped_column(String(40), nullable=False)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
