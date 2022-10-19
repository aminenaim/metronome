FROM python:3.10-slim

WORKDIR /app

COPY ./src .
COPY ./schema schema/
COPY requirements.txt ./


RUN apt-get update; apt-get install poppler-utils -y; apt-get clean
RUN pip install --no-cache-dir -r requirements.txt



CMD [ "python","-u", "./parser.py", "--config=/config", "--output=/ics", "--workdir=/tmp"]