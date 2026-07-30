"""Casos de uso disparados por eventos del proceso BPM (no por HTTP).

Es la contraparte de `iniciativa_controller.py`: mismos servicios de
aplicación, distinto adaptador de entrada. El proceso de Bonita publica en
RabbitMQ y estos manejadores ejecutan la tarea automática correspondiente.

    Bonita "Notificar áreas y aliados" ─► rse.convocatorias ─► sincronizar
    Proceso 2 "Enviar postulación"     ─► rse.postulaciones ─► registrar
    este servicio                      ─► rse.notificaciones ─► Bonita

Idempotencia: RabbitMQ garantiza entrega *al menos una vez*, así que un mismo
mensaje puede llegar repetido (p. ej. si el worker cae tras procesar y antes de
confirmar). Los manejadores están escritos para que reprocesar sea inocuo.
"""
from __future__ import annotations

import logging

from config import Config
from src.rse.application.iniciativa_servicio import IniciativaServicio
from src.shared.errores import NoEncontrado
from src.shared.eventos import EventoIntegracion, get_publicador

log = logging.getLogger(__name__)


class ManejadoresRSE:
    """Agrupa los manejadores del bounded context `rse`."""

    def __init__(self, servicio: IniciativaServicio | None = None, publicador=None) -> None:
        self._servicio = servicio or IniciativaServicio()
        self._publicador = publicador or get_publicador()

    # --- Entrada: convocatoria emitida por el Proceso 1 ---

    def sincronizar_convocatoria(self, evento: EventoIntegracion) -> None:
        """Crea en este servicio la iniciativa aprobada que anuncia el BPM.

        El código lo fija Bonita, de modo que la instancia del proceso y el
        agregado quedan correlacionados y el resto de la API REST puede
        consultarla por `GET /api/rse/iniciativas/<codigo>`.
        """
        datos = evento.datos
        iniciativa = self._servicio.sincronizar_convocatoria(
            codigo=str(datos.get("codigo", "")).strip(),
            nombre=str(datos.get("nombre", "")),
            tipo=str(datos.get("tipo", "")),
            presupuesto_aprobado=float(datos.get("presupuestoAprobado", 0.0)),
            requisitos=str(datos.get("requisitos", "")),
        )
        log.info("Iniciativa %s sincronizada desde la convocatoria BPM", iniciativa.codigo)

    # --- Entrada: postulación emitida por el Proceso 2 (Comunidad/Proveedores) ---

    def registrar_postulacion(self, evento: EventoIntegracion) -> None:
        """Anota la propuesta del proveedor como evidencia de avance.

        Si la postulación fue aceptada, notifica de vuelta al proceso BPM para
        que su ServiceTask de consolidación pueda continuar.
        """
        datos = evento.datos
        codigo = str(datos.get("codigoConvocatoria", "")).strip()
        proveedor = str(datos.get("proveedor", "desconocido"))

        try:
            self._servicio.registrar_evidencia(
                codigo=codigo,
                descripcion=(
                    f"Postulación de {proveedor}: {datos.get('propuesta', '')} "
                    f"(monto ofertado: {datos.get('montoOfertado', 0.0)}, "
                    f"certificación: {datos.get('certificacion', 'n/d')})"
                ),
                porcentaje_avance=float(datos.get("porcentajeAvance", 0.0)),
            )
        except NoEncontrado:
            # La convocatoria no llegó o llegó desordenada: no reencolar en
            # bucle, dejar traza para que el proceso BPM la reemita.
            log.warning(
                "Postulación de %s para una convocatoria desconocida (%s); se descarta",
                proveedor, codigo,
            )
            return

        if bool(datos.get("aceptada", False)):
            self.notificar_proceso(
                tipo="rse.postulacion.aceptada",
                datos={
                    "codigo": codigo,
                    "proveedor": proveedor,
                    "montoOfertado": datos.get("montoOfertado", 0.0),
                },
            )

    # --- Salida: notificación hacia el proceso BPM ---

    def notificar_proceso(self, tipo: str, datos: dict) -> None:
        self._publicador.publicar(
            Config.COLA_NOTIFICACIONES, EventoIntegracion(tipo=tipo, datos=datos)
        )


def registrar_suscripciones(consumidor) -> None:
    """Conecta las colas del proceso BPM con sus manejadores."""
    manejadores = ManejadoresRSE()
    consumidor.suscribir(Config.COLA_CONVOCATORIAS, manejadores.sincronizar_convocatoria)
    consumidor.suscribir(Config.COLA_POSTULACIONES, manejadores.registrar_postulacion)
