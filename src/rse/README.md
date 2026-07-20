# Proceso: Responsabilidad Social y Sostenibilidad (RSE) — `rse`

**Responsable:** Integrante 7.

Proceso §4 de la Práctica 4 y BPM del Laboratorio 5: formular iniciativa → evaluar →
ejecutar → monitorear KPIs → reportar → publicar. Reutiliza el **BDM del Lab 5**.

## Servicios / endpoints

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ referencia | POST | `/api/iniciativas` | Formular iniciativa RSE |
| ✅ referencia | GET | `/api/iniciativas/<codigo>` | Consultar iniciativa |
| ✅ referencia | GET | `/api/iniciativas` | Listar iniciativas |
| ⬜ TODO | POST | `/api/iniciativas/<codigo>/evaluacion` | Evaluar (comité) |
| ⬜ TODO | POST | `/api/iniciativas/<codigo>/indicadores` | Consolidar KPIs |
| ⬜ TODO | POST | `/api/iniciativas/<codigo>/evidencias` | Registrar evidencia de avance |
| ⬜ TODO | POST | `/api/iniciativas/<codigo>/reporte` | Generar reporte de sostenibilidad |
| ⬜ TODO | POST | `/api/iniciativas/<codigo>/reporte/publicacion` | Aprobar publicación |

El BDM completo (IndicadorKPI, EvidenciaAvance, ReporteSostenibilidad, AccionCorrectiva)
está en `laboratorios/lab5/.../Implementacion_P5_RSE.md`. Sigue el patrón del servicio
de referencia `iniciativa` (4 capas).
