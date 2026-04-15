# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "sqlite:///./meetings.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal = sessionmaker(bind=engine)

# Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()
# 🔥 Read DB URL from environment (IMPORTANT)
DATABASE_URL = os.getenv("DATABASE_URL")



# Create engine
engine = create_engine(DATABASE_URL)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base
Base = declarative_base()