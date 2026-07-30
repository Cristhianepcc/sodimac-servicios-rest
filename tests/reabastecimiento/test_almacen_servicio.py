"""Pruebas del servicio de aplicación de Almacén (Reabastecimiento).

El servicio se prueba con un repositorio en memoria (Fake) inyectado.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.almacen_servicio import AlmacenServicio
from src.reabastecimiento.infrastructure.almacen_memoria import AlmacenRepositorioMemoria
from src.shared.errores import Conflicto, NoEncontrado


@pytest.fixture
def servicio():
    return AlmacenServicio(repositorio=AlmacenRepositorioMemoria())


class TestUbicacionServicio:
    def test_registrar_y_consultar(self, servicio):
        u = servicio.registrar_ubicacion("UBI-001", "A", "1", "B")
        consultada = servicio.consultar_ubicacion("UBI-001")
        assert consultada.codigo == u.codigo

    def test_registrar_duplicada_falla(self, servicio):
        servicio.registrar_ubicacion("UBI-001", "A", "1", "B")
        with pytest.raises(Conflicto):
            servicio.registrar_ubicacion("UBI-001", "A", "2", "C")

    def test_consultar_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.consultar_ubicacion("UBI-NO-EXISTE")

    def test_listar(self, servicio):
        servicio.registrar_ubicacion("UBI-001", "A", "1", "B")
        servicio.registrar_ubicacion("UBI-002", "B", "2", "C")
        assert len(servicio.listar_ubicaciones()) == 2


class TestMercaderiaServicio:
    def test_ubicar_mercaderia(self, servicio):
        servicio.registrar_ubicacion("UBI-001", "A", "1", "B")
        m = servicio.ubicar_mercaderia("SKU-001", "UBI-001", 50)
        assert m.sku == "SKU-001"
        assert m.cantidad == 50

    def test_ubicar_en_ubicacion_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.ubicar_mercaderia("SKU-001", "UBI-NO-EXISTE", 50)

    def test_consultar_por_sku(self, servicio):
        servicio.registrar_ubicacion("UBI-001", "A", "1", "B")
        servicio.ubicar_mercaderia("SKU-001", "UBI-001", 50)
        servicio.ubicar_mercaderia("SKU-001", "UBI-001", 30)
        assert len(servicio.consultar_por_sku("SKU-001")) == 2
