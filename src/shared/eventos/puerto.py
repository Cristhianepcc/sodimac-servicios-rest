"""Puerto de mensajería: contrato entre la capa de aplicación y el broker.

La capa de aplicación publica **eventos de integración** sin conocer AMQP.
La infraestructura (`rabbitmq.py`, `memoria.py`) implementa el contrato.
Inversión de dependencias (la D de SOLID), igual que en los repositorios.
"""
from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class EventoIntegracion:
    """Mensaje inmutable que cruza la frontera entre bounded contexts.

    `tipo` identifica el hecho de negocio ocurrido (en pasado, según la
    convención de eventos de dominio); `datos` es la carga útil serializable.
    """

    tipo: str
    datos: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ocurrido_en: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    origen: str = "sodimac-api"

    def a_json(self) -> bytes:
        return json.dumps(
            {
                "id": self.id,
                "tipo": self.tipo,
                "ocurridoEn": self.ocurrido_en,
                "origen": self.origen,
                "datos": self.datos,
            },
            ensure_ascii=False,
        ).encode("utf-8")

    @classmethod
    def desde_json(cls, cuerpo: bytes | str) -> EventoIntegracion:
        """Reconstruye un evento. Tolera mensajes planos publicados por Bonita.

        Bonita puede enviar el payload de negocio sin el sobre (`tipo`, `id`,
        ...). En ese caso se envuelve para que los manejadores reciban siempre
        la misma forma.

        El discriminador es la clave `datos`, **no** `tipo`: el payload de
        negocio de RSE ya trae su propio `tipo` ("RECICLAJE", ...), así que
        usarlo para detectar el sobre confundiría un mensaje plano con uno
        envuelto y vaciaría la carga útil.
        """
        crudo = json.loads(cuerpo)
        if not isinstance(crudo, dict):
            raise ValueError("El cuerpo del mensaje debe ser un objeto JSON.")

        if not ("datos" in crudo and isinstance(crudo.get("datos"), dict)):
            return cls(tipo="mensaje.recibido", datos=crudo, origen="externo")

        return cls(
            tipo=crudo.get("tipo", "mensaje.recibido"),
            datos=crudo["datos"],
            id=crudo.get("id", str(uuid.uuid4())),
            ocurrido_en=crudo.get(
                "ocurridoEn", datetime.now(timezone.utc).isoformat()
            ),
            origen=crudo.get("origen", "externo"),
        )


#: Un manejador recibe el evento y ejecuta un caso de uso. No devuelve nada:
#: si lanza excepción, el consumidor decide si reencolar o descartar.
ManejadorEvento = Callable[[EventoIntegracion], None]


class PublicadorEventos(ABC):
    """Puerto de salida: publica eventos hacia el broker."""

    @abstractmethod
    def publicar(self, cola: str, evento: EventoIntegracion) -> None:
        """Envía `evento` a `cola`."""

    @abstractmethod
    def cerrar(self) -> None:
        """Libera la conexión con el broker."""


class ConsumidorEventos(ABC):
    """Puerto de entrada: recibe eventos del broker y los despacha."""

    @abstractmethod
    def suscribir(self, cola: str, manejador: ManejadorEvento) -> None:
        """Asocia un manejador a una cola."""

    @abstractmethod
    def escuchar(self) -> None:
        """Bloquea consumiendo mensajes de las colas suscritas."""
