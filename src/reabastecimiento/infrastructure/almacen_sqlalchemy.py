from __future__ import annotations

from src.reabastecimiento.domain.almacen import IAlmacenRepositorio, MercaderiaUbicada, Ubicacion
from src.shared.db import get_session

from .orm import MercaderiaUbicadaORM, UbicacionORM


class AlmacenRepositorioSQLAlchemy(IAlmacenRepositorio):
    def adicionar_ubicacion(self, ubicacion: Ubicacion) -> None:
        with get_session() as s:
            s.add(UbicacionORM(codigo=ubicacion.codigo, pasillo=ubicacion.pasillo, estante=ubicacion.estante, nivel=ubicacion.nivel))
            s.commit()

    def buscar_ubicacion(self, codigo: str) -> Ubicacion | None:
        with get_session() as s:
            row = s.get(UbicacionORM, codigo)
            return Ubicacion(codigo=row.codigo, pasillo=row.pasillo, estante=row.estante, nivel=row.nivel) if row else None

    def listar_ubicaciones(self) -> list[Ubicacion]:
        with get_session() as s:
            return [Ubicacion(codigo=r.codigo, pasillo=r.pasillo, estante=r.estante, nivel=r.nivel) for r in s.query(UbicacionORM).all()]

    def ubicar_mercaderia(self, mercaderia: MercaderiaUbicada) -> None:
        with get_session() as s:
            s.add(MercaderiaUbicadaORM(
                id=mercaderia.id, sku=mercaderia.sku, ubicacion_codigo=mercaderia.ubicacion_codigo,
                cantidad=mercaderia.cantidad, fecha_ubicacion=mercaderia.fecha_ubicacion,
            ))
            s.commit()

    def buscar_por_sku(self, sku: str) -> list[MercaderiaUbicada]:
        with get_session() as s:
            rows = s.query(MercaderiaUbicadaORM).filter_by(sku=sku).all()
            return [MercaderiaUbicada(id=r.id, sku=r.sku, ubicacion_codigo=r.ubicacion_codigo, cantidad=r.cantidad, fecha_ubicacion=r.fecha_ubicacion) for r in rows]

    def listar_toda_mercaderia(self) -> list[MercaderiaUbicada]:
        with get_session() as s:
            rows = s.query(MercaderiaUbicadaORM).all()
            return [MercaderiaUbicada(id=r.id, sku=r.sku, ubicacion_codigo=r.ubicacion_codigo, cantidad=r.cantidad, fecha_ubicacion=r.fecha_ubicacion) for r in rows]

    def actualizar_inventario_ubicacion(self, sku: str, ubicacion_codigo: str, cantidad: int) -> None:
        with get_session() as s:
            row = s.query(MercaderiaUbicadaORM).filter_by(sku=sku, ubicacion_codigo=ubicacion_codigo).first()
            if row:
                row.cantidad = cantidad
                s.commit()
