import os
import logging
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.model import user, login, security, token, product, product_publish, user_category, payment

# Load environment variables
load_dotenv()

# Use in-memory SQLite if TESTING is True, else use MySQL
TESTING = os.getenv("TESTING", "False").lower() == "true"

if TESTING:
    # SQLite for tests / CI
    DATABASE_URL = "sqlite:///:memory:"
    logging.info("** Using in-memory SQLite database for testing **")
else:
    # MySQL for local/dev
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("DB_NAME", "testdb")

    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Logging setup
logging.basicConfig(level=logging.INFO)

def check_db_connection():
    try:
        with engine.connect() as conn:
            logging.info("** Database Connected Successfully **")
    except SQLAlchemyError as e:
        logging.error("** Database Connection Failed **")
        logging.error(str(e))
        raise e  # Fail immediately if DB cannot connect

def create_db_and_tables():
    logging.info("** Creating tables **")
    SQLModel.metadata.create_all(engine)
    logging.info("** Tables created **")

def show_tables():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result]
            logging.info(f"** Existing tables: {tables} **")
    except SQLAlchemyError:
        logging.warning("SHOW TABLES not supported (SQLite). Skipping.")

def get_session():
    with Session(engine) as session:
        yield session

# Only run these for local development, not during testing
if not TESTING:
    check_db_connection()
    create_db_and_tables()
    show_tables()