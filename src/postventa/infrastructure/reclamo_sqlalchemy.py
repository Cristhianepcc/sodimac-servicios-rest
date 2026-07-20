"""Repositorio SQLAlchemy de Reclamo (PostgreSQL)."""
from __future__ import annotations

from src.postventa.domain.reclamo import EstadoReclamo, IReclamoRepositorio, Reclamo
from src.shared.db import get_session

from .orm import ReclamoORM


def _a_dominio(row: ReclamoORM) -> Reclamo:
    return Reclamo(
        id=row.id,
        cliente=row.cliente,
        producto=row.producto,
        motivo=row.motivo,
        estado=EstadoReclamo(row.estado),
    )


class ReclamoRepositorioSQLAlchemy(IReclamoRepositorio):
    def adicionar(self, reclamo: Reclamo) -> None:
        with get_session() as s:
            s.add(
                ReclamoORM(
                    id=reclamo.id,
                    cliente=reclamo.cliente,
                    producto=reclamo.producto,
                    motivo=reclamo.motivo,
                    estado=reclamo.estado.value,
                )
            )
            s.commit()

    def buscar(self, reclamo_id: str) -> Reclamo | None:
        with get_session() as s:
            row = s.get(ReclamoORM, reclamo_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[Reclamo]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(ReclamoORM).all()]
