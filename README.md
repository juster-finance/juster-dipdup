# juster-dipdup

This repo contains a Juster betting protocol indexer based on DipDup.

Juster protocol was sunsetted on May 2023; this repo is archived. Thanks for your support!

## Installation

Python 3.10 is required to run DipDup v6. Use the following commands to set up dev environment:

```shell
# Using poetry
$ poetry install
$ poetry shell

# Using pip
$ python3.10 -m venv .venv
$ source .venv/bin/activate
$ python3.10 -m pip install -e .
```

## Running and deployment

```shell
# SQLite database
$ dipdup run

# PostgreSQL in docker-compose
$ docker-compose up -d db hasura
$ dipdup -c dipdup.yml -c dipdup.local.yml run
```
