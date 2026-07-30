import pytest

from src import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_orden_compra_autorizar_y_enviar(client):
    resp = client.post(
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

    auth_resp = client.put(f"/api/ordenes-compra/{orden_id}/autorizar")
    assert auth_resp.status_code == 200
    assert auth_resp.get_json()["estado"] == "AUTORIZADA"

    send_resp = client.post(f"/api/ordenes-compra/{orden_id}/enviar")
    assert send_resp.status_code == 200
    assert send_resp.get_json()["estado"] == "ENVIADA"


def test_almacen_registrar_ubicacion_y_consultar(client):
    resp = client.post(
        "/api/almacenes/ubicaciones",
        json={"codigo": "A-01", "zona": "NORTE", "sku": "SKU001", "cantidad": 10},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["codigo"] == "A-01"
    assert data["sku"] == "SKU001"

    consulta = client.get("/api/almacenes/ubicaciones/SKU001")
    assert consulta.status_code == 200
    assert consulta.get_json()["codigo"] == "A-01"

    inventario = client.put(
        "/api/almacenes/inventario",
        json={"sku": "SKU001", "stock": 25},
    )
    assert inventario.status_code == 200
    assert inventario.get_json()["stock"] == 25
