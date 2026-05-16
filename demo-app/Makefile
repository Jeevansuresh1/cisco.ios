.PHONY: build up down logs shell test clean

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

shell:
	docker compose exec app /bin/bash

test:
	docker compose exec app python -m pytest tests/ -v

clean:
	docker compose down -v --rmi local
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
