"""Pruebas del servicio de aplicación de Auditoría (Reabastecimiento).

El servicio se prueba con repositorios en memoria (Fake) inyectados.
Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.reabastecimiento.application.auditoria_servicio import (
    AuditoriaServicio,
    MovimientoStockServicio,
)
from src.reabastecimiento.domain.auditoria import EstadoAuditoria
from src.reabastecimiento.infrastructure.auditoria_memoria import (
    AuditoriaRepositorioMemoria,
    MovimientoStockRepositorioMemoria,
)
from src.shared.errores import NoEncontrado


@pytest.fixture
def auditoria_servicio():
    return AuditoriaServicio(repositorio=AuditoriaRepositorioMemoria())


@pytest.fixture
def movimiento_servicio():
    return MovimientoStockServicio(repositorio=MovimientoStockRepositorioMemoria())


class TestAuditoriaServicio:
    def test_crear_y_obtener(self, auditoria_servicio):
        a = auditoria_servicio.crear("SKU-001", "FISICA")
        obtenida = auditoria_servicio.obtener(a.id)
        assert obtenida.id == a.id
        assert obtenida.estado is EstadoAuditoria.PENDIENTE

    def test_obtener_inexistente_falla(self, auditoria_servicio):
        with pytest.raises(NoEncontrado):
            auditoria_servicio.obtener("AUD-NO-EXISTE")

    def test_completar(self, auditoria_servicio):
        a = auditoria_servicio.crear("SKU-001", "FISICA")
        completada = auditoria_servicio.completar(a.id, "Inventario correcto")
        assert completada.estado is EstadoAuditoria.COMPLETADA

    def test_listar(self, auditoria_servicio):
        auditoria_servicio.crear("SKU-001", "FISICA")
        auditoria_servicio.crear("SKU-002", "CONTABLE")
        assert len(auditoria_servicio.listar()) == 2


class TestMovimientoStockServicio:
    def test_registrar_y_historial(self, movimiento_servicio):
        m = movimiento_servicio.registrar("SKU-001", "ENTRADA", 50, "Compra")
        assert m.sku == "SKU-001"
        assert m.cantidad == 50

        historial = movimiento_servicio.historial("SKU-001")
        assert len(historial) == 1

    def test_historial_vacio(self, movimiento_servicio):
        assert movimiento_servicio.historial("SKU-NO-EXISTE") == []

    def test_listar_todos(self, movimiento_servicio):
        movimiento_servicio.registrar("SKU-001", "ENTRADA", 10, "Compra")
        movimiento_servicio.registrar("SKU-002", "SALIDA", 5, "Venta")
        assert len(movimiento_servicio.listar_todos()) == 2
