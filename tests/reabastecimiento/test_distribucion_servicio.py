"""Pruebas del servicio de aplicación de Distribución (Reabastecimiento).

El servicio se prueba con un repositorio en memoria (Fake) inyectado.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.distribucion_servicio import DistribucionServicio
from src.reabastecimiento.domain.distribucion import EstadoEnvio, EstadoPedidoDistribucion
from src.reabastecimiento.infrastructure.distribucion_memoria import DistribucionRepositorioMemoria
from src.shared.errores import ErrorDominio, NoEncontrado


@pytest.fixture
def servicio():
    return DistribucionServicio(repositorio=DistribucionRepositorioMemoria())


def _items():
    return [{"sku": "SKU-001", "cantidad": 10}]


class TestPedidoServicio:
    def test_generar_y_obtener(self, servicio):
        p = servicio.generar_pedido("Tienda Norte", _items())
        obtenido = servicio.obtener_pedido(p.id)
        assert obtenido.id == p.id
        assert obtenido.estado is EstadoPedidoDistribucion.SOLICITADO

    def test_obtener_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.obtener_pedido("PD-NO-EXISTE")

    def test_listar(self, servicio):
        servicio.generar_pedido("T1", _items())
        servicio.generar_pedido("T2", _items())
        assert len(servicio.listar_pedidos()) == 2

    def test_picking_packing(self, servicio):
        p = servicio.generar_pedido("Tienda", _items())
        servicio.iniciar_picking(p.id)
        assert servicio.obtener_pedido(p.id).estado is EstadoPedidoDistribucion.EN_PICKING

        servicio.completar_packing(p.id)
        assert servicio.obtener_pedido(p.id).estado is EstadoPedidoDistribucion.EN_PACKING


class TestEnvioServicio:
    def test_programar_despacho(self, servicio):
        p = servicio.generar_pedido("Tienda", _items())
        envio = servicio.programar_despacho(p.id, "Transportista ABC")
        assert envio.estado is EstadoEnvio.DESPACHADO
        assert envio.transportista == "Transportista ABC"

    def test_despachar_duplicado_falla(self, servicio):
        p = servicio.generar_pedido("Tienda", _items())
        servicio.programar_despacho(p.id, "T1")
        with pytest.raises(ErrorDominio):
            servicio.programar_despacho(p.id, "T2")

    def test_actualizar_estado_envio(self, servicio):
        p = servicio.generar_pedido("Tienda", _items())
        envio = servicio.programar_despacho(p.id, "T")
        servicio.actualizar_estado_envio(envio.id, "EN_TRANSITO")
        assert servicio._repo.buscar_envio(envio.id).estado is EstadoEnvio.EN_TRANSITO

    def test_registrar_llegada(self, servicio):
        p = servicio.generar_pedido("Tienda", _items())
        envio = servicio.programar_despacho(p.id, "T")
        servicio.actualizar_estado_envio(envio.id, "EN_TRANSITO")
        servicio.registrar_llegada(envio.id)
        assert servicio._repo.buscar_envio(envio.id).estado is EstadoEnvio.ENTREGADO
        assert servicio.obtener_pedido(p.id).estado is EstadoPedidoDistribucion.ENTREGADO
