"""Mensajería asíncrona entre los procesos de negocio (Bonita) y los servicios web.

Sigue la misma convención que los repositorios: la aplicación depende de un
**puerto** (`PublicadorEventos`) y la infraestructura provee el adaptador
(RabbitMQ o un doble en memoria). Así los casos de uso se prueban sin broker.

    EVENTOS_BACKEND=memoria   -> doble de prueba (default)
    EVENTOS_BACKEND=rabbitmq  -> adaptador AMQP real
"""
from __future__ import annotations

from config import Config

from .puerto import EventoIntegracion, ManejadorEvento, PublicadorEventos

_publicador: PublicadorEventos | None = None


def get_publicador() -> PublicadorEventos:
    """Devuelve el publicador configurado (singleton perezoso)."""
    global _publicador
    if _publicador is None:
        _publicador = _construir_publicador()
    return _publicador


def set_publicador(publicador: PublicadorEventos | None) -> None:
    """Inyecta un publicador (usado por las pruebas para aislar el broker)."""
    global _publicador
    _publicador = publicador


def _construir_publicador() -> PublicadorEventos:
    if Config.EVENTOS_BACKEND == "rabbitmq":
        from .rabbitmq import PublicadorRabbitMQ

        return PublicadorRabbitMQ()

    from .memoria import PublicadorMemoria

    return PublicadorMemoria()


__all__ = [
    "EventoIntegracion",
    "ManejadorEvento",
    "PublicadorEventos",
    "get_publicador",
    "set_publicador",
]
