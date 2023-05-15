FROM python:3-alpine

WORKDIR /app
VOLUME ["/data"]

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY .env* .
COPY src .
COPY graphql /graphql

ENV APP_ENV=docker
CMD ["python3", "main.py"]
