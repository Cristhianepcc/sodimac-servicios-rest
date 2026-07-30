"""Pruebas del servicio de aplicación de Proveedor (Reabastecimiento).

El servicio se prueba con un repositorio en memoria (Fake) inyectado.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.proveedor_servicio import ProveedorServicio
from src.reabastecimiento.domain.proveedor import EstadoProveedor
from src.reabastecimiento.infrastructure.proveedor_memoria import ProveedorRepositorioMemoria
from src.shared.errores import ErrorDominio, NoEncontrado


@pytest.fixture
def servicio():
    return ProveedorServicio(repositorio=ProveedorRepositorioMemoria())


class TestRegistrarYObtener:
    def test_registrar_y_obtener(self, servicio):
        prov = servicio.registrar("EcoAndes SAC", "20512345678")
        obtenido = servicio.obtener(prov.id)
        assert obtenido.id == prov.id
        assert obtenido.estado is EstadoProveedor.REGISTRADO

    def test_obtener_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.obtener("PRV-NO-EXISTE")

    def test_listar(self, servicio):
        servicio.registrar("A", "11111111111")
        servicio.registrar("B", "22222222222")
        assert len(servicio.listar()) == 2


class TestCicloProveedor:
    def test_evaluar_aprobar(self, servicio):
        prov = servicio.registrar("EcoAndes SAC", "20512345678")
        evaluado = servicio.evaluar(prov.id, 85)
        assert evaluado.estado is EstadoProveedor.EVALUADO
        assert evaluado.puntaje == 85

        aprobado = servicio.aprobar(prov.id)
        assert aprobado.estado is EstadoProveedor.APROBADO

    def test_evaluar_rechazar(self, servicio):
        prov = servicio.registrar("EcoAndes SAC", "20512345678")
        servicio.evaluar(prov.id, 50)
        rechazado = servicio.rechazar(prov.id)
        assert rechazado.estado is EstadoProveedor.RECHAZADO

    def test_aprobar_puntaje_insuficiente_falla(self, servicio):
        prov = servicio.registrar("EcoAndes SAC", "20512345678")
        servicio.evaluar(prov.id, 60)
        with pytest.raises(ErrorDominio):
            servicio.aprobar(prov.id)

    def test_evaluar_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.evaluar("PRV-NO-EXISTE", 80)
