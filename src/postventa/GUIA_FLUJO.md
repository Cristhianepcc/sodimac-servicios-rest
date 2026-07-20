# Guía de flujo — Postventa y Experiencia · Integrante 6

> Rama: `feat/postventa`. El servicio **Reclamo** ya está implementado como referencia
> (4 capas). Completa el resto del proceso de postventa.

## Contexto del proceso
Postventa (Práctica 4 §5.6): `registrar caso → validar garantía → evaluar producto →
determinar solución → cerrar caso → notificar`.

## Qué implementar (endpoints)

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ hecho | POST | `/api/reclamos` | Registrar reclamo |
| ✅ hecho | GET | `/api/reclamos/<id>` | Consultar reclamo |
| ⬜ | PUT | `/api/reclamos/<id>` | Actualizar reclamo |
| ⬜ | POST | `/api/validaciones/verificar` | Validar requisitos de garantía |
| ⬜ | POST | `/api/evaluaciones` | Registrar evaluación técnica |
| ⬜ | POST | `/api/soluciones` | Registrar solución (reembolso/cambio/reparación) |
| ⬜ | POST | `/api/casos/cerrar` | Cerrar caso |
| ⬜ | POST | `/api/notificaciones` | Enviar notificación al cliente |

## Entidades de dominio sugeridas
- **Validacion**: `reclamo_id`, `cumple_garantia` (bool), `motivo`.
- **EvaluacionTecnica**: `reclamo_id`, `diagnostico`, `procede` (bool).
- **Solucion**: `reclamo_id`, `tipo {REEMBOLSO, CAMBIO, REPARACION}`, `aprobada` (bool).
- **Caso**: `reclamo_id`, `estado {ABIERTO, CERRADO}`.
- **Notificacion**: `cliente`, `mensaje`, `estado {ENVIADA}`.

## Pasos (por capa) — por cada servicio
1. **Dominio**: `domain/validacion.py`, `domain/evaluacion.py`, `domain/solucion.py`, etc.
2. **Infraestructura**: repos memoria + ORM + SQLAlchemy + providers.
3. Registra los ORM en `src/shared/db.py::crear_tablas`.
4. **Aplicación**: un servicio por área.
5. **Presentación**: nuevos `*_controller.py` con su `bp` (se autoregistran).
6. **Prueba BDD** en Postman (carpeta "Postventa").

> Nota: la Práctica 4 menciona RabbitMQ para notificaciones asíncronas. Para el Lab 7
> basta el endpoint REST **síncrono** (`POST /api/notificaciones` que guarda y responde 201).
> La mensajería asíncrona queda fuera de alcance.

## Criterio de aceptación (BDD ejemplo — Validar garantía)
- **GIVEN** un reclamo registrado.
- **WHEN** `POST /api/validaciones/verificar` con `{ "reclamoId": "...", "cumpleGarantia": true }`.
- **THEN** `201` y el reclamo pasa a `EN_EVALUACION`; **AND** si no cumple → solución no procede.

## Referencia
Servicio **Reclamo** (4 capas): `domain/reclamo.py`, `infrastructure/reclamo_*`,
`application/reclamo_servicio.py`, `presentation/reclamo_controller.py`.
