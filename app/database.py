"""

This file needed for get database connection 

"""
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated
from fastapi import Depends
from .config import SQLALCHEMY_DATABASE_URL

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    autocommit = False,
    autoflush= False,
    bind= async_engine,
    class_= AsyncSession,
    expire_on_commit= False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.aclose()

db_dependency = Annotated[AsyncSession, Depends(get_db)]
