from sqlalchemy.orm import Session
import models


def read_clients(database_session: Session, skip: int = 0, limit: int = 100):
    return database_session.query(models.Client).offset(skip).limit(limit).all()
