"""Pruebas del servicio de dominio `EvaluadorDeMetas`.

Cubren la regla del gateway «¿Metas cumplidas?» del proceso BPM.
"""
from __future__ import annotations

import pytest

from src.rse.domain.evaluacion_metas import EvaluadorDeMetas
from src.rse.domain.iniciativa import IndicadorKPI, IniciativaFabrica
from src.shared.errores import ErrorDominio


def _iniciativa(*kpis: IndicadorKPI):
    ini = IniciativaFabrica.desde_convocatoria(
        codigo="RSE-2026-001",
        nombre="Reciclaje de mermas",
        tipo="RECICLAJE",
        presupuesto_aprobado=15000.0,
    )
    for k in kpis:
        ini.agregar_indicador(k)
    return ini


def test_tolerancia_fuera_de_rango_es_rechazada():
    with pytest.raises(ErrorDominio):
        EvaluadorDeMetas(tolerancia=0)
    with pytest.raises(ErrorDominio):
        EvaluadorDeMetas(tolerancia=1.5)


def test_sin_indicadores_no_se_puede_evaluar():
    with pytest.raises(ErrorDominio):
        EvaluadorDeMetas().evaluar(_iniciativa())


def test_meta_alcanzada_cuenta_como_cumplida():
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 40.0, 50.0, 50.0))
    r = EvaluadorDeMetas().evaluar(ini)
    assert r.cumplidas is True
    assert r.porcentaje_global == 100.0
    assert r.rezagados == ()
    assert r.requiere_acciones_correctivas is False


def test_el_avance_se_mide_desde_la_linea_base_no_desde_cero():
    """Partir de 40 rumbo a 50 con valor 40 es 0 % de avance, no 80 %."""
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 40.0, 40.0, 50.0))
    r = EvaluadorDeMetas().evaluar(ini)
    assert r.porcentaje_global == 0.0
    assert r.cumplidas is False


def test_avance_parcial_por_debajo_de_la_tolerancia():
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 0.0, 50.0, 100.0))
    r = EvaluadorDeMetas(tolerancia=0.9).evaluar(ini)
    assert r.cumplidas is False
    assert r.porcentaje_global == 50.0
    assert r.rezagados == ("Merma valorizada",)


def test_la_tolerancia_permite_dar_por_cumplida_una_meta_casi_lograda():
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 0.0, 92.0, 100.0))
    assert EvaluadorDeMetas(tolerancia=0.9).evaluar(ini).cumplidas is True
    assert EvaluadorDeMetas(tolerancia=0.95).evaluar(ini).cumplidas is False


def test_un_solo_rezagado_arrastra_a_toda_la_iniciativa():
    ini = _iniciativa(
        IndicadorKPI("Merma valorizada", "t", 0.0, 100.0, 100.0),
        IndicadorKPI("Tiendas adheridas", "u", 0.0, 10.0, 100.0),
    )
    r = EvaluadorDeMetas().evaluar(ini)
    assert r.cumplidas is False
    assert r.indicadores_cumplidos == 1
    assert r.indicadores_totales == 2
    assert r.rezagados == ("Tiendas adheridas",)
    assert r.porcentaje_global == 55.0


def test_meta_igual_a_linea_base_no_divide_por_cero():
    ini = _iniciativa(IndicadorKPI("Incidentes ambientales", "u", 0.0, 0.0, 0.0))
    r = EvaluadorDeMetas().evaluar(ini)
    assert r.cumplidas is True
    assert r.porcentaje_global == 100.0


def test_el_avance_se_acota_y_no_supera_el_100():
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 0.0, 250.0, 100.0))
    assert EvaluadorDeMetas().evaluar(ini).porcentaje_global == 100.0


def test_retroceso_bajo_la_linea_base_no_da_avance_negativo():
    ini = _iniciativa(IndicadorKPI("Merma valorizada", "t", 50.0, 10.0, 100.0))
    r = EvaluadorDeMetas().evaluar(ini)
    assert r.porcentaje_global == 0.0
    assert r.cumplidas is False


def test_el_resultado_es_inmutable():
    r = EvaluadorDeMetas().evaluar(
        _iniciativa(IndicadorKPI("KPI", "u", 0.0, 100.0, 100.0))
    )
    with pytest.raises(Exception):
        r.cumplidas = False  # type: ignore[misc]
