from __future__ import annotations

import json

from src.reabastecimiento.domain.recepcion import (
    IInspeccionRepositorio,
    IRecepcionRepositorio,
    Inspeccion,
    ItemRecepcion,
    Recepcion,
)
from src.shared.db import get_session

from .orm import InspeccionORM, RecepcionORM


def _recepcion_a_dominio(row: RecepcionORM) -> Recepcion:
    items_dict = json.loads(row.items_json)
    items = [ItemRecepcion(**i) for i in items_dict]
    return Recepcion(
        id=row.id, orden_compra_id=row.orden_compra_id, fecha_llegada=row.fecha_llegada,
        estado=row.estado, items=items,
    )


class RecepcionRepositorioSQLAlchemy(IRecepcionRepositorio):
    def adicionar_recepcion(self, recepcion: Recepcion) -> None:
        with get_session() as s:
            s.add(RecepcionORM(
                id=recepcion.id, orden_compra_id=recepcion.orden_compra_id,
                fecha_llegada=recepcion.fecha_llegada, estado=recepcion.estado.value,
                items_json=json.dumps([{"sku": i.sku, "cantidad_recibida": i.cantidad_recibida} for i in recepcion.items]),
            ))
            s.commit()

    def buscar_recepcion(self, recepcion_id: str) -> Recepcion | None:
        with get_session() as s:
            row = s.get(RecepcionORM, recepcion_id)
            return _recepcion_a_dominio(row) if row else None

    def listar_recepciones(self) -> list[Recepcion]:
        with get_session() as s:
            return [_recepcion_a_dominio(r) for r in s.query(RecepcionORM).all()]

    def actualizar_recepcion(self, recepcion: Recepcion) -> None:
        with get_session() as s:
            row = s.get(RecepcionORM, recepcion.id)
            if row:
                row.estado = recepcion.estado.value
                s.commit()


class InspeccionRepositorioSQLAlchemy(IInspeccionRepositorio):
    def adicionar(self, inspeccion: Inspeccion) -> None:
        with get_session() as s:
            s.add(InspeccionORM(
                id=inspeccion.id, recepcion_id=inspeccion.recepcion_id,
                fecha=inspeccion.fecha, resultado=inspeccion.resultado.value,
                observaciones=inspeccion.observaciones,
            ))
            s.commit()

    def buscar(self, inspeccion_id: str) -> Inspeccion | None:
        with get_session() as s:
            row = s.get(InspeccionORM, inspeccion_id)
            if not row:
                return None
            return Inspeccion(
                id=row.id, recepcion_id=row.recepcion_id, fecha=row.fecha,
                resultado=row.resultado, observaciones=row.observaciones,
            )

    def listar_por_recepcion(self, recepcion_id: str) -> list[Inspeccion]:
        with get_session() as s:
            rows = s.query(InspeccionORM).filter_by(recepcion_id=recepcion_id).all()
            return [Inspeccion(id=r.id, recepcion_id=r.recepcion_id, fecha=r.fecha, resultado=r.resultado, observaciones=r.observaciones) for r in rows]

    def actualizar(self, inspeccion: Inspeccion) -> None:
        with get_session() as s:
            row = s.get(InspeccionORM, inspeccion.id)
            if row:
                row.resultado = inspeccion.resultado.value
                row.observaciones = inspeccion.observaciones
                s.commit()
