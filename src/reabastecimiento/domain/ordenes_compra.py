"""Dominio del servicio de Órdenes de Compra (Reabastecimiento)."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from src.shared.errores import Conflicto, ErrorDominio


class EstadoOrdenCompra(str, Enum):
    BORRADOR = "BORRADOR"
    AUTORIZADA = "AUTORIZADA"
    ENVIADA = "ENVIADA"
    CANCELADA = "CANCELADA"


@dataclass
class LineaOC:
    sku: str
    cantidad: int
    precio_unitario: float

    def __post_init__(self) -> None:
        if not self.sku or not self.sku.strip():
            raise ErrorDominio("El SKU de la línea es obligatorio.")
        if self.cantidad <= 0:
            raise ErrorDominio("La cantidad de la línea debe ser mayor que cero.")
        if self.precio_unitario < 0:
            raise ErrorDominio("El precio unitario no puede ser negativo.")
        self.sku = self.sku.strip()


@dataclass
class OrdenCompra:
    id: str
    proveedor_id: str
    lineas: List[LineaOC] = field(default_factory=list)
    estado: EstadoOrdenCompra = EstadoOrdenCompra.BORRADOR

    @property
    def total(self) -> float:
        return sum(linea.cantidad * linea.precio_unitario for linea in self.lineas)

    def autorizar(self) -> None:
        if self.estado != EstadoOrdenCompra.BORRADOR:
            raise Conflicto("Solo una orden en estado BORRADOR puede autorizarse.")
        self.estado = EstadoOrdenCompra.AUTORIZADA

    def cancelar(self) -> None:
        if self.estado == EstadoOrdenCompra.ENVIADA:
            raise Conflicto("No se puede cancelar una orden enviada.")
        if self.estado == EstadoOrdenCompra.CANCELADA:
            raise Conflicto("La orden ya está cancelada.")
        self.estado = EstadoOrdenCompra.CANCELADA

    def enviar(self) -> None:
        if self.estado != EstadoOrdenCompra.AUTORIZADA:
            raise Conflicto("Solo una orden autorizada puede enviarse.")
        self.estado = EstadoOrdenCompra.ENVIADA


class OrdenCompraFabrica:
    @staticmethod
    def crear(proveedor_id: str, lineas: List[dict]) -> OrdenCompra:
        if not proveedor_id or not proveedor_id.strip():
            raise ErrorDominio("El proveedor es obligatorio.")
        if not lineas or not isinstance(lineas, list):
            raise ErrorDominio("La orden debe contener al menos una línea.")

        orden_lineas: List[LineaOC] = []
        for linea in lineas:
            orden_lineas.append(
                LineaOC(
                    sku=linea.get("sku", ""),
                    cantidad=int(linea.get("cantidad", 0)),
                    precio_unitario=float(linea.get("precio_unitario", 0)),
                )
            )

        return OrdenCompra(
            id=f"OC-{uuid.uuid4().hex[:10].upper()}",
            proveedor_id=proveedor_id.strip(),
            lineas=orden_lineas,
        )


class IOrdenCompraRepositorio(ABC):
    @abstractmethod
    def adicionar(self, orden: OrdenCompra) -> None: ...

    @abstractmethod
    def buscar(self, orden_id: str) -> OrdenCompra | None: ...

    @abstractmethod
    def eliminar(self, orden_id: str) -> None: ...

    @abstractmethod
    def actualizar(self, orden: OrdenCompra) -> None: ...
