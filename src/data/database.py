from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings
from src.data.models import Base

# Create Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG, # Log SQL queries in debug mode
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initializes the database (creates tables if not exist)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session() -> AsyncSession:
    """Dependency for getting a DB session."""
    async with AsyncSessionLocal() as session:
        yield session
