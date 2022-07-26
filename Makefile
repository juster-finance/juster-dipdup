.ONESHELL:
.PHONY: $(MAKECMDGOALS)
##
##    🚧 DipDup developer tools
##
## DEV=1                Whether to install dev dependencies
DEV=1
## TAG=latest           Tag for the `image` command
TAG=latest

##

help:           ## Show this help (default)
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

all:            ## Run a whole CI pipeline: lint, run tests, build docs
	make install lint

install:        ## Install project dependencies
	poetry install \
	`if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

lint:           ## Lint with all tools
	make isort black flake mypy

##

isort:          ## Format with isort
	poetry run isort src

black:          ## Format with black
	poetry run black src

flake:          ## Lint with flake8
	poetry run flakeheaven lint src

mypy:           ## Lint with mypy
	poetry run mypy src

build:          ## Build Python wheel package
	poetry build

image:          ## Build Docker image
	docker buildx build . -t juster-dipdup:${TAG}

##

up:
	docker-compose -f docker-compose.yml up -d db hasura

down:
	docker-compose -f docker-compose.yml down
