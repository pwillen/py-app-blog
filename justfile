set shell := ["powershell.exe", "-c"]

# Django
start-server:
    uv run python manage.py runserver

make-migrations app_name="":
    uv run python manage.py makemigrations {{app_name}}

migrate:
    uv run python manage.py migrate

shell:
    uv run python manage.py shell

dbshell:
    uv run python manage.py dbshell

check:
    uv run python manage.py check

# Docker
up:
    docker-compose up -d

# Linting
ruff-check:
    uv run ruff check .
    uv run ruff format --check .

ruff-fix:
    uv run ruff check . --fix
    uv run ruff format .