# Asignación de flujos (7 integrantes)

Cada integrante implementa **al menos un Servicio Web (controlador) y un Caso de Prueba**
(request Postman con BDD), y lo demuestra con sus propios commits (requisito del Lab 7).

> Reemplacen "Integrante N" por sus nombres.

| # | Integrante (nombre) | Proceso | Servicio(s) a implementar | Estado base |
| --- | --- | --- | --- | --- |
| 1 | _(líder)_ ___________ | ventas | Carrito ✅ + Pago, Comprobante | referencia lista |
| 2 | ___________ | reabastecimiento | Inventario ✅ + Proveedores | referencia + stub |
| 3 | ___________ | reabastecimiento | Órdenes de Compra + Almacén | stubs 501 |
| 4 | ___________ | reabastecimiento | Recepción/Calidad + Distribución + Auditoría | stubs 501 |
| 5 | ___________ | servicios_cliente | Solicitud ✅ + Programación, Ejecución, Conformidad, Facturación | referencia lista |
| 6 | Erick Perez | postventa | Reclamo ✅ + Validación, Evaluación, Soluciones, Casos, Notificaciones | referencia lista |
| 7 | ___________ | rse | Iniciativa ✅ + KPIs, Evidencias, Reporte, Publicación | referencia lista |


## Checklist por integrante

Para cada servicio propio:

- [ ] Dominio: entidad + fábrica + interfaz de repositorio (`domain/`).
- [ ] Infraestructura: repo en memoria + ORM + repo SQLAlchemy + provider (`infrastructure/`).
- [ ] Registrar el ORM en `src/shared/db.py::crear_tablas`.
- [ ] Aplicación: servicio con el caso de uso (`application/`).
- [ ] Presentación: `*_controller.py` con `bp` (se autoregistra) (`presentation/`).
- [ ] Prueba de aceptación BDD en Postman (Given–When–Then), carpeta del proceso.
- [ ] Commit + push a `develop` con mensaje descriptivo → Pull Request.

## Flujo git

- `master` (estable) · `develop` (integración).
- `git clone` → `git checkout develop` → `git checkout -b feat/<proceso>-<servicio>`
  → trabajar → `git commit` → `git push -u origin feat/...` → Pull Request a `develop`.
