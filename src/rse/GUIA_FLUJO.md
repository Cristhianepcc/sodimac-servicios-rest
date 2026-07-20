# Guía de flujo — RSE y Sostenibilidad · Integrante 7

> Rama: `feat/rse`. El servicio **Iniciativa** ya está implementado como referencia
> (4 capas). Completa el ciclo de RSE reutilizando el **BDM del Lab 5**.

## Contexto del proceso
RSE (Práctica 4 §4 + BPM Lab 5): `formular iniciativa → evaluar (comité) →
ejecutar → monitorear KPIs → generar reporte → aprobar publicación`.

## Qué implementar (endpoints)

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ hecho | POST | `/api/iniciativas` | Formular iniciativa |
| ✅ hecho | GET | `/api/iniciativas/<codigo>` | Consultar iniciativa |
| ⬜ | POST | `/api/iniciativas/<codigo>/evaluacion` | Evaluar (aprobar + presupuesto) |
| ⬜ | POST | `/api/iniciativas/<codigo>/indicadores` | Agregar KPI |
| ⬜ | POST | `/api/iniciativas/<codigo>/evidencias` | Registrar evidencia de avance |
| ⬜ | POST | `/api/iniciativas/<codigo>/reporte` | Generar reporte de sostenibilidad |
| ⬜ | POST | `/api/iniciativas/<codigo>/reporte/publicacion` | Aprobar publicación |

## Modelo de dominio (BDM Lab 5 — ver `laboratorios/lab5/.../Implementacion_P5_RSE.md`)
Amplía **IniciativaRSE** (agregado) con sus composiciones:
- **IndicadorKPI**: `nombre`, `unidad`, `valor_linea_base`, `valor_actual`, `meta`.
- **EvidenciaAvance**: `fecha`, `descripcion`, `porcentaje_avance` (0–100), `archivo_url`.
- **ReporteSostenibilidad**: `codigo`, `fecha_generacion`, `resumen`, `url_publicacion`, `aprobado_publicacion`.
- **AccionCorrectiva**: `descripcion`, `responsable`, `fecha`.

Reglas (contratos del Lab 5): evaluar aprobada requiere `presupuesto_aprobado > 0`;
`porcentaje_avance` entre 0 y 100.

## Pasos (por capa)
1. **Dominio** `domain/iniciativa.py`: agrega las clases del BDM y métodos `evaluar()`, `agregar_indicador()`, `registrar_evidencia()`, `generar_reporte()`, `aprobar_publicacion()`.
2. **Infraestructura**: amplía el ORM (tablas hijas 1..*) + mapeo en el repo SQLAlchemy.
3. **Aplicación** `application/iniciativa_servicio.py`: agrega los casos de uso.
4. **Presentación** `presentation/iniciativa_controller.py`: agrega las rutas al `bp` existente.
5. **Prueba BDD** en Postman (carpeta "RSE").

## Criterio de aceptación (BDD ejemplo — Evaluar)
- **GIVEN** una iniciativa FORMULADA que requiere presupuesto.
- **WHEN** `POST /api/iniciativas/<codigo>/evaluacion` con `{ "aprobada": true, "presupuestoAprobado": 5000 }`.
- **THEN** `200` con `estado: "APROBADA"`; **AND** aprobada con presupuesto 0 → `400`.

## Referencia
Servicio **Iniciativa** (4 capas) + el BDM completo del Lab 5 ya documentado.
