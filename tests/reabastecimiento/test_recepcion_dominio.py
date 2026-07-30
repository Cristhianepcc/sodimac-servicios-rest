"""Pruebas unitarias del dominio de Recepción (Reabastecimiento).

Cubre: fábricas, confirmar, inspeccionar, validar, rechazar.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.recepcion import (
    Inspeccion,
    InspeccionFabrica,
    ItemRecepcion,
    Recepcion,
    RecepcionFabrica,
    ResultadoInspeccion,
)
from src.shared.errores import ErrorDominio


# --- Helpers ----------------------------------------------------------------

def _items_validos() -> list[dict]:
    return [
        {"sku": "SKU-001", "cantidadRecibida": 10},
        {"sku": "SKU-002", "cantidadRecibida": 5},
    ]


# --- Fábrica Recepción ------------------------------------------------------

class TestRecepcionFabrica:
    def test_crear_genera_id_y_estado_pendiente(self):
        rec = RecepcionFabrica.crear("OC-001", _items_validos())
        assert rec.id.startswith("REC-")
        assert rec.estado.value == "PENDIENTE"
        assert rec.orden_compra_id == "OC-001"
        assert len(rec.items) == 2

    def test_crear_orden_compra_id_obligatorio(self):
        with pytest.raises(ErrorDominio):
            RecepcionFabrica.crear("", _items_validos())

    def test_crear_orden_compra_id_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            RecepcionFabrica.crear("   ", _items_validos())

    def test_crear_sin_items_falla(self):
        with pytest.raises(ErrorDominio):
            RecepcionFabrica.crear("OC-001", [])

    def test_crear_cantidad_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            RecepcionFabrica.crear("OC-001", [{"sku": "X", "cantidadRecibida": 0}])

    def test_crear_cantidad_negativa_falla(self):
        with pytest.raises(ErrorDominio):
            RecepcionFabrica.crear("OC-001", [{"sku": "X", "cantidadRecibida": -1}])


# --- Confirmar Recepción ----------------------------------------------------

class TestConfirmarRecepcion:
    def test_confirmar_pendiente_con_items(self):
        rec = RecepcionFabrica.crear("OC-001", _items_validos())
        rec.confirmar()
        assert rec.estado.value == "CONFIRMADA"

    def test_confirmar_sin_items_falla(self):
        rec = Recepcion(id="REC-0", orden_compra_id="OC", fecha_llegada="2026-01-01", items=[])
        with pytest.raises(ErrorDominio):
            rec.confirmar()

    def test_confirmar_ya_confirmada_falla(self):
        rec = RecepcionFabrica.crear("OC-001", _items_validos())
        rec.confirmar()
        with pytest.raises(ErrorDominio):
            rec.confirmar()


# --- Fábrica Inspección -----------------------------------------------------

class TestInspeccionFabrica:
    def test_crear_genera_id_estado_pendiente(self):
        ins = InspeccionFabrica.crear("REC-001")
        assert ins.id.startswith("INS-")
        assert ins.recepcion_id == "REC-001"
        assert ins.resultado is ResultadoInspeccion.PENDIENTE

    def test_crear_recepcion_id_obligatorio(self):
        with pytest.raises(ErrorDominio):
            InspeccionFabrica.crear("")

    def test_crear_recepcion_id_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            InspeccionFabrica.crear("   ")


# --- Validar Inspección -----------------------------------------------------

class TestValidarInspeccion:
    def test_validar_pendiente(self):
        ins = InspeccionFabrica.crear("REC-001")
        ins.validar("Todo conforme")
        assert ins.resultado is ResultadoInspeccion.CONFORME
        assert ins.observaciones == "Todo conforme"

    def test_validar_sin_observaciones(self):
        ins = InspeccionFabrica.crear("REC-001")
        ins.validar()
        assert ins.resultado is ResultadoInspeccion.CONFORME

    def test_validar_ya_cerrada_falla(self):
        ins = InspeccionFabrica.crear("REC-001")
        ins.validar()
        with pytest.raises(ErrorDominio):
            ins.validar()


# --- Rechazar Inspección ----------------------------------------------------

class TestRechazarInspeccion:
    def test_rechazar_con_motivo(self):
        ins = InspeccionFabrica.crear("REC-001")
        ins.rechazar("Producto dañado")
        assert ins.resultado is ResultadoInspeccion.RECHAZADO
        assert ins.observaciones == "Producto dañado"

    def test_rechazar_sin_motivo_falla(self):
        ins = InspeccionFabrica.crear("REC-001")
        with pytest.raises(ErrorDominio):
            ins.rechazar("")

    def test_rechazar_motivo_blanco_falla(self):
        ins = InspeccionFabrica.crear("REC-001")
        with pytest.raises(ErrorDominio):
            ins.rechazar("   ")

    def test_rechazar_ya_cerrada_falla(self):
        ins = InspeccionFabrica.crear("REC-001")
        ins.validar()
        with pytest.raises(ErrorDominio):
            ins.rechazar("Motivo")
