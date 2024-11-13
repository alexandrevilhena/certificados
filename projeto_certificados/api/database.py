from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

Base = declarative_base()

DATABASE_URL = "mysql+mysqlconnector://user:password@db:3306/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

MAX_RETRIES = 10
RETRY_INTERVAL = 5

for attempt in range(MAX_RETRIES):
    try:
        engine.connect()
        print("Database is ready!")
        break
    except OperationalError:
        print(f"Attempt {attempt + 1} of {MAX_RETRIES}: Database is not ready, retrying in {RETRY_INTERVAL} seconds...")
        time.sleep(RETRY_INTERVAL)
else:
    print("Failed to connect to the database after multiple attempts.")
    raise Exception("Database connection could not be established.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
