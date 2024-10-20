from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.base import Base

from app.config import setting

if setting["database"] == "mysql":
    async_connection_string = f"mysql+aiomysql://{setting["mysql"]["user"]}:{setting["mysql"]["password"]}@{setting["mysql"]["host"]}/{setting["mysql"]["db"]}"
else:
    async_connection_string = f"sqlite+aiosqlite:///tgbot.db"

async_engine = create_async_engine(async_connection_string)
ASession = async_sessionmaker(bind=async_engine)


async def create_all():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
