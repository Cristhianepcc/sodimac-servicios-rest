"""Repositorio SQLAlchemy del servicio de Órdenes de Compra."""
from __future__ import annotations

from src.reabastecimiento.domain.ordenes_compra import IOrdenCompraRepositorio, LineaOC, OrdenCompra, EstadoOrdenCompra
from src.shared.db import get_session

from .orm import OrdenCompraORM, LineaOCORM


def _a_dominio(orden: OrdenCompraORM) -> OrdenCompra:
    lineas = [
        LineaOC(sku=linea.sku, cantidad=linea.cantidad, precio_unitario=linea.precio_unitario)
        for linea in orden.lineas
    ]
    return OrdenCompra(
        id=orden.id,
        proveedor_id=orden.proveedor_id,
        lineas=lineas,
        estado=EstadoOrdenCompra(orden.estado),
    )


class OrdenCompraRepositorioSQLAlchemy(IOrdenCompraRepositorio):
    def adicionar(self, orden: OrdenCompra) -> None:
        with get_session() as s:
            s.add(
                OrdenCompraORM(
                    id=orden.id,
                    proveedor_id=orden.proveedor_id,
                    estado=orden.estado.value,
                    lineas=[
                        LineaOCORM(
                            orden_id=orden.id,
                            sku=linea.sku,
                            cantidad=linea.cantidad,
                            precio_unitario=linea.precio_unitario,
                        )
                        for linea in orden.lineas
                    ],
                )
            )
            s.commit()

    def buscar(self, orden_id: str) -> OrdenCompra | None:
        with get_session() as s:
            orden = s.get(OrdenCompraORM, orden_id)
            return _a_dominio(orden) if orden else None

    def eliminar(self, orden_id: str) -> None:
        with get_session() as s:
            orden = s.get(OrdenCompraORM, orden_id)
            if orden:
                s.delete(orden)
                s.commit()

    def actualizar(self, orden: OrdenCompra) -> None:
        with get_session() as s:
            orden_row = s.get(OrdenCompraORM, orden.id)
            if orden_row:
                orden_row.proveedor_id = orden.proveedor_id
                orden_row.estado = orden.estado.value
                orden_row.lineas.clear()
                orden_row.lineas.extend(
                    [
                        LineaOCORM(
                            orden_id=orden.id,
                            sku=linea.sku,
                            cantidad=linea.cantidad,
                            precio_unitario=linea.precio_unitario,
                        )
                        for linea in orden.lineas
                    ]
                )
                s.commit()
