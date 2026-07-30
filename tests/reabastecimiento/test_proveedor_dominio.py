"""Pruebas unitarias del dominio de Proveedor (Reabastecimiento).

Cubre: fábrica, evaluar, aprobar, rechazar.
Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.domain.proveedor import (
    EstadoProveedor,
    Proveedor,
    ProveedorFabrica,
)
from src.shared.errores import ErrorDominio


# --- Helpers ----------------------------------------------------------------

def _proveedor(**kwargs) -> Proveedor:
    prov = ProveedorFabrica.crear("EcoAndes SAC", "20512345678")
    for k, v in kwargs.items():
        setattr(prov, k, v)
    return prov


# --- Fábrica ----------------------------------------------------------------

class TestProveedorFabrica:
    def test_crear_genera_id_y_estado_registrado(self):
        prov = ProveedorFabrica.crear("EcoAndes SAC", "20512345678")
        assert prov.id.startswith("PRV-")
        assert prov.estado is EstadoProveedor.REGISTRADO
        assert prov.puntaje == 0

    def test_crear_nombre_obligatorio(self):
        with pytest.raises(ErrorDominio):
            ProveedorFabrica.crear("", "20512345678")

    def test_crear_nombre_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            ProveedorFabrica.crear("   ", "20512345678")

    def test_crear_ruc_obligatorio(self):
        with pytest.raises(ErrorDominio):
            ProveedorFabrica.crear("EcoAndes SAC", "")

    def test_crear_ruc_blanco_falla(self):
        with pytest.raises(ErrorDominio):
            ProveedorFabrica.crear("EcoAndes SAC", "   ")

    def test_campos_se_recortan(self):
        prov = ProveedorFabrica.crear("  EcoAndes  ", "  20512345678  ")
        assert prov.nombre == "EcoAndes"
        assert prov.ruc == "20512345678"


# --- Evaluar ----------------------------------------------------------------

class TestEvaluar:
    def test_evaluar_puntaje_valido(self):
        prov = _proveedor()
        prov.evaluar(85)
        assert prov.puntaje == 85
        assert prov.estado is EstadoProveedor.EVALUADO

    def test_evaluar_puntaje_cero(self):
        prov = _proveedor()
        prov.evaluar(0)
        assert prov.puntaje == 0
        assert prov.estado is EstadoProveedor.EVALUADO

    def test_evaluar_puntaje_cien(self):
        prov = _proveedor()
        prov.evaluar(100)
        assert prov.puntaje == 100

    def test_evaluar_puntaje_negativo_falla(self):
        prov = _proveedor()
        with pytest.raises(ErrorDominio):
            prov.evaluar(-1)

    def test_evaluar_puntaje_mayor_100_falla(self):
        prov = _proveedor()
        with pytest.raises(ErrorDominio):
            prov.evaluar(101)


# --- Aprobar ----------------------------------------------------------------

class TestAprobar:
    def test_aprobar_con_puntaje_suficiente(self):
        prov = _proveedor()
        prov.evaluar(80)
        prov.aprobar()
        assert prov.estado is EstadoProveedor.APROBADO

    def test_aprobar_puntaje_limite_70(self):
        prov = _proveedor()
        prov.evaluar(70)
        prov.aprobar()
        assert prov.estado is EstadoProveedor.APROBADO

    def test_aprobar_puntaje_insuficiente_falla(self):
        prov = _proveedor()
        prov.evaluar(69)
        with pytest.raises(ErrorDominio):
            prov.aprobar()

    def test_aprobar_sin_evaluar_falla(self):
        prov = _proveedor()
        with pytest.raises(ErrorDominio):
            prov.aprobar()

    def test_aprobar_ya_aprobado_falla(self):
        prov = _proveedor()
        prov.evaluar(80)
        prov.aprobar()
        with pytest.raises(ErrorDominio):
            prov.aprobar()


# --- Rechazar ---------------------------------------------------------------

class TestRechazar:
    def test_rechazar_evaluado(self):
        prov = _proveedor()
        prov.evaluar(50)
        prov.rechazar()
        assert prov.estado is EstadoProveedor.RECHAZADO

    def test_rechazar_sin_evaluar_falla(self):
        prov = _proveedor()
        with pytest.raises(ErrorDominio):
            prov.rechazar()

    def test_rechazar_ya_aprobado_falla(self):
        prov = _proveedor()
        prov.evaluar(80)
        prov.aprobar()
        with pytest.raises(ErrorDominio):
            prov.rechazar()
