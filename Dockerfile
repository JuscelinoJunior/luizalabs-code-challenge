FROM python:3.10

WORKDIR /

COPY ./app /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PYTHONPATH=/

ENV SECRET_KEY="1234"
ENV DATABASE_URL="mysql+pymysql://root:root@mysql:3306/wishlist_db"
ENV PRODUCT_API_URL="http://challenge-api.luizalabs.com/api/product/"

# Initiate FastAPI app with reload
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]