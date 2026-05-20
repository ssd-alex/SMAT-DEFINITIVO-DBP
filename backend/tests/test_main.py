from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- TOKEN ---
def get_token():
    response = client.post("/token")
    return response.json()["access_token"]

# --- ESTACIONES ---
def test_crear_estacion():
    token = get_token()
    response = client.post(
        "/estaciones/",
        json={"nombre": "Estación Rímac", "ubicacion": "Chosica"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "Estación Rímac"

def test_listar_estaciones():
    response = client.get("/estaciones/")
    assert response.status_code == 200

# --- LECTURAS ---
def test_registrar_lectura():
    token = get_token()
    client.post(
        "/estaciones/",
        json={"nombre": "Estación Test", "ubicacion": "Lima"},
        headers={"Authorization": f"Bearer {token}"}
    )
    estaciones = client.get("/estaciones/").json()
    id_estacion = estaciones[0]["id"]
    response = client.post(
        "/lecturas/",
        json={"estacion_id": id_estacion, "valor": 12.5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

# --- RIESGO ---
def test_riesgo_peligro():
    token = get_token()
    estaciones = client.get("/estaciones/").json()
    id_estacion = estaciones[0]["id"]
    client.post(
        "/lecturas/",
        json={"estacion_id": id_estacion, "valor": 25.5},
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get(f"/estaciones/{id_estacion}/riesgo")
    assert response.status_code == 200
    assert response.json()["nivel"] == "PELIGRO"

def test_estacion_no_encontrada():
    response = client.get("/estaciones/999/riesgo")
    assert response.status_code == 404

# --- HISTORIAL ---
def test_historial_y_promedio():
    token = get_token()
    estaciones = client.get("/estaciones/").json()
    id_estacion = estaciones[0]["id"]
    client.post("/lecturas/", json={"estacion_id": id_estacion, "valor": 10.0}, headers={"Authorization": f"Bearer {token}"})
    client.post("/lecturas/", json={"estacion_id": id_estacion, "valor": 20.0}, headers={"Authorization": f"Bearer {token}"})
    client.post("/lecturas/", json={"estacion_id": id_estacion, "valor": 30.0}, headers={"Authorization": f"Bearer {token}"})
    response = client.get(f"/estaciones/{id_estacion}/historial")
    assert response.status_code == 200
    assert response.json()["conteo"] >= 3
    assert response.json()["promedio"] > 0