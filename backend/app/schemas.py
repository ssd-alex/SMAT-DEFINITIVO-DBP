from pydantic import BaseModel
from typing import List, Optional

class LecturaBase(BaseModel):
    valor: float
    estacion_id: int

class LecturaCreate(LecturaBase):
    pass

class LecturaDB(LecturaBase):
    id: int

    class Config:
        from_attributes = True

class EstacionBase(BaseModel):
    nombre: str
    ubicacion: str

class EstacionCreate(EstacionBase):
    pass

class EstacionUpdate(EstacionBase):
    pass

class EstacionDB(EstacionBase):
    id: int
    lecturas: List[LecturaDB] = []

    class Config:
        from_attributes = True