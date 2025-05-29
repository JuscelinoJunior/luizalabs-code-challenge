import json
import os
from typing import List, Dict, Optional
from fastapi import HTTPException
import httpx
from app.database import SessionLocal
from sqlalchemy.orm import Session

PRODUCT_API_URL = os.environ.get("PRODUCT_API_URL")

def get_mock_product(product_id: str, mock_path: str = "app/mock/mock_products.json") -> Optional[Dict]:
    try:
        with open(mock_path) as f:
            products: List[Dict] = json.load(f)
        return next((product for product in products if str(product["id"]) == str(product_id)), None)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Mock product file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in mock product file")


def fetch_product_data(product_id: str, test_products: bool) -> Optional[Dict]:
    if test_products:
        return get_mock_product(product_id)

    try:
        response = httpx.get(f"{PRODUCT_API_URL}{product_id}", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail=f"Product API service unavailable"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        else:
            raise HTTPException(
                status_code=503,
                detail=f"Product API service unavailable"
            )


def get_database_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()