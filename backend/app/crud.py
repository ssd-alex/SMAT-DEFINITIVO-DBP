from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas

# --- ESTACIONES ---

def get_estacion(db: Session, estacion_id: int):
    return db.query(models.EstacionDB).filter(models.EstacionDB.id == estacion_id).first()

def get_estaciones(db: Session):
    return db.query(models.EstacionDB).all()

def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    nueva = models.EstacionDB(nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def actualizar_estacion(db: Session, estacion_id: int, datos: schemas.EstacionUpdate):
    estacion = get_estacion(db, estacion_id)
    if not estacion:
        return None
    estacion.nombre = datos.nombre
    estacion.ubicacion = datos.ubicacion
    db.commit()
    db.refresh(estacion)
    return estacion

def eliminar_estacion(db: Session, estacion_id: int):
    estacion = get_estacion(db, estacion_id)
    if not estacion:
        return None
    db.delete(estacion)
    db.commit()
    return estacion

# --- LECTURAS ---

def crear_lectura(db: Session, lectura: schemas.LecturaCreate):
    nueva = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def get_lecturas(db: Session):
    return db.query(models.LecturaDB).all()

def get_lecturas_por_estacion(db: Session, estacion_id: int):
    return db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == estacion_id).all()

# --- STATS ---

def get_stats(db: Session):
    total_estaciones = db.query(func.count(models.EstacionDB.id)).scalar()
    total_lecturas = db.query(func.count(models.LecturaDB.id)).scalar()
    lectura_max = db.query(models.LecturaDB).order_by(models.LecturaDB.valor.desc()).first()
    return {
        "total_estaciones": total_estaciones,
        "total_lecturas": total_lecturas,
        "lectura_maxima": lectura_max.valor if lectura_max else 0,
        "estacion_critica": lectura_max.estacion_id if lectura_max else None
    }

