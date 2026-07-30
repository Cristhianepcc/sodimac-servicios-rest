"""Repositorio SQLAlchemy del servicio de Almacén."""
from __future__ import annotations

from src.reabastecimiento.domain.ubicacion import IUbicacionRepositorio, Ubicacion
from src.shared.db import get_session

from .orm import UbicacionORM


def _a_dominio(row: UbicacionORM) -> Ubicacion:
    return Ubicacion(codigo=row.codigo, zona=row.zona, sku=row.sku, cantidad=row.cantidad)


class UbicacionRepositorioSQLAlchemy(IUbicacionRepositorio):
    def adicionar(self, ubicacion: Ubicacion) -> None:
        with get_session() as s:
            s.add(
                UbicacionORM(
                    codigo=ubicacion.codigo.upper(),
                    zona=ubicacion.zona.upper(),
                    sku=ubicacion.sku.upper(),
                    cantidad=ubicacion.cantidad,
                )
            )
            s.commit()

    def buscar_por_codigo(self, codigo: str) -> Ubicacion | None:
        with get_session() as s:
            row = s.get(UbicacionORM, codigo.upper())
            return _a_dominio(row) if row else None

    def buscar_por_sku(self, sku: str) -> Ubicacion | None:
        with get_session() as s:
            row = s.query(UbicacionORM).filter(UbicacionORM.sku == sku.upper()).first()
            return _a_dominio(row) if row else None

    def actualizar(self, ubicacion: Ubicacion) -> None:
        with get_session() as s:
            row = s.get(UbicacionORM, ubicacion.codigo.upper())
            if row is not None:
                row.zona = ubicacion.zona.upper()
                row.sku = ubicacion.sku.upper()
                row.cantidad = ubicacion.cantidad
                s.commit()
