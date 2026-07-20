# Guía de flujo — Reabastecimiento: Recepción + Distribución + Auditoría · Integrante 4

> Rama: `feat/reab-recepcion-distr-auditoria`. Ya existen los stubs
> `recepcion_controller.py`, `distribucion_controller.py`, `auditoria_controller.py`
> con las rutas en 501 — reemplázalos.

## Contexto del proceso
Reabastecimiento (Práctica 4 §5.1). Cubres la parte final del ciclo logístico:
**Recepción/Calidad** (entrada al CD), **Distribución** (salida a tiendas) y **Auditoría** (control de stock).

## Servicio A — Recepción y Control de Calidad

| Método | Endpoint | Operación |
| --- | --- | --- |
| POST | `/api/recepciones` | Registrar llegada de mercadería |
| PUT | `/api/recepciones/<id>/confirmar` | Confirmar recepción |
| POST | `/api/inspecciones` | Inspeccionar mercadería |
| PUT | `/api/inspecciones/<id>/validar` | Validar conformidad |
| PUT | `/api/inspecciones/<id>/rechazar` | Registrar rechazo |

**Entidades:** `Recepcion` (`id`, `orden_id`, `estado {PENDIENTE, CONFIRMADA}`),
`Inspeccion` (`id`, `recepcion_id`, `resultado {PENDIENTE, CONFORME, RECHAZADA}`).

## Servicio B — Distribución

| Método | Endpoint | Operación |
| --- | --- | --- |
| POST | `/api/distribucion/pedidos` | Generar pedido de reabastecimiento |
| POST | `/api/distribucion/picking` | Preparar picking |
| POST | `/api/distribucion/packing` | Preparar packing |
| POST | `/api/distribucion/despachos` | Programar despacho |
| PUT | `/api/distribucion/<id>/estado` | Actualizar estado de envío |
| PUT | `/api/distribucion/<id>/llegada` | Registrar llegada a tienda |

**Entidad:** `Despacho` (`id`, `tienda`, `items[]`, `estado {PEDIDO, PICKING, PACKING, DESPACHADO, EN_RUTA, ENTREGADO}`).

## Servicio C — Auditoría

| Método | Endpoint | Operación |
| --- | --- | --- |
| POST | `/api/auditorias` | Crear auditoría |
| POST | `/api/auditorias/movimientos` | Registrar movimiento de stock |
| GET | `/api/auditorias/<id>/archivo` | Generar archivo de auditoría |
| GET | `/api/auditorias/<sku>` | Consultar historial de movimientos |

**Entidades:** `Auditoria` (`id`, `fecha`, `movimientos[]`), `MovimientoStock` (`sku`, `tipo {INGRESO, SALIDA, AJUSTE}`, `cantidad`, `fecha`).

## Pasos (por capa) — repite por servicio
1. **Dominio**: `domain/recepcion.py`, `domain/despacho.py`, `domain/auditoria.py`.
2. **Infraestructura**: repos memoria + ORM + SQLAlchemy + providers en `infrastructure/__init__.py`.
3. Registra los ORM en `src/shared/db.py::crear_tablas`.
4. **Aplicación**: un servicio por área.
5. **Presentación**: reemplaza los 3 stubs (conserva los `bp`).
6. **Prueba BDD** en Postman (carpeta "Reabastecimiento").

## Criterio de aceptación (BDD ejemplo — Estado de envío)
- **GIVEN** un despacho en estado PACKING.
- **WHEN** `PUT /api/distribucion/<id>/estado` con `{ "estado": "DESPACHADO" }`.
- **THEN** `200` y el nuevo estado; **AND** una transición inválida (p. ej. PEDIDO→ENTREGADO) → `400`.

## Referencia
Servicio **Inventario** (4 capas); para colecciones (`items[]`, `movimientos[]`)
mira `Carrito`/`items` en `src/ventas`.
