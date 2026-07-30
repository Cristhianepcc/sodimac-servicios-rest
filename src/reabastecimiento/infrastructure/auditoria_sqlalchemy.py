from __future__ import annotations

from src.reabastecimiento.domain.auditoria import Auditoria, IAuditoriaRepositorio, IMovimientoStockRepositorio, MovimientoStock
from src.shared.db import get_session

from .orm import AuditoriaORM, MovimientoStockORM


class AuditoriaRepositorioSQLAlchemy(IAuditoriaRepositorio):
    def adicionar_auditoria(self, auditoria: Auditoria) -> None:
        with get_session() as s:
            s.add(AuditoriaORM(
                id=auditoria.id, sku=auditoria.sku, tipo=auditoria.tipo.value,
                fecha=auditoria.fecha, estado=auditoria.estado.value,
                observaciones=auditoria.observaciones,
            ))
            s.commit()

    def buscar_auditoria(self, auditoria_id: str) -> Auditoria | None:
        with get_session() as s:
            row = s.get(AuditoriaORM, auditoria_id)
            if not row:
                return None
            return Auditoria(id=row.id, sku=row.sku, tipo=row.tipo, fecha=row.fecha, estado=row.estado, observaciones=row.observaciones)

    def listar_auditorias(self) -> list[Auditoria]:
        with get_session() as s:
            rows = s.query(AuditoriaORM).all()
            return [Auditoria(id=r.id, sku=r.sku, tipo=r.tipo, fecha=r.fecha, estado=r.estado, observaciones=r.observaciones) for r in rows]

    def actualizar_auditoria(self, auditoria: Auditoria) -> None:
        with get_session() as s:
            row = s.get(AuditoriaORM, auditoria.id)
            if row:
                row.estado = auditoria.estado.value
                row.observaciones = auditoria.observaciones
                s.commit()


class MovimientoStockRepositorioSQLAlchemy(IMovimientoStockRepositorio):
    def adicionar(self, movimiento: MovimientoStock) -> None:
        with get_session() as s:
            s.add(MovimientoStockORM(
                id=movimiento.id, sku=movimiento.sku, tipo=movimiento.tipo.value,
                cantidad=movimiento.cantidad, motivo=movimiento.motivo,
                fecha=movimiento.fecha, usuario=movimiento.usuario,
            ))
            s.commit()

    def listar_por_sku(self, sku: str) -> list[MovimientoStock]:
        with get_session() as s:
            rows = s.query(MovimientoStockORM).filter_by(sku=sku).all()
            return [MovimientoStock(id=r.id, sku=r.sku, tipo=r.tipo, cantidad=r.cantidad, motivo=r.motivo, fecha=r.fecha, usuario=r.usuario) for r in rows]

    def listar_todos(self) -> list[MovimientoStock]:
        with get_session() as s:
            rows = s.query(MovimientoStockORM).all()
            return [MovimientoStock(id=r.id, sku=r.sku, tipo=r.tipo, cantidad=r.cantidad, motivo=r.motivo, fecha=r.fecha, usuario=r.usuario) for r in rows]
