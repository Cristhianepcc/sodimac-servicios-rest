# Proceso: Servicios al Cliente (Instalaciones y Proyectos) — `servicios_cliente`

**Responsable:** Integrante 5.

Proceso §5.2 de la Práctica 4: solicitud → programación → ejecución → conformidad → facturación.

## Servicios / endpoints

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ referencia | POST | `/api/solicitudes` | Crear solicitud de servicio |
| ✅ referencia | GET | `/api/solicitudes/<id>` | Consultar solicitud |
| ✅ referencia | GET | `/api/solicitudes` | Listar solicitudes |
| ⬜ TODO | POST | `/api/solicitudes/<id>/programacion` | Asignar técnico y fecha |
| ⬜ TODO | POST | `/api/solicitudes/<id>/ejecucion` | Registrar ejecución/evidencia |
| ⬜ TODO | POST | `/api/solicitudes/<id>/conformidad` | Evaluar/aprobar servicio |
| ⬜ TODO | POST | `/api/solicitudes/<id>/facturacion` | Generar comprobante |

Sigue el patrón del servicio de referencia `solicitud` (4 capas) para agregar cada operación.
