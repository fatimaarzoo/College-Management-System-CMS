from sqlalchemy.orm  import sessionmaker,declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine= create_engine(DATABASE_URL,echo=True)
SessionLocal= sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base= declarative_base()

from database.models import *

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)

# asyncio.run(init_models())
Base.metadata.create_all(bind=engine,checkfirst=True)


def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()