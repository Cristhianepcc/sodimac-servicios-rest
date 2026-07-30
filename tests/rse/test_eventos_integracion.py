"""Pruebas del flujo guiado por eventos BPM ↔ servicio REST.

Usan los dobles en memoria (`ConsumidorMemoria` / `PublicadorMemoria`), así que
corren sin RabbitMQ. Los payloads son **exactamente** los que publica el
proceso de Bonita (ver `scripts/02_publicar_convocatoria.sh` y
`scripts/04_publicar_postulacion.sh` del repo BPM).
"""
from __future__ import annotations

import json

import pytest

from config import Config
from src.rse.application.iniciativa_servicio import IniciativaServicio
from src.rse.application.manejadores_evento import ManejadoresRSE
from src.rse.domain.iniciativa import EstadoIniciativa
from src.rse.infrastructure.iniciativa_memoria import IniciativaRepositorioMemoria
from src.shared.errores import ErrorDominio, NoEncontrado
from src.shared.eventos.memoria import ConsumidorMemoria, PublicadorMemoria
from src.shared.eventos.puerto import EventoIntegracion

CONVOCATORIA = {
    "codigo": "RSE-2026-001",
    "nombre": "Reciclaje de mermas en tiendas",
    "tipo": "RECICLAJE",
    "presupuestoAprobado": 15000.0,
    "requisitos": "Proveedor con certificacion ambiental ISO 14001",
}

POSTULACION = {
    "codigoConvocatoria": "RSE-2026-001",
    "proveedor": "EcoAndes SAC",
    "propuesta": "Recojo y valorizacion de mermas organicas 3x semana",
    "montoOfertado": 12800.0,
    "certificacion": "ISO 14001",
    "aceptada": True,
}


@pytest.fixture
def servicio() -> IniciativaServicio:
    return IniciativaServicio(repositorio=IniciativaRepositorioMemoria())


@pytest.fixture
def publicador() -> PublicadorMemoria:
    return PublicadorMemoria()


@pytest.fixture
def manejadores(servicio, publicador) -> ManejadoresRSE:
    return ManejadoresRSE(servicio=servicio, publicador=publicador)


# --- Deserialización del mensaje ---

def test_evento_acepta_el_sobre_completo():
    crudo = json.dumps(
        {"id": "abc", "tipo": "rse.convocatoria.emitida", "datos": CONVOCATORIA}
    )
    evento = EventoIntegracion.desde_json(crudo)
    assert evento.tipo == "rse.convocatoria.emitida"
    assert evento.datos["codigo"] == "RSE-2026-001"
    assert evento.id == "abc"


def test_evento_envuelve_payload_plano_de_bonita():
    """Bonita publica el payload de negocio sin sobre; debe envolverse."""
    evento = EventoIntegracion.desde_json(json.dumps(CONVOCATORIA))
    assert evento.origen == "externo"
    assert evento.datos["codigo"] == "RSE-2026-001"


def test_payload_plano_con_campo_tipo_no_se_confunde_con_el_sobre():
    """Regresión: el payload de RSE trae su propio `tipo` ("RECICLAJE").

    Si se usara `tipo` como discriminador del sobre, la carga útil se vaciaría
    y la convocatoria llegaría sin código al manejador.
    """
    evento = EventoIntegracion.desde_json(json.dumps(CONVOCATORIA))
    assert evento.datos == CONVOCATORIA
    assert evento.datos["tipo"] == "RECICLAJE"


def test_evento_rechaza_json_que_no_es_objeto():
    with pytest.raises(ValueError):
        EventoIntegracion.desde_json("[1, 2, 3]")


def test_ida_y_vuelta_json():
    original = EventoIntegracion(tipo="rse.prueba", datos={"n": 1})
    recuperado = EventoIntegracion.desde_json(original.a_json())
    assert recuperado.id == original.id
    assert recuperado.tipo == original.tipo
    assert recuperado.datos == original.datos


# --- Entrada: convocatoria ---

def test_convocatoria_crea_la_iniciativa_aprobada(manejadores, servicio):
    manejadores.sincronizar_convocatoria(
        EventoIntegracion(tipo="rse.convocatoria.emitida", datos=CONVOCATORIA)
    )

    iniciativa = servicio.obtener("RSE-2026-001")
    assert iniciativa.nombre == "Reciclaje de mermas en tiendas"
    assert iniciativa.aprobada is True
    assert iniciativa.estado == EstadoIniciativa.APROBADA
    assert iniciativa.presupuesto_aprobado == 15000.0


