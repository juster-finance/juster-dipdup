.ONESHELL:
.DEFAULT_GOAL: all

all: lint
lint: isort black pylint mypy

isort:
	poetry run isort juster/handlers

black:
	poetry run black juster/handlers

pylint:
	poetry run pylint juster/handlers || poetry run pylint-exit $$?

mypy:
	poetry run mypy juster/handlers

up:
	docker-compose -f docker-compose.local.yml up -d --build

down:
	docker-compose -f docker-compose.local.yml down -v