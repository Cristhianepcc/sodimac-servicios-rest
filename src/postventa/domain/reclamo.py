"""Dominio del proceso `postventa` — Reclamo (referencia).

Proceso: Postventa y Experiencia del Cliente. Entidad Reclamo + fábrica + repo.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoReclamo(str, Enum):
    REGISTRADO = "REGISTRADO"
    EN_EVALUACION = "EN_EVALUACION"
    RESUELTO = "RESUELTO"
    RECHAZADO = "RECHAZADO"


@dataclass
class Reclamo:
    id: str
    cliente: str
    producto: str
    motivo: str
    estado: EstadoReclamo = EstadoReclamo.REGISTRADO


class ReclamoFabrica:
    @staticmethod
    def crear(cliente: str, producto: str, motivo: str) -> Reclamo:
        if not cliente or not cliente.strip():
            raise ErrorDominio("El cliente es obligatorio.")
        if not producto or not producto.strip():
            raise ErrorDominio("El producto es obligatorio.")
        if not motivo or not motivo.strip():
            raise ErrorDominio("El motivo del reclamo es obligatorio.")
        return Reclamo(
            id=f"REC-{uuid.uuid4().hex[:8].upper()}",
            cliente=cliente.strip(),
            producto=producto.strip(),
            motivo=motivo.strip(),
            estado=EstadoReclamo.REGISTRADO,
        )


class IReclamoRepositorio(ABC):
    @abstractmethod
    def adicionar(self, reclamo: Reclamo) -> None: ...

    @abstractmethod
    def buscar(self, reclamo_id: str) -> Reclamo | None: ...

    @abstractmethod
    def listar(self) -> list[Reclamo]: ...
