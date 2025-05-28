from pydantic import EmailStr
from sqlalchemy.orm import Session
import models
import schemas


def read_customers(database_session: Session, skip: int = 0, limit: int = 100):
    return database_session.query(models.Customer).offset(skip).limit(limit).all()


def read_customer_by_email(database_session: Session, email: EmailStr):
    return database_session.query(models.Customer).filter(models.Customer.email == email).first()


def read_customer(database_session: Session, customer_id: int):
    return database_session.query(models.Customer).filter(models.Customer.id == customer_id).first()


def create_customer(database_session: Session, customer: schemas.CustomerCreate):
    customer_model = models.Customer(name=customer.name, email=customer.email)
    database_session.add(customer_model)
    database_session.commit()
    database_session.refresh(customer_model)
    return customer_model


def update_customer(database_session: Session, customer_id: int, customer_data: schemas.CustomerUpdate):
    customer_model = read_customer(database_session, customer_id)
    if customer_data.name is not None:
        customer_model.name = customer_data.name
    if customer_data.email is not None:
        customer_model.email = customer_data.email

    database_session.commit()
    database_session.refresh(customer_model)
    return customer_model


def delete_customer(database_session: Session, customer_id: int):
    customer_model = read_customer(database_session, customer_id)
    database_session.delete(customer_model)
    database_session.commit()


def is_product_in_wishlist(database_session: Session, customer_id: int, product_id: str) -> bool:
    return database_session.query(models.Wishlist).filter_by(customer_id=customer_id, product_id=product_id).first() is not None


def add_product_to_wishlist(database_session: Session, customer_id: int, product_id: str):
    retrieved_wishlist_register = models.Wishlist(customer_id=customer_id, product_id=product_id)
    database_session.add(retrieved_wishlist_register)
    database_session.commit()
    database_session.refresh(retrieved_wishlist_register)
    return retrieved_wishlist_register


def get_wishlist(database_session: Session, customer_id: int):
    return database_session.query(models.Wishlist).filter_by(customer_id=customer_id).all()


def remove_product_from_wishlist(database_session: Session, customer_id: int, product_id: str):
    retrieved_wishlist_register = database_session.query(models.Wishlist).filter_by(customer_id=customer_id, product_id=product_id).first()
    if retrieved_wishlist_register:
        database_session.delete(retrieved_wishlist_register)
        database_session.commit()
