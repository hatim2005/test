# Missing Files and Implementation TODO

This document tracks all files and structures that still need to be added to complete the Color Correction System monorepo.

## Progress Summary

### ✅ COMPLETED
- Root configuration files (Dockerfile, docker-compose.yml, Makefile, pyproject.toml, package.json)
- `/libs/cv/src/color_cv/` - Color correction library (aruco_detector.py, ccm.py, delta_e.py, white_balance.py)
- `/libs/ml/src/color_ml/` - ML library (background_removal.py)
- `/services/api/` - FastAPI service (main.py, schemas.py, Dockerfile)
- `/services/worker/` - Celery worker (tasks.py, Dockerfile)
- `/apps/` - Apps directory structure created
- `/apps/mobile/android/README.md` - Android app documentation
- `/apps/mobile/ios/README.md` - iOS app documentation

### ⏳ IN PROGRESS / TODO

## 1. Apps Directory - Desktop & Web

### `/apps/desktop/` - Python PyQt Desktop App
```
apps/desktop/
├── README.md                    # Setup and build instructions
├── requirements.txt             # Python dependencies
├── main.py                      # Application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main window
│   ├── capture_view.py         # Capture interface
│   ├── correction_view.py       # Color correction interface
│   └── batch_view.py           # Batch processing
├── core/
│   ├── __init__.py
│   ├── camera_manager.py       # Camera interface
│   ├── image_processor.py      # Image processing pipeline
│   └── export_manager.py       # Export functionality
└── tests/
    └── test_desktop.py
```

### `/apps/web/` - Next.js Web Portal
```
apps/web/
├── README.md
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── projects/
│   │   ├── upload/
│   │   └── analytics/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── UploadZone.tsx
│   │   └── AnalyticsDashboard.tsx
│   ├── lib/
│   │   └── api.ts
│   └── styles/
│       └── globals.css
└── public/
```

## 2. Libs Directory - Common

### `/libs/common/` - Shared Types and Utilities
```
libs/common/
├── README.md
├── setup.py
├── src/color_common/
│   ├── __init__.py
│   ├── types.py               # Data types and DTOs
│   ├── schemas.py             # JSON schemas
│   ├── errors.py              # Error codes and exceptions
│   ├── constants.py           # Shared constants
│   └── utils.py               # Utility functions
└── tests/
    └── test_common.py
```

## 3. Infrastructure Directory

### `/infrastructure/` - DevOps and Infrastructure
```
infrastructure/
├── README.md
├── docker/
│   ├── api.Dockerfile         # Consolidated API Dockerfile
│   ├── worker.Dockerfile      # Consolidated Worker Dockerfile
│   └── nginx.Dockerfile       # Nginx reverse proxy
├── terraform/
│   ├── README.md
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── ec2/
│   │   ├── rds/
│   │   ├── s3/
│   │   └── elasticache/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── production/
└── kubernetes/
    ├── api-deployment.yaml
    ├── worker-deployment.yaml
    ├── redis-statefulset.yaml
    └── ingress.yaml
```

## 4. Documentation Directory

### `/docs/` - Comprehensive Documentation
```
docs/
├── README.md
├── ARCHITECTURE.md            # System architecture
├── API.md                     # API documentation
├── COLOR_SCIENCE.md           # Color correction theory
├── PRINT_SPECS.md             # Color card printing specs
├── UX_DESIGN.md               # UX specifications
├── DEPLOYMENT.md              # Deployment guide
├── CONTRIBUTING.md            # Contribution guidelines
└── assets/
    ├── diagrams/
    ├── color-card-templates/   # Print-ready PDFs
    └── screenshots/
```

## 5. CI/CD Directory

### `/ci/` or `.github/workflows/` - GitHub Actions
```
.github/workflows/
├── lint.yml                   # Code linting
├── test.yml                   # Run tests
├── build.yml                  # Build artifacts
├── docker-publish.yml         # Publish Docker images
└── deploy.yml                 # Deploy to environments
```

## 6. Missing Files in Existing Directories

### `/libs/cv/` - Additional Files
- `tests/test_aruco.py`
- `tests/test_ccm.py`
- `tests/test_delta_e.py`
- `tests/test_white_balance.py`
- `requirements.txt`
- `README.md` (detailed usage)

### `/libs/ml/` - Additional Files
- `src/color_ml/models.py`             # Model definitions
- `src/color_ml/training.py`           # Training scripts
- `src/color_ml/export_onnx.py`        # ONNX export
- `tests/test_background_removal.py`
- `requirements.txt`
- `README.md`

### `/services/api/` - Additional Files
- `routers/`
  - `__init__.py`
  - `auth.py`
  - `images.py`
  - `detection.py`
  - `correction.py`
  - `batch.py`
  - `reports.py`
- `models/`
  - `__init__.py`
  - `database.py`
  - `user.py`
  - `image.py`
  - `job.py`
- `requirements.txt`
- `tests/`

### `/services/worker/` - Additional Files
- `processors/`
  - `__init__.py`
  - `detection_processor.py`
  - `correction_processor.py`
  - `background_processor.py`
- `requirements.txt`
- `tests/`

## 7. Color Card Design Files

### Physical Color Card Assets
```
assets/color-cards/
├── ColorChecker24_A4.pdf      # A4 print template
├── ColorChecker24_A5.pdf      # A5 print template
├── Extended_SkinTones.pdf     # Extended skin tone patches
├── Extended_Textiles.pdf      # Extended textile patches
├── ArUco_Markers_DICT_5X5_50.pdf  # ArUco markers
└── Printer_Profile_Guide.md   # Printer calibration guide
```

## 8. Test Datasets

### Sample Test Images
```
tests/fixtures/
├── images/
│   ├── raw_samples/
│   ├── jpeg_samples/
│   └── edge_cases/
└── expected_outputs/
```

## Priority Order

1. **HIGH PRIORITY** (Core Functionality)
   - [ ] Complete `/services/api/` with routers and models
   - [ ] Add requirements.txt to all Python modules
   - [ ] Create `/libs/common/` for shared code
   - [ ] Add tests to `/libs/cv/` and `/libs/ml/`

2. **MEDIUM PRIORITY** (DevOps & Deployment)
   - [ ] Create CI/CD workflows
   - [ ] Add comprehensive documentation
   - [ ] Create infrastructure Terraform templates
   - [ ] Add color card design files

3. **LOW PRIORITY** (Desktop & Extended Features)
   - [ ] Complete `/apps/desktop/` Python PyQt app
   - [ ] Complete `/apps/web/` Next.js portal
   - [ ] Add extended ML training scripts
   - [ ] Create sample datasets

## Implementation Notes

- All Python packages should follow the same structure with setup.py
- Use type hints throughout Python code
- Include inline comments and docstrings
- Write unit tests with >80% coverage
- Follow monorepo workspace conventions
- Use consistent code formatting (Black, Prettier, ESLint)

## Quick Start for Contributors

1. Pick a TODO item from the HIGH PRIORITY list
2. Create a new branch: `git checkout -b feature/add-api-routers`
3. Implement with tests and documentation
4. Submit PR with reference to this TODO
5. Update this file to mark item as complete

---

**Last Updated**: 2025-11-27  
**Current Completion**: ~40% (Core libraries and basic structure)  
**Target Completion**: 100% for MVP release
