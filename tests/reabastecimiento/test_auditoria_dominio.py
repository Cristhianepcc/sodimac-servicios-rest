"""Pruebas unitarias del dominio de Auditoría (Reabastecimiento).

Cubre: fábricas de Auditoría y MovimientoStock, completar auditoría.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.auditoria import (
    Auditoria,
    AuditoriaFabrica,
    EstadoAuditoria,
    MovimientoStock,
    MovimientoStockFabrica,
    TipoAuditoria,
    TipoMovimiento,
)
from src.shared.errores import ErrorDominio


# --- Fábrica Auditoría ------------------------------------------------------

class TestAuditoriaFabrica:
    def test_crear_auditoria_fisica(self):
        a = AuditoriaFabrica.crear("SKU-001", "FISICA")
        assert a.id.startswith("AUD-")
        assert a.sku == "SKU-001"
        assert a.tipo is TipoAuditoria.FISICA
        assert a.estado is EstadoAuditoria.PENDIENTE

    def test_crear_auditoria_contable(self):
        a = AuditoriaFabrica.crear("SKU-001", "CONTABLE")
        assert a.tipo is TipoAuditoria.CONTABLE

    def test_crear_sku_obligatorio(self):
        with pytest.raises(ErrorDominio):
            AuditoriaFabrica.crear("", "FISICA")

    def test_crear_sku_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            AuditoriaFabrica.crear("   ", "FISICA")

    def test_crear_tipo_invalido_falla(self):
        with pytest.raises(ErrorDominio):
            AuditoriaFabrica.crear("SKU-001", "NO_VALIDO")


# --- Completar Auditoría ----------------------------------------------------

class TestCompletarAuditoria:
    def test_completar_pendiente(self):
        a = AuditoriaFabrica.crear("SKU-001", "FISICA")
        a.completar("Inventario correcto")
        assert a.estado is EstadoAuditoria.COMPLETADA
        assert a.observaciones == "Inventario correcto"

    def test_completar_sin_observaciones(self):
        a = AuditoriaFabrica.crear("SKU-001", "FISICA")
        a.completar()
        assert a.estado is EstadoAuditoria.COMPLETADA

    def test_completar_ya_completada_falla(self):
        a = AuditoriaFabrica.crear("SKU-001", "FISICA")
        a.completar()
        with pytest.raises(ErrorDominio):
            a.completar()


# --- Fábrica MovimientoStock ------------------------------------------------

class TestMovimientoStockFabrica:
    def test_crear_movimiento_entrada(self):
        m = MovimientoStockFabrica.crear("SKU-001", "ENTRADA", 50, "Compra")
        assert m.id.startswith("MOV-")
        assert m.sku == "SKU-001"
        assert m.tipo is TipoMovimiento.ENTRADA
        assert m.cantidad == 50
        assert m.motivo == "Compra"

    def test_crear_movimiento_salida(self):
        m = MovimientoStockFabrica.crear("SKU-001", "SALIDA", 10, "Venta")
        assert m.tipo is TipoMovimiento.SALIDA

    def test_crear_movimiento_ajuste(self):
        m = MovimientoStockFabrica.crear("SKU-001", "AJUSTE", 5, "Corrección")
        assert m.tipo is TipoMovimiento.AJUSTE

    def test_crear_sku_obligatorio(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("", "ENTRADA", 10, "Motivo")

    def test_crear_tipo_invalido_falla(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("SKU-001", "NO_VALIDO", 10, "Motivo")

    def test_crear_cantidad_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("SKU-001", "ENTRADA", 0, "Motivo")

    def test_crear_cantidad_negativa_falla(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("SKU-001", "ENTRADA", -1, "Motivo")

    def test_crear_motivo_obligatorio(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("SKU-001", "ENTRADA", 10, "")

    def test_crear_motivo_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            MovimientoStockFabrica.crear("SKU-001", "ENTRADA", 10, "   ")

    def test_crear_con_usuario(self):
        m = MovimientoStockFabrica.crear("SKU-001", "ENTRADA", 10, "Compra", "admin")
        assert m.usuario == "admin"
