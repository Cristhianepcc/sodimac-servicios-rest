"""Repositorio SQLAlchemy de Reclamo (PostgreSQL)."""
from __future__ import annotations

from sqlalchemy import or_

from src.postventa.domain.reclamo import EstadoReclamo, IReclamoRepositorio, Reclamo
from src.shared.db import get_session

from .orm import ReclamoORM


def _a_dominio(row: ReclamoORM) -> Reclamo:
    return Reclamo(
        id=row.id,
        cliente=row.cliente,
        dni=row.dni,
        email=row.email,
        telefono=row.telefono,
        producto=row.producto,
        motivo=row.motivo,
        estado=EstadoReclamo(row.estado),
        cumple_garantia=row.cumple_garantia,
        motivo_validacion=row.motivo_validacion,
        diagnostico=row.diagnostico,
        procede_evaluacion=row.procede_evaluacion,
        tipo_solucion=row.tipo_solucion,
        mensaje_cliente=row.mensaje_cliente,
        fecha_cierre=row.fecha_cierre,
        fecha_notificacion=row.fecha_notificacion,
    )


class ReclamoRepositorioSQLAlchemy(IReclamoRepositorio):
    def adicionar(self, reclamo: Reclamo) -> None:
        with get_session() as s:
            s.add(
                ReclamoORM(
                    id=reclamo.id,
                    cliente=reclamo.cliente,
                    dni=reclamo.dni,
                    email=reclamo.email,
                    telefono=reclamo.telefono,
                    producto=reclamo.producto,
                    motivo=reclamo.motivo,
                    estado=reclamo.estado.value,
                    cumple_garantia=reclamo.cumple_garantia,
                    motivo_validacion=reclamo.motivo_validacion,
                    diagnostico=reclamo.diagnostico,
                    procede_evaluacion=reclamo.procede_evaluacion,
                    tipo_solucion=reclamo.tipo_solucion,
                    mensaje_cliente=reclamo.mensaje_cliente,
                    fecha_cierre=reclamo.fecha_cierre,
                    fecha_notificacion=reclamo.fecha_notificacion,
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

    def actualizar(self, reclamo: Reclamo) -> None:
        with get_session() as s:
            row = s.get(ReclamoORM, reclamo.id)
            if row is None:
                return
            row.cliente = reclamo.cliente
            row.dni = reclamo.dni
            row.email = reclamo.email
            row.telefono = reclamo.telefono
            row.producto = reclamo.producto
            row.motivo = reclamo.motivo
            row.estado = reclamo.estado.value
            row.cumple_garantia = reclamo.cumple_garantia
            row.motivo_validacion = reclamo.motivo_validacion
            row.diagnostico = reclamo.diagnostico
            row.procede_evaluacion = reclamo.procede_evaluacion
            row.tipo_solucion = reclamo.tipo_solucion
            row.mensaje_cliente = reclamo.mensaje_cliente
            row.fecha_cierre = reclamo.fecha_cierre
            row.fecha_notificacion = reclamo.fecha_notificacion
            s.commit()

    def listar_abiertos(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        with get_session() as s:
            q = s.query(ReclamoORM).filter(
                or_(
                    ReclamoORM.fecha_cierre.is_(None),
                    ReclamoORM.estado != EstadoReclamo.RESUELTO.value,
                )
            )
            total = q.count()
            rows = q.order_by(ReclamoORM.id).offset((page - 1) * size).limit(size).all()
            return [_a_dominio(r) for r in rows], total

    def listar_para_evaluacion(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        with get_session() as s:
            q = s.query(ReclamoORM).filter(ReclamoORM.cumple_garantia.is_(True))
            total = q.count()
            rows = q.order_by(ReclamoORM.id).offset((page - 1) * size).limit(size).all()
            return [_a_dominio(r) for r in rows], total

    def listar_para_solucion(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        with get_session() as s:
            q = s.query(ReclamoORM).filter(ReclamoORM.procede_evaluacion.is_(True))
            total = q.count()
            rows = q.order_by(ReclamoORM.id).offset((page - 1) * size).limit(size).all()
            return [_a_dominio(r) for r in rows], total
