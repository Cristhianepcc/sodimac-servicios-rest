from __future__ import annotations

from src.reabastecimiento.domain.distribucion import Envio, IDistribucionRepositorio, PedidoDistribucion


class DistribucionRepositorioMemoria(IDistribucionRepositorio):
    def __init__(self) -> None:
        self._pedidos: dict[str, PedidoDistribucion] = {}
        self._envios: dict[str, Envio] = {}

    def adicionar_pedido(self, pedido: PedidoDistribucion) -> None:
        self._pedidos[pedido.id] = pedido

    def buscar_pedido(self, pedido_id: str) -> PedidoDistribucion | None:
        return self._pedidos.get(pedido_id)

    def listar_pedidos(self) -> list[PedidoDistribucion]:
        return list(self._pedidos.values())

    def actualizar_pedido(self, pedido: PedidoDistribucion) -> None:
        self._pedidos[pedido.id] = pedido

    def adicionar_envio(self, envio: Envio) -> None:
        self._envios[envio.id] = envio

    def buscar_envio(self, envio_id: str) -> Envio | None:
        return self._envios.get(envio_id)

    def actualizar_envio(self, envio: Envio) -> None:
        self._envios[envio.id] = envio

    def buscar_envio_por_pedido(self, pedido_id: str) -> Envio | None:
        for e in self._envios.values():
            if e.pedido_id == pedido_id:
                return e
        return None
