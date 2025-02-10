from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from database import get_db, engine, Base
from schemas import UsuarioCreate, UsuarioDB, RecetaCreate, RecetaDB, RecetaCreateFront, RecetaUpdate
from crud import (
    create_usuario, get_usuarios, delete_usuario, get_usuario,
    create_receta, get_recetas, delete_receta, guardar_recetas_iniciales,
    reset_database, get_receta_por_nombre
)
from consultas import filtrar_recetas_por_tipo, cargar_recetas_iniciales, filtrar_recetas_por_ingrediente
from models import Usuario, Receta, Ingrediente
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

session_store = {}
#Endpoints setup o admin
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as db:
        result = await db.execute(select(Usuario).filter(Usuario.id == 1))
        usuario = result.scalars().first()
        
        if not usuario:
            usuario = Usuario(id=1, nombre="Usuario Inicial", contraseña="contraUserInicial")
            db.add(usuario)
            await db.commit()
            await db.refresh(usuario)

        result = await db.execute(select(Receta).limit(1))
        receta_existente = result.scalars().first()

        if not receta_existente:
            recetas_iniciales = cargar_recetas_iniciales()
            await guardar_recetas_iniciales(db, recetas_iniciales)

@app.post("/reset-db/")
async def reset_db_endpoint(db: AsyncSession = Depends(get_db)):
    await reset_database(db)
    return {"message": "Base de datos reiniciada"}

@app.get("/check_session")
async def check_session(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token and session_token in session_store:
        return {"message": "Sesión activa", "session_token": session_token}
    else:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    
def get_session_token(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token or session_token not in session_store:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    return session_token

#Endpoint Home
@app.get("/")
async def root(request : Request):
    session_token = request.cookies.get("session_token")
    return templates.TemplateResponse("base.html", {"request": request, "session_token": session_token})

#Endpoints Registro Usuario
@app.get("/signup/", response_class = HTMLResponse)
async def signup_html(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup/", response_model=UsuarioDB)
async def create_usuario_endpoint(usuario: UsuarioCreate, response : Response,  db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).filter(Usuario.nombre == usuario.nombre))
    usuario_existente = result.scalars().first()

    if usuario_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    
    nuevo_usuario = await create_usuario(db, usuario)

    session_token = str(uuid4())
    session_store[session_token] = nuevo_usuario
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600, expires=3600)
    return nuevo_usuario

#Endpoints Inicio sesion
@app.get("/signin/", response_class = HTMLResponse)
async def signin_html(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.post("/login/")
async def login(response: Response, usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Usuario).filter(Usuario.nombre == usuario.nombre, Usuario.contraseña == usuario.contraseña))
    usuario_db = result.scalars().first()
    if usuario_db is None:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    session_token = str(uuid4())
    session_store[session_token] = usuario_db
    response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600, expires=3600)
    return usuario_db

#Endpoint Cerrar sesion
@app.get("/logout")
async def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token in session_store:
        del session_store[session_token]
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_token")
    return response

# Rutas para Usuarios
# @app.get("/usuarios/", response_model=list[UsuarioDB])
# async def get_usuarios_endpoint(db: AsyncSession = Depends(get_db)):
#     return await get_usuarios(db)

# @app.get("/usuarios/{usuario_id}", response_model=UsuarioDB)
# async def get_usuario_endpoint(usuario_id : int , db: AsyncSession = Depends(get_db)):
#     usuario = await get_usuario(db, usuario_id)
#     if usuario is None:
#         raise HTTPException(status_code=404, detail="Usuario no encontrado")
#     return usuario

# @app.delete("/usuarios/{usuario_id}")
# async def delete_usuario_endpoint(usuario_id: int, db: AsyncSession = Depends(get_db)):
    usuario = await delete_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado"}

# Rutas para Recetas
# Crear Recestas
@app.get("/crearReceta/", response_class = HTMLResponse)
async def crear_receta_endpoint_html(request: Request):
    session_token = request.cookies.get("session_token")
    return templates.TemplateResponse("crearRecetas.html",  {"request": request, "session_token": session_token})

