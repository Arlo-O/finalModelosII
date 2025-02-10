from pydantic import BaseModel
from typing import List

class UsuarioBase(BaseModel):
    nombre: str
    
class UsuarioCreate(UsuarioBase):
    contraseña: str

class UsuarioDB(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class IngredienteBase(BaseModel):
    nombre: str

class IngredienteCreate(IngredienteBase):
    pass

class IngredienteDB(IngredienteBase):
    id: int
    receta_id: int

    class Config:
        from_attributes = True

class RecetaBase(BaseModel):
    nombre: str
    tiempo_preparacion: int
    usuario_id: int

class RecetaUpdate(BaseModel):
    nombre: str
    tiempo_preparacion: int
    ingredientes: list[str]

class RecetaCreate(RecetaBase):
    ingredientes: List[IngredienteCreate]

class RecetaCreateFront(BaseModel):
    nombre: str
    tiempo_preparacion: int
    ingredientes: List[IngredienteCreate]

class RecetaDB(RecetaBase):
    id: int
    usuario: UsuarioDB
    ingredientes: List[IngredienteDB]

    class Config:
        from_attributes = True