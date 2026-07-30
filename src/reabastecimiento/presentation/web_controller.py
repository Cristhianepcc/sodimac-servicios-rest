"""Rutas web del bounded context Reabastecimiento."""
from __future__ import annotations

from flask import Blueprint, render_template

from src.shared.auth import login_required

bp = Blueprint("reabastecimiento_web", __name__, url_prefix="/reabastecimiento")


@bp.get("/proveedores")
@login_required("ALMACENERO")
def proveedores():
    return render_template("reabastecimiento/proveedores.html")


@bp.get("/ordenes-compra")
@login_required("ALMACENERO")
def ordenes_compra():
    return render_template("reabastecimiento/ordenes_compra.html")


@bp.get("/recepciones")
@login_required("ALMACENERO")
def recepciones():
    return render_template("reabastecimiento/recepciones.html")


@bp.get("/distribucion")
@login_required("ALMACENERO")
def distribucion():
    return render_template("reabastecimiento/distribucion.html")


@bp.get("/almacen")
@login_required("ALMACENERO")
def almacen():
    return render_template("reabastecimiento/almacen.html")


@bp.get("/auditorias")
@login_required("ALMACENERO")
def auditorias():
    return render_template("reabastecimiento/auditorias.html")
