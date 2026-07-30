import pytest

from src import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def auth_client(client, app):
    """Cliente autenticado como ALMACENERO (necesario para APIs protegidas)."""
    with app.app_context():
        from src.web.auth_store import sembrar_usuarios_prueba
        sembrar_usuarios_prueba()
    with client.session_transaction() as sess:
        sess["usuario"] = {"id": 999, "nombre_usuario": "almacenero1", "rol": "ALMACENERO"}
    return client


def test_orden_compra_autorizar_y_enviar(auth_client):
    resp = auth_client.post(
        "/api/ordenes-compra",
        json={
            "proveedorId": "PROV001",
            "lineas": [
                {"sku": "SKU001", "cantidad": 2, "precioUnitario": 10},
                {"sku": "SKU002", "cantidad": 3, "precioUnitario": 20},
            ],
        },
    )
    assert resp.status_code == 201
    orden_id = resp.get_json()["id"]

    auth_resp = auth_client.put(f"/api/ordenes-compra/{orden_id}/autorizar")
    assert auth_resp.status_code == 200
    assert auth_resp.get_json()["estado"] == "AUTORIZADA"

    send_resp = auth_client.post(f"/api/ordenes-compra/{orden_id}/enviar")
    assert send_resp.status_code == 200
    assert send_resp.get_json()["estado"] == "ENVIADA"


def test_almacen_registrar_ubicacion_y_consultar(auth_client):
    resp = auth_client.post(
        "/api/almacenes/ubicaciones",
        json={"codigo": "A-01", "zona": "NORTE", "sku": "SKU001", "cantidad": 10},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["codigo"] == "A-01"
    assert data["sku"] == "SKU001"

    consulta = auth_client.get("/api/almacenes/ubicaciones/SKU001")
    assert consulta.status_code == 200
    assert consulta.get_json()["codigo"] == "A-01"

    inventario = auth_client.put(
        "/api/almacenes/inventario",
        json={"sku": "SKU001", "stock": 25},
    )
    assert inventario.status_code == 200
    assert inventario.get_json()["stock"] == 25


def test_api_sin_auth_retorna_401(client):
    """Verifica que las APIs protegidas rechacen peticiones sin sesión."""
    resp = client.get("/api/ordenes-compra")
    assert resp.status_code == 401
    assert "error" in resp.get_json()

    resp = client.post("/api/almacenes/ubicaciones", json={})
    assert resp.status_code == 401

    resp = client.get("/api/proveedores")
    assert resp.status_code == 401


def test_web_sin_auth_redirige_a_login(client):
    """Verifica que las rutas web sin sesión redirijan a login."""
    resp = client.get("/reabastecimiento/ordenes-compra")
    assert resp.status_code == 302

    resp = client.get("/reabastecimiento/almacen")
    assert resp.status_code == 302


def test_api_con_rol_incorrecto_retorna_403(client):
    """Usuario con rol CLIENTE no puede acceder a APIs de ALMACENERO."""
    with client.session_transaction() as sess:
        sess["usuario"] = {"id": 1, "nombre_usuario": "cliente1", "rol": "CLIENTE"}
    resp = client.get("/api/ordenes-compra")
    assert resp.status_code == 403
    assert "error" in resp.get_json()
