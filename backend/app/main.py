from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud
from app.database import engine, get_db
from app.auth import crear_token_acceso, obtener_identidad_actual

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
API robusta para la gestión y monitoreo de desastres naturales.
Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.

**Entidades principales:**
* **Estaciones:** Puntos de monitoreo físico.
* **Lecturas:** Datos capturados por sensores.
* **Riesgos:** Análisis de criticidad basado en umbrales.
""",
    version="1.0.0",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEGURIDAD ---

@app.post("/token", tags=["Seguridad"])
async def login_para_obtener_token():
    return {
        "access_token": crear_token_acceso({"sub": "admin_smat"}),
        "token_type": "bearer"
    }

# --- ESTACIONES ---

@app.post(
    "/estaciones/",
    status_code=201,
    tags=["Gestión de Infraestructura"],
    summary="Registrar una nueva estación de monitoreo",
    description="Inserta una estación física en la base de datos."
)
def crear_estacion(
    estacion: schemas.EstacionCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual)
):
    return crud.crear_estacion(db=db, estacion=estacion)

@app.get(
    "/estaciones/",
    response_model=List[schemas.EstacionDB],
    tags=["Gestión de Infraestructura"],
    summary="Listar todas las estaciones"
)
def listar_estaciones(db: Session = Depends(get_db)):
    return crud.get_estaciones(db)

@app.put(
    "/estaciones/{id}",
    tags=["Gestión de Infraestructura"],
    summary="Actualizar una estación existente"
)
def actualizar_estacion(
    id: int,
    datos: schemas.EstacionUpdate,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual)
):
    estacion = crud.actualizar_estacion(db=db, estacion_id=id, datos=datos)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@app.delete(
    "/estaciones/{id}",
    tags=["Gestión de Infraestructura"],
    summary="Eliminar una estación"
)
def eliminar_estacion(
    id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual)
):
    estacion = crud.eliminar_estacion(db=db, estacion_id=id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": "Estación eliminada correctamente"}

# --- LECTURAS ---

@app.post(
    "/lecturas/",
    status_code=201,
    tags=["Telemetría de Sensores"],
    summary="Recibir datos de telemetría",
    description="Recibe el valor capturado por un sensor y lo vincula a una estación existente."
)
def registrar_lectura(
    lectura: schemas.LecturaCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_identidad_actual)
):
    estacion = crud.get_estacion(db, lectura.estacion_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Error de Integridad: La estación no existe en la base de datos.")
    return crud.crear_lectura(db=db, lectura=lectura)

# --- ANÁLISIS ---

@app.get(
    "/estaciones/{id}/riesgo",
    tags=["Análisis de Riesgo"],
    summary="Evaluar nivel de peligro actual",
    description="Analiza la última lectura recibida y determina si el estado es NORMAL, ALERTA o PELIGRO."
)
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    estacion = crud.get_estacion(db, id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    lecturas = crud.get_lecturas_por_estacion(db, id)
    if not lecturas:
        return {"id": id, "nivel": "SIN DATOS", "valor": 0}
    ultima = lecturas[-1].valor
    if ultima > 20.0:
        nivel = "PELIGRO"
    elif ultima > 10.0:
        nivel = "ALERTA"
    else:
        nivel = "NORMAL"
    return {"id": id, "valor": ultima, "nivel": nivel}

@app.get(
    "/estaciones/{id}/historial",
    tags=["Reportes Históricos"],
    summary="Obtener historial y promedio de lecturas",
    description="Retorna la lista completa de lecturas, el conteo y el promedio de valores.",
    responses={404: {"description": "Estación no encontrada"}}
)
def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion = crud.get_estacion(db, id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    lecturas = crud.get_lecturas_por_estacion(db, id)
    valores = [l.valor for l in lecturas]
    promedio = round(sum(valores) / len(valores), 2) if len(valores) > 0 else 0.0
    return {
        "estacion_id": id,
        "lecturas": valores,
        "conteo": len(valores),
        "promedio": promedio
    }

@app.get(
    "/estaciones/stats",
    tags=["Auditoría"],
    summary="Dashboard ejecutivo del sistema"
)
def obtener_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)

@app.get(
    "/lecturas/",
    response_model=List[schemas.LecturaDB],
    tags=["Telemetría de Sensores"],
    summary="Listar todas las lecturas"
)
def listar_lecturas(db: Session = Depends(get_db)):
    return crud.get_lecturas(db)