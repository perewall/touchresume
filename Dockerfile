FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache --update build-base postgresql-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache build-base
