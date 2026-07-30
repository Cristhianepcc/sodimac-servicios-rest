"""Mapeo ORM de todos los servicios de Reabastecimiento → PostgreSQL."""
from __future__ import annotations

from sqlalchemy import Integer, String, Text
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


class OrdenCompraORM(Base):
    __tablename__ = "reabastecimiento_orden_compra"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    proveedor_id: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_emision: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="BORRADOR")
    lineas_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class UbicacionORM(Base):
    __tablename__ = "reabastecimiento_ubicacion"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    pasillo: Mapped[str] = mapped_column(String(20), nullable=False)
    estante: Mapped[str] = mapped_column(String(20), nullable=False)
    nivel: Mapped[str] = mapped_column(String(20), nullable=False)


class MercaderiaUbicadaORM(Base):
    __tablename__ = "reabastecimiento_mercaderia_ubicada"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    ubicacion_codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_ubicacion: Mapped[str] = mapped_column(String(40), nullable=False)


class RecepcionORM(Base):
    __tablename__ = "reabastecimiento_recepcion"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    orden_compra_id: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_llegada: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    items_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class InspeccionORM(Base):
    __tablename__ = "reabastecimiento_inspeccion"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    recepcion_id: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[str] = mapped_column(String(40), nullable=False)
    resultado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    observaciones: Mapped[str] = mapped_column(Text, nullable=False, default="")


class PedidoDistribucionORM(Base):
    __tablename__ = "reabastecimiento_pedido_distribucion"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    tienda_destino: Mapped[str] = mapped_column(String(80), nullable=False)
    fecha_solicitud: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="SOLICITADO")
    items_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")


class EnvioORM(Base):
    __tablename__ = "reabastecimiento_envio"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    pedido_id: Mapped[str] = mapped_column(String(20), nullable=False)
    transportista: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    fecha_despacho: Mapped[str] = mapped_column(String(40), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PREPARADO")


class AuditoriaORM(Base):
    __tablename__ = "reabastecimiento_auditoria"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[str] = mapped_column(String(40), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    observaciones: Mapped[str] = mapped_column(Text, nullable=False, default="")


class MovimientoStockORM(Base):
    __tablename__ = "reabastecimiento_movimiento_stock"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[str] = mapped_column(String(40), nullable=False)
    usuario: Mapped[str] = mapped_column(String(80), nullable=False, default="")
