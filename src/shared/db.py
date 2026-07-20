"""Infraestructura de base de datos (SQLAlchemy + PostgreSQL).

Expone el `engine`, la fábrica de sesiones `SessionLocal` y la `Base`
declarativa que heredan los modelos ORM de cada módulo. Solo se inicializa
cuando `REPO_BACKEND == 'sqlalchemy'`.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import Config


class Base(DeclarativeBase):
    """Base declarativa común para todos los modelos ORM (todos los módulos)."""


_engine = None
_SessionLocal = None


def init_engine():
    """Crea el engine/sesión una sola vez (lazy)."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(Config.DATABASE_URL, future=True)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine, _SessionLocal


def crear_tablas() -> None:
    """Crea todas las tablas registradas en `Base.metadata`.

    Importa aquí los modelos ORM de cada módulo para que queden registrados
    antes de `create_all` (cada integrante agrega su import al implementar su ORM).
    """
    engine, _ = init_engine()
    # Import perezoso de los modelos ORM de cada proceso para registrarlos en
    # Base.metadata antes de create_all. Cada integrante agrega aquí el import de
    # su ORM cuando implemente su servicio.
    from src.postventa.infrastructure import orm as _postventa_orm  # noqa: F401
    from src.reabastecimiento.infrastructure import orm as _reab_orm  # noqa: F401
    from src.rse.infrastructure import orm as _rse_orm  # noqa: F401
    from src.servicios_cliente.infrastructure import orm as _sc_orm  # noqa: F401
    from src.ventas.infrastructure import orm as _ventas_orm  # noqa: F401

    Base.metadata.create_all(engine)


def get_session():
    """Devuelve una nueva sesión de SQLAlchemy."""
    _, SessionLocal = init_engine()
    return SessionLocal()
