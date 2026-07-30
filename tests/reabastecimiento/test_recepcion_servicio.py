"""Pruebas del servicio de aplicación de Recepción (Reabastecimiento).

El servicio se prueba con repositorios en memoria (Fake) inyectados.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.recepcion_servicio import (
    InspeccionServicio,
    RecepcionServicio,
)
from src.reabastecimiento.infrastructure.recepcion_memoria import (
    InspeccionRepositorioMemoria,
    RecepcionRepositorioMemoria,
)
from src.shared.errores import NoEncontrado


@pytest.fixture
def recepcion_servicio():
    return RecepcionServicio(repositorio=RecepcionRepositorioMemoria())


@pytest.fixture
def inspeccion_servicio():
    return InspeccionServicio(repositorio=InspeccionRepositorioMemoria())


def _items():
    return [{"sku": "SKU-001", "cantidadRecibida": 10}]


class TestRecepcionServicio:
    def test_registrar_y_obtener(self, recepcion_servicio):
        rec = recepcion_servicio.registrar("OC-001", _items())
        obtenida = recepcion_servicio.obtener(rec.id)
        assert obtenida.id == rec.id

    def test_obtener_inexistente_falla(self, recepcion_servicio):
        with pytest.raises(NoEncontrado):
            recepcion_servicio.obtener("REC-NO-EXISTE")

    def test_confirmar(self, recepcion_servicio):
        rec = recepcion_servicio.registrar("OC-001", _items())
        confirmada = recepcion_servicio.confirmar(rec.id)
        assert confirmada.estado.value == "CONFIRMADA"

    def test_listar(self, recepcion_servicio):
        recepcion_servicio.registrar("OC-001", _items())
        recepcion_servicio.registrar("OC-002", _items())
        assert len(recepcion_servicio.listar()) == 2


class TestInspeccionServicio:
    def test_crear_y_obtener(self, inspeccion_servicio):
        ins = inspeccion_servicio.crear("REC-001")
        obtenida = inspeccion_servicio.obtener(ins.id)
        assert obtenida.id == ins.id

    def test_validar(self, inspeccion_servicio):
        ins = inspeccion_servicio.crear("REC-001")
        validada = inspeccion_servicio.validar(ins.id, "Conforme")
        assert validada.resultado.value == "CONFORME"

    def test_rechazar(self, inspeccion_servicio):
        ins = inspeccion_servicio.crear("REC-001")
        rechazada = inspeccion_servicio.rechazar(ins.id, "Producto dañado")
        assert rechazada.resultado.value == "RECHAZADO"

    def test_obtener_inexistente_falla(self, inspeccion_servicio):
        with pytest.raises(NoEncontrado):
            inspeccion_servicio.obtener("INS-NO-EXISTE")
