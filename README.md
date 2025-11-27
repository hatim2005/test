# Color Correction System - Production Backend

![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

> Professional color correction system with ArUco marker detection, color accuracy analysis, and AI background removal.

## Table of Contents

- [Project Overview](#project-overview)
- [Current State](#current-state)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Deployment](#deployment)
- [Known Issues](#known-issues)
- [Contributing](#contributing)

---

## Project Overview

This is a **comprehensive color correction system** designed for product and general photography with industry-grade accuracy. It features:

- ✅ **24-patch color card detection** with ArUco markers
- ✅ **Color Correction Matrix (CCM)** generation
- ✅ **ΔE (CIEDE2000) reporting** for quality metrics
- ✅ **RESTful API** with FastAPI & OpenAPI/Swagger
- ✅ **Batch processing** with Celery task queue
- ✅ **JWT authentication** with role-based access
- ✅ **Database** with SQLAlchemy ORM
- ✅ **Docker containerization** for easy deployment
- ✅ **Automated testing** with pytest
- ✅ **CI/CD pipelines** with GitHub Actions

---

## Current State

**Completion: ~15% of full specification**

### What's Built (✅)
- FastAPI backend with 6 API routers
- SQLAlchemy database models (User, Image, Job, etc.)
- JWT authentication & authorization
- Database migrations with Alembic
- Background task queue setup (Celery)
- Docker & docker-compose configuration
- GitHub Actions CI/CD workflows
- Comprehensive test suite

### What's Missing (❌)
- Mobile apps (Android/iOS)
- Desktop app (PyQt)
- Web portal (Next.js)
- Computer Vision library (ArUco, CCM, ΔE)
- ML training pipeline
- Celery worker implementation
- Main app refactoring (split modules)

**See [COMPREHENSIVE_AUDIT_AND_FIX.md](COMPREHENSIVE_AUDIT_AND_FIX.md) for full analysis.**

---

## Quick Start

### Prerequisites

```bash
# Required
- Python 3.10+
- Docker & Docker Compose
- Git

# Optional (for development)
- PostgreSQL 14+
- Redis 7+
```

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/hatim2005/test.git
cd test
```

#### 2. Python Virtual Environment
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
cd services/api
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 5. Run with Docker (Recommended)
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

API will be available at:
- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Architecture

```
├── services/
│  └── api/                    # FastAPI backend
│     ├── routers/              # API endpoints
│     │  ├── auth.py            # Auth/JWT
│     └── models/              # Database models
├── libs/
│  ├── cv/                  # Computer Vision (TODO)
│  └── ml/                  # ML Pipeline (TODO)
├── apps/
│  ├── mobile/              # Mobile apps (TODO)
│  ├── desktop/             # PyQt app (TODO)
│  └── web/                 # Next.js portal (TODO)
```

---

## API Documentation

### Authentication

```bash
# Sign up
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Upload Image

```bash
POST /api/v1/images
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@image.jpg

# Response
{
  "image_id": "uuid-123",
  "filename": "image.jpg",
  "size": 102400,
  "created_at": "2025-11-27T10:30:00Z"
}
```

**See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.**

---

## Development Guide

### Running Tests

```bash
cd services/api

# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test
pytest tests/test_auth.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .

# All
make lint
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Testing

### Test Coverage

- ✅ Authentication (JWT, roles)
- ✅ Database models
- ✅ API endpoints
- ✅ Utility functions
- ❌ ArUco detection
- ❌ Color correction
- ❌ Background removal

### Running Tests

```bash
cd services/api

# Development
pytest tests/ -v --tb=short

# With coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Watch mode (requires pytest-watch)
ptw
```

---

## Deployment

### Docker

```bash
# Build
docker build -t color-correction:latest .

# Run
docker run -p 8000:8000 --env-file .env color-correction:latest
```

### Docker Compose

```bash
# Development (SQLite, single container)
docker-compose up

# Production (PostgreSQL, Redis, multiple workers)
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` for all available options:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/colordb

# Redis/Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Auth
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# App
DEBUG=false
LOG_LEVEL=INFO
```

---

## Known Issues

1. **main.py file too large** - Needs to be split into modules
2. **ArUco detection not implemented** - Missing `libs/cv/`
3. **Color correction not implemented** - Missing CCM algorithm
4. **Celery not integrated** - Workers not deployed
5. **Background removal missing** - Needs U^2-Net or SAM
6. **No mobile/desktop apps** - Phase 2 deliverable

**Track progress:** [COMPREHENSIVE_AUDIT_AND_FIX.md](COMPREHENSIVE_AUDIT_AND_FIX.md)

---

## Contributing

### Setup Development Environment

```bash
# Clone
git clone https://github.com/hatim2005/test.git
cd test

# Install
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate`
cd services/api
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v
```

### Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Run tests: `pytest tests/ -v`
4. Push: `git push origin feature/my-feature`
5. Create PR

---

## License

MIT License - see LICENSE file

---

## Support

For issues and questions:
- Check [COMPREHENSIVE_AUDIT_AND_FIX.md](COMPREHENSIVE_AUDIT_AND_FIX.md)
- Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- Open an issue on GitHub

---

**Last Updated:** November 27, 2025
**Maintainer:** hatim2005
