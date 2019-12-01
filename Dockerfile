FROM python:3.6-alpine

ENV API_KEY unset

RUN apk update
RUN apk upgrade
RUN apk add bash

COPY bot /app/bot
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
COPY run_docker.sh /app/run.sh
WORKDIR /app

RUN pip install pipenv

RUN pipenv install

#CMD ["echo", "$test"]

#CMD ["pipenv", "run", "python", "/app"]
CMD ["/app/run.sh"]
