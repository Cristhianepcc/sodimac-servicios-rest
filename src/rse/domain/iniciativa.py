"""Dominio del proceso `rse` — Iniciativa RSE (agregado completo).

Reutiliza el Business Data Model (BDM) del Laboratorio 5 (proceso BPM
"Gestión de RSE y Sostenibilidad"). El agregado raíz `IniciativaRSE` encapsula
sus composiciones (KPIs, evidencias, reporte, acciones correctivas) y las
invariantes del proceso. Python puro (sin Flask ni SQLAlchemy).
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

from src.shared.errores import ErrorDominio


class TipoIniciativa(str, Enum):
    RECICLAJE = "RECICLAJE"
    EFICIENCIA_ENERGETICA = "EFICIENCIA_ENERGETICA"
    VOLUNTARIADO = "VOLUNTARIADO"
    PROVEEDORES_SOSTENIBLES = "PROVEEDORES_SOSTENIBLES"


class EstadoIniciativa(str, Enum):
    FORMULADA = "FORMULADA"
    EN_EVALUACION = "EN_EVALUACION"
    APROBADA = "APROBADA"
    ARCHIVADA = "ARCHIVADA"
    EN_EJECUCION = "EN_EJECUCION"
    EN_MONITOREO = "EN_MONITOREO"
    REPORTADA = "REPORTADA"
    PUBLICADA = "PUBLICADA"


# --- Composiciones del agregado (BDM Lab 5) ---

@dataclass
class IndicadorKPI:
    nombre: str
    unidad: str
    valor_linea_base: float = 0.0
    valor_actual: float = 0.0
    meta: float = 0.0


@dataclass
class EvidenciaAvance:
    fecha: date
    descripcion: str
    porcentaje_avance: float = 0.0
    archivo_url: str = ""


@dataclass
class AccionCorrectiva:
    descripcion: str
    responsable: str
    fecha: date


@dataclass
class ReporteSostenibilidad:
    codigo: str
    fecha_generacion: date
    resumen: str = ""
    url_publicacion: str = ""
    aprobado_publicacion: bool = False


# --- Agregado raíz ---

@dataclass
class IniciativaRSE:
    codigo: str
    nombre: str
    tipo: TipoIniciativa
    descripcion: str = ""
    requiere_presupuesto: bool = False
    presupuesto_solicitado: float = 0.0
    presupuesto_aprobado: float = 0.0
    estado: EstadoIniciativa = EstadoIniciativa.FORMULADA
    aprobada: bool = False
    metas_cumplidas: bool = False
    indicadores: list[IndicadorKPI] = field(default_factory=list)
    evidencias: list[EvidenciaAvance] = field(default_factory=list)
    acciones: list[AccionCorrectiva] = field(default_factory=list)
    reporte: ReporteSostenibilidad | None = None

    # --- Comportamiento de dominio (invariantes del proceso BPM) ---

    def evaluar(self, aprobada: bool, presupuesto_aprobado: float, comentario: str = "") -> None:
        """Caso de uso 'Evaluar' (gateway gw2 del BPM del Lab 5).

        Regla del contrato `teval`: una iniciativa aprobada requiere monto > 0.
        """
        if aprobada and presupuesto_aprobado <= 0:
            raise ErrorDominio("Una iniciativa aprobada requiere un presupuesto mayor que 0.")
        self.aprobada = aprobada
        self.presupuesto_aprobado = presupuesto_aprobado if aprobada else 0.0
        self.estado = EstadoIniciativa.APROBADA if aprobada else EstadoIniciativa.ARCHIVADA

    def agregar_indicador(self, indicador: IndicadorKPI) -> None:
        if self.estado == EstadoIniciativa.ARCHIVADA:
            raise ErrorDominio("No se pueden agregar indicadores a una iniciativa archivada.")
        self.indicadores.append(indicador)
        self.estado = EstadoIniciativa.EN_MONITOREO

    def registrar_evidencia(self, evidencia: EvidenciaAvance) -> None:
        if not 0 <= evidencia.porcentaje_avance <= 100:
            raise ErrorDominio("El porcentaje de avance debe estar entre 0 y 100.")
        self.evidencias.append(evidencia)
        self.estado = EstadoIniciativa.EN_EJECUCION

    def generar_reporte(self, resumen: str = "") -> ReporteSostenibilidad:
        if not self.aprobada:
            raise ErrorDominio("Solo una iniciativa aprobada puede generar reporte.")
        self.reporte = ReporteSostenibilidad(
            codigo=f"REP-{uuid.uuid4().hex[:6].upper()}",
            fecha_generacion=date.today(),
            resumen=resumen,
        )
        self.estado = EstadoIniciativa.REPORTADA
        return self.reporte

    def aprobar_publicacion(self, url_publicacion: str) -> None:
        if self.reporte is None:
            raise ErrorDominio("No hay reporte generado para publicar.")
        self.reporte.aprobado_publicacion = True
        self.reporte.url_publicacion = url_publicacion
        self.estado = EstadoIniciativa.PUBLICADA


# --- Fábrica ---

class IniciativaFabrica:
    @staticmethod
    def crear(
        nombre: str,
        tipo: str,
        descripcion: str = "",
        requiere_presupuesto: bool = False,
        presupuesto_solicitado: float = 0.0,
    ) -> IniciativaRSE:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre de la iniciativa es obligatorio.")
        if presupuesto_solicitado < 0:
            raise ErrorDominio("El presupuesto no puede ser negativo.")
        if requiere_presupuesto and presupuesto_solicitado <= 0:
            raise ErrorDominio("Si requiere presupuesto, debe ser mayor que 0.")
        try:
            tipo_enum = TipoIniciativa(tipo)
        except ValueError:
            validos = ", ".join(t.value for t in TipoIniciativa)
            raise ErrorDominio(f"Tipo inválido '{tipo}'. Permitidos: {validos}.")
        return IniciativaRSE(
            codigo=f"RSE-{uuid.uuid4().hex[:8].upper()}",
            nombre=nombre.strip(),
            tipo=tipo_enum,
            descripcion=descripcion,
            requiere_presupuesto=requiere_presupuesto,
            presupuesto_solicitado=presupuesto_solicitado,
            estado=EstadoIniciativa.FORMULADA,
        )

    @staticmethod
    def desde_convocatoria(
        codigo: str,
        nombre: str,
        tipo: str,
        presupuesto_aprobado: float = 0.0,
        requisitos: str = "",
    ) -> IniciativaRSE:
        """Reconstruye una iniciativa a partir de la convocatoria del proceso BPM.

        A diferencia de `crear()`, el **código lo impone Bonita** (es la clave
        de correlación entre la instancia del proceso y el agregado de este
        servicio) y la iniciativa llega ya aprobada: el proceso solo publica la
        convocatoria después de pasar el gateway de aprobación del comité.
        """
        if not codigo or not codigo.strip():
            raise ErrorDominio("La convocatoria debe traer el código de la iniciativa.")
        if not nombre or not nombre.strip():
            raise ErrorDominio("La convocatoria debe traer el nombre de la iniciativa.")
        if presupuesto_aprobado <= 0:
            raise ErrorDominio(
                "Una convocatoria proviene de una iniciativa aprobada: "
                "el presupuesto debe ser mayor que 0."
            )
        try:
            tipo_enum = TipoIniciativa(tipo)
        except ValueError:
            validos = ", ".join(t.value for t in TipoIniciativa)
            raise ErrorDominio(f"Tipo inválido '{tipo}'. Permitidos: {validos}.")

        return IniciativaRSE(
            codigo=codigo.strip(),
            nombre=nombre.strip(),
            tipo=tipo_enum,
            descripcion=requisitos,
            requiere_presupuesto=True,
            presupuesto_solicitado=presupuesto_aprobado,
            presupuesto_aprobado=presupuesto_aprobado,
            estado=EstadoIniciativa.APROBADA,
            aprobada=True,
        )


# --- Puerto (interfaz de repositorio) ---

class IIniciativaRepositorio(ABC):
    @abstractmethod
    def adicionar(self, iniciativa: IniciativaRSE) -> None: ...

    @abstractmethod
    def buscar(self, codigo: str) -> IniciativaRSE | None: ...

    @abstractmethod
    def actualizar(self, iniciativa: IniciativaRSE) -> None: ...

    @abstractmethod
    def listar(self) -> list[IniciativaRSE]: ...
