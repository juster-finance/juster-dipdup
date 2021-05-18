FROM python:3.9-slim-buster

RUN apt update && \
    apt install -y make git && \
    rm -rf /var/lib/apt/lists/*
RUN pip install poetry
RUN useradd -ms /bin/bash dipdup

WORKDIR /home/dipdup/baking_bet
COPY . .

RUN poetry config virtualenvs.create false
RUN make install DEV=0
RUN chown -R dipdup /home/dipdup/

USER dipdup

EXPOSE 8888
ENTRYPOINT ["python", "-m", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.prod.yml", "run"]
