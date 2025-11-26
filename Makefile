.PHONY: help install dev test clean docker-build docker-up docker-down

help:
	@echo "Color Correction System - Make Commands"
	@echo ""
	@echo "  install      - Install dependencies"
	@echo "  dev          - Run development environment"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up    - Start Docker containers"
	@echo "  docker-down  - Stop Docker containers"

install:
	@echo "Installing dependencies..."
	poetry install
	npm install

dev:
	@echo "Starting development environment..."
	docker-compose up -d

test:
	@echo "Running tests..."
	poetry run pytest
	npm test

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf node_modules/.cache

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
