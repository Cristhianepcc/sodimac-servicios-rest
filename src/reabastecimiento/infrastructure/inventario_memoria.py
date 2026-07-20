"""Repositorio en memoria (Fake) del servicio de Inventario."""
from __future__ import annotations

from src.reabastecimiento.domain.inventario import IProductoRepositorio, ProductoInventario


class ProductoRepositorioMemoria(IProductoRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, ProductoInventario] = {}

    def adicionar(self, producto: ProductoInventario) -> None:
        self._datos[producto.sku] = producto

    def buscar(self, sku: str) -> ProductoInventario | None:
        return self._datos.get(sku)

    def actualizar(self, producto: ProductoInventario) -> None:
        self._datos[producto.sku] = producto

    def listar_bajo_stock(self) -> list[ProductoInventario]:
        return [p for p in self._datos.values() if p.bajo_stock]
