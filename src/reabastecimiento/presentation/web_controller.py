"""Rutas web del bounded context Reabastecimiento."""
from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("reabastecimiento_web", __name__, url_prefix="/reabastecimiento")


@bp.get("/proveedores")
def proveedores():
    return render_template("reabastecimiento/proveedores.html")


@bp.get("/ordenes-compra")
def ordenes_compra():
    return render_template("reabastecimiento/ordenes_compra.html")


@bp.get("/recepciones")
def recepciones():
    return render_template("reabastecimiento/recepciones.html")


@bp.get("/distribucion")
def distribucion():
    return render_template("reabastecimiento/distribucion.html")


@bp.get("/almacen")
def almacen():
    return render_template("reabastecimiento/almacen.html")


@bp.get("/auditorias")
def auditorias():
    return render_template("reabastecimiento/auditorias.html")
