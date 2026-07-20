# Proceso: Venta y Atención al Cliente (Omnicanal) — `ventas`

**Responsable:** Integrante 1 (líder).

Proceso de negocio §4 de la Práctica 4: verificación de inventario, procesamiento
de pago, validación y emisión de comprobante.

## Servicios / endpoints

| Estado | Método | Endpoint | Operación |
| --- | --- | --- | --- |
| ✅ referencia | POST | `/api/ventas/carrito` | Crear carrito / cotización |
| ✅ referencia | GET | `/api/ventas/carrito/<id>` | Consultar carrito |
| ✅ referencia | GET | `/api/ventas/carrito` | Listar carritos |
| ⬜ TODO | POST | `/api/ventas/carrito/<id>/confirmar` | Confirmar compra (verificar stock) |
| ⬜ TODO | POST | `/api/ventas/pagos` | Procesar pago |
| ⬜ TODO | POST | `/api/ventas/comprobantes` | Emitir boleta/factura |

## Cómo agregar un servicio (patrón)

1. **Dominio** (`domain/`): entidad + fábrica + interfaz de repositorio.
2. **Infraestructura** (`infrastructure/`): repo en memoria + ORM + repo SQLAlchemy + provider en `__init__.py`.
3. **Aplicación** (`application/`): servicio con el caso de uso.
4. **Presentación** (`presentation/<servicio>_controller.py`): define `bp` (se autoregistra).
5. **Prueba BDD** en Postman (Given–When–Then) dentro de la carpeta del proceso.

> El servicio de referencia (`carrito`) está completo por las 4 capas: úsalo como plantilla.
