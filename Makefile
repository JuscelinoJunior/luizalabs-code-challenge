.PHONY: up down clean rebuild logs test

up:
	docker-compose up --build -d

down:
	docker-compose down

clean:
	docker-compose down -v

rebuild:
	docker-compose down
	docker-compose up --build -d

logs:
	docker-compose logs -f

test:
	python3 -m pip install -r requirements.txt
	DATABASE_URL="mysql+pymysql://root:root@mysql:3306/wishlist_db" PYTHONPATH=. pytest
