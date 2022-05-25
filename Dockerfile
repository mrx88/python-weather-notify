FROM python:3.10-slim-bullseye

WORKDIR /app/
COPY requirements.txt /app/

RUN pip install --upgrade pip \
  && pip install -r /app/requirements.txt

RUN adduser appuser
USER appuser

COPY foreca_notify.py .

CMD [ "python", "-u", "./foreca_notify.py" ]