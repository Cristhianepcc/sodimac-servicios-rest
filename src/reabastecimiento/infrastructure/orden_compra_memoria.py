from __future__ import annotations

from src.reabastecimiento.domain.orden_compra import IOrdenCompraRepositorio, OrdenCompra


class OrdenCompraRepositorioMemoria(IOrdenCompraRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, OrdenCompra] = {}

    def adicionar(self, orden: OrdenCompra) -> None:
        self._datos[orden.id] = orden

    def buscar(self, orden_id: str) -> OrdenCompra | None:
        return self._datos.get(orden_id)

    def listar(self) -> list[OrdenCompra]:
        return list(self._datos.values())

    def actualizar(self, orden: OrdenCompra) -> None:
        self._datos[orden.id] = orden
