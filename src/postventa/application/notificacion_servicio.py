"""Servicio de aplicacion para notificaciones simuladas."""
from __future__ import annotations

from src.postventa.application.reclamo_servicio import ReclamoServicio
from src.postventa.domain.reclamo import Reclamo


class NotificacionServicio:
    def __init__(self, reclamo_servicio: ReclamoServicio | None = None) -> None:
        self._reclamos = reclamo_servicio or ReclamoServicio()

    def enviar(self, reclamo_id: str, mensaje: str) -> Reclamo:
        return self._reclamos.registrar_notificacion(reclamo_id, mensaje)
