from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import schemas
import repositories
from services import fetch_product_data
from database import SessionLocal
import httpx

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
    existing_customer = repositories.read_customer(database_session, customer_id)
    if not existing_customer:
        raise HTTPException(status_code=404, detail="Costumer not found")

    if customer.email:
        # Check if already exists a user with same email
        other = repositories.read_customer_by_email(database_session, customer.email)
        if other and other.id != customer_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    return repositories.update_customer(database_session, customer_id, customer)


@app.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, database_session: Session = Depends(get_database_session)):
    existing_customer = repositories.read_customer(database_session, customer_id)
    if not existing_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    repositories.delete_customer(database_session, customer_id)


@app.post("/customers/{customer_id}/wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    customer_id: int,
    product_id: str,
    test_products: bool = Query(False),
    database_session: Session = Depends(get_database_session)
):
    customer = repositories.read_customer(database_session, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if repositories.is_product_in_wishlist(database_session, customer_id, product_id):
        raise HTTPException(status_code=400, detail="Product already in wishlist to this costumer")

    product = fetch_product_data(product_id, test_products)
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")

    return repositories.add_product_to_wishlist(database_session, customer_id, product_id)


@app.get("/customers/{customer_id}/wishlist", response_model=list[schemas.WishlistProductResponse])
def get_wishlist(customer_id: int,
                 test_products: bool = Query(False),
                 db: Session = Depends(get_database_session)
):
    wishlist = repositories.get_wishlist(db, customer_id)
    return [
        product for item in wishlist
        if (product := fetch_product_data(item.product_id, test_products))
    ]


@app.delete("/customers/{customer_id}/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(customer_id: int, product_id: str, db: Session = Depends(get_database_session)):
    if not repositories.is_product_in_wishlist(db, customer_id, product_id):
        raise HTTPException(status_code=404, detail="Product not in wishlist")
    repositories.remove_product_from_wishlist(db, customer_id, product_id)
