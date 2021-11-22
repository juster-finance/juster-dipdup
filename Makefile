.ONESHELL:
.DEFAULT_GOAL: all

DEV=1
TAG=latest

all: install lint test cover
lint: isort black flake mypy

debug:
	pip install . --force --no-deps

install:
	poetry install `if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

isort:
	poetry run isort juster

black:
	poetry run black juster

flake:
	poetry run flakehell lint juster

mypy:
	poetry run mypy juster

test:
	# poetry run pytest --cov-report=term-missing --cov=juster --cov-report=xml -v tests

cover:
	# poetry run diff-cover coverage.xml

build:
	poetry build

image:
	docker build . -t juster:${TAG}

up:
	docker-compose -f docker-compose.local.yml up -d db hasura

down:
	docker-compose -f docker-compose.local.yml down -v

run:
	TZ=Europe/Moscow poetry run dipdup -c dipdup.yml -c dipdup.local.yml run

bump:
	poetry run pip uninstall -y dipdup
	poetry update dipdup
	git add poetry.lock pyproject.toml Makefile
	git commit -m "Bump dipdup"
	git push

deploy:
	git pull
	swarmlet deploy /mnt/gfs/git/data/juster-staging
