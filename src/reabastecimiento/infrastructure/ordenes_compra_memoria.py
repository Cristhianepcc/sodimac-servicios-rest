"""Repositorio en memoria del servicio de Órdenes de Compra."""
from __future__ import annotations

from src.reabastecimiento.domain.ordenes_compra import IOrdenCompraRepositorio, OrdenCompra


class OrdenCompraRepositorioMemoria(IOrdenCompraRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, OrdenCompra] = {}

    def adicionar(self, orden: OrdenCompra) -> None:
        self._datos[orden.id] = orden

    def buscar(self, orden_id: str) -> OrdenCompra | None:
        return self._datos.get(orden_id)

    def eliminar(self, orden_id: str) -> None:
        self._datos.pop(orden_id, None)

    def actualizar(self, orden: OrdenCompra) -> None:
        self._datos[orden.id] = orden
