"""Adaptador AMQP sobre RabbitMQ (cliente `pika`).

Es la contraparte de los conectores del proceso BPM en Bonita: el proceso
publica en `rse.convocatorias` y este servicio consume; el servicio responde
por `rse.postulaciones` y el proceso continúa. Las colas son **durables** y los
mensajes **persistentes** para que ninguna de las dos partes pierda trabajo si
la otra está caída (acoplamiento temporal bajo).
"""
from __future__ import annotations

import logging

import pika

from config import Config

from .puerto import (
    ConsumidorEventos,
    EventoIntegracion,
    ManejadorEvento,
    PublicadorEventos,
)

log = logging.getLogger(__name__)

#: Entrega persistente (RabbitMQ escribe el mensaje a disco).
_PERSISTENTE = 2


def _parametros() -> pika.ConnectionParameters:
    return pika.ConnectionParameters(
        host=Config.RABBITMQ_HOST,
        port=Config.RABBITMQ_PORT,
        virtual_host=Config.RABBITMQ_VHOST,
        credentials=pika.PlainCredentials(
            Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD
        ),
        heartbeat=Config.RABBITMQ_HEARTBEAT,
        blocked_connection_timeout=Config.RABBITMQ_TIMEOUT,
    )


class PublicadorRabbitMQ(PublicadorEventos):
    """Publica eventos. Reconecta de forma perezosa si el canal se cae."""

    def __init__(self) -> None:
        self._conexion: pika.BlockingConnection | None = None
        self._canal = None

    def _asegurar_canal(self):
        if self._canal is not None and self._canal.is_open:
            return self._canal
        self._conexion = pika.BlockingConnection(_parametros())
        self._canal = self._conexion.channel()
        return self._canal

    def publicar(self, cola: str, evento: EventoIntegracion) -> None:
        canal = self._asegurar_canal()
        canal.queue_declare(queue=cola, durable=True)
        canal.basic_publish(
            exchange="",
            routing_key=cola,
            body=evento.a_json(),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=_PERSISTENTE,
                message_id=evento.id,
                type=evento.tipo,
            ),
        )
        log.info("Evento %s publicado en '%s' (id=%s)", evento.tipo, cola, evento.id)

    def cerrar(self) -> None:
        if self._conexion is not None and self._conexion.is_open:
            self._conexion.close()
        self._conexion = None
        self._canal = None


class ConsumidorRabbitMQ(ConsumidorEventos):
    """Consume mensajes y los despacha a los manejadores registrados.

    Usa `basic_qos(prefetch_count=1)` para repartir la carga si se levanta más
    de una réplica del worker, y ack manual para no perder mensajes: solo se
    confirma el mensaje cuando el manejador terminó bien.
    """

    def __init__(self) -> None:
        self._suscripciones: dict[str, list[ManejadorEvento]] = {}
        self._conexion: pika.BlockingConnection | None = None

    def suscribir(self, cola: str, manejador: ManejadorEvento) -> None:
        self._suscripciones.setdefault(cola, []).append(manejador)

    def _procesar(self, cola: str, canal, metodo, _propiedades, cuerpo: bytes) -> None:
        try:
            evento = EventoIntegracion.desde_json(cuerpo)
        except (ValueError, UnicodeDecodeError):
            # Mensaje ilegible: descartar sin reencolar (evita bucle infinito).
            log.exception("Mensaje no parseable en '%s'; se descarta", cola)
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)
            return

        try:
            for manejador in self._suscripciones[cola]:
                manejador(evento)
        except Exception:
            log.exception("Fallo procesando %s en '%s'; se descarta", evento.tipo, cola)
            canal.basic_nack(delivery_tag=metodo.delivery_tag, requeue=False)
            return

        canal.basic_ack(delivery_tag=metodo.delivery_tag)
        log.info("Evento %s procesado desde '%s'", evento.tipo, cola)

    def escuchar(self) -> None:
        self._conexion = pika.BlockingConnection(_parametros())
        canal = self._conexion.channel()
        canal.basic_qos(prefetch_count=1)

        for cola in self._suscripciones:
            canal.queue_declare(queue=cola, durable=True)
            canal.basic_consume(
                queue=cola,
                on_message_callback=(
                    lambda ch, m, p, b, _c=cola: self._procesar(_c, ch, m, p, b)
                ),
            )
            log.info("Suscrito a la cola '%s'", cola)

        try:
            canal.start_consuming()
        except KeyboardInterrupt:
            canal.stop_consuming()
        finally:
            if self._conexion.is_open:
                self._conexion.close()
