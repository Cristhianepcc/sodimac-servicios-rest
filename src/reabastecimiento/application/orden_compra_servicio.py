from __future__ import annotations

from src.reabastecimiento.domain.orden_compra import OrdenCompra, OrdenCompraFabrica
from src.reabastecimiento.infrastructure import get_orden_compra_repositorio
from src.shared.errores import NoEncontrado


class OrdenCompraServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_orden_compra_repositorio()

    def generar(self, proveedor_id: str, lineas: list[dict]) -> OrdenCompra:
        orden = OrdenCompraFabrica.crear(proveedor_id, lineas)
        self._repo.adicionar(orden)
        return orden

    def obtener(self, orden_id: str) -> OrdenCompra:
        orden = self._repo.buscar(orden_id)
        if orden is None:
            raise NoEncontrado(f"No existe la orden de compra '{orden_id}'.")
        return orden

    def listar(self) -> list[OrdenCompra]:
        return self._repo.listar()

    def autorizar(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener(orden_id)
        orden.autorizar()
        self._repo.actualizar(orden)
        return orden

    def cancelar(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener(orden_id)
        orden.cancelar()
        self._repo.actualizar(orden)
        return orden

    def enviar(self, orden_id: str) -> OrdenCompra:
        orden = self.obtener(orden_id)
        orden.enviar()
        self._repo.actualizar(orden)
        return orden
