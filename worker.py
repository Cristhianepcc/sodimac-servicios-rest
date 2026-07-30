"""Worker de eventos: consume las colas del proceso BPM y ejecuta casos de uso.

Corre **aparte** de la API HTTP (`run.py`): son dos adaptadores de entrada
distintos sobre la misma capa de aplicación, y se escalan por separado.

Uso:
    EVENTOS_BACKEND=rabbitmq python worker.py

Requiere el broker levantado (ver el `docker-compose.yml` del repo BPM).
"""
from __future__ import annotations

import logging
import sys

from config import Config
from src.rse.application.manejadores_evento import registrar_suscripciones

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)s  %(message)s",
)
log = logging.getLogger("worker")


def main() -> int:
    if Config.EVENTOS_BACKEND != "rabbitmq":
        log.error(
            "EVENTOS_BACKEND='%s'. El worker necesita un broker real: "
            "ejecuta 'EVENTOS_BACKEND=rabbitmq python worker.py'.",
            Config.EVENTOS_BACKEND,
        )
        return 1

    if Config.REPO_BACKEND != "sqlalchemy":
        # Fallo ruidoso a propósito: con el repositorio en memoria el worker
        # arranca, consume y "funciona"... pero guarda en su propia RAM. La API
        # es otro proceso, así que responde 404 a lo que el worker acaba de
        # sincronizar, sin ningún error visible. En una demo esto parece un bug
        # de la integración cuando en realidad es configuración.
        log.error(
            "REPO_BACKEND='%s'. El worker y la API son procesos distintos: con el "
            "repositorio en memoria NO comparten estado y la API devolverá 404 a "
            "las iniciativas que este worker sincronice.",
            Config.REPO_BACKEND,
        )
        log.error("Arranca ambos así:")
        log.error("  REPO_BACKEND=sqlalchemy python run.py")
        log.error("  REPO_BACKEND=sqlalchemy EVENTOS_BACKEND=rabbitmq python worker.py")
        return 1

    # El esquema lo creaba solo `create_app()`, así que un worker arrancado
    # antes que la API (o sin ella) fallaba con "relation ... does not exist" en
    # el primer mensaje. El worker es un punto de entrada de pleno derecho: debe
    # poder arrancar solo.
    if Config.AUTO_CREATE_TABLES:
        from src.shared.db import crear_tablas

        crear_tablas()
        log.info("Esquema de base de datos verificado")

    from src.shared.eventos.rabbitmq import ConsumidorRabbitMQ

    consumidor = ConsumidorRabbitMQ()
    registrar_suscripciones(consumidor)

    log.info(
        "Worker de eventos conectando a amqp://%s:%s%s",
        Config.RABBITMQ_HOST, Config.RABBITMQ_PORT, Config.RABBITMQ_VHOST,
    )
    try:
        consumidor.escuchar()
    except Exception:
        log.exception("El worker terminó por un error de conexión con el broker")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
