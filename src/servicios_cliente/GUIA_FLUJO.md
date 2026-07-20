# Guía de flujo — Servicios al Cliente (Instalaciones) · Integrante 5

> Rama: `feat/servicios-cliente`. El servicio **Solicitud** ya está implementado como
> referencia (4 capas). Extiende el flujo con las etapas siguientes.

## Contexto del proceso
Servicios al Cliente (Práctica 4 §5.2): `solicitud → programación → ejecución →
conformidad → facturación`. Ej.: instalación de pisos, armado de muebles.

## Qué implementar (endpoints)

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ hecho | POST | `/api/solicitudes` | Crear solicitud |
| ✅ hecho | GET | `/api/solicitudes/<id>` | Consultar solicitud |
| ⬜ | POST | `/api/solicitudes/<id>/programacion` | Asignar técnico y fecha |
| ⬜ | POST | `/api/solicitudes/<id>/ejecucion` | Registrar ejecución/evidencia |
| ⬜ | POST | `/api/solicitudes/<id>/conformidad` | Evaluar/aprobar servicio (acta) |
| ⬜ | POST | `/api/solicitudes/<id>/facturacion` | Generar comprobante |

## Modelo de dominio
Amplía la entidad **SolicitudServicio** (ya existe) con el avance de estado:
`REGISTRADA → PROGRAMADA → EJECUTADA → CONFORME`. Entidades de apoyo sugeridas:
- **Programacion**: `tecnico`, `fecha`.
- **Evidencia**: `descripcion`, `foto_url`.
- **Conformidad**: `aprobado` (bool), `observacion`.

Puedes modelarlas como campos/objetos de valor dentro de `SolicitudServicio` (agregado)
o como entidades propias con su repositorio.

## Pasos (por capa)
1. **Dominio** `domain/solicitud.py`: agrega métodos `programar()`, `ejecutar()`, `dar_conformidad()` con sus reglas de transición de estado.
2. **Infraestructura**: si añades entidades nuevas, crea sus repos/ORM y providers.
3. **Aplicación** `application/solicitud_servicio.py`: agrega los casos de uso.
4. **Presentación** `presentation/solicitud_controller.py`: agrega las rutas nuevas al `bp` existente.
5. **Prueba BDD** en Postman (carpeta "Servicios al Cliente").

## Criterio de aceptación (BDD ejemplo — Programar)
- **GIVEN** una solicitud en estado REGISTRADA.
- **WHEN** `POST /api/solicitudes/<id>/programacion` con `{ "tecnico": "T-01", "fecha": "2026-08-01" }`.
- **THEN** `200` con `estado: "PROGRAMADA"`; **AND** dar conformidad antes de ejecutar → `400`.

## Referencia
Servicio **Solicitud** (ya en las 4 capas): `domain/solicitud.py`,
`infrastructure/solicitud_*`, `application/solicitud_servicio.py`,
`presentation/solicitud_controller.py`.
