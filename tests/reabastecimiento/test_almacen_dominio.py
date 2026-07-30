"""Pruebas unitarias del dominio de Almacén (Reabastecimiento).

Cubre: fábricas de Ubicación y MercaderíaUbicada.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.almacen import (
    MercaderiaUbicada,
    MercaderiaUbicadaFabrica,
    Ubicacion,
    UbicacionFabrica,
)
from src.shared.errores import ErrorDominio


# --- Fábrica Ubicación ------------------------------------------------------

class TestUbicacionFabrica:
    def test_crear_ubicacion_valida(self):
        u = UbicacionFabrica.crear("UBI-001", "A", "1", "B")
        assert u.codigo == "UBI-001"
        assert u.pasillo == "A"
        assert u.estante == "1"
        assert u.nivel == "B"

    def test_crear_codigo_obligatorio(self):
        with pytest.raises(ErrorDominio):
            UbicacionFabrica.crear("", "A", "1", "B")

    def test_crear_codigo_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            UbicacionFabrica.crear("   ", "A", "1", "B")

    def test_crear_pasillo_obligatorio(self):
        with pytest.raises(ErrorDominio):
            UbicacionFabrica.crear("UBI-001", "", "1", "B")

    def test_crear_estante_obligatorio(self):
        with pytest.raises(ErrorDominio):
            UbicacionFabrica.crear("UBI-001", "A", "", "B")

    def test_crear_nivel_obligatorio(self):
        with pytest.raises(ErrorDominio):
            UbicacionFabrica.crear("UBI-001", "A", "1", "")

    def test_campos_se_recortan(self):
        u = UbicacionFabrica.crear("  UBI-001  ", "  A  ", "  1  ", "  B  ")
        assert u.codigo == "UBI-001"
        assert u.pasillo == "A"
        assert u.estante == "1"
        assert u.nivel == "B"


# --- Fábrica MercaderíaUbicada ----------------------------------------------

class TestMercaderiaUbicadaFabrica:
    def test_crear_mercaderia_valida(self):
        m = MercaderiaUbicadaFabrica.crear("SKU-001", "UBI-001", 50)
        assert m.id.startswith("UBI-")
        assert m.sku == "SKU-001"
        assert m.ubicacion_codigo == "UBI-001"
        assert m.cantidad == 50
        assert m.fecha_ubicacion is not None

    def test_crear_sku_obligatorio(self):
        with pytest.raises(ErrorDominio):
            MercaderiaUbicadaFabrica.crear("", "UBI-001", 50)

    def test_crear_sku_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            MercaderiaUbicadaFabrica.crear("   ", "UBI-001", 50)

    def test_crear_ubicacion_obligatoria(self):
        with pytest.raises(ErrorDominio):
            MercaderiaUbicadaFabrica.crear("SKU-001", "", 50)

    def test_crear_cantidad_mayor_a_cero(self):
        with pytest.raises(ErrorDominio):
            MercaderiaUbicadaFabrica.crear("SKU-001", "UBI-001", 0)

    def test_crear_cantidad_negativa_falla(self):
        with pytest.raises(ErrorDominio):
            MercaderiaUbicadaFabrica.crear("SKU-001", "UBI-001", -5)