def test_convocatoria_repetida_es_idempotente(manejadores, servicio):
    """RabbitMQ entrega al menos una vez: reprocesar no debe duplicar."""
    evento = EventoIntegracion(tipo="rse.convocatoria.emitida", datos=CONVOCATORIA)
    manejadores.sincronizar_convocatoria(evento)
    manejadores.sincronizar_convocatoria(evento)

    assert len(servicio.listar()) == 1


def test_convocatoria_sin_presupuesto_es_rechazada(manejadores):
    datos = CONVOCATORIA | {"presupuestoAprobado": 0.0}
    with pytest.raises(ErrorDominio):
        manejadores.sincronizar_convocatoria(
            EventoIntegracion(tipo="rse.convocatoria.emitida", datos=datos)
        )


# --- Entrada: postulación ---

def test_postulacion_registra_evidencia_y_notifica(manejadores, servicio, publicador):
    manejadores.sincronizar_convocatoria(
        EventoIntegracion(tipo="rse.convocatoria.emitida", datos=CONVOCATORIA)
    )
    manejadores.registrar_postulacion(
        EventoIntegracion(tipo="rse.postulacion.recibida", datos=POSTULACION)
    )

    iniciativa = servicio.obtener("RSE-2026-001")
    assert len(iniciativa.evidencias) == 1
    assert "EcoAndes SAC" in iniciativa.evidencias[0].descripcion

    notificaciones = publicador.eventos_de(Config.COLA_NOTIFICACIONES)
    assert len(notificaciones) == 1
    assert notificaciones[0].tipo == "rse.postulacion.aceptada"
    assert notificaciones[0].datos["proveedor"] == "EcoAndes SAC"


def test_postulacion_rechazada_no_notifica(manejadores, publicador):
    manejadores.sincronizar_convocatoria(
        EventoIntegracion(tipo="rse.convocatoria.emitida", datos=CONVOCATORIA)
    )
    manejadores.registrar_postulacion(
        EventoIntegracion(
            tipo="rse.postulacion.recibida", datos=POSTULACION | {"aceptada": False}
        )
    )
    assert publicador.eventos_de(Config.COLA_NOTIFICACIONES) == []


def test_postulacion_huerfana_se_descarta_sin_romper(manejadores, publicador):
    """Si la convocatoria nunca llegó, el worker no debe caerse ni reencolar."""
    manejadores.registrar_postulacion(
        EventoIntegracion(tipo="rse.postulacion.recibida", datos=POSTULACION)
    )
    assert publicador.eventos_de(Config.COLA_NOTIFICACIONES) == []


# --- Cableado del consumidor ---

def test_consumidor_despacha_a_la_cola_correcta(manejadores, servicio):
    consumidor = ConsumidorMemoria()
    consumidor.suscribir(Config.COLA_CONVOCATORIAS, manejadores.sincronizar_convocatoria)
    consumidor.suscribir(Config.COLA_POSTULACIONES, manejadores.registrar_postulacion)

    consumidor.entregar(
        Config.COLA_CONVOCATORIAS,
        EventoIntegracion.desde_json(json.dumps(CONVOCATORIA)),
    )
    consumidor.entregar(
        Config.COLA_POSTULACIONES,
        EventoIntegracion.desde_json(json.dumps(POSTULACION)),
    )

    iniciativa = servicio.obtener("RSE-2026-001")
    assert iniciativa.estado == EstadoIniciativa.EN_EJECUCION
    assert len(iniciativa.evidencias) == 1


def test_flujo_extremo_a_extremo_bpm(manejadores, servicio, publicador):
    """Convocatoria → postulación → notificación de vuelta al proceso BPM."""
    consumidor = ConsumidorMemoria()
    consumidor.suscribir(Config.COLA_CONVOCATORIAS, manejadores.sincronizar_convocatoria)
    consumidor.suscribir(Config.COLA_POSTULACIONES, manejadores.registrar_postulacion)

    consumidor.entregar(
        Config.COLA_CONVOCATORIAS, EventoIntegracion.desde_json(json.dumps(CONVOCATORIA))
    )
    with pytest.raises(NoEncontrado):
        servicio.obtener("RSE-9999")

    consumidor.entregar(
        Config.COLA_POSTULACIONES, EventoIntegracion.desde_json(json.dumps(POSTULACION))
    )

    assert len(publicador.eventos_de(Config.COLA_NOTIFICACIONES)) == 1
