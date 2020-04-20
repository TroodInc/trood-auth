default: run

build:
	@docker-compose build

test:
	@docker-compose exec authorization pytest

makemigrations:
	@docker-compose exec authorization python manage.py makemigrations

migrate:
	@docker-compose exec authorization python manage.py migrate

bash:
	@docker-compose exec authorization bash

run: build
	@docker-compose up -d

down:
	@docker-compose down

.PHONY: run default build test down
