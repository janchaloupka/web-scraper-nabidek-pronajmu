FROM python:3-alpine

WORKDIR /app
VOLUME ["/data"]

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV APP_ENV=docker

COPY .env* .
COPY src .
COPY graphql ./graphql

CMD ["python3", "main.py"]
