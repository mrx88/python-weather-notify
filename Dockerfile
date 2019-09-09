FROM python:3.7.2-alpine

WORKDIR /app/
COPY requirements.txt /app/

RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r /app/requirements.txt \
  && apk del build-dependencies

RUN adduser -D appuser
USER appuser

COPY foreca_notify.py .

CMD [ "python", "-u", "./foreca_notify.py" ]