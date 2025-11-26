# Color Correction System API Documentation

**Version:** 1.0.0  
**Status:** Production-Ready  
**Last Updated:** 2025-11-27

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Deployment](#deployment)

---

## 🎯 Overview

The Color Correction System is a production-grade FastAPI application designed for professional color image processing. It supports:

- **RAW Image Processing**: Handle professional camera formats (RAW, DNG, CR2, NEF, etc.)
- **ArUco Marker Detection**: Automatically detect color reference cards using ArUco markers
- **Color Correction Matrix (CCM) Computation**: Generate accurate color correction profiles
- **Delta-E Color Accuracy**: Measure and report color accuracy using CIE Delta-E metrics
- **Batch Processing**: Process multiple images asynchronously using Celery
- **Real-time Monitoring**: Track batch jobs with progress updates via WebSocket
- **Secure Authentication**: JWT-based token authentication for all endpoints
- **Database Flexibility**: Support for both SQLite (dev) and PostgreSQL (prod)

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Client    │────────▶│  FastAPI API │────────▶│  SQLAlchemy  │
│  (Web/App)  │         │  with JWT    │         │     ORM      │
└─────────────┘         └──────────────┘         └──────────────┘
                               │                        │
                               ▼                        ▼
                        ┌──────────────┐         ┌──────────────┐
                        │  Pydantic    │         │   Database   │
                        │  Validation  │         │ (SQLite/PG)  │
                        └──────────────┘         └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Celery    │
                        │   Workers    │
                        └──────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
           ┌──────────┐  ┌──────────┐  ┌──────────┐
           │ OpenCV  │  │ NumPy    │  │ Custom   │
           │ ArUco   │  │ SciPy    │  │ CV Libs  │
           └──────────┘  └──────────┘  └──────────┘
```

### Technology Stack

- **Framework**: FastAPI 0.95+
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (PyJWT)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Async Tasks**: Celery with Redis/RabbitMQ
- **Image Processing**: OpenCV, NumPy, SciPy
- **Validation**: Pydantic 2.0+
- **CORS**: fastapi-cors
- **Monitoring**: Flower (Celery monitoring)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (for production)
- Redis 6.0+ (for Celery tasks)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/hatim2005/test.git
cd test/services/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# - Set SECRET_KEY
# - Configure DATABASE_URL
# - Set CELERY_BROKER_URL if using Celery
```

### Running the Application

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Celery worker (for background tasks)
celery -A celery_config worker --loglevel=info

# Celery monitoring (Flower)
celery -A celery_config flower

# Apply database migrations
alembic upgrade head

# Create initial admin user
python scripts/create_admin.py
```

---

## 🔌 API Endpoints

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "access_token": "jwt_token"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=secure_password

Response: 200 OK
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### Image Endpoints

#### Upload Image
```
POST /api/images/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (binary image file)
metadata: {"camera_model": "Canon 5D", "lens": "Canon 24-70mm"}

Response: 201 Created
{
  "id": "uuid",
  "filename": "550e8400.jpg",
  "size_bytes": 2560000,
  "upload_date": "2025-11-27T10:30:00Z"
}
```

#### List Images
```
GET /api/images?skip=0&limit=20
Authorization: Bearer {token}

Response: 200 OK
{
  "total": 100,
  "items": [
    {
      "id": "uuid",
      "filename": "550e8400.jpg",
      "size_bytes": 2560000,
      "upload_date": "2025-11-27T10:30:00Z"
    }
  ]
}
```

### Detection Endpoints

#### Detect ArUco Markers
```
POST /api/detection/aruco
Authorization: Bearer {token}
Content-Type: application/json

{
  "image_id": "uuid",
  "marker_size": 50
}

Response: 200 OK
{
  "markers_detected": 4,
  "detection_points": [
    {"x": 100, "y": 100, "z": 0},
    {"x": 200, "y": 100, "z": 0},
    {"x": 100, "y": 200, "z": 0},
    {"x": 200, "y": 200, "z": 0}
  ],
  "confidence": 0.98
}
```

### Color Correction Endpoints

#### Compute Color Correction Matrix
```
POST /api/correction/compute-ccm
Authorization: Bearer {token}
Content-Type: application/json

{
  "image_id": "uuid",
  "reference_colors": [
    {"label": "white", "rgb": [255, 255, 255]},
    {"label": "gray", "rgb": [128, 128, 128]}
  ]
}

Response: 200 OK
{
  "ccm": [[1.02, -0.01, 0.03], ...],
  "delta_e_avg": 2.5,
  "status": "success"
}
```

### Batch Processing Endpoints

#### Submit Batch Job
```
POST /api/batch/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "image_ids": ["uuid1", "uuid2", "uuid3"],
  "operation": "color_correction",
  "parameters": {}
}

Response: 202 Accepted
{
  "job_id": "uuid",
  "status": "queued",
  "total_images": 3,
  "processed": 0
}
```

#### Get Job Status
```
GET /api/batch/jobs/{job_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "job_id": "uuid",
  "status": "processing",
  "total_images": 3,
  "processed": 1,
  "progress_percentage": 33,
  "estimated_time_remaining": "2m 30s"
}
```

---

## 🔐 Authentication

All protected endpoints require JWT authentication.

### Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Expiration
- Default: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Refresh tokens: Not yet implemented (TODO)

---

## 📊 Data Models

### User
```python
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "hashed_password": "$2b$12$...",
  "is_active": True,
  "created_at": "2025-11-27T10:00:00Z",
  "updated_at": "2025-11-27T10:00:00Z"
}
```

### Image
```python
{
  "id": "uuid",
  "user_id": "uuid",
  "filename": "550e8400.jpg",
  "original_filename": "photo.jpg",
  "size_bytes": 2560000,
  "file_hash": "sha256_hash",
  "upload_date": "2025-11-27T10:00:00Z",
  "metadata": {}
}
```

### Job
```python
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "processing",
  "operation": "color_correction",
  "total_images": 10,
  "processed_images": 5,
  "created_at": "2025-11-27T10:00:00Z",
  "completed_at": None
}
```

---

## ⚠️ Error Handling

### Error Response Format
```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2025-11-27T10:30:00Z"
}
```

### Common HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created
- `202 Accepted`: Async job accepted
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File too large
- `500 Internal Server Error`: Server error

---

## 🚢 Deployment

### Docker Deployment
```bash
# Build image
docker build -t color-correction:latest .

# Run with compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

### Environment Variables for Production
```bash
ENVIRONMENT=production
SECRET_KEY=your-secure-key-here
DATABASE_URL=postgresql://user:pass@db:5432/color_correction
CELERY_BROKER_URL=redis://redis:6379/0
CORS_ORIGINS=https://yourfrontend.com
LOG_LEVEL=WARNING
```

### Monitoring
- **API Health**: `GET /health`
- **Celery**: Flower web UI (http://localhost:5555)
- **Logs**: `/var/log/color-correction/api.log`

---

## 📝 Notes

- This is a **professional-grade** API designed for production use
- All code includes comprehensive docstrings and type hints
- Database migrations managed via Alembic
- Background tasks handled by Celery for scalability
- Full JWT security implementation
- CORS enabled for frontend integration

For more information, see README.md and COMPLETION_GUIDE.md
