from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://u403218763_bitdefiblock:4Rs+O6DHf!@srv1938.hstgr.io:3306/u403218763_bitdefiblock"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()