# EEXI Calculator Architecture & Deployment Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Production Deployment](#production-deployment)
5. [Workflows & CI/CD](#workflows--cicd)
6. [Key Concepts Used](#key-concepts-used)

---

## Architecture Overview

The system is a **3-tier web application** built using modern, production-grade technologies:
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS
- **Backend**: Flask 3 + Gunicorn + SQLAlchemy
- **Database**: PostgreSQL 15 (production) / SQLite (development)
- **Containerization**: Docker & Docker Compose

### High-Level Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│                     (Next.js Frontend on :3000)                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ API Requests
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Backend (:5000)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Blueprints: calculators, constants, history, admin       │  │
│  │  Calculators: EEXI, CII, EGBP, PipeWall, Interpolator     │  │
│  │  Security: Talisman, CORS, Rate Limiting                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                        │
│                   (Stores calculations, history)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backend Architecture

### Core Components
1. **Application Factory** (`app.py`)
   - Initializes Flask with configuration from `config.py`
   - Sets up security (Talisman), CORS, rate limiting
   - Registers API blueprints
   - Initializes database (SQLAlchemy) and migrations (Flask-Migrate)

2. **Configuration Management** (`config.py`)
   - All config via environment variables (12-Factor App)
   - Separate configs for dev/test/prod
   - Database connection pooling, CORS origins, rate limits

3. **API Blueprints** (`api/`)
   - `calculators.py`: Calculation endpoints for all tools
   - `constants.py`: Shared constants (fuel factors, ship types, etc.)
   - `history.py`: Calculation history retrieval
   - `admin.py`: Admin dashboard endpoints
   - `reports.py`: PDF report generation

4. **Calculators** (`calculators/`)
   - Modular calculator implementations
   - Each in own subdirectory
   - Shared utilities in `utils/` (validators, ship params, fuel factors)

5. **Database** (`database/db.py`)
   - SQLAlchemy ORM models for all calculation types
   - Connection pooling configured in `config.py`

6. **Logging** (`utils/logger.py`)
   - Structured JSON logging
   - Logs to stdout for containerized deployments
   - Request/response logging with context (ship type, calculation status, etc.)

7. **PDF Reports** (`reports/pdf_generator.py`)
   - ReportLab-based PDF generation
   - Separate generators for each calculator type

---

## Frontend Architecture

### Core Components
1. **App Router Structure** (`src/app/`)
   - Route-based pages for each calculator
   - Layout components (`AppLayout`, `Sidebar`, `TopBar`) for consistent UI
   - Global styles with Tailwind CSS

2. **Reusable Components** (`src/components/`)
   - `ErrorBoundary.tsx`: Graceful error handling for runtime errors
   - Navigation components for multi-tool suite

3. **API Layer** (`src/lib/`)
   - `api.ts`: Typed API client with error handling and report downloads
   - `types.ts`: TypeScript interfaces for form data and responses
   - `constants.ts`: Frontend constants (synced from backend API)

### Key Features
- TypeScript for type safety
- Tailwind CSS for modern, responsive styling
- Error boundary for graceful degradation
- Environment-based API base URL configuration

---

## Production Deployment

### 1. Prerequisites
- Docker & Docker Compose installed
- Environment variables configured (see `.env.example`)
- Persistent storage for database and reports

### 2. Docker Compose Deployment
```bash
# Copy and configure .env
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Environment Variables (.env)
```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key-here

# Database
DATABASE_URI=postgresql://user:password@postgres:5432/eexi_db

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Rate Limiting
RATE_LIMIT_DEFAULT=200 per minute
```

### 4. Production Best Practices
1. **Security**
   - Use HTTPS (e.g., with Nginx as reverse proxy)
   - Never expose backend directly to internet (use reverse proxy)
   - Rotate secrets regularly
   - Keep dependencies updated

2. **Scalability**
   - Backend: Horizontal scaling with load balancer
   - Database: Read replicas for high traffic
   - Frontend: CDN for static assets

3. **Monitoring**
   - Healthcheck endpoints: `/health` (simple) and `/api/health` (database check)
   - Structured logging for debugging
   - Resource limits in Docker Compose

4. **Database Migrations**
   ```bash
   # Run migrations
   docker-compose exec backend flask db upgrade
   
   # Create new migration
   docker-compose exec backend flask db migrate -m "description"
   ```

---

## Workflows & CI/CD

### CI/CD Pipeline (GitHub Actions)
Located at `.github/workflows/ci.yml`, it:
1. **Runs on push/PR to main/master**
2. **Backend Tests**:
   - Spins up PostgreSQL service
   - Installs dependencies
   - Runs pytest suite
3. **Frontend Checks**:
   - Installs npm packages (with caching)
   - Runs linter (`npm run lint`)
   - Builds production bundle to catch errors early

### Development Workflow
1. Create feature branch
2. Make changes
3. Test locally with `docker-compose`
4. Push branch and open PR
5. CI runs automatically
6. Merge to main after approval

---

## Key Concepts Used

### 1. 12-Factor App Principles
- **Config**: All config in environment variables
- **Dependencies**: Explicitly declared in `requirements.txt` and `package.json`
- **Backing Services**: Database as attached resource
- **Logs**: Logs as event stream to stdout
- **Processes**: Stateless, one process per container

### 2. Microservice-Inspired (Monolith for Simplicity)
- Modular blueprints for separation of concerns
- Clear API boundaries for future scalability
- Can split into separate services later if needed

### 3. Containerization & Orchestration
- **Docker**: Consistent environments across dev/prod
- **Docker Compose**: Local orchestration for multi-service setup
- **Non-root users**: Security best practice for containers
- **Named volumes**: Persistent data for database and reports

### 4. Production-Grade Backend
- **Gunicorn**: Production WSGI server (replaces Flask dev server)
- **Flask-Talisman**: Security headers (X-Content-Type-Options, X-Frame-Options, etc.)
- **Flask-Limiter**: Rate limiting to prevent abuse
- **Flask-Migrate**: Database versioning and migrations
- **Structured Logging**: JSON logs for easier parsing by monitoring tools
- **Healthchecks**: Readiness and liveness probes for orchestration

### 5. Modern Frontend
- **Next.js**: React framework with SSR/SSG capabilities
- **TypeScript**: Type safety for better maintainability
- **Tailwind CSS**: Utility-first CSS for rapid, consistent styling
- **Error Boundaries**: Graceful error handling for better UX

### 6. CI/CD
- **GitHub Actions**: Automated testing and builds on every PR/push
- **Test Isolation**: Ephemeral PostgreSQL container for backend tests
- **Caching**: Dependency caching for faster builds

---

## Summary of Optimizations Made

1. **Backend**
   - Structured JSON logging
   - Proper error handling with error handlers
   - Healthcheck endpoints
   - Security headers (Talisman)
   - Rate limiting
   - Flask-Migrate for database migrations
   - Gunicorn configuration file
   - Non-root user in Docker
   - Added `requests` for healthchecks
   - Blueprint URL prefixes

2. **Frontend**
   - Added ErrorBoundary component

3. **Infrastructure**
   - Enhanced Docker Compose with healthchecks, resource limits, named volumes
   - GitHub Actions CI/CD pipeline
   - Updated `.env.example`
   - Architecture documentation

4. **Dependencies**
   - Added `flask-talisman`, `flask-migrate`, `python-json-logger`, `requests`
