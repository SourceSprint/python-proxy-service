FROM python:3.10-slim-buster

ENV FLASK_APP="proxyservice"
ENV FLASK_ENV="production"
ENV FLASK_DEBUG=0

LABEL maintainer="david.ibia@boxmarshall.com"

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD [ "gunicorn", "proxyservice", "--access-logfile -"]