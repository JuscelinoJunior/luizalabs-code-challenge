from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas
from app import repositories
from app.authentication import create_access_token, authenticate_user, get_current_user
from app. services import fetch_product_data, get_database_session

app = FastAPI()

def allow_self_or_admin(user_id: int = Path(...), current_user: schemas.UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")

def allow_admin(current_user: schemas.UserResponse = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")

@app.get("/users", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, _: None = Depends(allow_admin), database_session: Session = Depends(get_database_session)):
    return repositories.read_users(database_session, skip, limit)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user_by_id(
        user_id: int,
        _: None = Depends(allow_self_or_admin),
        database_session: Session = Depends(get_database_session)
):
    user = repositories.read_user(database_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
        user_id: int,
        user_data: schemas.UserUpdate,
        _: None = Depends(allow_self_or_admin),
        database_session: Session = Depends(get_database_session)
):
    user = repositories.read_user(database_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email:
        other = repositories.read_user_by_email(database_session, user_data.email)
        if other and other.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    return repositories.update_user(database_session, user_id, user_data)


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, _: None = Depends(allow_self_or_admin), database_session: Session = Depends(get_database_session)):
    user = repositories.read_user(database_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    repositories.delete_user(database_session, user_id)


@app.post("/users/{user_id}/wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
        user_id: int,
        product_id: str,
        test_products: bool = Query(False),
        _: None = Depends(allow_self_or_admin),
        database_session: Session = Depends(get_database_session)
):
    user = repositories.read_user(database_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can have wishlists")

    if repositories.is_product_in_wishlist(database_session, user_id, product_id):
        raise HTTPException(status_code=400, detail="Product already in wishlist")

    wishlist = repositories.get_wishlist(database_session, user_id)
    if len(wishlist) >= 5:
        raise HTTPException(status_code=400, detail="Wishlist limit of 5 products reached")

    product = fetch_product_data(product_id, test_products)
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")

    return repositories.add_product_to_wishlist(database_session, user_id, product_id)


@app.get("/users/{user_id}/wishlist", response_model=list[schemas.WishlistProductResponse])
def get_wishlist(user_id: int, test_products: bool = Query(False), _: None = Depends(allow_self_or_admin), database_session: Session = Depends(get_database_session)):
    user = repositories.read_user(database_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers have wishlists")

    wishlist = repositories.get_wishlist(database_session, user_id)
    return [product for item in wishlist if (product := fetch_product_data(item.product_id, test_products))]


@app.delete("/users/{user_id}/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(user_id: int, product_id: str, _: None = Depends(allow_self_or_admin), db: Session = Depends(get_database_session)):
    if not repositories.is_product_in_wishlist(db, user_id, product_id):
        raise HTTPException(status_code=404, detail="Product not in wishlist")
    repositories.remove_product_from_wishlist(db, user_id, product_id)


@app.post("/token", response_model=schemas.Token)
async def access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database_session: Session = Depends(get_database_session)
):
    user = authenticate_user(database_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expire = timedelta(hours=1)
    token = create_access_token(data={"sub": user.email, "role": user.role}, expires=expire)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def register_user(user: schemas.UserCreate, _: None = Depends(allow_admin), database_session: Session = Depends(get_database_session)):
    existing = repositories.read_user_by_email(database_session, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repositories.create_user(database_session, user)

