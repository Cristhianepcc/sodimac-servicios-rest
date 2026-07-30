from __future__ import annotations

from src.reabastecimiento.domain.distribucion import (
    Envio,
    EnvioFabrica,
    EstadoEnvio,
    EstadoPedidoDistribucion,
    PedidoDistribucion,
    PedidoDistribucionFabrica,
)
from src.reabastecimiento.infrastructure import get_distribucion_repositorio
from src.shared.errores import Conflicto, NoEncontrado


class DistribucionServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_distribucion_repositorio()

    def generar_pedido(self, tienda_destino: str, items: list[dict]) -> PedidoDistribucion:
        pedido = PedidoDistribucionFabrica.crear(tienda_destino, items)
        self._repo.adicionar_pedido(pedido)
        return pedido

    def obtener_pedido(self, pedido_id: str) -> PedidoDistribucion:
        p = self._repo.buscar_pedido(pedido_id)
        if p is None:
            raise NoEncontrado(f"No existe el pedido '{pedido_id}'.")
        return p

    def listar_pedidos(self) -> list[PedidoDistribucion]:
        return self._repo.listar_pedidos()

    def iniciar_picking(self, pedido_id: str) -> PedidoDistribucion:
        p = self.obtener_pedido(pedido_id)
        p.iniciar_picking()
        self._repo.actualizar_pedido(p)
        return p

    def completar_packing(self, pedido_id: str) -> PedidoDistribucion:
        p = self.obtener_pedido(pedido_id)
        p.completar_packing()
        self._repo.actualizar_pedido(p)
        return p

    def programar_despacho(self, pedido_id: str, transportista: str) -> Envio:
        p = self.obtener_pedido(pedido_id)
        p.estado = EstadoPedidoDistribucion.DESPACHADO
        envio_existente = self._repo.buscar_envio_por_pedido(pedido_id)
        if envio_existente:
            raise Conflicto("Ya existe un envío para este pedido.")
        envio = EnvioFabrica.crear(pedido_id)
        envio.despachar(transportista)
        self._repo.actualizar_pedido(p)
        self._repo.adicionar_envio(envio)
        return envio

    def actualizar_estado_envio(self, envio_id: str, nuevo_estado: str) -> Envio:
        envio = self._repo.buscar_envio(envio_id)
        if envio is None:
            raise NoEncontrado(f"No existe el envío '{envio_id}'.")
        envio.actualizar_estado(EstadoEnvio(nuevo_estado))
        self._repo.actualizar_envio(envio)
        if nuevo_estado == EstadoEnvio.ENTREGADO.value:
            pedido = self.obtener_pedido(envio.pedido_id)
            pedido.estado = EstadoPedidoDistribucion.ENTREGADO
            self._repo.actualizar_pedido(pedido)
        return envio

    def registrar_llegada(self, envio_id: str) -> Envio:
        envio = self._repo.buscar_envio(envio_id)
        if envio is None:
            raise NoEncontrado(f"No existe el envío '{envio_id}'.")
        envio.registrar_llegada()
        self._repo.actualizar_envio(envio)
        pedido = self.obtener_pedido(envio.pedido_id)
        pedido.estado = EstadoPedidoDistribucion.ENTREGADO
        self._repo.actualizar_pedido(pedido)
        return envio


