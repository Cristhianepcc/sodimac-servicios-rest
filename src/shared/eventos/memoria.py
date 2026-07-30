"""Doble de prueba del broker: colas en memoria.

Permite ejecutar y probar los casos de uso guiados por eventos sin levantar
RabbitMQ (mismo criterio que `*_memoria.py` en los repositorios).
"""
from __future__ import annotations

from collections import defaultdict

from .puerto import (
    ConsumidorEventos,
    EventoIntegracion,
    ManejadorEvento,
    PublicadorEventos,
)


class PublicadorMemoria(PublicadorEventos):
    """Acumula lo publicado para poder inspeccionarlo en las pruebas."""

    def __init__(self) -> None:
        self.publicados: dict[str, list[EventoIntegracion]] = defaultdict(list)

    def publicar(self, cola: str, evento: EventoIntegracion) -> None:
        self.publicados[cola].append(evento)

    def eventos_de(self, cola: str) -> list[EventoIntegracion]:
        return list(self.publicados[cola])

    def limpiar(self) -> None:
        self.publicados.clear()

    def cerrar(self) -> None:  # nada que liberar
        return None


class ConsumidorMemoria(ConsumidorEventos):
    """Entrega síncrona: `entregar()` invoca los manejadores suscritos."""

    def __init__(self) -> None:
        self._manejadores: dict[str, list[ManejadorEvento]] = defaultdict(list)

    def suscribir(self, cola: str, manejador: ManejadorEvento) -> None:
        self._manejadores[cola].append(manejador)

    def entregar(self, cola: str, evento: EventoIntegracion) -> None:
        for manejador in self._manejadores[cola]:
            manejador(evento)

    def escuchar(self) -> None:  # no bloquea: la entrega es explícita
        return None