@app.post("/crearReceta/", response_model=RecetaDB)
async def create_receta_endpoint(receta: RecetaCreateFront, request: Request, db: AsyncSession = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    if not session_store or session_token not in session_store:
        raise HTTPException(status_code=401, detail="No hay sesión activa")
    
    usuario = session_store[session_token]
    receta_db = RecetaCreate(
        nombre=receta.nombre,
        tiempo_preparacion=receta.tiempo_preparacion,
        ingredientes=receta.ingredientes,
        usuario_id=usuario.id
    )   
    return await create_receta(db, receta_db)

# Consultar recetas
@app.get("/recetas/", response_class= HTMLResponse)
async def recetas_endpoint_html(request: Request):
    session_token = request.cookies.get("session_token")
    return templates.TemplateResponse("consultarRecetas.html", {"request": request, "session_token": session_token})

@app.get("/recetas/saludables", response_model=list[str])
async def obtener_recetas_saludables_endpoint(db: AsyncSession = Depends(get_db)):
    try:
        recetas_db = await get_recetas(db)
        recetas_filtradas = filtrar_recetas_por_tipo(recetas_db, "saludable")
        return [receta.nombre for receta in recetas_db if receta.nombre in recetas_filtradas]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al buscar recetas saludables")

@app.get("/listarecetas/", response_model=list[RecetaDB])
async def get_recetas_endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Receta)
                              .options(selectinload(Receta.ingredientes), selectinload(Receta.usuario)))
    recetas = result.scalars().all()
    return recetas

# Endpoint para buscar recetas por ingrediente
@app.get("/recetas/por_ingrediente/", response_model=list[str])
async def get_recetas_por_ingrediente_endpoint(ingrediente: str, db: AsyncSession = Depends(get_db)):
    try:
        recetas_db = await get_recetas(db)
        recetas_filtradas = filtrar_recetas_por_ingrediente(recetas_db, ingrediente)
        return [receta.nombre for receta in recetas_db if receta.nombre in recetas_filtradas]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al buscar recetas por ingrediente")

# Endpoint para obtener recetas sencillas o elaboradas
@app.get("/recetas/{tipo}/", response_model=list[str])
async def get_recetas_tipo_endpoint(tipo: str, db: AsyncSession = Depends(get_db)):
    if tipo not in ["sencilla", "elaborada"]:
        raise HTTPException(status_code=400, detail="Tipo de receta no válido")
    try:
        recetas_db = await get_recetas(db)
        recetas_filtradas = filtrar_recetas_por_tipo(recetas_db, tipo)
        return [receta.nombre for receta in recetas_db if receta.nombre in recetas_filtradas]  # Devolver solo nombres
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al obtener recetas sencillas o elaboradas")

# Endpoint para obtener los detalles de una receta
@app.get("/recetas/detalle/{nombre}", response_model=RecetaDB)
async def get_receta_detalle(nombre: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Receta)
                              .options(selectinload(Receta.ingredientes), selectinload(Receta.usuario))
                              .filter(Receta.nombre == nombre))
    receta = result.scalars().first()
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return receta

@app.get("/editar-eliminar-receta/{id}")
async def editar_eliminar_receta_html(id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Receta)
                              .options(selectinload(Receta.ingredientes), selectinload(Receta.usuario))
                              .filter(Receta.id == id))
    receta = result.scalars().first()
    
    # Convertir los ingredientes a una lista si es necesario
    ingredientes_lista = receta.ingredientes if isinstance(receta.ingredientes, list) else [str(ingrediente) for ingrediente in receta.ingredientes]

    return templates.TemplateResponse("editar_eliminar_receta.html", {"request": request, "receta": receta, "ingredientes_lista": ingredientes_lista})

@app.post("/editar-eliminar-receta/{receta_id}")
async def editar_receta_endpoint(
    receta_id: int,
    receta_data: RecetaUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Obtener la receta
    result = await db.execute(select(Receta).filter(Receta.id == receta_id))
    receta = result.scalars().first()

    if receta is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # Actualizar los valores básicos
    receta.nombre = receta_data.nombre
    receta.tiempo_preparacion = receta_data.tiempo_preparacion

    # Eliminar los ingredientes existentes
    await db.execute(delete(Ingrediente).where(Ingrediente.receta_id == receta_id))

    # Agregar los nuevos ingredientes
    nuevos_ingredientes = [
        Ingrediente(nombre=nombre, receta_id=receta.id)
        for nombre in receta_data.ingredientes
    ]
    db.add_all(nuevos_ingredientes)

    # Guardar cambios
    await db.commit()

    session_token = request.cookies.get("session_token")
    return templates.TemplateResponse(
        "consultarRecetas.html",
        {"request": request, "session_token": session_token}
    )

@app.post("/eliminar-receta/{receta_id}")
async def eliminar_receta_endpoint(receta_id: str, db: AsyncSession = Depends(get_db)):
    receta = await db.execute(select(Receta).filter(Receta.id == receta_id))
    receta = receta.scalars().first()
    if receta is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    await db.delete(receta)
    await db.commit()
    
    return RedirectResponse(url="/recetas/", status_code=303)  # Redirige a la lista de recetas después de eliminar
