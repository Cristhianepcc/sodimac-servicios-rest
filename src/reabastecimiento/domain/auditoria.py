from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from src.shared.errores import ErrorDominio


class TipoAuditoria(str, Enum):
    FISICA = "FISICA"
    CONTABLE = "CONTABLE"


class EstadoAuditoria(str, Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADA = "COMPLETADA"


class TipoMovimiento(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"


@dataclass
class Auditoria:
    id: str
    sku: str
    tipo: TipoAuditoria
    fecha: str
    estado: EstadoAuditoria = EstadoAuditoria.PENDIENTE
    observaciones: str = ""

    def completar(self, observaciones: str = "") -> None:
        if self.estado != EstadoAuditoria.PENDIENTE:
            raise ErrorDominio("La auditoría ya fue completada.")
        self.estado = EstadoAuditoria.COMPLETADA
        self.observaciones = observaciones


@dataclass
class MovimientoStock:
    id: str
    sku: str
    tipo: TipoMovimiento
    cantidad: int
    motivo: str
    fecha: str
    usuario: str = ""


class AuditoriaFabrica:
    @staticmethod
    def crear(sku: str, tipo: str) -> Auditoria:
        if not sku or not sku.strip():
            raise ErrorDominio("El SKU es obligatorio.")
        try:
            tipo_aud = TipoAuditoria(tipo)
        except ValueError:
            raise ErrorDominio(f"Tipo de auditoría inválido: {tipo}")
        return Auditoria(
            id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            sku=sku.strip(),
            tipo=tipo_aud,
            fecha=datetime.now(timezone.utc).isoformat(),
        )


class MovimientoStockFabrica:
    @staticmethod
    def crear(sku: str, tipo: str, cantidad: int, motivo: str, usuario: str = "") -> MovimientoStock:
        if not sku or not sku.strip():
            raise ErrorDominio("El SKU es obligatorio.")
        try:
            tipo_mov = TipoMovimiento(tipo)
        except ValueError:
            raise ErrorDominio(f"Tipo de movimiento inválido: {tipo}")
        if cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser mayor a cero.")
        if not motivo or not motivo.strip():
            raise ErrorDominio("El motivo es obligatorio.")
        return MovimientoStock(
            id=f"MOV-{uuid.uuid4().hex[:8].upper()}",
            sku=sku.strip(),
            tipo=tipo_mov,
            cantidad=cantidad,
            motivo=motivo.strip(),
            fecha=datetime.now(timezone.utc).isoformat(),
            usuario=usuario.strip(),
        )


class IAuditoriaRepositorio(ABC):
    @abstractmethod
    def adicionar_auditoria(self, auditoria: Auditoria) -> None: ...
    @abstractmethod
    def buscar_auditoria(self, auditoria_id: str) -> Auditoria | None: ...
    @abstractmethod
    def listar_auditorias(self) -> list[Auditoria]: ...
    @abstractmethod
    def actualizar_auditoria(self, auditoria: Auditoria) -> None: ...


class IMovimientoStockRepositorio(ABC):
    @abstractmethod
    def adicionar(self, movimiento: MovimientoStock) -> None: ...
    @abstractmethod
    def listar_por_sku(self, sku: str) -> list[MovimientoStock]: ...
    @abstractmethod
    def listar_todos(self) -> list[MovimientoStock]: ...
