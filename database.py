from sqlalchemy.orm  import sessionmaker,declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine= create_engine(DATABASE_URL,echo=True)
SessionLocal= sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base= declarative_base()

from models import *

Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()