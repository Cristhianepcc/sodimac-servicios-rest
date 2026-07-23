# Sodimac — Servicios Web REST (Laboratorio 7, enfoque BDD)

API REST de los **procesos de negocio de Sodimac**, implementada con arquitectura por
capas / **DDD** y guiada por **BDD** (pruebas de aceptación en Postman). Continuación de la
**Práctica 4** (identificación de servicios) y del **Laboratorio 5** (modelado BPM).

- **Stack:** Python · Flask · SQLAlchemy · PostgreSQL.
- **Curso:** Desarrollo de Software Empresarial — UNSA.

## Procesos de negocio (bounded contexts)

| Proceso | Paquete | Responsable |
| --- | --- | --- |
| Venta y Atención al Cliente (Omnicanal) | `src/ventas` | Integrante 1 (líder) |
| Cadena de Suministro / Reabastecimiento | `src/reabastecimiento` | Integrantes 2, 3, 4 |
| Servicios al Cliente (Instalaciones) | `src/servicios_cliente` | Integrante 5 |
| Postventa y Experiencia | `src/postventa` | Integrante 6 |
| RSE y Sostenibilidad | `src/rse` | Integrante 7 |

> El detalle de endpoints por integrante está en [`docs/ASIGNACION_FLUJOS.md`](docs/ASIGNACION_FLUJOS.md).

## Cómo ejecutar (rápido, sin base de datos)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py            # API en http://localhost:5000 (repositorio en memoria)
```

## Con PostgreSQL

```bash
docker compose up -d          # levanta Postgres
cp .env.example .env
REPO_BACKEND=sqlalchemy python run.py
```

## Flujo de trabajo del equipo (git)

- `master`: estable. `develop`: integración.
- Cada integrante: `clone/fork` → rama desde `develop` → `commit + push` de su servicio →
  Pull Request a `develop`.
- Buenas prácticas de commit: mensajes descriptivos (*clean code*).

## Pruebas unitarias

Prueban el **dominio** (invariantes del proceso) y los **servicios de aplicación**
con repositorios en memoria (dobles/Fakes), sin base de datos ni HTTP. La estructura
de `tests/` refleja la de `src/`.

```bash
pip install -r requirements-dev.txt
pytest
```

## Pruebas de aceptación (BDD)

Colección Postman en [`Pruebas de API/`](Pruebas%20de%20API/). Cada request sigue
**Given–When–Then**. Ejecutar con *Run Collection* o con Newman:

```bash
newman run "Pruebas de API/Sodimac.postman_collection.json" -e "Pruebas de API/Sodimac_local.postman_environment.json"
```
