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

    def programar(self, tecnico: str, fecha: str) -> None:
        if self.estado != EstadoSolicitud.REGISTRADA:
            raise ErrorDominio(f"No se puede programar una solicitud en estado {self.estado.value}.")
        if not tecnico or not tecnico.strip():
            raise ErrorDominio("El técnico es obligatorio para la programación.")
        if not fecha or not fecha.strip():
            raise ErrorDominio("La fecha es obligatoria para la programación.")
        self.tecnico = tecnico.strip()
        self.fecha = fecha.strip()
        self.estado = EstadoSolicitud.PROGRAMADA

    def ejecutar(self, descripcion: str, foto_url: str) -> None:
        if self.estado != EstadoSolicitud.PROGRAMADA:
            raise ErrorDominio(f"No se puede registrar ejecución para una solicitud en estado {self.estado.value}.")
        if not descripcion or not descripcion.strip():
            raise ErrorDominio("La descripción de la evidencia es obligatoria.")
        if not foto_url or not foto_url.strip():
            raise ErrorDominio("La URL de la foto de evidencia es obligatoria.")
        self.evidencia_descripcion = descripcion.strip()
        self.evidencia_foto_url = foto_url.strip()
        self.estado = EstadoSolicitud.EJECUTADA


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
