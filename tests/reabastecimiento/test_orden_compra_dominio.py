"""Pruebas unitarias del dominio de OrdenCompra (Reabastecimiento).

Cubre: fábrica, transiciones de estado, invariantes y propiedades.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.orden_compra import (
    EstadoOrden,
    LineaOC,
    OrdenCompra,
    OrdenCompraFabrica,
)
from src.shared.errores import ErrorDominio


# --- Helpers ----------------------------------------------------------------

def _lineas_validas() -> list[dict]:
    return [
        {"sku": "SKU-001", "cantidad": 10, "precioUnitario": 25.5},
        {"sku": "SKU-002", "cantidad": 5, "precioUnitario": 100.0},
    ]


def _oc(**kwargs) -> OrdenCompra:
    orden = OrdenCompraFabrica.crear("PRV-001", _lineas_validas())
    for k, v in kwargs.items():
        setattr(orden, k, v)
    return orden


# --- Fábrica ----------------------------------------------------------------

class TestOrdenCompraFabrica:
    def test_crear_genera_id_y_estado_pendiente(self):
        oc = OrdenCompraFabrica.crear("PRV-001", _lineas_validas())
        assert oc.id.startswith("OC-")
        assert oc.estado is EstadoOrden.PENDIENTE_AUTORIZACION
        assert oc.proveedor_id == "PRV-001"

    def test_crear_requiere_proveedor(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("", _lineas_validas())

    def test_crear_requiere_proveedor_no_blanco(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("   ", _lineas_validas())

    def test_crear_requiere_al_una_linea(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("PRV-001", [])

    def test_crear_cantidad_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("PRV-001", [{"sku": "X", "cantidad": 0, "precioUnitario": 10}])

    def test_crear_precio_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("PRV-001", [{"sku": "X", "cantidad": 1, "precioUnitario": 0}])

    def test_crear_precio_negativo_falla(self):
        with pytest.raises(ErrorDominio):
            OrdenCompraFabrica.crear("PRV-001", [{"sku": "X", "cantidad": 1, "precioUnitario": -5}])

    def test_proveedor_se_recorta(self):
        oc = OrdenCompraFabrica.crear("  PRV-001  ", _lineas_validas())
        assert oc.proveedor_id == "PRV-001"


# --- Propiedades ------------------------------------------------------------

class TestPropiedades:
    def test_total_suma_subtotales(self):
        oc = OrdenCompraFabrica.crear("PRV-001", _lineas_validas())
        # 10*25.5 + 5*100 = 255 + 500 = 755
        assert oc.total == 755.0

    def test_linea_subtotal(self):
        linea = LineaOC(sku="X", cantidad=3, precio_unitario=20.0)
        assert linea.subtotal == 60.0

    def test_total_sin_lineas_es_cero(self):
        oc = OrdenCompra(id="OC-0", proveedor_id="P", fecha_emision="2026-01-01", lineas=[])
        assert oc.total == 0.0


# --- Transiciones de estado -------------------------------------------------

class TestTransicionesEstado:
    def test_autorizar_desde_pendiente(self):
        oc = _oc()
        oc.autorizar()
        assert oc.estado is EstadoOrden.AUTORIZADA

    def test_autorizar_sin_ser_pendiente_falla(self):
        oc = _oc(estado=EstadoOrden.BORRADOR)
        with pytest.raises(ErrorDominio):
            oc.autorizar()

    def test_enviar_desde_autorizada(self):
        oc = _oc(estado=EstadoOrden.AUTORIZADA)
        oc.enviar()
        assert oc.estado is EstadoOrden.ENVIADA

    def test_enviar_sin_ser_autorizada_falla(self):
        oc = _oc()
        with pytest.raises(ErrorDominio):
            oc.enviar()

    def test_cancelar_desde_pendiente(self):
        oc = _oc()
        oc.cancelar()
        assert oc.estado is EstadoOrden.CANCELADA

    def test_cancelar_desde_autorizada(self):
        oc = _oc(estado=EstadoOrden.AUTORIZADA)
        oc.cancelar()
        assert oc.estado is EstadoOrden.CANCELADA

    def test_cancelar_enviada_falla(self):
        oc = _oc(estado=EstadoOrden.ENVIADA)
        with pytest.raises(ErrorDominio):
            oc.cancelar()

    def test_cancelar_ya_cancelada_falla(self):
        oc = _oc(estado=EstadoOrden.CANCELADA)
        with pytest.raises(ErrorDominio):
            oc.cancelar()

    def test_flujo_completo(self):
        oc = _oc()
        oc.autorizar()
        oc.enviar()
        assert oc.estado is EstadoOrden.ENVIADA
