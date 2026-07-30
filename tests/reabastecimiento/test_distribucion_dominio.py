"""Pruebas unitarias del dominio de Distribución (Reabastecimiento).

Cubre: fábricas, picking/packing, envío, transiciones de estado.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.distribucion import (
    Envio,
    EnvioFabrica,
    EstadoEnvio,
    EstadoPedidoDistribucion,
    PedidoDistribucion,
    PedidoDistribucionFabrica,
)
from src.shared.errores import ErrorDominio


# --- Helpers ----------------------------------------------------------------

def _items_validos() -> list[dict]:
    return [{"sku": "SKU-001", "cantidad": 10}, {"sku": "SKU-002", "cantidad": 5}]


def _pedido(**kwargs) -> PedidoDistribucion:
    p = PedidoDistribucionFabrica.crear("Tienda Central", _items_validos())
    for k, v in kwargs.items():
        setattr(p, k, v)
    return p


# --- Fábrica Pedido ---------------------------------------------------------

class TestPedidoDistribucionFabrica:
    def test_crear_genera_id_y_estado_solicitado(self):
        p = PedidoDistribucionFabrica.crear("Tienda Norte", _items_validos())
        assert p.id.startswith("PD-")
        assert p.estado is EstadoPedidoDistribucion.SOLICITADO
        assert p.tienda_destino == "Tienda Norte"
        assert len(p.items) == 2

    def test_crear_tienda_obligatoria(self):
        with pytest.raises(ErrorDominio):
            PedidoDistribucionFabrica.crear("", _items_validos())

    def test_crear_tienda_blanca_falla(self):
        with pytest.raises(ErrorDominio):
            PedidoDistribucionFabrica.crear("   ", _items_validos())

    def test_crear_sin_items_falla(self):
        with pytest.raises(ErrorDominio):
            PedidoDistribucionFabrica.crear("Tienda", [])

    def test_crear_cantidad_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            PedidoDistribucionFabrica.crear("Tienda", [{"sku": "X", "cantidad": 0}])

    def test_crear_cantidad_negativa_falla(self):
        with pytest.raises(ErrorDominio):
            PedidoDistribucionFabrica.crear("Tienda", [{"sku": "X", "cantidad": -1}])


# --- Picking / Packing ------------------------------------------------------

class TestPickingPacking:
    def test_iniciar_picking(self):
        p = _pedido()
        p.iniciar_picking()
        assert p.estado is EstadoPedidoDistribucion.EN_PICKING

    def test_iniciar_picking_no_solicitado_falla(self):
        p = _pedido(estado=EstadoPedidoDistribucion.EN_PICKING)
        with pytest.raises(ErrorDominio):
            p.iniciar_picking()

    def test_completar_packing(self):
        p = _pedido(estado=EstadoPedidoDistribucion.EN_PICKING)
        p.completar_packing()
        assert p.estado is EstadoPedidoDistribucion.EN_PACKING

    def test_completar_packing_sin_picking_falla(self):
        p = _pedido()
        with pytest.raises(ErrorDominio):
            p.completar_packing()

    def test_flujo_picking_packing(self):
        p = _pedido()
        p.iniciar_picking()
        p.completar_packing()
        assert p.estado is EstadoPedidoDistribucion.EN_PACKING


# --- Fábrica Envío ----------------------------------------------------------

class TestEnvioFabrica:
    def test_crear_genera_id_y_estado_preparado(self):
        envio = EnvioFabrica.crear("PD-001")
        assert envio.id.startswith("ENV-")
        assert envio.pedido_id == "PD-001"
        assert envio.estado is EstadoEnvio.PREPARADO

    def test_crear_pedido_id_obligatorio(self):
        with pytest.raises(ErrorDominio):
            EnvioFabrica.crear("")

    def test_crear_pedido_id_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            EnvioFabrica.crear("   ")


# --- Despachar Envío --------------------------------------------------------

class TestDespacharEnvio:
    def test_despachar_preparado(self):
        envio = EnvioFabrica.crear("PD-001")
        envio.despachar("Transportista ABC")
        assert envio.estado is EstadoEnvio.DESPACHADO
        assert envio.transportista == "Transportista ABC"
        assert envio.fecha_despacho is not None

    def test_despachar_no_preparado_falla(self):
        envio = EnvioFabrica.crear("PD-001")
        envio.despachar("T")
        with pytest.raises(ErrorDominio):
            envio.despachar("Otro")

    def test_despachar_sin_transportista_falla(self):
        envio = EnvioFabrica.crear("PD-001")
        with pytest.raises(ErrorDominio):
            envio.despachar("")

    def test_despachar_transportista_blanco_falla(self):
        envio = EnvioFabrica.crear("PD-001")
        with pytest.raises(ErrorDominio):
            envio.despachar("   ")


# --- Actualizar estado Envío ------------------------------------------------

class TestActualizarEstadoEnvio:
    def test_flujo_completo(self):
        envio = EnvioFabrica.crear("PD-001")
        envio.despachar("T")
        envio.actualizar_estado(EstadoEnvio.EN_TRANSITO)
        assert envio.estado is EstadoEnvio.EN_TRANSITO
        envio.registrar_llegada()
        assert envio.estado is EstadoEnvio.ENTREGADO

    def test_transicion_invalida_falla(self):
        envio = EnvioFabrica.crear("PD-001")
        with pytest.raises(ErrorDominio):
            envio.actualizar_estado(EstadoEnvio.ENTREGADO)

    def test_registrar_llegada_no_en_transito_falla(self):
        envio = EnvioFabrica.crear("PD-001")
        with pytest.raises(ErrorDominio):
            envio.registrar_llegada()
