# Proceso: Postventa y Experiencia del Cliente — `postventa`

**Responsable:** Integrante 6.

Proceso §5.6 de la Práctica 4: registrar caso → validar garantía → evaluar producto →
determinar solución → cerrar caso → notificar.

## Servicios / endpoints

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ referencia | POST | `/api/reclamos` | Registrar reclamo |
| ✅ referencia | GET | `/api/reclamos/<id>` | Consultar reclamo |
| ✅ referencia | GET | `/api/reclamos` | Listar reclamos |
| ⬜ TODO | PUT | `/api/reclamos/<id>` | Actualizar reclamo |
| ⬜ TODO | POST | `/api/validaciones/verificar` | Validar requisitos de garantía |
| ⬜ TODO | POST | `/api/evaluaciones` | Registrar evaluación técnica |
| ⬜ TODO | POST | `/api/soluciones` | Registrar solución (reembolso/cambio/reparación) |
| ⬜ TODO | POST | `/api/casos/cerrar` | Cerrar caso |
| ⬜ TODO | POST | `/api/notificaciones` | Enviar notificación al cliente |

> Nota: la Práctica 4 menciona RabbitMQ para notificaciones asíncronas; para el Lab 7
> basta implementar el endpoint REST síncrono (la mensajería queda fuera de alcance).

Sigue el patrón del servicio de referencia `reclamo` (4 capas).
