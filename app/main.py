from fastapi import FastAPI, Depends
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

@app.get("/clients", response_model=list[schemas.ClientResponse])
def read_clients(skip: int = 0, limit: int = 100, database_session: Session = Depends(get_database_session)):
    return repositories.read_clients(database_session, skip, limit)

