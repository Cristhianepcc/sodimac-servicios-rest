# Guía de flujo — Ventas (Omnicanal) · Integrante 1 (líder)

> Rama: `feat/ventas`. Esta guía te dice **qué implementar** en este flujo y **cómo**.

## Contexto del proceso
Venta y Atención al Cliente (Omnicanal). Práctica 4 §4:
`carrito/cotización → verificar inventario → procesar pago → emitir comprobante`.

El servicio **Carrito** ya está implementado como referencia (las 4 capas). Tu trabajo
es completar el resto del flujo de venta reutilizando ese patrón.

## Qué implementar (endpoints)

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ hecho | POST | `/api/ventas/carrito` | Crear carrito |
| ✅ hecho | GET | `/api/ventas/carrito/<id>` | Consultar carrito |
| ⬜ | POST | `/api/ventas/carrito/<id>/confirmar` | Confirmar compra (cambia estado a CONFIRMADO) |
| ⬜ | POST | `/api/ventas/pagos` | Procesar pago de un carrito |
| ⬜ | POST | `/api/ventas/comprobantes` | Emitir boleta/factura |

## Entidades de dominio sugeridas
- **Pago**: `id`, `carrito_id`, `monto`, `medio {TARJETA, EFECTIVO, TRANSFERENCIA}`, `estado {PENDIENTE, APROBADO, RECHAZADO}`.
- **Comprobante**: `id`, `carrito_id`, `tipo {BOLETA, FACTURA}`, `monto`, `fecha`.
- Reutiliza **Carrito** (`domain/modelo.py`) para `confirmar()` (ya tiene el método).

## Pasos (por capa) — para cada servicio nuevo
1. **Dominio** `src/ventas/domain/pago.py`: entidad `Pago` + `PagoFabrica` + `IPagoRepositorio`.
2. **Infraestructura**: `pago_memoria.py`, `orm.py` (tabla), `pago_sqlalchemy.py`; añade el provider `get_pago_repositorio()` en `infrastructure/__init__.py`.
3. Registra el ORM en `src/shared/db.py::crear_tablas` (añade el import).
4. **Aplicación** `src/ventas/application/pago_servicio.py`: caso de uso `procesar_pago(...)`.
5. **Presentación** `src/ventas/presentation/pago_controller.py`: define `bp` con `POST /api/ventas/pagos` (se autoregistra solo).
6. **Prueba BDD** en Postman (carpeta "Ventas"): Given–When–Then.

## Criterio de aceptación (BDD ejemplo — Procesar pago)
- **GIVEN** un carrito confirmado con total 100.
- **WHEN** `POST /api/ventas/pagos` con `{ "carritoId": "...", "monto": 100, "medio": "TARJETA" }`.
- **THEN** responde `201` con `estado: "APROBADO"` y el pago referencia al carrito.
- **AND** si el monto ≠ total del carrito → `400`.

## Cómo probar
```bash
python run.py    # backend en memoria
curl -X POST localhost:5000/api/ventas/pagos -H 'Content-Type: application/json' \
  -d '{"carritoId":"CAR-XXXX","monto":100,"medio":"TARJETA"}'
```

## Referencia
Copia el patrón del servicio **Carrito**: `domain/modelo.py`, `domain/fabrica.py`,
`domain/repositorio.py`, `infrastructure/*`, `application/carrito_servicio.py`,
`presentation/carrito_controller.py`.
