"""Repositorio SQLAlchemy de Iniciativa RSE (PostgreSQL)."""
from __future__ import annotations

from src.rse.domain.iniciativa import (
    EstadoIniciativa,
    IIniciativaRepositorio,
    IniciativaRSE,
    TipoIniciativa,
)
from src.shared.db import get_session

from .orm import IniciativaRSEORM


def _a_dominio(row: IniciativaRSEORM) -> IniciativaRSE:
    return IniciativaRSE(
        codigo=row.codigo,
        nombre=row.nombre,
        tipo=TipoIniciativa(row.tipo),
        descripcion=row.descripcion,
        requiere_presupuesto=row.requiere_presupuesto,
        presupuesto_solicitado=row.presupuesto_solicitado,
        estado=EstadoIniciativa(row.estado),
    )


class IniciativaRepositorioSQLAlchemy(IIniciativaRepositorio):
    def adicionar(self, iniciativa: IniciativaRSE) -> None:
        with get_session() as s:
            s.add(
                IniciativaRSEORM(
                    codigo=iniciativa.codigo,
                    nombre=iniciativa.nombre,
                    tipo=iniciativa.tipo.value,
                    descripcion=iniciativa.descripcion,
                    requiere_presupuesto=iniciativa.requiere_presupuesto,
                    presupuesto_solicitado=iniciativa.presupuesto_solicitado,
                    estado=iniciativa.estado.value,
                )
            )
            s.commit()

    def buscar(self, codigo: str) -> IniciativaRSE | None:
        with get_session() as s:
            row = s.get(IniciativaRSEORM, codigo)
            return _a_dominio(row) if row else None

    def listar(self) -> list[IniciativaRSE]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(IniciativaRSEORM).all()]
