"""Repositorio SQLAlchemy del agregado Carrito (persistencia real en PostgreSQL).

Traduce entre el modelo de dominio (dataclasses) y el modelo ORM.
"""
from __future__ import annotations

from src.shared.db import get_session
from src.ventas.domain.modelo import Carrito, EstadoCarrito, ItemCarrito
from src.ventas.domain.repositorio import ICarritoRepositorio

from .orm import CarritoORM, ItemCarritoORM


def _a_dominio(row: CarritoORM) -> Carrito:
    return Carrito(
        id=row.id,
        cliente=row.cliente,
        estado=EstadoCarrito(row.estado),
        items=[
            ItemCarrito(sku=i.sku, cantidad=i.cantidad, precio_unitario=i.precio_unitario)
            for i in row.items
        ],
    )


class CarritoRepositorioSQLAlchemy(ICarritoRepositorio):
    def adicionar(self, carrito: Carrito) -> None:
        with get_session() as s:
            row = CarritoORM(id=carrito.id, cliente=carrito.cliente, estado=carrito.estado.value)
            row.items = [
                ItemCarritoORM(sku=i.sku, cantidad=i.cantidad, precio_unitario=i.precio_unitario)
                for i in carrito.items
            ]
            s.add(row)
            s.commit()

    def buscar(self, carrito_id: str) -> Carrito | None:
        with get_session() as s:
            row = s.get(CarritoORM, carrito_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[Carrito]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(CarritoORM).all()]
