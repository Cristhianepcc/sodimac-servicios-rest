# Guía de flujo — Reabastecimiento: Proveedores · Integrante 2

> Rama: `feat/reab-proveedores`. Ya existe el stub `presentation/proveedores_controller.py`
> con las rutas devolviendo 501 — reemplaza los `no_implementado(...)` por tu implementación.

## Contexto del proceso
Reabastecimiento (Práctica 4 §5.1) → Subsistema de Gestión de Compras. Tu servicio
gestiona el ciclo de **proveedores**: consultar, evaluar y aprobar/rechazar.

El servicio **Inventario** ya está implementado como referencia (4 capas). Cópialo.

## Qué implementar (endpoints — ya definidos en el stub)

| Método | Endpoint | Operación |
| --- | --- | --- |
| GET | `/api/proveedores` | Listar proveedores |
| GET | `/api/proveedores/<id>` | Consultar proveedor |
| POST | `/api/proveedores/<id>/evaluar` | Evaluar proveedor (registra puntaje) |
| PUT | `/api/proveedores/<id>/aprobar` | Aprobar proveedor |
| PUT | `/api/proveedores/<id>/rechazar` | Rechazar proveedor |

## Entidad de dominio sugerida
- **Proveedor**: `id`, `nombre`, `ruc`, `puntaje` (0–100), `estado {REGISTRADO, EVALUADO, APROBADO, RECHAZADO}`.
- Regla: solo se puede **aprobar** un proveedor ya **evaluado** con `puntaje >= 70` (ajústalo a criterio del equipo).

## Pasos (por capa)
1. **Dominio** `domain/proveedor.py`: `Proveedor` + `ProveedorFabrica` + `IProveedorRepositorio` (métodos: adicionar, buscar, listar, actualizar).
2. **Infraestructura**: `proveedor_memoria.py`, `orm.py` (tabla `reabastecimiento_proveedor`), `proveedor_sqlalchemy.py`; añade `get_proveedor_repositorio()` en `infrastructure/__init__.py`.
3. Registra el ORM en `src/shared/db.py::crear_tablas`.
4. **Aplicación** `application/proveedor_servicio.py`: `registrar`, `evaluar`, `aprobar`, `rechazar`, `listar`.
5. **Presentación**: reemplaza el cuerpo de `presentation/proveedores_controller.py` (mantén el `bp`).
6. **Prueba BDD** en Postman (carpeta "Reabastecimiento").

## Criterio de aceptación (BDD ejemplo — Aprobar proveedor)
- **GIVEN** un proveedor evaluado con puntaje 80.
- **WHEN** `PUT /api/proveedores/<id>/aprobar`.
- **THEN** responde `200` con `estado: "APROBADO"`.
- **AND** aprobar un proveedor NO evaluado → `400`.

## Cómo probar
```bash
python run.py
curl -X POST localhost:5000/api/proveedores -H 'Content-Type: application/json' \
  -d '{"nombre":"Aceros SAC","ruc":"20123456789"}'
```

## Referencia
Servicio **Inventario**: `domain/inventario.py`, `infrastructure/inventario_*`,
`application/inventario_servicio.py`, `presentation/inventario_controller.py`.
