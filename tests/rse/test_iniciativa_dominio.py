"""Pruebas unitarias del dominio del proceso `rse` (Iniciativa RSE).

Cubre las invariantes del agregado `IniciativaRSE` (ciclo BPM del Lab 5) y su
fábrica. Python puro: sin Flask ni base de datos.
"""
from __future__ import annotations

from datetime import date

import pytest

from src.rse.domain.iniciativa import (
    AccionCorrectiva,
    EstadoIniciativa,
    EvidenciaAvance,
    IndicadorKPI,
    IniciativaFabrica,
    IniciativaRSE,
    ReporteSostenibilidad,
    TipoIniciativa,
)
from src.shared.errores import ErrorDominio


# --- Helpers ----------------------------------------------------------------

def _iniciativa(**kwargs) -> IniciativaRSE:
    base = dict(
        codigo="RSE-TEST",
        nombre="Reciclaje de maderas",
        tipo=TipoIniciativa.RECICLAJE,
    )
    base.update(kwargs)
    return IniciativaRSE(**base)


# --- Fábrica ----------------------------------------------------------------

class TestIniciativaFabrica:
    def test_crear_genera_codigo_y_estado_formulada(self):
        ini = IniciativaFabrica.crear("Reciclaje", "RECICLAJE")
        assert ini.codigo.startswith("RSE-")
        assert ini.tipo is TipoIniciativa.RECICLAJE
        assert ini.estado is EstadoIniciativa.FORMULADA

    def test_crear_recorta_nombre(self):
        ini = IniciativaFabrica.crear("  Voluntariado  ", "VOLUNTARIADO")
        assert ini.nombre == "Voluntariado"

    def test_crear_sin_nombre_falla(self):
        with pytest.raises(ErrorDominio):
            IniciativaFabrica.crear("   ", "RECICLAJE")

    def test_crear_tipo_invalido_falla(self):
        with pytest.raises(ErrorDominio):
            IniciativaFabrica.crear("X", "NO_EXISTE")

    def test_crear_presupuesto_negativo_falla(self):
        with pytest.raises(ErrorDominio):
            IniciativaFabrica.crear("X", "RECICLAJE", presupuesto_solicitado=-1)

    def test_crear_requiere_presupuesto_pero_cero_falla(self):
        with pytest.raises(ErrorDominio):
            IniciativaFabrica.crear(
                "X", "RECICLAJE", requiere_presupuesto=True, presupuesto_solicitado=0
            )

    def test_crear_requiere_presupuesto_valido_ok(self):
        ini = IniciativaFabrica.crear(
            "X", "RECICLAJE", requiere_presupuesto=True, presupuesto_solicitado=5000
        )
        assert ini.presupuesto_solicitado == 5000
        assert ini.requiere_presupuesto is True


# --- Evaluar (gateway gw2, contrato `teval`) --------------------------------

class TestEvaluar:
    def test_aprobar_con_presupuesto_positivo(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=True, presupuesto_aprobado=8000)
        assert ini.aprobada is True
        assert ini.presupuesto_aprobado == 8000
        assert ini.estado is EstadoIniciativa.APROBADA

    def test_aprobar_sin_presupuesto_falla(self):
        ini = _iniciativa()
        with pytest.raises(ErrorDominio):
            ini.evaluar(aprobada=True, presupuesto_aprobado=0)

    def test_rechazar_archiva_y_anula_presupuesto(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=False, presupuesto_aprobado=8000)
        assert ini.aprobada is False
        assert ini.presupuesto_aprobado == 0.0
        assert ini.estado is EstadoIniciativa.ARCHIVADA


# --- Indicadores ------------------------------------------------------------

class TestIndicadores:
    def test_agregar_indicador_pasa_a_monitoreo(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=True, presupuesto_aprobado=100)
        ini.agregar_indicador(IndicadorKPI("CO2", "ton", 10, 8, 5))
        assert len(ini.indicadores) == 1
        assert ini.estado is EstadoIniciativa.EN_MONITOREO

    def test_no_agregar_indicador_si_archivada(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=False, presupuesto_aprobado=0)  # → ARCHIVADA
        with pytest.raises(ErrorDominio):
            ini.agregar_indicador(IndicadorKPI("CO2", "ton"))


# --- Evidencias -------------------------------------------------------------

class TestEvidencias:
    def test_registrar_evidencia_valida_pasa_a_ejecucion(self):
        ini = _iniciativa()
        ini.registrar_evidencia(EvidenciaAvance(date.today(), "avance", 50))
        assert len(ini.evidencias) == 1
        assert ini.estado is EstadoIniciativa.EN_EJECUCION

    @pytest.mark.parametrize("pct", [-1, 101, 150])
    def test_evidencia_porcentaje_fuera_de_rango_falla(self, pct):
        ini = _iniciativa()
        with pytest.raises(ErrorDominio):
            ini.registrar_evidencia(EvidenciaAvance(date.today(), "x", pct))


# --- Reporte y publicación --------------------------------------------------

class TestReporteYPublicacion:
    def test_generar_reporte_requiere_aprobacion(self):
        ini = _iniciativa()  # aún no aprobada
        with pytest.raises(ErrorDominio):
            ini.generar_reporte("resumen")

    def test_generar_reporte_tras_aprobar(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=True, presupuesto_aprobado=100)
        reporte = ini.generar_reporte("resumen anual")
        assert isinstance(reporte, ReporteSostenibilidad)
        assert reporte.codigo.startswith("REP-")
        assert ini.estado is EstadoIniciativa.REPORTADA

    def test_publicar_sin_reporte_falla(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=True, presupuesto_aprobado=100)
        with pytest.raises(ErrorDominio):
            ini.aprobar_publicacion("http://sodimac.pe/rse")

    def test_publicar_tras_reporte(self):
        ini = _iniciativa()
        ini.evaluar(aprobada=True, presupuesto_aprobado=100)
        ini.generar_reporte()
        ini.aprobar_publicacion("http://sodimac.pe/rse")
        assert ini.reporte.aprobado_publicacion is True
        assert ini.reporte.url_publicacion == "http://sodimac.pe/rse"
        assert ini.estado is EstadoIniciativa.PUBLICADA


def test_la_evaluacion_conserva_el_comentario_del_comite():
    """El comentario del contrato `teval` se persiste en el agregado.

    Antes viajaba desde el controlador hasta `evaluar()` y se descartaba
    silenciosamente, así que la justificación del comité se perdía.
    """
    ini = IniciativaFabrica.crear(
        "Reciclaje de mermas", "RECICLAJE", requiere_presupuesto=True,
        presupuesto_solicitado=15000.0,
    )
    ini.evaluar(True, 15000.0, "Aprobada con presupuesto reducido por el comité.")
    assert ini.comentario_evaluacion == "Aprobada con presupuesto reducido por el comité."


def test_el_comentario_tambien_se_conserva_si_se_rechaza():
    ini = IniciativaFabrica.crear("Voluntariado", "VOLUNTARIADO")
    ini.evaluar(False, 0.0, "Sin alineación con los objetivos del año.")
    assert ini.comentario_evaluacion == "Sin alineación con los objetivos del año."
    assert ini.estado == EstadoIniciativa.ARCHIVADA
