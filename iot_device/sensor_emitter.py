import requests
import time
import random

API_URL = "http://localhost:8000/lecturas/"
ESTACION_ID = 1
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbl9zbWF0IiwiZXhwIjoxNzc5ODk4MzQ0fQ.Omb3_08mzYjZr6aq6f8JhBH5XEekoykFua77Aw71WYo"

def leer_sensor_emulado():
    return round(random.uniform(10.5, 85.0), 2)

def enviar_telemetria():
    while True:
        valor = leer_sensor_emulado()

        if valor > 70.0:
            print("[ALERTA] Umbral de inundación superado")
            espera = 2
        else:
            espera = 10

        payload = {
            "valor": valor,
            "estacion_id": ESTACION_ID
        }

        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code in (200, 201):
                print(f"[OK] Lectura enviada: {valor} cm")
            else:
                print(f"[ERROR] Código: {response.status_code}")
        except Exception as e:
            print(f"[CRÍTICO] No hay conexión con el servidor: {e}")

        time.sleep(espera)

if __name__ == "__main__":
    enviar_telemetria()