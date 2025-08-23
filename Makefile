.PHONY: help setup dev-setup test lint format clean docker-build docker-up docker-down

help:
	@echo "IoT Simulator - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup        Setup development environment"
	@echo "  dev-setup    Setup development environment (alias)"
	@echo ""
	@echo "Development:"
	@echo "  test         Run all tests"
	@echo "  lint         Lint all code"
	@echo "  format       Format all code"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker images"
	@echo "  docker-up    Start services with Docker Compose"
	@echo "  docker-down  Stop Docker Compose services"
	@echo ""
	@echo "Backend specific:"
	@echo "  backend-test Run backend tests"
	@echo "  backend-lint Lint backend code"
	@echo "  backend-run  Run backend development server"
	@echo ""
	@echo "Frontend specific:"
	@echo "  frontend-test Run frontend tests"
	@echo "  frontend-lint Lint frontend code"
	@echo "  frontend-run  Run frontend development server"

setup: dev-setup

dev-setup:
	@echo "Setting up development environment..."
	@echo "Please run the following commands manually:"
	@echo ""
	@echo "Backend setup:"
	@echo "  cd backend"
	@echo "  python -m venv venv"
	@echo "  venv\\Scripts\\activate  (Windows) or source venv/bin/activate (Linux/Mac)"
	@echo "  pip install -r requirements-dev.txt"
	@echo ""
	@echo "Frontend setup:"
	@echo "  cd frontend"
	@echo "  npm install"
	@echo ""
	@echo "Pre-commit hooks:"
	@echo "  pip install pre-commit"
	@echo "  pre-commit install"

test:
	@echo "Running all tests..."
	cd backend && python -m pytest --cov=app --cov-report=term-missing
	cd frontend && npm test -- --watchAll=false

backend-test:
	cd backend && python -m pytest --cov=app --cov-report=term-missing

frontend-test:
	cd frontend && npm test -- --watchAll=false

lint:
	@echo "Linting all code..."
	cd backend && flake8 app tests && mypy app && black --check app tests && isort --check-only app tests
	cd frontend && npm run lint && npm run format:check

backend-lint:
	cd backend && flake8 app tests && mypy app && black --check app tests && isort --check-only app tests

frontend-lint:
	cd frontend && npm run lint && npm run format:check

format:
	@echo "Formatting all code..."
	cd backend && black app tests && isort app tests
	cd frontend && npm run format && npm run lint:fix

backend-format:
	cd backend && black app tests && isort app tests

frontend-format:
	cd frontend && npm run format && npm run lint:fix

backend-run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-run:
	cd frontend && npm run dev

clean:
	@echo "Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete || true
	find . -type d -name "__pycache__" -delete || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	rm -rf backend/build/ || true
	rm -rf backend/dist/ || true
	rm -rf backend/.coverage || true
	rm -rf backend/htmlcov/ || true
	rm -rf backend/.pytest_cache/ || true
	rm -rf backend/.mypy_cache/ || true
	rm -rf frontend/node_modules/.cache/ || true
	rm -rf frontend/dist/ || true
	rm -rf frontend/coverage/ || true

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f