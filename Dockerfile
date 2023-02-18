FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y curl

ARG PORT=5000

ARG FLASK_DEBUG=0

ENV FLASK_APP "proxyservice"

LABEL maintainer="david.ibia@boxmarshall.com"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:${PORT}/health || exit 1

CMD [ "gunicorn", "proxyservice", "--access-logfile -"]