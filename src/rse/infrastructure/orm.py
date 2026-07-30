"""Mapeo ORM de Iniciativa RSE y sus composiciones → PostgreSQL.

El agregado IniciativaRSE se persiste con tablas hijas para indicadores,
evidencias, acciones correctivas y el reporte (1..* / 0..1). Cascada por
composición: al guardar/borrar la iniciativa se guardan/borran sus hijos.
"""
from __future__ import annotations

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.db import Base


class IniciativaRSEORM(Base):
    __tablename__ = "rse_iniciativa"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    requiere_presupuesto: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    presupuesto_solicitado: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    presupuesto_aprobado: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="FORMULADA")
    aprobada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metas_cumplidas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    indicadores: Mapped[list["IndicadorKPIORM"]] = relationship(
        back_populates="iniciativa", cascade="all, delete-orphan", lazy="selectin"
    )
    evidencias: Mapped[list["EvidenciaAvanceORM"]] = relationship(
        back_populates="iniciativa", cascade="all, delete-orphan", lazy="selectin"
    )
    acciones: Mapped[list["AccionCorrectivaORM"]] = relationship(
        back_populates="iniciativa", cascade="all, delete-orphan", lazy="selectin"
    )
    reporte: Mapped["ReporteSostenibilidadORM"] = relationship(
        back_populates="iniciativa", cascade="all, delete-orphan", uselist=False, lazy="selectin"
    )


class IndicadorKPIORM(Base):
    __tablename__ = "rse_indicador_kpi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iniciativa_codigo: Mapped[str] = mapped_column(ForeignKey("rse_iniciativa.codigo"))
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    unidad: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    valor_linea_base: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    valor_actual: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    meta: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    iniciativa: Mapped["IniciativaRSEORM"] = relationship(back_populates="indicadores")


class EvidenciaAvanceORM(Base):
    __tablename__ = "rse_evidencia_avance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iniciativa_codigo: Mapped[str] = mapped_column(ForeignKey("rse_iniciativa.codigo"))
    fecha: Mapped["Date"] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    porcentaje_avance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    archivo_url: Mapped[str] = mapped_column(String(300), nullable=False, default="")

    iniciativa: Mapped["IniciativaRSEORM"] = relationship(back_populates="evidencias")


class AccionCorrectivaORM(Base):
    __tablename__ = "rse_accion_correctiva"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    iniciativa_codigo: Mapped[str] = mapped_column(ForeignKey("rse_iniciativa.codigo"))
    descripcion: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    responsable: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    fecha: Mapped["Date"] = mapped_column(Date, nullable=False)

    iniciativa: Mapped["IniciativaRSEORM"] = relationship(back_populates="acciones")


class ReporteSostenibilidadORM(Base):
    __tablename__ = "rse_reporte_sostenibilidad"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    iniciativa_codigo: Mapped[str] = mapped_column(ForeignKey("rse_iniciativa.codigo"))
    fecha_generacion: Mapped["Date"] = mapped_column(Date, nullable=False)
    resumen: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    url_publicacion: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    aprobado_publicacion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    iniciativa: Mapped["IniciativaRSEORM"] = relationship(back_populates="reporte")
