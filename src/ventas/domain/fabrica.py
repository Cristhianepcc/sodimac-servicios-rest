"""Fábrica del agregado Carrito (patrón Factory de DDD)."""
from __future__ import annotations

import uuid

from src.shared.errores import ErrorDominio

from .modelo import Carrito, EstadoCarrito, ItemCarrito


class CarritoFabrica:
    @staticmethod
    def crear(cliente: str, items: list[dict]) -> Carrito:
        if not cliente or not cliente.strip():
            raise ErrorDominio("El cliente es obligatorio.")
        if not items:
            raise ErrorDominio("El carrito debe tener al menos un ítem.")

        carrito = Carrito(
            id=f"CAR-{uuid.uuid4().hex[:8].upper()}",
            cliente=cliente.strip(),
            estado=EstadoCarrito.ABIERTO,
        )
        for it in items:
            try:
                item = ItemCarrito(
                    sku=str(it["sku"]),
                    cantidad=int(it["cantidad"]),
                    precio_unitario=float(it.get("precio_unitario", 0.0)),
                )
            except (KeyError, TypeError, ValueError):
                raise ErrorDominio("Cada ítem requiere 'sku' y 'cantidad' válidos.")
            try:
                carrito.agregar_item(item)
            except ValueError as exc:
                raise ErrorDominio(str(exc))
        return carrito
