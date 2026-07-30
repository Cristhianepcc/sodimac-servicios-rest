"""Repositorio SQLAlchemy del servicio de Proveedores (PostgreSQL)."""
from __future__ import annotations

from src.reabastecimiento.domain.proveedor import (
    EstadoProveedor,
    IProveedorRepositorio,
    Proveedor,
)
from src.shared.db import get_session

from .orm import ProveedorORM


def _a_dominio(row: ProveedorORM) -> Proveedor:
    return Proveedor(
        id=row.id,
        nombre=row.nombre,
        ruc=row.ruc,
        puntaje=row.puntaje,
        estado=EstadoProveedor(row.estado),
    )


class ProveedorRepositorioSQLAlchemy(IProveedorRepositorio):
    def adicionar(self, proveedor: Proveedor) -> None:
        with get_session() as s:
            s.add(
                ProveedorORM(
                    id=proveedor.id,
                    nombre=proveedor.nombre,
                    ruc=proveedor.ruc,
                    puntaje=proveedor.puntaje,
                    estado=proveedor.estado.value,
                )
            )
            s.commit()

    def buscar(self, proveedor_id: str) -> Proveedor | None:
        with get_session() as s:
            row = s.get(ProveedorORM, proveedor_id)
            return _a_dominio(row) if row else None

    def listar(self) -> list[Proveedor]:
        with get_session() as s:
            rows = s.query(ProveedorORM).all()
            return [_a_dominio(r) for r in rows]

    def actualizar(self, proveedor: Proveedor) -> None:
        with get_session() as s:
            row = s.get(ProveedorORM, proveedor.id)
            if row:
                row.nombre = proveedor.nombre
                row.ruc = proveedor.ruc
                row.puntaje = proveedor.puntaje
                row.estado = proveedor.estado.value
                s.commit()
