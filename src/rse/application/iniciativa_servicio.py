"""Servicio de aplicación de Iniciativas RSE (casos de uso del proceso completo)."""
from __future__ import annotations

from datetime import date

from src.rse.domain.evaluacion_metas import EvaluadorDeMetas, ResultadoEvaluacion
from src.rse.domain.iniciativa import (
    EvidenciaAvance,
    IndicadorKPI,
    IniciativaFabrica,
    IniciativaRSE,
)
from src.rse.infrastructure import get_iniciativa_repositorio
from src.shared.errores import NoEncontrado


class IniciativaServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_iniciativa_repositorio()

    # --- Formulación / consulta ---

    def crear(
        self,
        nombre: str,
        tipo: str,
        descripcion: str = "",
        requiere_presupuesto: bool = False,
        presupuesto_solicitado: float = 0.0,
    ) -> IniciativaRSE:
        iniciativa = IniciativaFabrica.crear(
            nombre, tipo, descripcion, requiere_presupuesto, presupuesto_solicitado
        )
        self._repo.adicionar(iniciativa)
        return iniciativa

    def obtener(self, codigo: str) -> IniciativaRSE:
        iniciativa = self._repo.buscar(codigo)
        if iniciativa is None:
            raise NoEncontrado(f"No existe la iniciativa '{codigo}'.")
        return iniciativa

    def listar(self) -> list[IniciativaRSE]:
        return self._repo.listar()

    # --- Integración guiada por eventos ---

    def sincronizar_convocatoria(
        self,
        codigo: str,
        nombre: str,
        tipo: str,
        presupuesto_aprobado: float = 0.0,
        requisitos: str = "",
    ) -> IniciativaRSE:
        """Materializa la iniciativa que anuncia el proceso BPM por RabbitMQ.

        **Idempotente**: si el código ya existe se devuelve el agregado tal
        cual. El broker entrega *al menos una vez*, así que el mismo mensaje
        puede reprocesarse y no debe duplicar ni pisar datos.
        """
        existente = self._repo.buscar(codigo)
        if existente is not None:
            return existente

        iniciativa = IniciativaFabrica.desde_convocatoria(
            codigo=codigo,
            nombre=nombre,
            tipo=tipo,
            presupuesto_aprobado=presupuesto_aprobado,
            requisitos=requisitos,
        )
        self._repo.adicionar(iniciativa)
        return iniciativa

    # --- Ciclo del proceso BPM ---

    def evaluar(self, codigo: str, aprobada: bool, presupuesto_aprobado: float,
                comentario: str = "") -> IniciativaRSE:
        iniciativa = self.obtener(codigo)
        iniciativa.evaluar(aprobada, presupuesto_aprobado, comentario)
        self._repo.actualizar(iniciativa)
        return iniciativa

    def agregar_indicador(self, codigo: str, nombre: str, unidad: str,
                          valor_linea_base: float = 0.0, valor_actual: float = 0.0,
                          meta: float = 0.0) -> IniciativaRSE:
        iniciativa = self.obtener(codigo)
        iniciativa.agregar_indicador(
            IndicadorKPI(nombre, unidad, valor_linea_base, valor_actual, meta)
        )
        self._repo.actualizar(iniciativa)
        return iniciativa

    def registrar_evidencia(self, codigo: str, descripcion: str,
                            porcentaje_avance: float, archivo_url: str = "") -> IniciativaRSE:
        iniciativa = self.obtener(codigo)
        iniciativa.registrar_evidencia(
            EvidenciaAvance(date.today(), descripcion, porcentaje_avance, archivo_url)
        )
        self._repo.actualizar(iniciativa)
        return iniciativa

    def evaluar_metas(self, codigo: str, tolerancia: float = 0.9) -> ResultadoEvaluacion:
        """Gateway «¿Metas cumplidas?» del proceso BPM.

        Delega la política al servicio de dominio y persiste el veredicto en el
        agregado, que es quien conserva el estado.
        """
        iniciativa = self.obtener(codigo)
        resultado = EvaluadorDeMetas(tolerancia).evaluar(iniciativa)
        iniciativa.metas_cumplidas = resultado.cumplidas
        self._repo.actualizar(iniciativa)
        return resultado

    def generar_reporte(self, codigo: str, resumen: str = "") -> IniciativaRSE:
        iniciativa = self.obtener(codigo)
        iniciativa.generar_reporte(resumen)
        self._repo.actualizar(iniciativa)
        return iniciativa

    def aprobar_publicacion(self, codigo: str, url_publicacion: str) -> IniciativaRSE:
        iniciativa = self.obtener(codigo)
        iniciativa.aprobar_publicacion(url_publicacion)
        self._repo.actualizar(iniciativa)
        return iniciativa
