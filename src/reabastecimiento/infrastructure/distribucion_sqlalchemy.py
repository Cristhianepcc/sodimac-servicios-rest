from __future__ import annotations

import json

from src.reabastecimiento.domain.distribucion import (
    Envio,
    IDistribucionRepositorio,
    ItemPedido,
    PedidoDistribucion,
)
from src.shared.db import get_session

from .orm import EnvioORM, PedidoDistribucionORM


def _pedido_a_dominio(row: PedidoDistribucionORM) -> PedidoDistribucion:
    items_dict = json.loads(row.items_json)
    items = [ItemPedido(**i) for i in items_dict]
    return PedidoDistribucion(
        id=row.id, tienda_destino=row.tienda_destino, fecha_solicitud=row.fecha_solicitud,
        estado=row.estado, items=items,
    )


class DistribucionRepositorioSQLAlchemy(IDistribucionRepositorio):
    def adicionar_pedido(self, pedido: PedidoDistribucion) -> None:
        with get_session() as s:
            s.add(PedidoDistribucionORM(
                id=pedido.id, tienda_destino=pedido.tienda_destino,
                fecha_solicitud=pedido.fecha_solicitud, estado=pedido.estado.value,
                items_json=json.dumps([{"sku": i.sku, "cantidad": i.cantidad} for i in pedido.items]),
            ))
            s.commit()

    def buscar_pedido(self, pedido_id: str) -> PedidoDistribucion | None:
        with get_session() as s:
            row = s.get(PedidoDistribucionORM, pedido_id)
            return _pedido_a_dominio(row) if row else None

    def listar_pedidos(self) -> list[PedidoDistribucion]:
        with get_session() as s:
            return [_pedido_a_dominio(r) for r in s.query(PedidoDistribucionORM).all()]

    def actualizar_pedido(self, pedido: PedidoDistribucion) -> None:
        with get_session() as s:
            row = s.get(PedidoDistribucionORM, pedido.id)
            if row:
                row.estado = pedido.estado.value
                s.commit()

    def adicionar_envio(self, envio: Envio) -> None:
        with get_session() as s:
            s.add(EnvioORM(
                id=envio.id, pedido_id=envio.pedido_id, transportista=envio.transportista,
                fecha_despacho=envio.fecha_despacho, estado=envio.estado.value,
            ))
            s.commit()

    def buscar_envio(self, envio_id: str) -> Envio | None:
        with get_session() as s:
            row = s.get(EnvioORM, envio_id)
            if not row:
                return None
            return Envio(id=row.id, pedido_id=row.pedido_id, transportista=row.transportista, fecha_despacho=row.fecha_despacho, estado=row.estado)

    def actualizar_envio(self, envio: Envio) -> None:
        with get_session() as s:
            row = s.get(EnvioORM, envio.id)
            if row:
                row.estado = envio.estado.value
                row.transportista = envio.transportista
                row.fecha_despacho = envio.fecha_despacho
                s.commit()

    def buscar_envio_por_pedido(self, pedido_id: str) -> Envio | None:
        with get_session() as s:
            row = s.query(EnvioORM).filter_by(pedido_id=pedido_id).first()
            if not row:
                return None
            return Envio(id=row.id, pedido_id=row.pedido_id, transportista=row.transportista, fecha_despacho=row.fecha_despacho, estado=row.estado)
