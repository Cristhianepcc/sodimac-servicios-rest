"""Pruebas del servicio de aplicación de OrdenCompra (Reabastecimiento).

El servicio se prueba con un repositorio en memoria (Fake) inyectado.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.orden_compra_servicio import OrdenCompraServicio
from src.reabastecimiento.domain.orden_compra import EstadoOrden
from src.reabastecimiento.infrastructure.orden_compra_memoria import OrdenCompraRepositorioMemoria
from src.shared.errores import ErrorDominio, NoEncontrado


@pytest.fixture
def servicio():
    return OrdenCompraServicio(repositorio=OrdenCompraRepositorioMemoria())


def _lineas():
    return [{"sku": "SKU-001", "cantidad": 10, "precioUnitario": 25.0}]


class TestGenerarYObtener:
    def test_generar_y_obtener(self, servicio):
        oc = servicio.generar("PRV-001", _lineas())
        obtenida = servicio.obtener(oc.id)
        assert obtenida.id == oc.id
        assert obtenida.estado is EstadoOrden.PENDIENTE_AUTORIZACION

    def test_obtener_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.obtener("OC-NO-EXISTE")

    def test_listar(self, servicio):
        servicio.generar("PRV-001", _lineas())
        servicio.generar("PRV-002", _lineas())
        assert len(servicio.listar()) == 2


class TestCicloOC:
    def test_flujo_completo_autorizar_enviar(self, servicio):
        oc = servicio.generar("PRV-001", _lineas())
        autorizada = servicio.autorizar(oc.id)
        assert autorizada.estado is EstadoOrden.AUTORIZADA

        enviada = servicio.enviar(oc.id)
        assert enviada.estado is EstadoOrden.ENVIADA

    def test_cancelar(self, servicio):
        oc = servicio.generar("PRV-001", _lineas())
        cancelada = servicio.cancelar(oc.id)
        assert cancelada.estado is EstadoOrden.CANCELADA

    def test_autorizar_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.autorizar("OC-NO-EXISTE")

    def test_enviar_sin_autorizar_falla(self, servicio):
        oc = servicio.generar("PRV-001", _lineas())
        with pytest.raises(ErrorDominio):
            servicio.enviar(oc.id)
