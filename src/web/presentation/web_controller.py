"""Rutas web con autenticacion simple y dashboards por rol."""
from __future__ import annotations

from functools import wraps

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from src.web.auth_store import autenticar, crear_usuario, listar_reclamos_usuario, sembrar_usuarios_prueba, vincular_reclamo

bp = Blueprint("postventa_web", __name__)

ROLE_HOME = {
    "CLIENTE": "postventa_web.cliente_registrar",
    "POSTVENTA": "postventa_web.postventa_reclamos",
    "TECNICO": "postventa_web.tecnico_evaluaciones",
    "ALMACENERO": "reabastecimiento_web.proveedores",
}


def login_required(role: str | None = None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("postventa_web.login"))
            if role and session["usuario"]["rol"] != role:
                return redirect(url_for(ROLE_HOME.get(session["usuario"]["rol"], "postventa_web.login")))
            return view(*args, **kwargs)

        return wrapped

    return decorator


@bp.get("/")
def index():
    if "usuario" in session:
        return redirect(url_for(ROLE_HOME[session["usuario"]["rol"]]))
    return redirect(url_for("postventa_web.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    sembrar_usuarios_prueba()
    if request.method == "POST":
        usuario = autenticar(request.form.get("nombre_usuario", ""), request.form.get("password", ""))
        if usuario:
            session["usuario"] = usuario
            return redirect(url_for(ROLE_HOME[usuario["rol"]]))
        flash("Credenciales invalidas.", "danger")
    return render_template("auth/login.html")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        ok, mensaje = crear_usuario(
            request.form.get("nombre_usuario", ""),
            request.form.get("password", ""),
            request.form.get("rol", ""),
        )
        flash(mensaje, "success" if ok else "danger")
        if ok:
            return redirect(url_for("postventa_web.login"))
    return render_template("auth/registro.html")


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("postventa_web.login"))


@bp.get("/cliente/reclamos/nuevo")
@login_required("CLIENTE")
def cliente_registrar():
    return render_template("cliente/registrar_reclamo.html")


@bp.get("/cliente/reclamos")
@login_required("CLIENTE")
def cliente_reclamos():
    return render_template("cliente/mis_reclamos.html")


@bp.get("/postventa/reclamos")
@login_required("POSTVENTA")
def postventa_reclamos():
    return render_template("postventa/reclamos.html")


@bp.get("/tecnico/evaluaciones")
@login_required("TECNICO")
def tecnico_evaluaciones():
    return render_template("tecnico/evaluaciones.html")


@bp.get("/tecnico/soluciones")
@login_required("TECNICO")
def tecnico_soluciones():
    return render_template("tecnico/soluciones.html")


@bp.post("/web/reclamos-vinculados")
@login_required("CLIENTE")
def guardar_reclamo_cliente():
    data = request.get_json(silent=True) or {}
    vincular_reclamo(session["usuario"]["id"], data.get("reclamoId", ""))
    return jsonify({"ok": True}), 201


@bp.get("/web/mis-reclamos")
@login_required("CLIENTE")
def mis_reclamos_ids():
    return jsonify({"items": listar_reclamos_usuario(session["usuario"]["id"])})
