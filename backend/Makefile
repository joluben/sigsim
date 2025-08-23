.PHONY: help install dev-install lint format test test-cov clean run

help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  dev-install  Install development dependencies"
	@echo "  lint         Run linting (flake8, mypy)"
	@echo "  format       Format code (black, isort)"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  clean        Clean cache and build files"
	@echo "  run          Run development server"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

lint:
	flake8 app tests
	mypy app

format:
	black app tests
	isort app tests

format-check:
	black --check app tests
	isort --check-only app tests

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database commands
init-db:
	python scripts/init_db.py

init-db-sample:
	python scripts/init_db.py --sample-data

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"

migrate-downgrade:
	alembic downgrade -1

db-reset:
	rm -f data/app.db
	$(MAKE) init-db-sample