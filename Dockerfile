FROM python:3-slim

WORKDIR /app
RUN mkdir /data

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV REMEMBERED_OFFERS_FILE=/data/remembered_offers.txt
CMD [ "python3", "main.py"]
