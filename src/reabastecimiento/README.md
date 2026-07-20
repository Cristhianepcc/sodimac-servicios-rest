# Proceso: Cadena de Suministro / Reabastecimiento — `reabastecimiento`

**Responsables:** Integrantes 2, 3 y 4 (proceso más grande, dividido por servicio).

Proceso §5.1 de la Práctica 4: detectar bajo stock → evaluar proveedores → generar
OC → recibir mercadería → control de calidad → almacenar → distribuir → auditar.

## Servicios / endpoints (Práctica 4 §5.1)

| Estado | Servicio | Endpoints | Responsable |
| --- | --- | --- | --- |
| ✅ referencia | **Inventario** | `POST /api/inventario`, `GET /api/inventario/bajo-stock`, `GET/PUT /api/inventario/<sku>` | Int. 2 (base) |
| 🟡 stub 501 | **Proveedores** | `GET /api/proveedores`, `GET /api/proveedores/<id>`, `POST .../evaluar`, `PUT .../aprobar`, `PUT .../rechazar` | Int. 2 |
| 🟡 stub 501 | **Órdenes de Compra** | `POST /api/ordenes-compra`, `GET .../<id>`, `PUT .../autorizar`, `DELETE .../<id>`, `POST .../enviar` | Int. 3 |
| 🟡 stub 501 | **Recepción y Calidad** | `POST /api/recepciones`, `PUT .../confirmar`, `POST /api/inspecciones`, `PUT .../validar`, `PUT .../rechazar` | Int. 4 |
| 🟡 stub 501 | **Almacén** | `POST /api/almacenes/ubicaciones`, `POST .../mercaderia`, `GET .../ubicaciones/<sku>`, `PUT .../inventario` | Int. 3 |
| 🟡 stub 501 | **Distribución** | `POST /api/distribucion/{pedidos,picking,packing,despachos}`, `PUT .../<id>/{estado,llegada}` | Int. 4 |
| 🟡 stub 501 | **Auditoría** | `POST /api/auditorias`, `POST .../movimientos`, `GET .../<id>/archivo`, `GET .../<sku>` | Int. 4 |

> Sugerencia de reparto interno: **Int.2** = Inventario+Proveedores · **Int.3** =
> Órdenes de Compra+Almacén · **Int.4** = Recepción+Distribución+Auditoría. Ajústenlo
> en `docs/ASIGNACION_FLUJOS.md`.

## Cómo implementar un stub

Cada `*_controller.py` marcado 🟡 ya tiene las **rutas** definidas devolviendo `501`.
Reemplaza los `no_implementado(...)` implementando las 4 capas siguiendo el servicio
de referencia **Inventario** (`domain/inventario.py`, `infrastructure/inventario_*`,
`application/inventario_servicio.py`, `presentation/inventario_controller.py`).
Recuerda registrar tu ORM en `src/shared/db.py::crear_tablas`.
