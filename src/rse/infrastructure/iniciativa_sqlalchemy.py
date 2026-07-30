"""Repositorio SQLAlchemy de Iniciativa RSE (PostgreSQL).

Traduce el agregado (con sus composiciones) entre dominio y ORM.
"""
from __future__ import annotations

from src.rse.domain.iniciativa import (
    AccionCorrectiva,
    EstadoIniciativa,
    EvidenciaAvance,
    IIniciativaRepositorio,
    IndicadorKPI,
    IniciativaRSE,
    ReporteSostenibilidad,
    TipoIniciativa,
)
from src.shared.db import get_session

from .orm import (
    AccionCorrectivaORM,
    EvidenciaAvanceORM,
    IndicadorKPIORM,
    IniciativaRSEORM,
    ReporteSostenibilidadORM,
)


def _a_dominio(row: IniciativaRSEORM) -> IniciativaRSE:
    ini = IniciativaRSE(
        codigo=row.codigo,
        nombre=row.nombre,
        tipo=TipoIniciativa(row.tipo),
        descripcion=row.descripcion,
        requiere_presupuesto=row.requiere_presupuesto,
        presupuesto_solicitado=row.presupuesto_solicitado,
        presupuesto_aprobado=row.presupuesto_aprobado,
        estado=EstadoIniciativa(row.estado),
        aprobada=row.aprobada,
        metas_cumplidas=row.metas_cumplidas,
        comentario_evaluacion=row.comentario_evaluacion,
    )
    ini.indicadores = [
        IndicadorKPI(i.nombre, i.unidad, i.valor_linea_base, i.valor_actual, i.meta)
        for i in row.indicadores
    ]
    ini.evidencias = [
        EvidenciaAvance(e.fecha, e.descripcion, e.porcentaje_avance, e.archivo_url)
        for e in row.evidencias
    ]
    ini.acciones = [
        AccionCorrectiva(a.descripcion, a.responsable, a.fecha) for a in row.acciones
    ]
    if row.reporte is not None:
        ini.reporte = ReporteSostenibilidad(
            codigo=row.reporte.codigo,
            fecha_generacion=row.reporte.fecha_generacion,
            resumen=row.reporte.resumen,
            url_publicacion=row.reporte.url_publicacion,
            aprobado_publicacion=row.reporte.aprobado_publicacion,
        )
    return ini


def _volcar_hijos(row: IniciativaRSEORM, ini: IniciativaRSE) -> None:
    row.indicadores = [
        IndicadorKPIORM(
            nombre=i.nombre,
            unidad=i.unidad,
            valor_linea_base=i.valor_linea_base,
            valor_actual=i.valor_actual,
            meta=i.meta,
        )
        for i in ini.indicadores
    ]
    row.evidencias = [
        EvidenciaAvanceORM(
            fecha=e.fecha,
            descripcion=e.descripcion,
            porcentaje_avance=e.porcentaje_avance,
            archivo_url=e.archivo_url,
        )
        for e in ini.evidencias
    ]
    row.acciones = [
        AccionCorrectivaORM(descripcion=a.descripcion, responsable=a.responsable, fecha=a.fecha)
        for a in ini.acciones
    ]
    row.reporte = (
        ReporteSostenibilidadORM(
            codigo=ini.reporte.codigo,
            fecha_generacion=ini.reporte.fecha_generacion,
            resumen=ini.reporte.resumen,
            url_publicacion=ini.reporte.url_publicacion,
            aprobado_publicacion=ini.reporte.aprobado_publicacion,
        )
        if ini.reporte is not None
        else None
    )


def _volcar_escalares(row: IniciativaRSEORM, ini: IniciativaRSE) -> None:
    row.nombre = ini.nombre
    row.tipo = ini.tipo.value
    row.descripcion = ini.descripcion
    row.requiere_presupuesto = ini.requiere_presupuesto
    row.presupuesto_solicitado = ini.presupuesto_solicitado
    row.presupuesto_aprobado = ini.presupuesto_aprobado
    row.estado = ini.estado.value
    row.aprobada = ini.aprobada
    row.metas_cumplidas = ini.metas_cumplidas
    row.comentario_evaluacion = ini.comentario_evaluacion


class IniciativaRepositorioSQLAlchemy(IIniciativaRepositorio):
    def adicionar(self, iniciativa: IniciativaRSE) -> None:
        with get_session() as s:
            row = IniciativaRSEORM(codigo=iniciativa.codigo)
            _volcar_escalares(row, iniciativa)
            _volcar_hijos(row, iniciativa)
            s.add(row)
            s.commit()

    def buscar(self, codigo: str) -> IniciativaRSE | None:
        with get_session() as s:
            row = s.get(IniciativaRSEORM, codigo)
            return _a_dominio(row) if row else None

    def actualizar(self, iniciativa: IniciativaRSE) -> None:
        with get_session() as s:
            row = s.get(IniciativaRSEORM, iniciativa.codigo)
            if row is None:
                return
            _volcar_escalares(row, iniciativa)
            _volcar_hijos(row, iniciativa)
            s.commit()

    def listar(self) -> list[IniciativaRSE]:
        with get_session() as s:
            return [_a_dominio(r) for r in s.query(IniciativaRSEORM).all()]
