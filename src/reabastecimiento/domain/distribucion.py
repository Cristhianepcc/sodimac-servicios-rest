from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoPedidoDistribucion(str, Enum):
    SOLICITADO = "SOLICITADO"
    EN_PICKING = "EN_PICKING"
    EN_PACKING = "EN_PACKING"
    DESPACHADO = "DESPACHADO"
    EN_TRANSITO = "EN_TRANSITO"
    ENTREGADO = "ENTREGADO"


class EstadoEnvio(str, Enum):
    PREPARADO = "PREPARADO"
    DESPACHADO = "DESPACHADO"
    EN_TRANSITO = "EN_TRANSITO"
    ENTREGADO = "ENTREGADO"


@dataclass
class ItemPedido:
    sku: str
    cantidad: int


@dataclass
class PedidoDistribucion:
    id: str
    tienda_destino: str
    fecha_solicitud: str
    estado: EstadoPedidoDistribucion = EstadoPedidoDistribucion.SOLICITADO
    items: list[ItemPedido] = field(default_factory=list)

    def iniciar_picking(self) -> None:
        if self.estado != EstadoPedidoDistribucion.SOLICITADO:
            raise ErrorDominio("Solo pedidos solicitados pueden pasar a picking.")
        self.estado = EstadoPedidoDistribucion.EN_PICKING

    def completar_packing(self) -> None:
        if self.estado != EstadoPedidoDistribucion.EN_PICKING:
            raise ErrorDominio("Debe completar el picking antes del packing.")
        self.estado = EstadoPedidoDistribucion.EN_PACKING


@dataclass
class Envio:
    id: str
    pedido_id: str
    transportista: str = ""
    fecha_despacho: str | None = None
    estado: EstadoEnvio = EstadoEnvio.PREPARADO

    def despachar(self, transportista: str) -> None:
        if self.estado != EstadoEnvio.PREPARADO:
            raise ErrorDominio("Solo envíos preparados pueden despacharse.")
        if not transportista or not transportista.strip():
            raise ErrorDominio("Debe indicar el transportista.")
        self.transportista = transportista.strip()
        self.fecha_despacho = datetime.now(timezone.utc).isoformat()
        self.estado = EstadoEnvio.DESPACHADO

    def actualizar_estado(self, nuevo_estado: EstadoEnvio) -> None:
        orden_valido = {
            EstadoEnvio.DESPACHADO: [EstadoEnvio.PREPARADO],
            EstadoEnvio.EN_TRANSITO: [EstadoEnvio.DESPACHADO],
            EstadoEnvio.ENTREGADO: [EstadoEnvio.EN_TRANSITO],
        }
        if nuevo_estado not in orden_valido or self.estado not in orden_valido[nuevo_estado]:
            raise ErrorDominio(f"No se puede pasar de {self.estado.value} a {nuevo_estado.value}.")
        self.estado = nuevo_estado

    def registrar_llegada(self) -> None:
        if self.estado != EstadoEnvio.EN_TRANSITO:
            raise ErrorDominio("Solo envíos en tránsito pueden registrar llegada.")
        self.estado = EstadoEnvio.ENTREGADO


class PedidoDistribucionFabrica:
    @staticmethod
    def crear(tienda_destino: str, items: list[dict]) -> PedidoDistribucion:
        if not tienda_destino or not tienda_destino.strip():
            raise ErrorDominio("La tienda destino es obligatoria.")
        if not items:
            raise ErrorDominio("El pedido debe tener al menos un item.")
        items_dominio = [
            ItemPedido(sku=i["sku"], cantidad=int(i["cantidad"]))
            for i in items
        ]
        for it in items_dominio:
            if it.cantidad <= 0:
                raise ErrorDominio("La cantidad debe ser mayor a cero.")
        return PedidoDistribucion(
            id=f"PD-{uuid.uuid4().hex[:8].upper()}",
            tienda_destino=tienda_destino.strip(),
            fecha_solicitud=datetime.now(timezone.utc).isoformat(),
            items=items_dominio,
        )


class EnvioFabrica:
    @staticmethod
    def crear(pedido_id: str) -> Envio:
        if not pedido_id or not pedido_id.strip():
            raise ErrorDominio("El ID del pedido es obligatorio.")
        return Envio(
            id=f"ENV-{uuid.uuid4().hex[:8].upper()}",
            pedido_id=pedido_id.strip(),
        )


class IDistribucionRepositorio(ABC):
    @abstractmethod
    def adicionar_pedido(self, pedido: PedidoDistribucion) -> None: ...
    @abstractmethod
    def buscar_pedido(self, pedido_id: str) -> PedidoDistribucion | None: ...
    @abstractmethod
    def listar_pedidos(self) -> list[PedidoDistribucion]: ...
    @abstractmethod
    def actualizar_pedido(self, pedido: PedidoDistribucion) -> None: ...
    @abstractmethod
    def adicionar_envio(self, envio: Envio) -> None: ...
    @abstractmethod
    def buscar_envio(self, envio_id: str) -> Envio | None: ...
    @abstractmethod
    def actualizar_envio(self, envio: Envio) -> None: ...
    @abstractmethod
    def buscar_envio_por_pedido(self, pedido_id: str) -> Envio | None: ...
