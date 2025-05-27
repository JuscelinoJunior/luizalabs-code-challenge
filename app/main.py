from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas
import repositories
from database import SessionLocal

app = FastAPI()

def get_database_session():
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()


@app.get("/customers", response_model=list[schemas.CustomerResponse])
def read_customers(skip: int = 0, limit: int = 100, database_session: Session = Depends(get_database_session)):
    return repositories.read_customers(database_session, skip, limit)
