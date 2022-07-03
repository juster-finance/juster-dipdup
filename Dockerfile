# FROM dipdup/dipdup:5.2
FROM ghcr.io/dipdup-net/dipdup-py:feat-db-rollback
COPY . .
RUN inject_pyproject
