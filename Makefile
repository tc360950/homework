COMPOSE_FILES := -f docker-compose.yml
DOCKER_COMPOSE := docker compose

format:
	cd service && python -m ruff format && python -m ruff check --fix

test-unit:
	cd service && python3 -m pytest -m "unit" tests -v --cov-report term --cov-report html:htmlcov --cov-report xml --cov-fail-under=90 --cov=./service

build:
	$(DOCKER_COMPOSE) $(DEV_COMPOSE_FILES) build
up:
	$(DOCKER_COMPOSE) $(DEV_COMPOSE_FILES) up -d
up-rebuild:
	$(DOCKER_COMPOSE) $(DEV_COMPOSE_FILES) up --build -d --force-recreate
remove:
	$(DOCKER_COMPOSE) $(DEV_COMPOSE_FILES) down --volumes --remove-orphans
down:
	$(DOCKER_COMPOSE) $(DEV_COMPOSE_FILES) down