# Docker Implementation Plan - PostgreSQL Edition

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan.

**Goal:** Containerize the OneEmployeeOrg Academy with PostgreSQL database, environment-based configuration, and both production and development setups.

**Architecture:** Multi-service Docker Compose with FastAPI app and PostgreSQL 16, using Pydantic Settings for configuration.

**Tech Stack:** Docker, Docker Compose, PostgreSQL 16, asyncpg, multi-stage builds

---

## File Structure

```
OneEmployeeOrg/
├── Dockerfile                 # Multi-stage production build
├── Dockerfile.dev             # Development build with hot reload
├── docker-compose.yml         # Production orchestration
├── docker-compose.dev.yml     # Development overrides
├── .dockerignore              # Files to exclude from Docker context
├── .env.example               # Environment variable template
├── src/oneorg/
│   └── config.py              # NEW: Pydantic settings
└── requirements.txt           # MODIFIED: Add asyncpg
```

---

## Chunk 1: Configuration System

**Files:**
- Create: `src/oneorg/config.py`
- Modify: `src/oneorg/db/database.py`
- Modify: `src/oneorg/services/auth.py`

### Task 1.1: Create Pydantic Settings

- [ ] **Step 1: Create src/oneorg/config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///data/oneorg.db"
    
    # Auth
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_days: int = 7
    
    # App
    app_name: str = "OneEmployeeOrg Academy"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

- [ ] **Step 2: Test config module**

Create `tests/test_config.py`:
```python
import pytest
from oneorg.config import get_settings, Settings

@pytest.mark.asyncio
async def test_settings_defaults():
    settings = Settings()
    assert "sqlite" in settings.database_url
    assert settings.secret_key == "dev-secret-change-in-production"
    assert settings.access_token_expire_days == 7

@pytest.mark.asyncio
async def test_settings_from_env():
    import os
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test"
    
    settings = Settings()
    assert settings.secret_key == "test-secret-key"
    assert settings.database_url == "postgresql://test"
    
    # Cleanup
    del os.environ["SECRET_KEY"]
    del os.environ["DATABASE_URL"]
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_config.py -v`

Expected: 2 tests pass

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/config.py tests/test_config.py
git commit -m "feat: add Pydantic settings for environment-based configuration"
```

### Task 1.2: Update Database Module

- [ ] **Step 1: Read current database.py**

Already read. Current implementation uses hardcoded SQLite path.

- [ ] **Step 2: Modify src/oneorg/db/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from oneorg.config import get_settings

settings = get_settings()

# Handle both SQLite and PostgreSQL
if settings.database_url.startswith("sqlite"):
    # SQLite: ensure data directory exists
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    data_dir = Path(db_path).parent
    data_dir.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

- [ ] **Step 3: Test database with config**

Run: `pytest tests/test_db.py -v`

Expected: Tests pass with both SQLite paths

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/db/database.py
git commit -m "feat: update database module to use Pydantic settings"
```

### Task 1.3: Update Auth Service

- [ ] **Step 1: Modify src/oneorg/services/auth.py**

Replace hardcoded secret with settings:
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from oneorg.db.models import User, Student
from oneorg.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode() if isinstance(hashed_password, str) else hashed_password
    )

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

async def create_user(db: AsyncSession, email: str, password: str) -> User:
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.access_token_expire_days))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    return result.scalar()
```

- [ ] **Step 2: Test auth with config**

Run: `pytest tests/test_auth.py -v`

Expected: All tests pass

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/services/auth.py
git commit -m "feat: update auth service to use Pydantic settings"
```

---

## Chunk 2: Docker Configuration Files

**Files:**
- Create: `.dockerignore`
- Create: `.env.example`

### Task 2.1: Create .dockerignore

- [ ] **Step 1: Create .dockerignore**

```
# Python
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/

# Git
.git/
.gitignore

# Data (will be volume-mounted)
data/
*.db
*.sqlite

# Documentation
docs/
*.md
!README.md

# Tests
tests/
.pytest_cache/
.coverage

# Environment
.env
.env.*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
Dockerfile*
docker-compose*.yml
.dockerignore
```

- [ ] **Step 2: Commit**

