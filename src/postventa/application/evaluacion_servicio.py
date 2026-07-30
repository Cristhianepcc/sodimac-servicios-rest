"""Servicio de aplicacion para evaluaciones de reclamos."""
from __future__ import annotations

from src.postventa.application.reclamo_servicio import ReclamoServicio
from src.postventa.domain.reclamo import Reclamo


class EvaluacionServicio:
    def __init__(self, reclamo_servicio: ReclamoServicio | None = None) -> None:
        self._reclamos = reclamo_servicio or ReclamoServicio()

    def registrar(self, reclamo_id: str, diagnostico: str, procede: bool) -> Reclamo:
        return self._reclamos.actualizar_evaluacion(reclamo_id, diagnostico, procede)

    def listar(self, page: int = 1, size: int = 20) -> dict:
        return self._reclamos.listar_para_evaluacion(page, size)
