"""Servicio de aplicacion para soluciones de reclamos."""
from __future__ import annotations

from src.postventa.application.reclamo_servicio import ReclamoServicio
from src.postventa.domain.reclamo import Reclamo


class SolucionServicio:
    def __init__(self, reclamo_servicio: ReclamoServicio | None = None) -> None:
        self._reclamos = reclamo_servicio or ReclamoServicio()

    def registrar(self, reclamo_id: str, tipo_solucion: str) -> Reclamo:
        return self._reclamos.registrar_solucion(reclamo_id, tipo_solucion)

    def listar(self, page: int = 1, size: int = 20) -> dict:
        return self._reclamos.listar_para_solucion(page, size)