```bash
git add .dockerignore
git commit -m "chore: add .dockerignore"
```

### Task 2.2: Create .env.example

- [ ] **Step 1: Create .env.example**

```env
# =============================================================================
# OneEmployeeOrg Academy - Environment Configuration
# =============================================================================
# Copy this file to .env and customize for your deployment

# REQUIRED: Secret key for JWT tokens (min 32 characters)
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secure-random-string-min-32-chars

# Database URL
# SQLite (local development):
# DATABASE_URL=sqlite+aiosqlite:///data/oneorg.db
#
# PostgreSQL (Docker production):
DATABASE_URL=postgresql+asyncpg://oneorg:oneorg@db:5432/oneorg

# Optional Settings
# DEBUG=false
# ACCESS_TOKEN_EXPIRE_DAYS=7
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "chore: add .env.example template"
```

---

## Chunk 3: Dockerfiles

**Files:**
- Create: `Dockerfile`
- Create: `Dockerfile.dev`

### Task 3.1: Create Production Dockerfile

- [ ] **Step 1: Create Dockerfile**

```dockerfile
# =============================================================================
# OneEmployeeOrg Academy - Production Dockerfile
# Multi-stage build for smaller image size
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# Installs build dependencies and Python packages
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# Minimal runtime environment
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY requirements.txt .

# Install in editable mode
RUN pip install -e .

# Create non-root user for security
RUN useradd -m -u 1000 oneorg && \
    mkdir -p /app/data && \
    chown -R oneorg:oneorg /app
USER oneorg

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "oneorg.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Test Dockerfile syntax**

Run: `docker build -t oneorg:test -f Dockerfile . --no-cache`

Expected: Build succeeds (may have warnings about missing asyncpg)

- [ ] **Step 3: Commit**

```bash
git add Dockerfile
git commit -m "feat: add production Dockerfile with multi-stage build"
```

### Task 3.2: Create Development Dockerfile

- [ ] **Step 1: Create Dockerfile.dev**

```dockerfile
# =============================================================================
# OneEmployeeOrg Academy - Development Dockerfile
# Hot reload enabled for local development
# =============================================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Install in editable mode
RUN pip install -e .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run with hot reload for development
CMD ["uvicorn", "oneorg.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]
```

- [ ] **Step 2: Commit**

```bash
git add Dockerfile.dev
git commit -m "feat: add development Dockerfile with hot reload"
```

---

## Chunk 4: Docker Compose Files

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.dev.yml`
- Modify: `requirements.txt` (add asyncpg)

### Task 4.1: Create Production Docker Compose

- [ ] **Step 1: Read current requirements.txt**

Already read. Need to add asyncpg.

- [ ] **Step 2: Modify requirements.txt**

Add to requirements.txt:
```
asyncpg>=0.29.0
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
# =============================================================================
# OneEmployeeOrg Academy - Production Docker Compose
# FastAPI app + PostgreSQL database
# =============================================================================

version: "3.11"

services:
  # ---------------------------------------------------------------------------
  # Application Service
  # ---------------------------------------------------------------------------
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: oneorg-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://oneorg:oneorg@db:5432/oneorg
      - SECRET_KEY=${SECRET_KEY:?SECRET_KEY is required. Copy .env.example to .env and set a secure value.}
      - DEBUG=false
    volumes:
      # Persist SQLite data if using SQLite
      - ./data:/app/data
    depends_on:
      db:
        condition: service_healthy
    networks:
      - oneorg-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # ---------------------------------------------------------------------------
  # Database Service
  # ---------------------------------------------------------------------------
  db:
    image: postgres:16-alpine
    container_name: oneorg-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: oneorg
      POSTGRES_PASSWORD: oneorg
      POSTGRES_DB: oneorg
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - oneorg-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U oneorg -d oneorg"]
      interval: 10s
      timeout: 5s
      retries: 5

# -----------------------------------------------------------------------------
# Networks
# -----------------------------------------------------------------------------
networks:
  oneorg-network:
    driver: bridge

# -----------------------------------------------------------------------------
# Volumes
# -----------------------------------------------------------------------------
volumes:
  pgdata:
    driver: local
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt docker-compose.yml
git commit -m "feat: add Docker Compose for production with PostgreSQL"
```

### Task 4.2: Create Development Docker Compose

- [ ] **Step 1: Create docker-compose.dev.yml**

```yaml
# =============================================================================
# OneEmployeeOrg Academy - Development Docker Compose
# Overrides production compose for local development
# =============================================================================

version: "3.11"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: oneorg-app-dev
    volumes:
      # Mount source code for hot reload
      - ./src:/app/src:ro
      # Persist data
      - ./data:/app/data
    environment:
      - DATABASE_URL=postgresql+asyncpg://oneorg:oneorg@db:5432/oneorg
      - SECRET_KEY=dev-secret-not-for-production
      - DEBUG=true
    command: ["uvicorn", "oneorg.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]

  db:
    ports:
      # Expose PostgreSQL for local development tools
      - "5432:5432"
```

- [ ] **Step 2: Commit**

```bash
git add docker-compose.dev.yml
git commit -m "feat: add Docker Compose for development with hot reload"
```

---

## Chunk 5: Integration and Testing

### Task 5.1: Update Package Exports

- [ ] **Step 1: Update src/oneorg/__init__.py**

```python
from oneorg.config import get_settings, Settings

__version__ = "2.0.0"
__all__ = ["get_settings", "Settings"]
```

- [ ] **Step 2: Commit**

```bash
git add src/oneorg/__init__.py
git commit -m "chore: export config from package root"
```

### Task 5.2: Test Docker Build

- [ ] **Step 1: Build production image**

```bash
docker build -t oneorg:prod -f Dockerfile .
```

Expected: Build succeeds

- [ ] **Step 2: Build development image**

```bash
docker build -t oneorg:dev -f Dockerfile.dev .
```

Expected: Build succeeds

- [ ] **Step 3: Commit any fixes**

If builds fail, fix and commit.

### Task 5.3: Test Docker Compose

- [ ] **Step 1: Create .env file**

```bash
cp .env.example .env
# Edit .env and set a secure SECRET_KEY
```

- [ ] **Step 2: Test production compose**

```bash
docker compose up --build -d
sleep 10  # Wait for startup
curl http://localhost:8000/api/health
docker compose down
```

Expected: Health check returns `{"status": "healthy"}`

- [ ] **Step 3: Test development compose**

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
curl http://localhost:8000/api/health
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

Expected: Health check passes

- [ ] **Step 4: Test database connectivity**

```bash
docker compose up -d db
# Wait for DB to be ready
docker compose exec db psql -U oneorg -d oneorg -c "SELECT 1"
docker compose down
```

Expected: Returns `1`

- [ ] **Step 5: Commit fixes**

```bash
git add .
git commit -m "fix: Docker build and compose configuration"
```

### Task 5.4: Run All Tests

- [ ] **Step 1: Run test suite**

```bash
pytest tests/ -v
```

Expected: All tests pass (14+ tests)

- [ ] **Step 2: Final commit**

```bash
git add .
git commit -m "feat: complete Docker implementation with PostgreSQL"
```

---

## Usage Guide

After implementation, users can:

```bash
# Development (hot reload, exposed PostgreSQL)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production
docker compose up --build -d

# View logs
docker compose logs -f app

# Stop
docker compose down

# Reset database (⚠️ deletes all data)
docker compose down -v
```

---

## Summary of Changes

| Category | Files | Changes |
|----------|-------|---------|
| **New** | `src/oneorg/config.py` | Pydantic settings |
| **New** | `Dockerfile` | Multi-stage production |
| **New** | `Dockerfile.dev` | Development with hot reload |
| **New** | `docker-compose.yml` | Production orchestration |
| **New** | `docker-compose.dev.yml` | Development overrides |
| **New** | `.dockerignore` | Docker context exclusions |
| **New** | `.env.example` | Environment template |
| **New** | `tests/test_config.py` | Config tests |
| **Modified** | `src/oneorg/db/database.py` | Use settings |
| **Modified** | `src/oneorg/services/auth.py` | Use settings |
| **Modified** | `src/oneorg/__init__.py` | Export config |
| **Modified** | `requirements.txt` | Add asyncpg |

**Total:** 7 new files, 4 modified files
