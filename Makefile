SHELL := /bin/bash
DOCKER_COMPOSE = docker-compose

.PHONY: build up down test

build:
	$(DOCKER_COMPOSE) build

up: build
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down