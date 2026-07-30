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
