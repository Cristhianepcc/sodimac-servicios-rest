"""Servicio de aplicación del Inventario (casos de uso)."""
from __future__ import annotations

from src.reabastecimiento.domain.inventario import ProductoFabrica, ProductoInventario
from src.reabastecimiento.infrastructure import get_inventario_repositorio
from src.shared.errores import Conflicto, NoEncontrado


class InventarioServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_inventario_repositorio()

    def registrar_producto(
        self, sku: str, nombre: str, stock: int = 0, stock_minimo: int = 0
    ) -> ProductoInventario:
        if self._repo.buscar(sku):
            raise Conflicto(f"Ya existe un producto con SKU '{sku}'.")
        producto = ProductoFabrica.crear(sku, nombre, stock, stock_minimo)
        self._repo.adicionar(producto)
        return producto

    def consultar_stock(self, sku: str) -> ProductoInventario:
        producto = self._repo.buscar(sku)
        if producto is None:
            raise NoEncontrado(f"No existe el producto '{sku}'.")
        return producto

    def actualizar_stock(self, sku: str, nuevo_stock: int) -> ProductoInventario:
        producto = self.consultar_stock(sku)
        producto.actualizar_stock(nuevo_stock)
        self._repo.actualizar(producto)
        return producto

    def listar_bajo_stock(self) -> list[ProductoInventario]:
        return self._repo.listar_bajo_stock()
