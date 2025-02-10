from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Crear motor de base de datos
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear sesión
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de la BD
async def get_db():
    async with SessionLocal() as session:
        yield session
