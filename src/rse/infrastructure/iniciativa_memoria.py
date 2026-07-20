"""Repositorio en memoria (Fake) de Iniciativas RSE."""
from __future__ import annotations

from src.rse.domain.iniciativa import IIniciativaRepositorio, IniciativaRSE


class IniciativaRepositorioMemoria(IIniciativaRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, IniciativaRSE] = {}

    def adicionar(self, iniciativa: IniciativaRSE) -> None:
        self._datos[iniciativa.codigo] = iniciativa

    def buscar(self, codigo: str) -> IniciativaRSE | None:
        return self._datos.get(codigo)

    def listar(self) -> list[IniciativaRSE]:
        return list(self._datos.values())
