"""Dominio del proceso `servicios_cliente` — Solicitud de Servicio (referencia).

Proceso: Instalaciones y Proyectos. Entidad SolicitudServicio + fábrica + repo.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoSolicitud(str, Enum):
    REGISTRADA = "REGISTRADA"
    PROGRAMADA = "PROGRAMADA"
    EJECUTADA = "EJECUTADA"
    CONFORME = "CONFORME"


@dataclass
class SolicitudServicio:
    id: str
    cliente: str
    tipo_servicio: str
    direccion: str
    estado: EstadoSolicitud = EstadoSolicitud.REGISTRADA
    tecnico: str | None = None
    fecha: str | None = None
    evidencia_descripcion: str | None = None
    evidencia_foto_url: str | None = None
    conformidad_aprobado: bool | None = None
    conformidad_observacion: str | None = None
    comprobante: str | None = None


class SolicitudFabrica:
    @staticmethod
    def crear(cliente: str, tipo_servicio: str, direccion: str) -> SolicitudServicio:
        if not cliente or not cliente.strip():
            raise ErrorDominio("El cliente es obligatorio.")
        if not tipo_servicio or not tipo_servicio.strip():
            raise ErrorDominio("El tipo de servicio es obligatorio.")
        if not direccion or not direccion.strip():
            raise ErrorDominio("La dirección es obligatoria.")
        return SolicitudServicio(
            id=f"SOL-{uuid.uuid4().hex[:8].upper()}",
            cliente=cliente.strip(),
            tipo_servicio=tipo_servicio.strip(),
            direccion=direccion.strip(),
            estado=EstadoSolicitud.REGISTRADA,
        )


class ISolicitudRepositorio(ABC):
    @abstractmethod
    def adicionar(self, solicitud: SolicitudServicio) -> None: ...

    @abstractmethod
    def buscar(self, solicitud_id: str) -> SolicitudServicio | None: ...

    @abstractmethod
    def listar(self) -> list[SolicitudServicio]: ...
