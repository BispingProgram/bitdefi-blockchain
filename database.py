import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"ssl": {"ssl_mode": "REQUIRED"}}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()