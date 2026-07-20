"""Servicio de aplicación de Iniciativas RSE (casos de uso)."""
from __future__ import annotations

from src.rse.domain.iniciativa import IniciativaFabrica, IniciativaRSE
from src.rse.infrastructure import get_iniciativa_repositorio
from src.shared.errores import NoEncontrado


class IniciativaServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_iniciativa_repositorio()

    def crear(
        self,
        nombre: str,
        tipo: str,
        descripcion: str = "",
        requiere_presupuesto: bool = False,
        presupuesto_solicitado: float = 0.0,
    ) -> IniciativaRSE:
        iniciativa = IniciativaFabrica.crear(
            nombre, tipo, descripcion, requiere_presupuesto, presupuesto_solicitado
        )
        self._repo.adicionar(iniciativa)
        return iniciativa

    def obtener(self, codigo: str) -> IniciativaRSE:
        iniciativa = self._repo.buscar(codigo)
        if iniciativa is None:
            raise NoEncontrado(f"No existe la iniciativa '{codigo}'.")
        return iniciativa

    def listar(self) -> list[IniciativaRSE]:
        return self._repo.listar()
