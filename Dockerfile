FROM dipdup/dipdup:6.0.0-rc1
# FROM ghcr.io/dipdup-net/dipdup-py:feat-db-rollback
COPY . .
RUN inject_pyproject
