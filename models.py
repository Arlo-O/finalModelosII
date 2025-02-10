from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    contraseña = Column(String)

    recetas = relationship("Receta", back_populates="usuario")

class Receta(Base):
    __tablename__ = "recetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tiempo_preparacion = Column(Integer)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="recetas")
    ingredientes = relationship("Ingrediente", back_populates="receta")

class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    receta_id = Column(Integer, ForeignKey("recetas.id"))
    
    receta = relationship("Receta", back_populates="ingredientes")