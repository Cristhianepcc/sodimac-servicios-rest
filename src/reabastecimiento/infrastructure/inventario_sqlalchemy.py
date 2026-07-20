"""Repositorio SQLAlchemy del servicio de Inventario (PostgreSQL)."""
from __future__ import annotations

from src.reabastecimiento.domain.inventario import IProductoRepositorio, ProductoInventario
from src.shared.db import get_session

from .orm import ProductoInventarioORM


def _a_dominio(row: ProductoInventarioORM) -> ProductoInventario:
    return ProductoInventario(
        sku=row.sku, nombre=row.nombre, stock=row.stock, stock_minimo=row.stock_minimo
    )


class ProductoRepositorioSQLAlchemy(IProductoRepositorio):
    def adicionar(self, producto: ProductoInventario) -> None:
        with get_session() as s:
            s.add(
                ProductoInventarioORM(
                    sku=producto.sku,
                    nombre=producto.nombre,
                    stock=producto.stock,
                    stock_minimo=producto.stock_minimo,
                )
            )
            s.commit()

    def buscar(self, sku: str) -> ProductoInventario | None:
        with get_session() as s:
            row = s.get(ProductoInventarioORM, sku)
            return _a_dominio(row) if row else None

    def actualizar(self, producto: ProductoInventario) -> None:
        with get_session() as s:
            row = s.get(ProductoInventarioORM, producto.sku)
            if row:
                row.nombre = producto.nombre
                row.stock = producto.stock
                row.stock_minimo = producto.stock_minimo
                s.commit()

    def listar_bajo_stock(self) -> list[ProductoInventario]:
        with get_session() as s:
            rows = (
                s.query(ProductoInventarioORM)
                .filter(ProductoInventarioORM.stock <= ProductoInventarioORM.stock_minimo)
                .all()
            )
            return [_a_dominio(r) for r in rows]
