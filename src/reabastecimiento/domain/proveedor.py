"""Dominio del servicio de Proveedores (Reabastecimiento).

Entidad Proveedor + fábrica + interfaz de repositorio. Python puro.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from src.shared.errores import ErrorDominio


class EstadoProveedor(str, Enum):
    REGISTRADO = "REGISTRADO"
    EVALUADO = "EVALUADO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


@dataclass
class Proveedor:
    id: str
    nombre: str
    ruc: str
    puntaje: int = 0
    estado: EstadoProveedor = EstadoProveedor.REGISTRADO

    def evaluar(self, puntaje: int) -> None:
        if puntaje < 0 or puntaje > 100:
            raise ErrorDominio("El puntaje debe estar entre 0 y 100.")
        self.puntaje = puntaje
        self.estado = EstadoProveedor.EVALUADO

    def aprobar(self) -> None:
        if self.estado != EstadoProveedor.EVALUADO:
            raise ErrorDominio("Solo se puede aprobar un proveedor evaluado.")
        if self.puntaje < 70:
            raise ErrorDominio("El puntaje debe ser >= 70 para aprobar.")
        self.estado = EstadoProveedor.APROBADO

    def rechazar(self) -> None:
        if self.estado != EstadoProveedor.EVALUADO:
            raise ErrorDominio("Solo se puede rechazar un proveedor evaluado.")
        self.estado = EstadoProveedor.RECHAZADO


class ProveedorFabrica:
    @staticmethod
    def crear(nombre: str, ruc: str) -> Proveedor:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre del proveedor es obligatorio.")
        if not ruc or not ruc.strip():
            raise ErrorDominio("El RUC del proveedor es obligatorio.")
        id_prov = f"PRV-{uuid.uuid4().hex[:8].upper()}"
        return Proveedor(id=id_prov, nombre=nombre.strip(), ruc=ruc.strip())


class IProveedorRepositorio(ABC):
    @abstractmethod
    def adicionar(self, proveedor: Proveedor) -> None: ...

    @abstractmethod
    def buscar(self, proveedor_id: str) -> Proveedor | None: ...

    @abstractmethod
    def listar(self) -> list[Proveedor]: ...

    @abstractmethod
    def actualizar(self, proveedor: Proveedor) -> None: ...
