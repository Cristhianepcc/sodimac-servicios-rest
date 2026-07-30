# Modelo de Dominio

Entidades por bounded context. Las de **referencia** ya están implementadas
(`src/<proceso>/domain/`); el resto se agrega al implementar cada servicio.

## ventas
- **Carrito** (raíz): `id`, `cliente`, `items[]`, `estado {ABIERTO, COTIZADO, CONFIRMADO}`, `total` (calculado).
- **ItemCarrito**: `sku`, `cantidad`, `precio_unitario`, `subtotal` (calculado).

## reabastecimiento
- **ProductoInventario** (referencia): `sku`, `nombre`, `stock`, `stock_minimo`, `bajo_stock` (calculado).
- Por implementar: **Proveedor**, **OrdenCompra** + **LineaOC**, **Recepcion**, **Inspeccion**,
  **Ubicacion**, **PedidoDistribucion**, **Auditoria** + **MovimientoStock**.

## servicios_cliente
- **SolicitudServicio** (referencia): `id`, `cliente`, `tipo_servicio`, `direccion`,
  `estado {REGISTRADA, PROGRAMADA, EJECUTADA, CONFORME}`.
- Por implementar: **Programacion**, **Ejecucion/Evidencia**, **Conformidad**, **Comprobante**.

## postventa
- **Reclamo** : `id`, `cliente`, `dni`, `email`, `telefono`, `producto`, `motivo`,
`estado`, `cumpleGarantia`, `motivoValidacion`, `diagnostico`,
`procedeEvaluacion`, `tipoSolucion`, `mensajeCliente`,
`fechaCierre`, `fechaNotificacion`.

## rse  (reutiliza el BDM del Lab 5)
- **IniciativaRSE** (referencia): `codigo`, `nombre`, `tipo {RECICLAJE, EFICIENCIA_ENERGETICA,
  VOLUNTARIADO, PROVEEDORES_SOSTENIBLES}`, `descripcion`, `requiere_presupuesto`,
  `presupuesto_solicitado`, `estado {FORMULADA, EN_EVALUACION, APROBADA, ARCHIVADA}`.
- Por implementar (del BDM Lab 5): **IndicadorKPI**, **EvidenciaAvance**,
  **ReporteSostenibilidad**, **AccionCorrectiva**.

> Convenciones de nombrado (Python/PEP8): clases `PascalCase`, funciones/atributos
> `snake_case`, paquetes en minúscula. JSON de la API en `camelCase`.
