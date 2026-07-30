"""Servicio de dominio: evaluación del cumplimiento de metas de una iniciativa.

Es un **servicio de dominio** y no un método del agregado porque la regla
"¿se cumplieron las metas?" combina la política de tolerancia de la
organización con el conjunto de KPIs, y no es responsabilidad de un
`IndicadorKPI` individual ni un estado que `IniciativaRSE` deba conocer:
la iniciativa guarda el resultado, no la política que lo produce.

Corresponde al gateway **«¿Metas cumplidas?»** del proceso BPM: la misma
decisión que en Bonita toma el flujo, aquí es una regla de negocio explícita y
probada, invocable tanto por HTTP como por un evento de RabbitMQ.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.shared.errores import ErrorDominio

from .iniciativa import IndicadorKPI, IniciativaRSE


@dataclass(frozen=True)
class ResultadoEvaluacion:
    """Veredicto del servicio (objeto de valor)."""

    cumplidas: bool
    porcentaje_global: float
    indicadores_cumplidos: int
    indicadores_totales: int
    rezagados: tuple[str, ...]

    @property
    def requiere_acciones_correctivas(self) -> bool:
        return not self.cumplidas


class EvaluadorDeMetas:
    """Decide si una iniciativa cumplió sus metas.

    `tolerancia` es la fracción de la meta que basta para darla por cumplida
    (0.9 = se acepta alcanzar el 90 %). Es política de la organización, por eso
    se inyecta en vez de estar fija en el agregado.
    """

    def __init__(self, tolerancia: float = 0.9) -> None:
        if not 0 < tolerancia <= 1:
            raise ErrorDominio("La tolerancia debe estar en el rango (0, 1].")
        self._tolerancia = tolerancia

    def evaluar(self, iniciativa: IniciativaRSE) -> ResultadoEvaluacion:
        indicadores = iniciativa.indicadores
        if not indicadores:
            raise ErrorDominio(
                "No se puede evaluar el cumplimiento sin indicadores registrados."
            )

        cumplidos = [k for k in indicadores if self._cumple(k)]
        rezagados = tuple(k.nombre for k in indicadores if not self._cumple(k))

        avances = [self._avance(k) for k in indicadores]
        porcentaje_global = round(sum(avances) / len(avances) * 100, 2)

        return ResultadoEvaluacion(
            cumplidas=len(rezagados) == 0,
            porcentaje_global=porcentaje_global,
            indicadores_cumplidos=len(cumplidos),
            indicadores_totales=len(indicadores),
            rezagados=rezagados,
        )

    # --- Reglas ---

    def _avance(self, kpi: IndicadorKPI) -> float:
        """Progreso relativo desde la línea base hacia la meta, acotado a [0, 1].

        Se mide contra el recorrido `meta - línea base`, no contra la meta
        absoluta: una iniciativa que parte de 40 y debe llegar a 50 no está al
        80 % el primer día. Si meta y línea base coinciden, no hay recorrido y
        el KPI cuenta como cumplido.
        """
        recorrido = kpi.meta - kpi.valor_linea_base
        if recorrido == 0:
            return 1.0
        avance = (kpi.valor_actual - kpi.valor_linea_base) / recorrido
        return max(0.0, min(1.0, avance))

    def _cumple(self, kpi: IndicadorKPI) -> bool:
        return self._avance(kpi) >= self._tolerancia
