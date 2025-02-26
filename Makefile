SHELL := /bin/bash
DOCKER_COMPOSE = docker-compose
DB_SERVICE = event_management_app
PYTHON = python3

.PHONY: build up down makemigration migrate downgrade

build:
	$(DOCKER_COMPOSE) build

# "up" depends on the "build" target to ensure images are built before starting.
# Removing the "-d" flag so logs show in the current terminal session.
up: build
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down

# Create a new Alembic migration file (auto-generating changes).
# Usage example: make makemigration message="Add users table"
makemigration:
	$(DOCKER_COMPOSE) run --rm $(DB_SERVICE) alembic revision --autogenerate -m "$(message)"

# Apply (upgrade) all migrations to the database.
migrate:
	$(DOCKER_COMPOSE) run --rm $(DB_SERVICE) alembic upgrade head

# Downgrade the database by a revision (or multiple revisions).
# Usage examples:
#   make downgrade revision="ae1027a6acf"  (downgrades to a specific revision)
#   make downgrade revision="-1"  (downgrades one revision)
downgrade:
	$(DOCKER_COMPOSE) run --rm $(DB_SERVICE) alembic downgrade $(revision)