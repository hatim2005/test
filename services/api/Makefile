.PHONY: help install dev test lint format clean run migrate

help:
	@echo "Color Correction System - Available Commands"
	@echo "=============================================="
	@echo "install      Install production dependencies"
	@echo "dev          Install development dependencies"
	@echo "test         Run all tests"
	@echo "test-cov     Run tests with coverage report"
	@echo "lint         Run code quality checks"
	@echo "format       Format code with Black"
	@echo "clean        Clean up temporary files"
	@echo "run          Start development server"
	@echo "migrate      Run database migrations"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt

test:
	pytest -v

test-cov:
	pytest --cov=./ --cov-report=html

test-auth:
	pytest tests/test_auth.py -v

lint:
	black .
	flake8 . --max-line-length=100
	mypy .

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(MESSAGE)"

celery:
	celery -A celery_config worker --loglevel=info

flower:
	celery -A celery_config flower
