"""

This file needed for get database connection 

"""
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import os


load_dotenv()
database_url = os.getenv("SQLALCHEMY_DATABASE_URL")

if database_url is None:
    raise ValueError("SQLALCHEMY_DATABASE_URL is not set in the environment variables")

async_engine = create_async_engine(database_url)

AsyncSessionLocal = async_sessionmaker(
    autocommit = False,
    autoflush= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False
)

Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.aclose()