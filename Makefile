.ONESHELL:
.PHONY: $(MAKECMDGOALS)
##
##    🚧 DipDup developer tools
##
## DEV=1                Install dev dependencies
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
	`if [ "${DEV}" = "0" ]; then echo "--without dev"; fi`

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
	docker buildx build . --progress plain -t juster-dipdup:${TAG}

##

clean:          ## Remove all files from .gitignore except for `.venv`
	git clean -xdf --exclude=".venv"

update:         ## Update dependencies, export requirements.txt (wait an eternity)
	make install
	poetry update
	poetry export --without-hashes -o requirements.txt
