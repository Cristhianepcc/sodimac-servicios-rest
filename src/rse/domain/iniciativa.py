"""Dominio del proceso `rse` — Iniciativa RSE (referencia).

Reutiliza el BDM del Laboratorio 5 (proceso BPM "Gestión de RSE y Sostenibilidad").
Entidad IniciativaRSE + fábrica + repo.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from src.shared.errores import ErrorDominio


class TipoIniciativa(str, Enum):
    RECICLAJE = "RECICLAJE"
    EFICIENCIA_ENERGETICA = "EFICIENCIA_ENERGETICA"
    VOLUNTARIADO = "VOLUNTARIADO"
    PROVEEDORES_SOSTENIBLES = "PROVEEDORES_SOSTENIBLES"


class EstadoIniciativa(str, Enum):
    FORMULADA = "FORMULADA"
    EN_EVALUACION = "EN_EVALUACION"
    APROBADA = "APROBADA"
    ARCHIVADA = "ARCHIVADA"


@dataclass
class IniciativaRSE:
    codigo: str
    nombre: str
    tipo: TipoIniciativa
    descripcion: str = ""
    requiere_presupuesto: bool = False
    presupuesto_solicitado: float = 0.0
    estado: EstadoIniciativa = EstadoIniciativa.FORMULADA


class IniciativaFabrica:
    @staticmethod
    def crear(
        nombre: str,
        tipo: str,
        descripcion: str = "",
        requiere_presupuesto: bool = False,
        presupuesto_solicitado: float = 0.0,
    ) -> IniciativaRSE:
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre de la iniciativa es obligatorio.")
        if presupuesto_solicitado < 0:
            raise ErrorDominio("El presupuesto no puede ser negativo.")
        if requiere_presupuesto and presupuesto_solicitado <= 0:
            raise ErrorDominio("Si requiere presupuesto, debe ser mayor que 0.")
        try:
            tipo_enum = TipoIniciativa(tipo)
        except ValueError:
            validos = ", ".join(t.value for t in TipoIniciativa)
            raise ErrorDominio(f"Tipo inválido '{tipo}'. Permitidos: {validos}.")
        return IniciativaRSE(
            codigo=f"RSE-{uuid.uuid4().hex[:8].upper()}",
            nombre=nombre.strip(),
            tipo=tipo_enum,
            descripcion=descripcion,
            requiere_presupuesto=requiere_presupuesto,
            presupuesto_solicitado=presupuesto_solicitado,
            estado=EstadoIniciativa.FORMULADA,
        )


class IIniciativaRepositorio(ABC):
    @abstractmethod
    def adicionar(self, iniciativa: IniciativaRSE) -> None: ...

    @abstractmethod
    def buscar(self, codigo: str) -> IniciativaRSE | None: ...

    @abstractmethod
    def listar(self) -> list[IniciativaRSE]: ...
