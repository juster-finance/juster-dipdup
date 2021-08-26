FROM python:3.8-slim-buster

RUN apt update && \
    apt install -y make git && \
    rm -rf /var/lib/apt/lists/*
RUN pip install poetry

RUN useradd -ms /bin/bash dipdup
WORKDIR /home/dipdup/juster

COPY pyproject.toml poetry.lock README.md ./
RUN poetry config virtualenvs.create false && poetry install --no-dev
COPY . ./

RUN chown -R dipdup /home/dipdup/
USER dipdup

ENTRYPOINT ["dipdup"]
CMD ["run"]