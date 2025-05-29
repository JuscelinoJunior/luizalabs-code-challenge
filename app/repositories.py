from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.utils import get_password_hash
from app.models import User, Wishlist
from app import schemas


def read_users(database_session: Session, skip: int = 0, limit: int = 100):
    return database_session.query(User).offset(skip).limit(limit).all()


def read_user_by_email(database_session: Session, email: EmailStr):
    return database_session.query(User).filter(User.email == email).first()


def read_user(database_session: Session, user_id: int):
    return database_session.query(User).filter(User.id == user_id).first()


def create_user(database_session: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role if hasattr(user, "role") and user.role else "customer"
    )
    database_session.add(db_user)
    database_session.commit()
    database_session.refresh(db_user)
    return db_user


def update_user(database_session: Session, user_id: int, user_data: schemas.UserUpdate):
    user_model = read_user(database_session, user_id)
    if not user_model:
        return None

    if user_data.name is not None:
        user_model.name = user_data.name
    if user_data.email is not None:
        user_model.email = user_data.email
    if hasattr(user_data, "role") and user_data.role is not None:
        user_model.role = user_data.role

    database_session.commit()
    database_session.refresh(user_model)
    return user_model


def delete_user(database_session: Session, user_id: int):
    user_model = read_user(database_session, user_id)
    if user_model:
        database_session.query(Wishlist).filter_by(user_id=user_id).delete()

        database_session.delete(user_model)
        database_session.commit()


def is_product_in_wishlist(database_session: Session, user_id: int, product_id: str) -> bool:
    return database_session.query(Wishlist).filter_by(user_id=user_id, product_id=product_id).first() is not None


def add_product_to_wishlist(database_session: Session, user_id: int, product_id: str):
    wishlist_entry = Wishlist(user_id=user_id, product_id=product_id)
    database_session.add(wishlist_entry)
    database_session.commit()
    database_session.refresh(wishlist_entry)
    return wishlist_entry


def get_wishlist(database_session: Session, user_id: int):
    return database_session.query(Wishlist).filter_by(user_id=user_id).all()


def remove_product_from_wishlist(database_session: Session, user_id: int, product_id: str):
    wishlist_entry = database_session.query(Wishlist).filter_by(user_id=user_id, product_id=product_id).first()
    if wishlist_entry:
        database_session.delete(wishlist_entry)
        database_session.commit()
