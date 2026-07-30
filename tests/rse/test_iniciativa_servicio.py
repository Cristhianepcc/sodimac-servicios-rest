"""Pruebas unitarias del servicio de aplicación del proceso `rse`.

El servicio se prueba con un repositorio en memoria (doble/Fake) inyectado,
recorriendo el ciclo BPM completo: formular → evaluar → monitorear → ejecutar
→ reportar → publicar. Sin base de datos ni HTTP.
"""
from __future__ import annotations

import pytest

from src.rse.application.iniciativa_servicio import IniciativaServicio
from src.rse.domain.iniciativa import EstadoIniciativa
from src.rse.infrastructure.iniciativa_memoria import IniciativaRepositorioMemoria
from src.shared.errores import ErrorDominio, NoEncontrado


@pytest.fixture
def servicio():
    return IniciativaServicio(repositorio=IniciativaRepositorioMemoria())


class TestFormulacionYConsulta:
    def test_crear_y_obtener(self, servicio):
        creada = servicio.crear("Reciclaje maderas", "RECICLAJE")
        obtenida = servicio.obtener(creada.codigo)
        assert obtenida.codigo == creada.codigo
        assert obtenida.estado is EstadoIniciativa.FORMULADA

    def test_obtener_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.obtener("RSE-NO-EXISTE")

    def test_listar(self, servicio):
        servicio.crear("A", "RECICLAJE")
        servicio.crear("B", "VOLUNTARIADO")
        assert len(servicio.listar()) == 2


class TestCicloBPM:
    def test_flujo_completo_hasta_publicacion(self, servicio):
        ini = servicio.crear("Eficiencia energética", "EFICIENCIA_ENERGETICA")
        cod = ini.codigo

        servicio.evaluar(cod, aprobada=True, presupuesto_aprobado=12000)
        assert servicio.obtener(cod).estado is EstadoIniciativa.APROBADA

        servicio.agregar_indicador(cod, "kWh ahorrados", "kWh", 1000, 800, 500)
        assert servicio.obtener(cod).estado is EstadoIniciativa.EN_MONITOREO

        servicio.registrar_evidencia(cod, "Instalación de paneles", 60)
        assert servicio.obtener(cod).estado is EstadoIniciativa.EN_EJECUCION

        servicio.generar_reporte(cod, "Reporte de sostenibilidad 2026")
        assert servicio.obtener(cod).estado is EstadoIniciativa.REPORTADA

        servicio.aprobar_publicacion(cod, "http://sodimac.pe/rse/2026")
        publicada = servicio.obtener(cod)
        assert publicada.estado is EstadoIniciativa.PUBLICADA
        assert publicada.reporte.aprobado_publicacion is True

    def test_evaluar_iniciativa_inexistente_falla(self, servicio):
        with pytest.raises(NoEncontrado):
            servicio.evaluar("RSE-XXX", aprobada=True, presupuesto_aprobado=100)

    def test_generar_reporte_sin_aprobar_falla(self, servicio):
        ini = servicio.crear("Voluntariado", "VOLUNTARIADO")
        with pytest.raises(ErrorDominio):
            servicio.generar_reporte(ini.codigo)

    def test_persiste_cambios_en_repositorio(self, servicio):
        # El servicio debe llamar a repositorio.actualizar tras cada transición.
        ini = servicio.crear("Proveedores sostenibles", "PROVEEDORES_SOSTENIBLES")
        servicio.evaluar(ini.codigo, aprobada=True, presupuesto_aprobado=5000)
        # Nueva consulta desde el repo refleja el estado actualizado.
        assert servicio.obtener(ini.codigo).presupuesto_aprobado == 5000
