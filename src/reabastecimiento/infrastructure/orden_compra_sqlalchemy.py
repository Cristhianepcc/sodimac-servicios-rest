from __future__ import annotations

import json

from src.reabastecimiento.domain.orden_compra import (
    EstadoOrden,
    IOrdenCompraRepositorio,
    LineaOC,
    OrdenCompra,
)
from src.shared.db import get_session

from .orm import OrdenCompraORM


def _a_dominio(row: OrdenCompraORM) -> OrdenCompra:
    lineas_dict = json.loads(row.lineas_json)
    lineas = [LineaOC(**l) for l in lineas_dict]
    return OrdenCompra(
        id=row.id,
        proveedor_id=row.proveedor_id,
        fecha_emision=row.fecha_emision,
        lineas=lineas,
        estado=EstadoOrden(row.estado),
    )


class OrdenCompraRepositorioSQLAlchemy(IOrdenCompraRepositorio):
    def adicionar(self, orden: OrdenCompra) -> None:
        with get_session() as s:
            s.add(
                OrdenCompraORM(
                    id=orden.id,
                    proveedor_id=orden.proveedor_id,
                    fecha_emision=orden.fecha_emision,
                    estado=orden.estado.value,
                    lineas_json=json.dumps(
                        [{"sku": l.sku, "cantidad": l.cantidad, "precio_unitario": l.precio_unitario} for l in orden.lineas]
                    ),
                )
            )
            s.commit()

    def buscar(self, orden_id: str) -> OrdenCompra | None:
        with get_session() as s:
            row = s.get(OrdenCompraORM, orden_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[OrdenCompra]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(OrdenCompraORM).all()]

    def actualizar(self, orden: OrdenCompra) -> None:
        with get_session() as s:
            row = s.get(OrdenCompraORM, orden.id)
            if row:
                row.estado = orden.estado.value
                s.commit()
