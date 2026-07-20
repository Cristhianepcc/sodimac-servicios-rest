# Vista General de Arquitectura

Arquitectura **DDD + en Capas**, organizada por **bounded contexts** (un proceso de
negocio = un paquete en `src/`). Cada bounded context tiene las 4 capas.

## Capas (dentro de cada `src/<proceso>/`)

```
presentation/   Controladores REST (Flask Blueprints). Punto de entrada HTTP.
                Cada *_controller.py expone `bp` y se AUTOREGISTRA en el app factory.
        │  (depende de ↓)
application/    Servicios de aplicación: orquestan casos de uso. Sin reglas de negocio
                ni detalles HTTP. Obtienen el repositorio vía get_*_repositorio().
        │  (depende de ↓)
domain/         Entidades, objetos de valor, fábricas e INTERFACES de repositorio.
                Python puro (dataclasses). No conoce Flask ni SQLAlchemy.
        ▲  (implementado por ↓ — inversión de dependencias)
infrastructure/ Repositorio en memoria (Fake) + ORM SQLAlchemy + repositorio Postgres.
                Traduce entre dominio y persistencia.
```

Kernel compartido `src/shared/`: conexión a BD (`db.py`), errores de dominio
(`errores.py`), utilidades HTTP (`http.py`) y helper de stubs (`stub.py`).

## Diagrama de paquetes (bounded contexts)

```
                         ┌───────────────────────── src/ ─────────────────────────┐
   HTTP  ── Flask ──►    │  ventas   reabastecimiento   servicios_cliente          │
   (create_app          │  postventa   rse            ── cada uno: 4 capas ──►     │
    autoregistra bp)     │                                                         │
                         │  shared (db · errores · http · stub)  ◄── usado por todos│
                         └─────────────────────────────────────────────────────────┘
                                    │ REPO_BACKEND=sqlalchemy
                                    ▼
                             PostgreSQL (docker-compose)
```

## Decisiones clave

- **Autoregistro de blueprints:** `create_app()` escanea `src/*/presentation/*_controller.py`
  y registra cada `bp`. Nadie edita un router central → mínimos conflictos de merge (7 personas).
- **Doble de prueba por defecto:** `REPO_BACKEND=memoria` permite correr y probar sin BD.
- **Inversión de dependencias (SOLID):** la aplicación depende de la interfaz de repositorio
  del dominio; la infraestructura la implementa.
- **Frameworks:** Flask (MVC/REST) + SQLAlchemy (ORM) sobre PostgreSQL — permitidos por el enunciado.

## Flujo de una petición (ejemplo `POST /api/inventario`)

```
Controller (presentation) → InventarioServicio (application)
   → ProductoFabrica / ProductoInventario (domain)
   → get_inventario_repositorio() → RepositorioMemoria | RepositorioSQLAlchemy (infrastructure)
```
