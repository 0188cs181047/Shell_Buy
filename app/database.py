import os
import logging
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.model import user, login, security, token, product, product_publish, user_category

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

logging.basicConfig(level=logging.INFO)

def check_db_connection():
    try:
        with engine.connect() as conn:
            logging.info("** Database Connected Successfully **")
    except SQLAlchemyError as e:
        logging.error("** Database Connection Failed **")
        logging.error(str(e))

def create_db_and_tables():
    logging.info("** Creating tables **")
    SQLModel.metadata.create_all(engine)
    logging.info("** Tables created **")

def show_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
        logging.info(f"** Existing tables: {tables} **")

def get_session():
    with Session(engine) as session:
        yield session

# Startup test
check_db_connection()
create_db_and_tables()
show_tables()