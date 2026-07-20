# Proceso: Responsabilidad Social y Sostenibilidad (RSE) — `rse`

**Responsable:** Integrante 7.

Proceso §4 de la Práctica 4 y BPM del Laboratorio 5: formular iniciativa → evaluar →
ejecutar → monitorear KPIs → reportar → publicar. Reutiliza el **BDM del Lab 5**.

## Servicios / endpoints

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ hecho | POST | `/api/iniciativas` | Formular iniciativa RSE |
| ✅ hecho | GET | `/api/iniciativas/<codigo>` | Consultar iniciativa |
| ✅ hecho | GET | `/api/iniciativas` | Listar iniciativas |
| ✅ hecho | POST | `/api/iniciativas/<codigo>/evaluacion` | Evaluar (comité) |
| ✅ hecho | POST | `/api/iniciativas/<codigo>/indicadores` | Consolidar KPIs |
| ✅ hecho | POST | `/api/iniciativas/<codigo>/evidencias` | Registrar evidencia de avance |
| ✅ hecho | POST | `/api/iniciativas/<codigo>/reporte` | Generar reporte de sostenibilidad |
| ✅ hecho | POST | `/api/iniciativas/<codigo>/reporte/publicacion` | Aprobar publicación |

> **Flujo RSE completado** (Integrante 7): las 4 capas del agregado `IniciativaRSE` con
> KPIs, evidencias, reporte y publicación. Persistencia validada en memoria y PostgreSQL.
> Pruebas BDD en `Pruebas de API/` (carpeta "RSE") → 15 asserts OK con newman.

El BDM completo (IndicadorKPI, EvidenciaAvance, ReporteSostenibilidad, AccionCorrectiva)
está en `laboratorios/lab5/.../Implementacion_P5_RSE.md`. Sigue el patrón del servicio
de referencia `iniciativa` (4 capas).
