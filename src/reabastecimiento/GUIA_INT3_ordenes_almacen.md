# Guía de flujo — Reabastecimiento: Órdenes de Compra + Almacén · Integrante 3

> Rama: `feat/reab-ordenes-almacen`. Ya existen los stubs
> `presentation/ordenes_compra_controller.py` y `presentation/almacen_controller.py`
> con las rutas en 501 — reemplázalos por tu implementación.

## Contexto del proceso
Reabastecimiento (Práctica 4 §5.1). Cubres dos servicios del ciclo:
**Órdenes de Compra** (adquisición a proveedores) y **Almacén** (ubicación de mercadería en el CD).

## Servicio A — Órdenes de Compra

| Método | Endpoint | Operación |
| --- | --- | --- |
| POST | `/api/ordenes-compra` | Generar orden de compra |
| GET | `/api/ordenes-compra/<id>` | Consultar orden |
| PUT | `/api/ordenes-compra/<id>/autorizar` | Autorizar orden |
| DELETE | `/api/ordenes-compra/<id>` | Cancelar orden |
| POST | `/api/ordenes-compra/<id>/enviar` | Enviar orden al proveedor |

**Entidades:** `OrdenCompra` (`id`, `proveedor_id`, `lineas[]`, `total`, `estado {BORRADOR, AUTORIZADA, ENVIADA, CANCELADA}`) y `LineaOC` (`sku`, `cantidad`, `precio_unitario`).
**Regla:** solo se puede **enviar** una orden **AUTORIZADA**; no se cancela una ya ENVIADA.

## Servicio B — Almacén

| Método | Endpoint | Operación |
| --- | --- | --- |
| POST | `/api/almacenes/ubicaciones` | Registrar ubicación (pasillo/estante) |
| POST | `/api/almacenes/mercaderia` | Ubicar mercadería en una ubicación |
| GET | `/api/almacenes/ubicaciones/<sku>` | Consultar ubicación de un SKU |
| PUT | `/api/almacenes/inventario` | Actualizar inventario en el CD |

**Entidad:** `Ubicacion` (`codigo`, `zona`, `sku`, `cantidad`).

## Pasos (por capa) — repite para cada servicio
1. **Dominio** `domain/orden_compra.py` y `domain/ubicacion.py` (entidad + fábrica + interfaz repo).
2. **Infraestructura**: repos memoria + ORM + SQLAlchemy + providers en `infrastructure/__init__.py`.
3. Registra los ORM en `src/shared/db.py::crear_tablas`.
4. **Aplicación**: `application/orden_compra_servicio.py`, `application/almacen_servicio.py`.
5. **Presentación**: reemplaza los stubs (conserva los `bp`).
6. **Prueba BDD** en Postman (carpeta "Reabastecimiento").

## Criterio de aceptación (BDD ejemplo — Autorizar orden)
- **GIVEN** una orden en estado BORRADOR con 2 líneas.
- **WHEN** `PUT /api/ordenes-compra/<id>/autorizar`.
- **THEN** `200` con `estado: "AUTORIZADA"`; **AND** enviar sin autorizar → `400`.

## Referencia
Servicio **Inventario** (4 capas). Para la orden con líneas, mira cómo `Carrito`
maneja `items[]` en `src/ventas` (relación 1..*).
