FROM python:3.9.6-slim

ENV CURL_CA_BUNDLE="" CRYPTOGRAPHY_DONT_BUILD_RUST=1 PYTHONWARNINGS="ignore:Unverified HTTPS request"
WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install gcc libpq-dev -y && \
    apt clean

COPY . ./

RUN pip3 install poetry --no-cache-dir && poetry install --no-dev && rm -rf ~/.cache/

VOLUME /usr/src/app/static

CMD ["gunicorn", "cloud_services.wsgi:application", "--bind", "0.0.0.0:8000"]