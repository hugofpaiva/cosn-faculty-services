VENV := venv
BIN := $(VENV)/bin
PYTHON := $(BIN)/python
SHELL := /bin/bash

# This ensures make has access to environment variables stored in a file called .env. 
# This allows Make to utilize these variables in its commands, for example, the name of my virtual environment, or to pass in $(DBNAME) to psql.
#include .env

.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv: ## Make a new virtual environment
	python3 -m venv $(VENV) && source $(BIN)/activate

.PHONY: install
install: venv ## Make venv and install requirements
	$(PYTHON) -m pip install --upgrade pip
	$(BIN)/pip install --upgrade -r requirements.txt

.PHONY: freeze
freeze: ## Pin current dependencies
	$(BIN)/pip freeze > requirements.txt

.PHONY: migrate
migrate: ## Make and run migrations
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate

.PHONY: adminuser
adminuser: ## Create super user
	$(PYTHON) manage.py createsuperuser

.PHONY: test
test: ## Run tests 
	$(PYTHON) manage.py test --verbosity=0 --failfast

.PHONY: run
run: ## Run the Django server
	$(PYTHON) manage.py runserver

.PHONY: prod
prod: ## Start all services containers
	docker-compose build
	docker-compose up -d