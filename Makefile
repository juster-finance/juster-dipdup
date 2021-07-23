.ONESHELL:
.DEFAULT_GOAL: all

all: lint
lint: isort black pylint mypy

isort:
	poetry run isort src tests

black:
	poetry run black src tests

pylint:
	poetry run pylint src tests || poetry run pylint-exit $$?

mypy:
	poetry run mypy src tests

local:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d