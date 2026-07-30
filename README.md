# Sodimac — Servicios Web del Negocio

Servicios REST que dan soporte a las **tareas automáticas** de los procesos de negocio
modelados en BPMN, e integrados con ellos de forma asíncrona vía **RabbitMQ**.

Es el **repositorio de servicios web** del Proyecto Final del curso *Desarrollo de
Software Empresarial* (UNSA). Su contraparte es el repositorio del proyecto BPM en
Bonita: [`Cristhianepcc/laboratorio_6`](https://github.com/Cristhianepcc/laboratorio_6).

---

## 1. Equipo de trabajo

| | |
| --- | --- |
| **Equipo** | *(por completar)* |
| **Cliente** | Sodimac (organización ficticia — retail de mejoramiento del hogar) |
| **Curso** | Desarrollo de Software Empresarial — UNSA, 2026-B |
| **Docente** | Edgar Sarmiento Calisaya |

**Integrantes**

| # | Apellidos y Nombres | Módulo a cargo |
| --- | --- | --- |
| 1 | *(por completar)* | `src/ventas` — Venta y Atención al Cliente |
| 2 | *(por completar)* | `src/reabastecimiento` — Órdenes de compra y almacén |
| 3 | *(por completar)* | `src/reabastecimiento` — Proveedores |
| 4 | *(por completar)* | `src/reabastecimiento` — Recepción, distribución y auditoría |
| 5 | *(por completar)* | `src/servicios_cliente` — Instalaciones |
| 6 |  Erick Pérez     | `src/postventa` — Reclamos |
| 7 | Taipe, Cristhian | `src/rse` — RSE y Sostenibilidad, e integración por eventos |

---

## 2. Propósito del proyecto

Los procesos de negocio de Sodimac se modelan y ejecutan en **Bonita** (BPMN), pero un
motor BPM no debe albergar la lógica del negocio: la orquesta. Este repositorio provee
esa lógica como **servicios web autónomos y reutilizables**, de modo que:

- las **tareas automáticas** de los procesos (consolidar KPIs, registrar evidencias,
  notificar aliados) se resuelvan invocando servicios en vez de scripts embebidos;
- un mismo servicio pueda componerse desde **varios procesos** sin duplicarse
  (reutilización, el objetivo central de SOA);
- procesos y servicios evolucionen y se desplieguen **por separado**, comunicándose por
  un broker de mensajes en lugar de acoplarse en el tiempo.

---

## 3. Visión general de arquitectura: DDD

Arquitectura **por capas** con **Domain-driven Design**. Cada proceso de negocio es un
*bounded context* independiente, con su propio modelo, en `src/<contexto>/`:

```
src/<contexto>/
├── domain/          Entidades, objetos de valor, agregados, fábricas
│                    y el PUERTO del repositorio (interfaz abstracta).
│                    Python puro: no importa Flask ni SQLAlchemy.
├── application/     Servicios de aplicación (casos de uso). Orquestan el
│                    dominio y la persistencia; no contienen reglas.
├── infrastructure/  Implementaciones del repositorio (memoria / SQLAlchemy)
│                    y el mapeo ORM.
└── presentation/    Adaptadores de entrada: controladores REST (Blueprints).
```

**La dependencia apunta siempre hacia adentro.** El dominio define la interfaz del
repositorio y la infraestructura la implementa (inversión de dependencias, la *D* de
SOLID); por eso el mismo caso de uso corre contra PostgreSQL o contra un doble en
memoria sin cambiar una línea.

### Bloques tácticos de DDD y dónde están

| Bloque | Dónde está |
| --- | --- |
| **Entidad** | `IniciativaRSE`, `Carrito`, `ProductoInventario`, `Reclamo`, `SolicitudServicio` — identidad propia y ciclo de vida |
| **Objeto de valor** | `IndicadorKPI`, `EvidenciaAvance`, `AccionCorrectiva`, `ItemCarrito`; `EventoIntegracion` y `ResultadoEvaluacion` son inmutables (`frozen`) |
| **Agregado** | `IniciativaRSE` como raíz: encapsula KPIs, evidencias, reporte y acciones correctivas. `Carrito` sobre `ItemCarrito` |
| **Servicio de dominio** | `EvaluadorDeMetas` — la regla del gateway «¿Metas cumplidas?» combina política y KPIs, y no pertenece a ninguna entidad |
| **Fábrica** | `IniciativaFabrica` (`.crear()` / `.desde_convocatoria()`), `CarritoFabrica`, `ProductoFabrica`, `ReclamoFabrica`, `SolicitudFabrica` |
| **Repositorio** | Puertos `IIniciativaRepositorio`, `ICarritoRepositorio`, `IProductoRepositorio`, `IReclamoRepositorio`, `ISolicitudRepositorio` + adaptadores `…Memoria` / `…SQLAlchemy` |
| **Servicio de aplicación** | `IniciativaServicio`, `CarritoServicio`, `InventarioServicio`, `ReclamoServicio`, `SolicitudServicio` |
| **Módulo** | Un paquete por *bounded context* (`ventas`, `reabastecimiento`, `servicios_cliente`, `postventa`, `rse`) |

> ⚠️ La entidad de instalaciones se llama `SolicitudServicio` (una *solicitud de
> servicio*), que se presta a confusión con un servicio de dominio. Es una entidad;
> el único servicio de dominio del proyecto es `EvaluadorDeMetas`.

Las **invariantes viven en el agregado**, no en el controlador. Por ejemplo, "una
iniciativa aprobada requiere presupuesto > 0" está en `IniciativaRSE.evaluar()`, así que
se cumple tanto si la llamada llega por HTTP como por un evento de RabbitMQ.

### Arquitectura guiada por eventos

La API HTTP y el consumidor de mensajes son **dos adaptadores de entrada distintos sobre
la misma capa de aplicación**:

```
        ┌─────────────── Bonita (procesos BPMN) ───────────────┐
        │  ServiceTask "Notificar áreas"                       │
        └───────────────────────┬──────────────────────────────┘
                                │ conector REST (publica)
                       rse.convocatorias
                                ▼
   run.py  (HTTP)  ┐                            ┌  worker.py (AMQP)
                   ├──►  application/  ──►  domain/  ◄──┤
   controllers     ┘         (casos de uso)              └  manejadores_evento
                                ▲
                       rse.postulaciones           rse.notificaciones
                                │                          │
                    Proceso 2 (Proveedores)      ──► de vuelta a Bonita
```

| Cola | Sentido | Contenido |
| --- | --- | --- |
| `rse.convocatorias` | Bonita → servicio | Iniciativa aprobada; el servicio la materializa |
| `rse.postulaciones` | Proceso 2 → servicio | Propuesta de proveedor; se registra como evidencia |
| `rse.notificaciones` | Servicio → Bonita | Resultado de la tarea automática |

Detalles de diseño que importan:

- **Puerto + adaptadores** (`src/shared/eventos/`): la aplicación publica eventos sin
  conocer AMQP; hay un doble en memoria para probar sin broker.
- **Idempotencia**: RabbitMQ entrega *al menos una vez*, así que reprocesar un mensaje no
  debe duplicar datos. `sincronizar_convocatoria()` es idempotente por diseño.
- **Ack manual y `prefetch=1`**: el mensaje se confirma solo cuando el caso de uso
  terminó bien; si el worker cae a medio camino, el trabajo no se pierde.
- **Colas durables y mensajes persistentes**: ninguna de las dos partes pierde trabajo si
  la otra está caída (acoplamiento temporal bajo).

---

## 4. Principales servicios web REST

Documentación en **formato estándar OpenAPI 3.0.3**, generada desde el propio código y
explorable con **Swagger UI**:

| | |
| --- | --- |
| Especificación | `GET /openapi.json` |
| Swagger UI | `GET /docs` |

> La spec se **deriva del `url_map` de Flask**, no de un YAML mantenido a mano: con 5
> *bounded contexts* y 7 integrantes, un documento paralelo se desincroniza al primer
> merge. La fuente de verdad es el código, y hay pruebas que verifican que ninguna ruta
> quede fuera.

En Swagger las operaciones aparecen **agrupadas por proceso de negocio**.

### Recurso `iniciativas` — RSE y Sostenibilidad
*Propósito: gestionar el ciclo completo de una iniciativa de sostenibilidad, desde su
formulación hasta la publicación del reporte.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/iniciativas` | cuerpo: `nombre`, `tipo`, `descripcion`, `requierePresupuesto`, `presupuestoSolicitado` |
| `GET` | `/api/iniciativas` | — |
| `GET` | `/api/iniciativas/{codigo}` | ruta: `codigo` |
| `POST` | `/api/iniciativas/{codigo}/evaluacion` | ruta: `codigo`; cuerpo: `aprobada`, `presupuestoAprobado`, `comentario` |
| `POST` | `/api/iniciativas/{codigo}/indicadores` | ruta: `codigo`; cuerpo: `nombre`, `unidad`, `valorLineaBase`, `valorActual`, `meta` |
| `POST` | `/api/iniciativas/{codigo}/evidencias` | ruta: `codigo`; cuerpo: `descripcion`, `porcentajeAvance`, `archivoUrl` |
| `POST` | `/api/iniciativas/{codigo}/reporte` | ruta: `codigo`; cuerpo: `resumen` |
| `POST` | `/api/iniciativas/{codigo}/reporte/publicacion` | ruta: `codigo`; cuerpo: `urlPublicacion` |
| `GET` | `/api/iniciativas/{codigo}/cumplimiento` | ruta: `codigo`; query: `tolerancia` (def. 0.9) |

**Modelos:** agregado `IniciativaRSE` (raíz) · objetos de valor `IndicadorKPI`,
`EvidenciaAvance`, `AccionCorrectiva`, `ReporteSostenibilidad` · servicio de dominio
`EvaluadorDeMetas`.

### Recurso `ventas/carrito` — Venta y Atención al Cliente
*Propósito: armar la cotización/carrito omnicanal del cliente.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/ventas/carrito` | cuerpo: `cliente`, `items[]` (`sku`, `cantidad`, `precioUnitario`) |
| `GET` | `/api/ventas/carrito` | — |
| `GET` | `/api/ventas/carrito/{carrito_id}` | ruta: `carrito_id` |

**Modelos:** agregado `Carrito` (raíz) · objeto de valor `ItemCarrito` · fábrica `CarritoFabrica`.

### Recurso `ordenes-compra` — Cadena de Suministro
*Propósito: emitir y autorizar órdenes de compra a proveedores.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/ordenes-compra` | cuerpo de la orden |
| `GET` | `/api/ordenes-compra/{orden_id}` | ruta: `orden_id` |
| `PUT` | `/api/ordenes-compra/{orden_id}/autorizar` | ruta: `orden_id` |
| `POST` | `/api/ordenes-compra/{orden_id}/enviar` | ruta: `orden_id` |
| `DELETE` | `/api/ordenes-compra/{orden_id}` | ruta: `orden_id` |

### Recurso `inventario` — Cadena de Suministro
*Propósito: controlar existencias y disparar el reabastecimiento.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/inventario` | cuerpo: `sku`, `nombre`, `stock`, `stockMinimo` |
| `GET` | `/api/inventario/{sku}` | ruta: `sku` |
| `PUT` | `/api/inventario/{sku}` | ruta: `sku`; cuerpo: `stock` |
| `GET` | `/api/inventario/bajo-stock` | — |

**Modelos:** agregado `ProductoInventario` (regla `bajoStock` derivada de `stockMinimo`).

### Recurso `solicitudes` — Servicios al Cliente
*Propósito: registrar y seguir solicitudes de instalación.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/solicitudes` | cuerpo de la solicitud |
| `GET` | `/api/solicitudes` | — |
| `GET` | `/api/solicitudes/{solicitud_id}` | ruta: `solicitud_id` |

**Modelos:** agregado `Solicitud`.

### Recurso `reclamos` — Postventa y Experiencia
*Propósito: registrar reclamos y su atención.*

| Método | URL | Parámetros |
| --- | --- | --- |
| `POST` | `/api/reclamos` | Registrar reclamo |
| `GET` | `/api/reclamos` | Listar reclamos abiertos (paginado) |
| `GET` | `/api/reclamos/{reclamo_id}` | Consultar detalle de reclamo |
| `PUT` | `/api/reclamos/{reclamo_id}` | Actualizar datos del reclamo |
| `PATCH` | `/api/reclamos/{reclamo_id}/garantia` | Validar garantía |
| `GET` | `/api/evaluaciones` | Listar reclamos pendientes de evaluación |
| `PATCH` | `/api/reclamos/{reclamo_id}/evaluacion` | Registrar evaluación técnica |
| `GET` | `/api/soluciones` | Listar reclamos aptos para solución |
| `PATCH` | `/api/reclamos/{reclamo_id}/solucion` | Registrar solución |
| `POST` | `/api/reclamos/{reclamo_id}/notificacion` | Enviar notificación al cliente |

**Modelos:** agregado `Reclamo`.

### Otros recursos de Cadena de Suministro

`proveedores`, `recepciones`, `inspecciones`, `distribucion`, `almacenes` y `auditorias`
—con sus operaciones completas— están documentados en `/docs`.

### Respuestas de error

Las excepciones de dominio se traducen a HTTP en un único punto
(`src/shared/http.py`), así que los controladores no repiten `try/except`:

| Excepción | HTTP | Significado |
| --- | --- | --- |
| `ErrorDominio` | `400` | Violación de una regla de negocio |
| `NoEncontrado` | `404` | El recurso no existe |
| `Conflicto` | `409` | Conflicto de estado |

---

## 5. Cómo ejecutar

### API REST (sin base de datos)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py            # http://localhost:5000  ·  Swagger en /docs
```

### Con PostgreSQL

```bash
docker compose up -d
cp .env.example .env
REPO_BACKEND=sqlalchemy python run.py
```

### Worker de eventos (integración con Bonita)

Requiere el broker levantado — el `docker-compose.yml` está en el repositorio BPM:

```bash
# 1) en el repo laboratorio_6:
docker compose up -d                       # RabbitMQ (5672 AMQP, 15672 UI)

# 2) aquí, en otra terminal:
EVENTOS_BACKEND=rabbitmq python worker.py
```

Para comprobar el flujo sin Bonita, los scripts `scripts/02_publicar_convocatoria.sh` y
`scripts/04_publicar_postulacion.sh` del repositorio BPM publican con **el mismo POST que
usa el conector REST** del proceso. El worker consume, ejecuta el caso de uso y deja la
respuesta en `rse.notificaciones` (visible en <http://localhost:15672>).

---

## 6. Pruebas

```bash
pip install -r requirements-dev.txt
pytest                                     # 63 pruebas
```

| Tipo | Qué cubre |
| --- | --- |
| Dominio | Invariantes de los agregados, sin HTTP ni base de datos |
| Aplicación | Casos de uso contra repositorios en memoria (dobles) |
| Eventos | Flujo BPM completo con dobles del broker: convocatoria → postulación → notificación, más idempotencia y mensajes malformados |
| OpenAPI | Que la spec cubra **todas** las rutas y sea estructuralmente válida |

**Aceptación (BDD)** — colección Postman en [`Pruebas de API/`](Pruebas%20de%20API/), cada
request en **Given–When–Then**:

```bash
newman run "Pruebas de API/Sodimac.postman_collection.json" \
  -e "Pruebas de API/Sodimac_local.postman_environment.json"
```

---

## 7. Flujo de trabajo del equipo (git)

| Rama | Rol |
| --- | --- |
| `main` | Estable (equivale a *master* en el enunciado) |
| `develop` | Integración (equivale a *desarrollo*) |
| `feat/<nombre>` | Una por *feature* / integrante |

Ciclo: rama desde `develop` → commits → Pull Request a `develop` → merge a `main`.
`develop` se sincroniza con `main` por *rebase* o *merge* antes de cada integración.

---

## 8. Documentación adicional

| Documento | Contenido |
| --- | --- |
| [`docs/PROPOSITO.md`](docs/PROPOSITO.md) | Propósito y alcance |
| [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) | Vista de arquitectura y diagrama de paquetes |
| [`docs/MODELO_DOMINIO.md`](docs/MODELO_DOMINIO.md) | Modelo de dominio (diagrama de clases) |
| [`docs/ASIGNACION_FLUJOS.md`](docs/ASIGNACION_FLUJOS.md) | Reparto de endpoints por integrante |
