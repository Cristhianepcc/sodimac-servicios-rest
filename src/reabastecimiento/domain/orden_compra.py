from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoOrden(str, Enum):
    BORRADOR = "BORRADOR"
    PENDIENTE_AUTORIZACION = "PENDIENTE_AUTORIZACION"
    AUTORIZADA = "AUTORIZADA"
    ENVIADA = "ENVIADA"
    CANCELADA = "CANCELADA"


@dataclass
class LineaOC:
    sku: str
    cantidad: int
    precio_unitario: float

    @property
    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario


@dataclass
class OrdenCompra:
    id: str
    proveedor_id: str
    fecha_emision: str
    lineas: list[LineaOC] = field(default_factory=list)
    estado: EstadoOrden = EstadoOrden.BORRADOR

    @property
    def total(self) -> float:
        return sum(l.subtotal for l in self.lineas)

    def autorizar(self) -> None:
        if self.estado != EstadoOrden.PENDIENTE_AUTORIZACION:
            raise ErrorDominio("Solo órdenes pendientes pueden autorizarse.")
        self.estado = EstadoOrden.AUTORIZADA

    def cancelar(self) -> None:
        if self.estado in (EstadoOrden.ENVIADA, EstadoOrden.CANCELADA):
            raise ErrorDominio("No se puede cancelar una orden ya enviada o cancelada.")
        self.estado = EstadoOrden.CANCELADA

    def enviar(self) -> None:
        if self.estado != EstadoOrden.AUTORIZADA:
            raise ErrorDominio("Solo órdenes autorizadas pueden enviarse.")
        self.estado = EstadoOrden.ENVIADA


class OrdenCompraFabrica:
    @staticmethod
    def crear(proveedor_id: str, lineas: list[dict]) -> OrdenCompra:
        if not proveedor_id or not proveedor_id.strip():
            raise ErrorDominio("El ID del proveedor es obligatorio.")
        if not lineas:
            raise ErrorDominio("La orden debe tener al menos una línea.")
        lineas_dominio = [
            LineaOC(
                sku=l["sku"],
                cantidad=int(l["cantidad"]),
                precio_unitario=float(l["precioUnitario"]),
            )
            for l in lineas
        ]
        for ln in lineas_dominio:
            if ln.cantidad <= 0:
                raise ErrorDominio("La cantidad debe ser mayor a cero.")
            if ln.precio_unitario <= 0:
                raise ErrorDominio("El precio unitario debe ser mayor a cero.")
        id_oc = f"OC-{uuid.uuid4().hex[:8].upper()}"
        ahora = datetime.now(timezone.utc).isoformat()
        return OrdenCompra(
            id=id_oc,
            proveedor_id=proveedor_id.strip(),
            fecha_emision=ahora,
            lineas=lineas_dominio,
            estado=EstadoOrden.PENDIENTE_AUTORIZACION,
        )


class IOrdenCompraRepositorio(ABC):
    @abstractmethod
    def adicionar(self, orden: OrdenCompra) -> None: ...
    @abstractmethod
    def buscar(self, orden_id: str) -> OrdenCompra | None: ...
    @abstractmethod
    def listar(self) -> list[OrdenCompra]: ...
    @abstractmethod
    def actualizar(self, orden: OrdenCompra) -> None: ...
