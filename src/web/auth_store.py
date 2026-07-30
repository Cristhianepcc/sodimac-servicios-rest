"""Persistencia SQLite para autenticacion web."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app

ROLES = {"CLIENTE", "POSTVENTA", "TECNICO"}


def _db_path() -> Path:
    instance_path = Path(current_app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)
    return instance_path / "usuarios.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (rol IN ('CLIENTE', 'POSTVENTA', 'TECNICO'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usuario_reclamos (
            usuario_id INTEGER NOT NULL,
            reclamo_id TEXT NOT NULL,
            PRIMARY KEY (usuario_id, reclamo_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """
    )
    conn.commit()
    return conn


def crear_usuario(nombre_usuario: str, password: str, rol: str) -> tuple[bool, str]:
    nombre = (nombre_usuario or "").strip()
    clave = password or ""
    rol = (rol or "").strip().upper()
    if not nombre or not clave:
        return False, "Usuario y password son obligatorios."
    if rol not in ROLES:
        return False, "Rol no permitido."

    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre_usuario, password, rol) VALUES (?, ?, ?)",
                (nombre, clave, rol),
            )
            conn.commit()
        return True, "Usuario registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "El usuario ya existe."


def autenticar(nombre_usuario: str, password: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, nombre_usuario, rol FROM usuarios WHERE nombre_usuario = ? AND password = ?",
            ((nombre_usuario or "").strip(), password or ""),
        ).fetchone()
    return dict(row) if row else None


def vincular_reclamo(usuario_id: int, reclamo_id: str) -> None:
    if not reclamo_id:
        return
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO usuario_reclamos (usuario_id, reclamo_id) VALUES (?, ?)",
            (usuario_id, reclamo_id),
        )
        conn.commit()


def listar_reclamos_usuario(usuario_id: int) -> list[str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT reclamo_id FROM usuario_reclamos WHERE usuario_id = ? ORDER BY reclamo_id",
            (usuario_id,),
        ).fetchall()
    return [row["reclamo_id"] for row in rows]
