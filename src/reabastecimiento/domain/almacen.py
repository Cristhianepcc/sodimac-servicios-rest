from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

from src.shared.errores import ErrorDominio


@dataclass
class Ubicacion:
    codigo: str
    pasillo: str
    estante: str
    nivel: str


@dataclass
class MercaderiaUbicada:
    id: str
    sku: str
    ubicacion_codigo: str
    cantidad: int
    fecha_ubicacion: str


class UbicacionFabrica:
    @staticmethod
    def crear(codigo: str, pasillo: str, estante: str, nivel: str) -> Ubicacion:
        if not codigo or not codigo.strip():
            raise ErrorDominio("El código de ubicación es obligatorio.")
        if not pasillo or not pasillo.strip():
            raise ErrorDominio("El pasillo es obligatorio.")
        if not estante or not estante.strip():
            raise ErrorDominio("El estante es obligatorio.")
        if not nivel or not nivel.strip():
            raise ErrorDominio("El nivel es obligatorio.")
        return Ubicacion(codigo.strip(), pasillo.strip(), estante.strip(), nivel.strip())


class MercaderiaUbicadaFabrica:
    @staticmethod
    def crear(sku: str, ubicacion_codigo: str, cantidad: int) -> MercaderiaUbicada:
        if not sku or not sku.strip():
            raise ErrorDominio("El SKU es obligatorio.")
        if not ubicacion_codigo or not ubicacion_codigo.strip():
            raise ErrorDominio("El código de ubicación es obligatorio.")
        if cantidad <= 0:
            raise ErrorDominio("La cantidad debe ser mayor a cero.")
        return MercaderiaUbicada(
            id=f"UBI-{uuid.uuid4().hex[:8].upper()}",
            sku=sku.strip(),
            ubicacion_codigo=ubicacion_codigo.strip(),
            cantidad=cantidad,
            fecha_ubicacion=datetime.now(timezone.utc).isoformat(),
        )


class IAlmacenRepositorio(ABC):
    @abstractmethod
    def adicionar_ubicacion(self, ubicacion: Ubicacion) -> None: ...
    @abstractmethod
    def buscar_ubicacion(self, codigo: str) -> Ubicacion | None: ...
    @abstractmethod
    def listar_ubicaciones(self) -> list[Ubicacion]: ...
    @abstractmethod
    def ubicar_mercaderia(self, mercaderia: MercaderiaUbicada) -> None: ...
    @abstractmethod
    def buscar_por_sku(self, sku: str) -> list[MercaderiaUbicada]: ...
    @abstractmethod
    def actualizar_inventario_ubicacion(self, sku: str, ubicacion_codigo: str, cantidad: int) -> None: ...
