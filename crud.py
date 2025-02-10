from sqlalchemy.future import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from models import Usuario, Ingrediente, Receta
from schemas import UsuarioCreate, RecetaCreate, IngredienteBase

async def reset_database(db: AsyncSession):
    await db.execute(text("DELETE FROM ingredientes"))
    await db.execute(text("DELETE FROM recetas"))
    await db.execute(text("DELETE FROM usuarios"))
    await db.commit()

async def get_usuarios(db: AsyncSession):
    result = await db.execute(select(Usuario))
    return result.scalars().all()

async def get_usuario(db: AsyncSession, usuario_id: int):
    result = await db.execute(select(Usuario).filter(Usuario.id == usuario_id))
    return result.scalar_one_or_none()

async def create_usuario(db: AsyncSession, usuario: UsuarioCreate):
    nuevo_usuario = Usuario(nombre=usuario.nombre, contraseña=usuario.contraseña)
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario

async def delete_usuario(db: AsyncSession, usuario_id: int):
    usuario = await get_usuario(db, usuario_id)
    if usuario:
        await db.delete(usuario)
        await db.commit()
    return usuario

async def get_recetas(db: AsyncSession):
    result = await db.execute(select(Receta))
    recetas = result.scalars().all()

    for receta in recetas:
        await db.refresh(receta, ["ingredientes", "usuario"])

    return recetas

async def create_receta(db: AsyncSession, receta_data: RecetaCreate):
    query = select(Receta).filter(Receta.nombre == receta_data.nombre)
    result = await db.execute(query)
    receta_existente = result.scalars().first()

    if receta_existente:
        # Verificar si los ingredientes son los mismos
        await db.refresh(receta_existente, ["ingredientes"])
        ingredientes_existentes = {ing.nombre for ing in receta_existente.ingredientes}
        ingredientes_nuevos = {ing.nombre for ing in receta_data.ingredientes}

        if ingredientes_existentes == ingredientes_nuevos:
            return {"mensaje": "La receta ya existe con los mismos ingredientes"}
    nueva_receta = Receta(
        nombre=receta_data.nombre,
        tiempo_preparacion=receta_data.tiempo_preparacion,
        usuario_id=receta_data.usuario_id
    )
    db.add(nueva_receta)
    await db.commit()
    await db.refresh(nueva_receta)
    ingredientes = [
        Ingrediente(nombre=ing.nombre, receta_id=nueva_receta.id) 
        for ing in receta_data.ingredientes
    ]
    db.add_all(ingredientes)
    await db.commit()
    await db.refresh(nueva_receta, ["ingredientes", "usuario"])
        
    return nueva_receta

async def delete_receta(db: AsyncSession, receta_id: int):
    result = await db.execute(select(Receta).filter(Receta.id == receta_id))
    receta = result.scalar_one_or_none()
    if receta:
        await db.delete(receta)
        await db.commit()
    return receta

async def get_receta_por_nombre(db: AsyncSession, nombre: str):
    try:
        result = await db.execute(select(Receta).filter(Receta.nombre == nombre))
        receta = result.scalars().first()  # Obtiene el primer resultado o None si no se encuentra
        if receta:
            return receta
        else:
            return None

    except Exception as e:
        print(f"Error al obtener la receta: {e}")
        return None

async def guardar_recetas_iniciales(db: AsyncSession, recetas_data: RecetaCreate):
    for receta_data in recetas_data:
        # Crear la receta asociada al usuario con id=1
        nueva_receta = Receta(
            nombre=receta_data["nombre"],
            tiempo_preparacion=receta_data["tiempo"],
            usuario_id=1,  # Asumimos que el usuario con id=1 existe
        )
        db.add(nueva_receta)
        await db.commit()
        await db.refresh(nueva_receta)

        # Insertar los ingredientes de la receta
        ingredientes = [
            Ingrediente(nombre=ingrediente, receta_id=nueva_receta.id)
            for ingrediente in receta_data["ingredientes"]
        ]
        db.add_all(ingredientes)
        await db.commit()

    return nueva_receta