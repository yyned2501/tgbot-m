from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.base import Base

from app.config import setting

async_connection_string = f"mysql+aiomysql://{setting["mysql"]["user"]}:{setting["mysql"]["password"]}@{setting["mysql"]["host"]}/{setting["mysql"]["db"]}"
async_engine = create_async_engine(async_connection_string)
ASession = async_sessionmaker(bind=async_engine)


async def create_all():
    from . import redpocket

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
