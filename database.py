from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:orjJGgFilIHdPTnJINrtkUbnAMvMhDsV@centerbeam.proxy.rlwy.net:51857/railway"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()