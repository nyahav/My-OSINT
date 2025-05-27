
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.db.models.user import User
from app.db.models.scan import Scan
from app.db.base import Base 


engine = create_async_engine(settings.DATABASE_URL, echo=False) 


AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession, 
    expire_on_commit=False 
)


async def get_db():
    """
    Provides an asynchronous database session for FastAPI dependencies.
    The session is automatically closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Creates all database tables defined by SQLAlchemy models.
    This function should be called on application startup.
    It uses the Base.metadata to discover and create tables.
    """
    print("Attempting to create database tables...")
    async with engine.begin() as conn:
        print("Tables registered in Base.metadata:", Base.metadata.tables.keys())
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables creation process completed.")