# Cloud Services interview task

## Requirements

- Python 3.9
- Docker
- Docker-Compose

## Quickstart

```bash
docker-compose up -d --build
docker-compose logs -f
```

## Installation

```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install poetry
poetry install
```

## Usage

Docs are here:  http://localhost:8000/api/v1/docs

Run server: ```python manage.py runserver 8000```

Build image: ```docker build . --rm -t cloud_services```

Run container: ```docker run -itd -p 8000:8000 cloud_services```

## Initialization

Creating user: http://localhost:8000/api/v1/auth/

## Configuration

Example env vars are available in ```local.env```

```DEBUG_MODE``` - allows for responding with internal errors details

```DEV_MODE``` - tells Huey to use SQLite db

```TEST_MODE``` - swaps Redis dictionary to basic python and prevents emails sending

```DEV_REDIS``` - uses Docker to create Redis instance while running server

```DISABLE_AUTH``` - disables auth requirments
## Authorization

#### Creating JWT token

```http://localhost:8000/api/v1/auth/jwt/create``` with body

```json
{
  "username": "admin",
  "password": "adminadmin"
}
```

#### Verifying JWT token

```http://localhost:8000/api/v1/auth/jwt/verify``` with body

```json
{
  "token": "ACCESS_TOKEN"
}
```

#### Using JWT Token

```http://localhost:8000/``` with headers

```json
{
  "Authorization": "JWT ACCESS_TOKEN"
}
```

## Testing

#### Using Docker image

```bash
docker build -f .\dev.Dockerfile . --rm -t cloud_services
docker run --env-file .\test.env cloud_services python -m pytest -s -vvv -p no:cacheprovider
```

#### Local

```bash
export $(grep -v '#.*' test.env | xargs)
python -m pytest tests -s -vvv -p no:cacheprovider
```

#### Using PyCharm

![img1.PNG](img1.PNG)
![img2.PNG](img2.PNG)

EnvFile plugin: https://plugins.jetbrains.com/plugin/7861-envfile

### Coverage

```bash
export $(grep -v '#.*' test.env | xargs)
python -m pytest tests -s -vvv --cov=. --cov-report html -p no:cacheprovider
```

Then, open ```index.html``` in ```htmlcov``` directory.

## Author

Oleksandr Kudryavtsev (```14zsoddenu@gmail.com```).