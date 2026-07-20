"""Repositorio en memoria (Fake) de Solicitudes de Servicio."""
from __future__ import annotations

from src.servicios_cliente.domain.solicitud import ISolicitudRepositorio, SolicitudServicio


class SolicitudRepositorioMemoria(ISolicitudRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, SolicitudServicio] = {}

    def adicionar(self, solicitud: SolicitudServicio) -> None:
        self._datos[solicitud.id] = solicitud

    def buscar(self, solicitud_id: str) -> SolicitudServicio | None:
        return self._datos.get(solicitud_id)

    def listar(self) -> list[SolicitudServicio]:
        return list(self._datos.values())
