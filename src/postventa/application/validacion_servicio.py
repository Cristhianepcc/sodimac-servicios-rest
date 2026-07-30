"""Servicio de aplicacion para validar garantia de reclamos."""
from __future__ import annotations

from src.postventa.application.reclamo_servicio import ReclamoServicio
from src.postventa.domain.reclamo import Reclamo


class ValidacionServicio:
    def __init__(self, reclamo_servicio: ReclamoServicio | None = None) -> None:
        self._reclamos = reclamo_servicio or ReclamoServicio()

    def verificar(self, reclamo_id: str, cumple_garantia: bool, motivo: str) -> Reclamo:
        return self._reclamos.actualizar_garantia(reclamo_id, cumple_garantia, motivo)
