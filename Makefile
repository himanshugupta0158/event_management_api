SHELL := /bin/bash

.PHONY: build up down

build:
	$(DOCKER_COMPOSE) build

up: build
	$(DOCKER_COMPOSE) up

down:
	$(DOCKER_COMPOSE) down