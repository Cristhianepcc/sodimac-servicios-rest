"""Dominio del proceso `postventa` — Reclamo (referencia).

Proceso: Postventa y Experiencia del Cliente. Entidad Reclamo + fábrica + repo.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
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
    dni: str
    email: str
    telefono: str
    producto: str
    motivo: str
    estado: EstadoReclamo = EstadoReclamo.REGISTRADO
    cumple_garantia: bool | None = None
    motivo_validacion: str | None = None
    diagnostico: str | None = None
    procede_evaluacion: bool | None = None
    tipo_solucion: str | None = None
    mensaje_cliente: str | None = None
    fecha_cierre: datetime | None = None
    fecha_notificacion: datetime | None = None


class ReclamoFabrica:
    @staticmethod
    def crear(
        cliente: str,
        dni: str,
        email: str,
        telefono: str,
        producto: str,
        motivo: str,
    ) -> Reclamo:
        if not cliente or not cliente.strip():
            raise ErrorDominio("El cliente es obligatorio.")
        if not dni or not dni.strip():
            raise ErrorDominio("El DNI es obligatorio.")
        if not email or not email.strip():
            raise ErrorDominio("El email es obligatorio.")
        if not telefono or not telefono.strip():
            raise ErrorDominio("El telefono es obligatorio.")
        if not producto or not producto.strip():
            raise ErrorDominio("El producto es obligatorio.")
        if not motivo or not motivo.strip():
            raise ErrorDominio("El motivo del reclamo es obligatorio.")
        return Reclamo(
            id=f"REC-{uuid.uuid4().hex[:8].upper()}",
            cliente=cliente.strip(),
            dni=dni.strip(),
            email=email.strip(),
            telefono=telefono.strip(),
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

    @abstractmethod
    def actualizar(self, reclamo: Reclamo) -> None: ...

    @abstractmethod
    def listar_abiertos(self, page: int, size: int) -> tuple[list[Reclamo], int]: ...

    @abstractmethod
    def listar_para_evaluacion(self, page: int, size: int) -> tuple[list[Reclamo], int]: ...

    @abstractmethod
    def listar_para_solucion(self, page: int, size: int) -> tuple[list[Reclamo], int]: ...
