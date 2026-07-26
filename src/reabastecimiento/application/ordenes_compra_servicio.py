"""Servicio de aplicación del servicio de Órdenes de Compra (Reabastecimiento)."""
from __future__ import annotations

from src.reabastecimiento.domain.ordenes_compra import (
    IOrdenCompraRepositorio,
    OrdenCompra,
    OrdenCompraFabrica,
)
from src.reabastecimiento.infrastructure import get_ordenes_compra_repositorio
from src.shared.errores import NoEncontrado


class OrdenCompraServicio:
    def __init__(self, repositorio: IOrdenCompraRepositorio | None = None) -> None:
        self._repo = repositorio or get_ordenes_compra_repositorio()

    def crear_orden_compra(self, proveedor_id: str, lineas: list[dict]) -> OrdenCompra:
        orden = OrdenCompraFabrica.crear(proveedor_id=proveedor_id, lineas=lineas)
        self._repo.adicionar(orden)
        return orden

    def obtener_orden_compra(self, orden_id: str) -> OrdenCompra:
        orden = self._repo.buscar(orden_id)
        if orden is None:
            raise NoEncontrado(f"No existe la orden de compra '{orden_id}'.")
        return orden

    def autorizar_orden_compra(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener_orden_compra(orden_id)
        orden.autorizar()
        self._repo.actualizar(orden)
        return orden

    def cancelar_orden_compra(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener_orden_compra(orden_id)
        orden.cancelar()
        self._repo.actualizar(orden)
        return orden

    def enviar_orden_compra(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener_orden_compra(orden_id)
        orden.enviar()
        self._repo.actualizar(orden)
        return orden
