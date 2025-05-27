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

@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def read_customers(customer_id: int, database_session: Session = Depends(get_database_session)):
    retrieved_customer = repositories.read_customer(database_session, customer_id)

    if not retrieved_customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    return repositories.read_customer(database_session, customer_id)


@app.post("/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, database_session: Session = Depends(get_database_session)):
    # Check if already exists a user with same email
    existing = repositories.read_customer_by_email(database_session, customer.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repositories.create_customer(database_session, customer)


@app.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, database_session: Session = Depends(get_database_session)):
    existing = repositories.read_customer(database_session, customer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Costumer not found")

    if customer.email:
        # Check if already exists a user with same email
        other = repositories.read_customer_by_email(database_session, customer.email)
        if other and other.id != customer_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    return repositories.update_customer(database_session, customer_id, customer)


@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, database_session: Session = Depends(get_database_session)):
    existing = repositories.read_customer(database_session, customer_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    repositories.delete_customer(database_session, customer_id)
