from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoRecepcion(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"


class ResultadoInspeccion(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFORME = "CONFORME"
    RECHAZADO = "RECHAZADO"


@dataclass
class ItemRecepcion:
    sku: str
    cantidad_recibida: int


@dataclass
class Recepcion:
    id: str
    orden_compra_id: str
    fecha_llegada: str
    estado: EstadoRecepcion = EstadoRecepcion.PENDIENTE
    items: list[ItemRecepcion] = field(default_factory=list)

    def confirmar(self) -> None:
        if self.estado != EstadoRecepcion.PENDIENTE:
            raise ErrorDominio("Solo recepciones pendientes pueden confirmarse.")
        if not self.items:
            raise ErrorDominio("La recepción debe tener al menos un item.")
        self.estado = EstadoRecepcion.CONFIRMADA


@dataclass
class Inspeccion:
    id: str
    recepcion_id: str
    fecha: str
    resultado: ResultadoInspeccion = ResultadoInspeccion.PENDIENTE
    observaciones: str = ""

    def validar(self, observaciones: str = "") -> None:
        if self.resultado != ResultadoInspeccion.PENDIENTE:
            raise ErrorDominio("La inspección ya fue cerrada.")
        self.resultado = ResultadoInspeccion.CONFORME
        self.observaciones = observaciones

    def rechazar(self, observaciones: str) -> None:
        if not observaciones or not observaciones.strip():
            raise ErrorDominio("Debe indicar el motivo del rechazo.")
        if self.resultado != ResultadoInspeccion.PENDIENTE:
            raise ErrorDominio("La inspección ya fue cerrada.")
        self.resultado = ResultadoInspeccion.RECHAZADO
        self.observaciones = observaciones


class RecepcionFabrica:
    @staticmethod
    def crear(orden_compra_id: str, items: list[dict]) -> Recepcion:
        if not orden_compra_id or not orden_compra_id.strip():
            raise ErrorDominio("El ID de la orden de compra es obligatorio.")
        if not items:
            raise ErrorDominio("Debe incluir al menos un item.")
        items_dominio = [
            ItemRecepcion(sku=i["sku"], cantidad_recibida=int(i["cantidadRecibida"]))
            for i in items
        ]
        for it in items_dominio:
            if it.cantidad_recibida <= 0:
                raise ErrorDominio("La cantidad recibida debe ser mayor a cero.")
        return Recepcion(
            id=f"REC-{uuid.uuid4().hex[:8].upper()}",
            orden_compra_id=orden_compra_id.strip(),
            fecha_llegada=datetime.now(timezone.utc).isoformat(),
            items=items_dominio,
        )


class InspeccionFabrica:
    @staticmethod
    def crear(recepcion_id: str) -> Inspeccion:
        if not recepcion_id or not recepcion_id.strip():
            raise ErrorDominio("El ID de recepción es obligatorio.")
        return Inspeccion(
            id=f"INS-{uuid.uuid4().hex[:8].upper()}",
            recepcion_id=recepcion_id.strip(),
            fecha=datetime.now(timezone.utc).isoformat(),
        )


class IRecepcionRepositorio(ABC):
    @abstractmethod
    def adicionar_recepcion(self, recepcion: Recepcion) -> None: ...
    @abstractmethod
    def buscar_recepcion(self, recepcion_id: str) -> Recepcion | None: ...
    @abstractmethod
    def listar_recepciones(self) -> list[Recepcion]: ...
    @abstractmethod
    def actualizar_recepcion(self, recepcion: Recepcion) -> None: ...


class IInspeccionRepositorio(ABC):
    @abstractmethod
    def adicionar(self, inspeccion: Inspeccion) -> None: ...
    @abstractmethod
    def buscar(self, inspeccion_id: str) -> Inspeccion | None: ...
    @abstractmethod
    def listar_por_recepcion(self, recepcion_id: str) -> list[Inspeccion]: ...
    @abstractmethod
    def actualizar(self, inspeccion: Inspeccion) -> None: ...
