FROM python:3-alpine

WORKDIR /app
VOLUME ["/data"]

COPY requirements.txt requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip3 install -r requirements.txt && \
    apk del .build-deps

ENV APP_ENV=docker

COPY .env* .
COPY src .
COPY graphql ./graphql

CMD ["python3", "main.py"]
