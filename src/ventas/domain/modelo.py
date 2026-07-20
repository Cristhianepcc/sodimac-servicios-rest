"""Dominio del proceso `ventas` (Venta y Atención al Cliente – Omnicanal).

Entidad de referencia: Carrito de compra/cotización. Python puro, sin Flask ni
SQLAlchemy (independencia funcional / ocultamiento de información).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EstadoCarrito(str, Enum):
    ABIERTO = "ABIERTO"
    COTIZADO = "COTIZADO"
    CONFIRMADO = "CONFIRMADO"


@dataclass
class ItemCarrito:
    sku: str
    cantidad: int
    precio_unitario: float = 0.0

    @property
    def subtotal(self) -> float:
        return self.cantidad * self.precio_unitario


@dataclass
class Carrito:
    """Agregado raíz del proceso de venta."""

    id: str
    cliente: str
    items: list[ItemCarrito] = field(default_factory=list)
    estado: EstadoCarrito = EstadoCarrito.ABIERTO

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    def agregar_item(self, item: ItemCarrito) -> None:
        if item.cantidad <= 0:
            raise ValueError("La cantidad de un ítem debe ser mayor que 0.")
        self.items.append(item)

    def confirmar(self) -> None:
        if not self.items:
            raise ValueError("No se puede confirmar un carrito vacío.")
        self.estado = EstadoCarrito.CONFIRMADO
