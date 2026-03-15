# MVP Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development to implement this plan.

**Goal:** Build a core edu-tainment platform with student accounts, quests, XP tracking, and web UI.

**Architecture:** SQLite database + FastAPI + HTMX frontend. Replace JSON persistence with SQLAlchemy. Minimal auth (email/password, sessions).

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, HTMX, Jinja2, bcrypt, pytest

---

## File Structure

```
src/oneorg/
├── __init__.py
├── cli.py (modify)
├── api/
│   ├── __init__.py
│   ├── main.py (modify)
│   ├── dependencies.py (modify)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py (new)
│   │   ├── students.py (new)
│   │   ├── quests.py (new)
│   │   └── ui.py (new)
│   └── templates/
│       ├── base.html (new)
│       ├── dashboard.html (new)
│       ├── login.html (new)
│       ├── quests.html (new)
│       └── profile.html (new)
├── db/
│   ├── __init__.py
│   ├── database.py (new)
│   ├── models.py (new)
│   └── init_db.py (new)
├── services/
│   ├── __init__.py
│   ├── auth.py (new)
│   ├── quest_engine.py (new)
│   └── gamification.py (new)
└── models/ (existing - will replace with DB models)

data/
└── oneorg.db (new SQLite file)

tests/
├── test_auth.py (new)
├── test_quests.py (new)
└── test_api.py (new)
```

---

## Chunk 1: Database Foundation

**Files:**
- Create: `src/oneorg/db/database.py`
- Create: `src/oneorg/db/models.py`
- Create: `src/oneorg/db/init_db.py`
- Modify: `pyproject.toml` (add dependencies)
- Modify: `requirements.txt`

### Task 1.1: Add Dependencies

- [ ] **Step 1: Update pyproject.toml**

Add to `[project]` dependencies section:
```toml
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
    "rich>=13.0.0",
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "jinja2>=3.1.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.19.0",
    "python-multipart>=0.0.6",
    "bcrypt>=4.0.0",
    "python-jose[cryptography]>=3.3.0",
]
```

- [ ] **Step 2: Update requirements.txt**

```text
click>=8.1.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0
rich>=13.0.0
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
jinja2>=3.1.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
python-multipart>=0.0.6
bcrypt>=4.0.0
python-jose[cryptography]>=3.3.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -e .`

Expected: All packages install successfully

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml requirements.txt
git commit -m "chore: add SQLAlchemy, auth, and async SQLite dependencies"
```

### Task 1.2: Create Database Engine

- [ ] **Step 1: Create src/oneorg/db/database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'oneorg.db'}"

engine = create_async_engine(
    DATABASE_URL,
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

- [ ] **Step 2: Write test for database connection**

Create `tests/test_db.py`:
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from oneorg.db.database import engine, get_db

@pytest.mark.asyncio
async def test_database_connection():
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_get_db_yields_session():
    async for session in get_db():
        assert isinstance(session, AsyncSession)
        break
```

- [ ] **Step 3: Run test to verify database setup**

Run: `pytest tests/test_db.py -v`

Expected: 2 tests pass

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/db/database.py tests/test_db.py
git commit -m "feat: add async SQLite database engine with aiosqlite"
```

### Task 1.3: Create Database Models

- [ ] **Step 1: Create src/oneorg/db/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from oneorg.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    student_id = Column(String, unique=True, index=True)  # public-facing ID
    name = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    current_quest_id = Column(Integer, ForeignKey("quests.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="student")
    completions = relationship("QuestCompletion", back_populates="student")
    badges = relationship("StudentBadge", back_populates="student")

class Quest(Base):
    __tablename__ = "quests"
    
    id = Column(Integer, primary_key=True, index=True)
    quest_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    xp_reward = Column(Integer, default=100)
    difficulty = Column(Integer, default=1)  # 1-5
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    completions = relationship("QuestCompletion", back_populates="quest")

class QuestCompletion(Base):
    __tablename__ = "quest_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    quest_id = Column(Integer, ForeignKey("quests.id"))
    score = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)
    feedback = Column(Text)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="completions")
    quest = relationship("Quest", back_populates="completions")

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    badge_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String, default="🏆")
    criteria = Column(Text)  # JSON string for criteria
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student_badges = relationship("StudentBadge", back_populates="badge")

class StudentBadge(Base):
    __tablename__ = "student_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="badges")
    badge = relationship("Badge", back_populates="student_badges")
```

- [ ] **Step 2: Create database initialization script**

Create `src/oneorg/db/init_db.py`:
```python
import asyncio
from oneorg.db.database import engine, Base
from oneorg.db.models import User, Student, Quest, QuestCompletion, Badge, StudentBadge

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

async def seed_quests():
    from oneorg.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Check if quests already exist
        from sqlalchemy import select
        result = await session.execute(select(Quest).limit(1))
        if result.scalar():
            print("Quests already seeded")
            return
        
        sample_quests = [
            Quest(
                quest_id="intro_welcome",
                title="Welcome to the Academy",
                description="Complete your first quest and learn how the platform works.",
                xp_reward=50,
                difficulty=1,
                category="onboarding"
            ),
            Quest(
                quest_id="math_addition",
                title="Addition Explorer",
                description="Master basic addition with fun challenges.",
                xp_reward=100,
                difficulty=2,
                category="math"
            ),
            Quest(
                quest_id="sci_lab",
                title="Virtual Lab Assistant",
                description="Help clean up the science lab and learn about lab safety.",
                xp_reward=75,
                difficulty=1,
                category="science"
            ),
        ]
        
        for quest in sample_quests:
            session.add(quest)
        
        await session.commit()
        print(f"Seeded {len(sample_quests)} quests")

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_quests())
```

- [ ] **Step 3: Test models**

Create `tests/test_models.py`:
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from oneorg.db.models import User, Student, Quest
from oneorg.db.database import AsyncSessionLocal, init_db

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncSessionLocal() as session:
        user = User(email="test@example.com", hashed_password="hashed")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_student():
    async with AsyncSessionLocal() as session:
        user = User(email="student@example.com", hashed_password="hashed")
        session.add(user)
        await session.flush()
        
        student = Student(
            user_id=user.id,
            student_id="stu_001",
            name="Test Student",
            grade_level=5
        )
        session.add(student)
        await session.commit()
        
        assert student.id is not None
        assert student.name == "Test Student"
```

- [ ] **Step 4: Run database init and tests**

```bash
python -m oneorg.db.init_db
pytest tests/test_models.py -v
```

Expected: Database created, 2 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/oneorg/db/
git commit -m "feat: add SQLAlchemy models for users, students, quests, completions, badges"
```

---

## Chunk 2: Authentication System

**Files:**
- Create: `src/oneorg/services/auth.py`
- Create: `src/oneorg/api/routes/auth.py`
- Create: `tests/test_auth.py`

### Task 2.1: Create Auth Service

- [ ] **Step 1: Create src/oneorg/services/auth.py**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from oneorg.db.models import User, Student

SECRET_KEY = "your-secret-key-change-in-production"  # Use env var in prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

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
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(db: AsyncSession, token: str) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    return result.scalar()
```

- [ ] **Step 2: Write auth service tests**

Add to `tests/test_auth.py`:
```python
import pytest
from oneorg.services.auth import (
    get_password_hash, verify_password, create_user,
    authenticate_user, create_access_token, get_current_user
)
from oneorg.db.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_password_hashing():
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

@pytest.mark.asyncio
async def test_create_and_authenticate_user():
    async with AsyncSessionLocal() as session:
        email = "auth_test@example.com"
        password = "testpass123"
        
        # Create user
        user = await create_user(session, email, password)
        assert user.email == email
        
        # Authenticate
        auth_user = await authenticate_user(session, email, password)
        assert auth_user is not None
        assert auth_user.email == email
        
        # Wrong password
        wrong_auth = await authenticate_user(session, email, "wrong")
        assert wrong_auth is None

@pytest.mark.asyncio
async def test_access_token():
    token = create_access_token({"sub": "123"})
    assert isinstance(token, str)
    
    async with AsyncSessionLocal() as session:
        user = await get_current_user(session, token)
        # Will be None because user 123 doesn't exist, but no error
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_auth.py -v`

Expected: 3 tests pass

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/services/auth.py tests/test_auth.py
git commit -m "feat: add authentication service with bcrypt and JWT"
```

### Task 2.2: Create Auth Routes

- [ ] **Step 1: Create src/oneorg/api/routes/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from oneorg.db.database import get_db
from oneorg.services.auth import (
    create_user, authenticate_user, create_access_token, get_current_user
)

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    grade_level: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/register", response_model=dict)
async def register_api(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """API endpoint for registration."""
    from sqlalchemy import select
    from oneorg.db.models import User
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = await create_user(db, data.email, data.password)
    
    # Create student profile
    from oneorg.db.models import Student
    import uuid
    student = Student(
        user_id=user.id,
        student_id=f"stu_{uuid.uuid4().hex[:8]}",
        name=data.name,
        grade_level=data.grade_level
    )
    db.add(student)
    await db.commit()
    
    return {"message": "User created successfully", "student_id": student.student_id}

@router.post("/api/auth/login")
async def login_api(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """API endpoint for login, returns token."""
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/register")
async def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    grade_level: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Form handler for registration."""
    from sqlalchemy import select
    from oneorg.db.models import User, Student
    import uuid
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar():
        return RedirectResponse("/register?error=email_exists", status_code=302)
    
    # Create user
    user = await create_user(db, email, password)
    
    # Create student
    student = Student(
        user_id=user.id,
        student_id=f"stu_{uuid.uuid4().hex[:8]}",
        name=name,
        grade_level=grade_level
    )
    db.add(student)
    await db.commit()
    
    # Login and redirect
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=604800)
    return response

@router.post("/auth/login")
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Form handler for login."""
    user = await authenticate_user(db, email, password)
    if not user:
        return RedirectResponse("/login?error=invalid", status_code=302)
    
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=604800)
    return response

@router.get("/auth/logout")
async def logout():
    """Logout and clear session."""
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("access_token")
    return response
```

- [ ] **Step 2: Test auth routes**

Add to `tests/test_auth.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from oneorg.api.main import app

@pytest.mark.asyncio
async def test_register_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/auth/register", json={
            "email": "route_test@example.com",
            "password": "testpass123",
            "name": "Test User",
            "grade_level": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert "student_id" in data

@pytest.mark.asyncio
async def test_login_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First register
        await client.post("/api/auth/register", json={
            "email": "login_test@example.com",
            "password": "testpass123",
            "name": "Login Test",
            "grade_level": 6
        })
        
        # Then login
        response = await client.post("/api/auth/login", json={
            "email": "login_test@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_auth.py -v`

Expected: 5 tests pass

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/api/routes/auth.py
git commit -m "feat: add auth routes for API and form-based auth"
```

---

## Chunk 3: Quest System

**Files:**
- Create: `src/oneorg/services/quest_engine.py`
- Create: `src/oneorg/api/routes/quests.py`
- Create: `tests/test_quests.py`

### Task 3.1: Create Quest Engine

- [ ] **Step 1: Create src/oneorg/services/quest_engine.py**

```python
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from oneorg.db.models import Quest, QuestCompletion, Student, StudentBadge, Badge

async def get_available_quests(db: AsyncSession, student_id: int) -> List[Quest]:
    """Get quests not yet completed by student."""
    # Get completed quest IDs
    result = await db.execute(
        select(QuestCompletion.quest_id)
        .where(QuestCompletion.student_id == student_id)
    )
    completed_ids = {row[0] for row in result.all()}
    
    # Get available quests
    result = await db.execute(
        select(Quest)
        .where(and_(
            Quest.is_active == True,
            ~Quest.id.in_(completed_ids) if completed_ids else True
        ))
    )
    return result.scalars().all()

async def get_quest(db: AsyncSession, quest_id: str) -> Optional[Quest]:
    """Get quest by ID."""
    result = await db.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    return result.scalar()

async def complete_quest(
    db: AsyncSession,
    student_id: int,
    quest_id: int,
    score: float = 1.0,
    feedback: Optional[str] = None
) -> dict:
    """Complete a quest and award XP."""
    # Get quest
    result = await db.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar()
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Check if already completed
    result = await db.execute(
        select(QuestCompletion)
        .where(and_(
            QuestCompletion.student_id == student_id,
            QuestCompletion.quest_id == quest_id
        ))
    )
    if result.scalar():
        raise ValueError("Quest already completed")
    
    # Create completion
    xp_earned = int(quest.xp_reward * score)
    completion = QuestCompletion(
        student_id=student_id,
        quest_id=quest_id,
        score=score,
        xp_earned=xp_earned,
        feedback=feedback
    )
    db.add(completion)
    
    # Update student XP
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar()
    student.xp += xp_earned
    student.updated_at = datetime.utcnow()
    
    # Update streak
    today = datetime.utcnow().date()
    if student.last_activity_date:
        last_date = student.last_activity_date.date() if isinstance(student.last_activity_date, datetime) else student.last_activity_date
        if last_date == today - timedelta(days=1):
            student.current_streak += 1
        elif last_date != today:
            student.current_streak = 1
    else:
        student.current_streak = 1
    
    student.last_activity_date = datetime.utcnow()
    student.longest_streak = max(student.longest_streak, student.current_streak)
    
    await db.commit()
    
    return {
        "xp_earned": xp_earned,
        "total_xp": student.xp,
        "level": (student.xp // 500) + 1,
        "streak": student.current_streak
    }

async def get_student_progress(db: AsyncSession, student_id: int) -> dict:
    """Get comprehensive progress for a student."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    if not student:
        raise ValueError("Student not found")
    
    # Get completions with quest info
    result = await db.execute(
        select(QuestCompletion, Quest)
        .join(Quest, QuestCompletion.quest_id == Quest.id)
        .where(QuestCompletion.student_id == student_id)
        .order_by(QuestCompletion.completed_at.desc())
    )
    completions = result.all()
    
    # Get badges
    result = await db.execute(
        select(StudentBadge, Badge)
        .join(Badge, StudentBadge.badge_id == Badge.id)
        .where(StudentBadge.student_id == student_id)
    )
    badges = result.all()
    
    level = (student.xp // 500) + 1
    xp_to_next = 500 - (student.xp % 500)
    
    return {
        "student_id": student.student_id,
        "name": student.name,
        "grade": student.grade_level,
        "xp": student.xp,
        "level": level,
        "xp_to_next": xp_to_next,
        "streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "quests_completed": len(completions),
        "recent_completions": [
            {
                "quest_title": quest.title,
                "xp": completion.xp_earned,
                "date": completion.completed_at.isoformat()
            }
            for completion, quest in completions[:5]
        ],
        "badges": [
            {"name": badge.name, "icon": badge.icon}
            for _, badge in badges
        ]
    }
```

- [ ] **Step 2: Write quest engine tests**

Create `tests/test_quests.py`:
```python
import pytest
from oneorg.services.quest_engine import (
    get_available_quests, get_quest, complete_quest, get_student_progress
)
from oneorg.db.database import AsyncSessionLocal
from oneorg.db.models import Quest, Student, User
from oneorg.services.auth import create_user

@pytest.mark.asyncio
async def test_get_available_quests():
    async with AsyncSessionLocal() as session:
        # Get first student and quest
        from sqlalchemy import select
        result = await session.execute(select(Student))
        student = result.scalar()
        
        quests = await get_available_quests(session, student.id)
        assert isinstance(quests, list)

@pytest.mark.asyncio
async def test_complete_quest():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        
        # Get student and quest
        result = await session.execute(select(Student))
        student = result.scalar()
        
        result = await session.execute(select(Quest))
        quest = result.scalar()
        
        initial_xp = student.xp
        
        result = await complete_quest(session, student.id, quest.id, score=0.9)
        
        assert result["xp_earned"] > 0
        assert result["total_xp"] > initial_xp
        assert "level" in result
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_quests.py -v`

Expected: Tests pass (may need data seeded)

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/services/quest_engine.py tests/test_quests.py
git commit -m "feat: add quest engine with completion and progress tracking"
```

### Task 3.2: Create Quest Routes

- [ ] **Step 1: Create src/oneorg/api/routes/quests.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from oneorg.db.database import get_db
from oneorg.services.quest_engine import (
    get_available_quests, get_quest, complete_quest, get_student_progress
)
from oneorg.services.auth import get_current_user

router = APIRouter()

async def get_current_student_id(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current student ID from session cookie."""
    from sqlalchemy import select
    from oneorg.db.models import Student
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return student.id

@router.get("/api/quests")
async def list_quests(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """List available quests for current student."""
    quests = await get_available_quests(db, student_id)
    return {
        "quests": [
            {
                "id": q.quest_id,
                "title": q.title,
                "description": q.description,
                "xp_reward": q.xp_reward,
                "difficulty": q.difficulty,
                "category": q.category
            }
            for q in quests
        ]
    }

@router.get("/api/quests/{quest_id}")
async def get_quest_detail(
    quest_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get quest details."""
    quest = await get_quest(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    return {
        "id": quest.quest_id,
        "title": quest.title,
        "description": quest.description,
        "xp_reward": quest.xp_reward,
        "difficulty": quest.difficulty,
        "category": quest.category
    }

@router.post("/api/quests/{quest_id}/complete")
async def complete_quest_api(
    quest_id: str,
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Complete a quest via API."""
    from sqlalchemy import select
    from oneorg.db.models import Quest
    
    result = await db.execute(select(Quest).where(Quest.quest_id == quest_id))
    quest = result.scalar()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    try:
        result = await complete_quest(db, student_id, quest.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/progress")
async def get_progress_api(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Get student progress."""
    progress = await get_student_progress(db, student_id)
    return progress

@router.post("/quests/{quest_id}/complete")
async def complete_quest_form(
    quest_id: str,
    request: Request,
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Complete quest via form submission."""
    from sqlalchemy import select
    from oneorg.db.models import Quest
    
    result = await db.execute(select(Quest).where(Quest.quest_id == quest_id))
    quest = result.scalar()
    if not quest:
        return RedirectResponse("/quests?error=not_found", status_code=302)
    
    try:
        await complete_quest(db, student_id, quest.id)
        return RedirectResponse("/dashboard?success=quest_completed", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/quests/{quest_id}?error={str(e)}", status_code=302)
```

- [ ] **Step 2: Commit**

```bash
git add src/oneorg/api/routes/quests.py
git commit -m "feat: add quest routes for listing, viewing, and completing quests"
```

---

## Chunk 4: UI Templates

**Files:**
- Create: `src/oneorg/api/templates/*.html`
- Create: `src/oneorg/api/routes/ui.py`

### Task 4.1: Create Base Template

- [ ] **Step 1: Create src/oneorg/api/templates/base.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OneEmployeeOrg Academy{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            color: white;
        }
        .nav {
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 20px;
            background: rgba(255,255,255,0.2);
            transition: background 0.3s;
        }
        .nav a:hover {
            background: rgba(255,255,255,0.3);
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .btn:hover { background: #5568d3; }
        .btn-secondary {
            background: #764ba2;
        }
        .btn-secondary:hover { background: #663d8f; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .stat {
            text-align: center;
            padding: 20px;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 8px;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add src/oneorg/api/templates/base.html
git commit -m "feat: add base HTML template with styling"
```

### Task 4.2: Create Login and Register Pages

- [ ] **Step 1: Create src/oneorg/api/templates/login.html**

```html
{% extends "base.html" %}

{% block title %}Login - OneEmployeeOrg Academy{% endblock %}

{% block content %}
<div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
    <div class="card" style="width: 100%; max-width: 400px;">
        <h1 style="text-align: center; margin-bottom: 24px; color: #667eea;">Welcome Back!</h1>
        
        {% if request.query_params.error == 'invalid' %}
        <div class="error">Invalid email or password. Please try again.</div>
        {% endif %}
        
        <form action="/auth/login" method="POST">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required placeholder="you@example.com">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter your password">
            </div>
            
            <button type="submit" class="btn" style="width: 100%;">Sign In</button>
        </form>
        
        <p style="text-align: center; margin-top: 20px;">
            Don't have an account? <a href="/register" style="color: #667eea;">Sign up</a>
        </p>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Create src/oneorg/api/templates/register.html**

```html
{% extends "base.html" %}

{% block title %}Register - OneEmployeeOrg Academy{% endblock %}

{% block content %}
<div class="container" style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
    <div class="card" style="width: 100%; max-width: 400px;">
        <h1 style="text-align: center; margin-bottom: 24px; color: #667eea;">Join the Academy!</h1>
        
        {% if request.query_params.error == 'email_exists' %}
        <div class="error">This email is already registered. <a href="/login">Sign in instead</a>?</div>
        {% endif %}
        
        <form action="/auth/register" method="POST">
            <div class="form-group">
                <label for="name">Your Name</label>
                <input type="text" id="name" name="name" required placeholder="Enter your name">
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required placeholder="you@example.com">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Create a password" minlength="8">
            </div>
            
            <div class="form-group">
                <label for="grade_level">Grade Level</label>
                <select id="grade_level" name="grade_level" required>
                    <option value="">Select your grade...</option>
                    {% for i in range(1, 13) %}
                    <option value="{{ i }}">Grade {{ i }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <button type="submit" class="btn" style="width: 100%;">Create Account</button>
        </form>
        
        <p style="text-align: center; margin-top: 20px;">
            Already have an account? <a href="/login" style="color: #667eea;">Sign in</a>
        </p>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 3: Commit**

```bash
git add src/oneorg/api/templates/login.html src/oneorg/api/templates/register.html
git commit -m "feat: add login and register page templates"
```

### Task 4.3: Create Dashboard and Quests Pages

- [ ] **Step 1: Create src/oneorg/api/templates/dashboard.html**

```html
{% extends "base.html" %}

{% block title %}Dashboard - OneEmployeeOrg Academy{% endblock %}

{% block content %}
<div class="container">
    <div class="header">
        <h1>Hello, {{ name }}! 👋</h1>
        <nav class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/quests">Quests</a>
            <a href="/profile">Profile</a>
            <a href="/auth/logout">Logout</a>
        </nav>
    </div>
    
    {% if request.query_params.success == 'quest_completed' %}
    <div class="success">🎉 Quest completed! XP earned!</div>
    {% endif %}
    
    <div class="grid">
        <div class="card">
            <div class="stat">
                <div class="stat-value">{{ level }}</div>
                <div class="stat-label">Level</div>
            </div>
        </div>
        
        <div class="card">
            <div class="stat">
                <div class="stat-value">{{ xp }}</div>
                <div class="stat-label">Total XP</div>
            </div>
        </div>
        
        <div class="card">
            <div class="stat">
                <div class="stat-value">{{ xp_to_next }}</div>
                <div class="stat-label">XP to Next Level</div>
            </div>
        </div>
        
        <div class="card">
            <div class="stat">
                <div class="stat-value">{{ streak }} 🔥</div>
                <div class="stat-label">Day Streak</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2 style="margin-bottom: 16px;">Recent Quests</h2>
        {% if recent_completions %}
        <div style="display: flex; flex-direction: column; gap: 12px;">
            {% for completion in recent_completions %}
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #f5f5f5; border-radius: 8px;">
                <span>{{ completion.quest_title }}</span>
                <span style="color: #667eea; font-weight: bold;">+{{ completion.xp }} XP</span>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p style="color: #666;">No quests completed yet. <a href="/quests" style="color: #667eea;">Start your first quest!</a></p>
        {% endif %}
    </div>
    
    {% if badges %}
    <div class="card">
        <h2 style="margin-bottom: 16px;">Badges</h2>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            {% for badge in badges %}
            <div style="text-align: center; padding: 16px; background: #f5f5f5; border-radius: 12px;">
                <div style="font-size: 2em;">{{ badge.icon }}</div>
                <div style="font-weight: bold; margin-top: 8px;">{{ badge.name }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 2: Create src/oneorg/api/templates/quests.html**

```html
{% extends "base.html" %}

{% block title %}Quests - OneEmployeeOrg Academy{% endblock %}

{% block content %}
<div class="container">
    <div class="header">
        <h1>Available Quests 🗺️</h1>
        <nav class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/quests">Quests</a>
            <a href="/profile">Profile</a>
            <a href="/auth/logout">Logout</a>
        </nav>
    </div>
    
    {% if request.query_params.error == 'not_found' %}
    <div class="error">Quest not found.</div>
    {% endif %}
    
    <div class="grid">
        {% for quest in quests %}
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <h3 style="color: #667eea;">{{ quest.title }}</h3>
                <span style="background: #667eea; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px;">{{ quest.category }}</span>
            </div>
            
            <p style="color: #666; margin-bottom: 16px;">{{ quest.description }}</p>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span>⭐ Difficulty: {{ quest.difficulty }}/5</span>
                <span style="color: #667eea; font-weight: bold;">🏆 {{ quest.xp_reward }} XP</span>
            </div>
            
            <a href="/quests/{{ quest.id }}" class="btn" style="width: 100%; text-align: center;">Start Quest</a>
        </div>
        {% endfor %}
    </div>
    
    {% if not quests %}
    <div class="card" style="text-align: center; padding: 48px;">
        <p style="font-size: 1.2em; color: #666;">No quests available right now. Check back later!</p>
    </div>
    {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 3: Create src/oneorg/api/templates/quest_detail.html**

```html
{% extends "base.html" %}

{% block title %}{{ quest.title }} - OneEmployeeOrg Academy{% endblock %}

{% block content %}
<div class="container">
    <div class="header">
        <h1>{{ quest.title }}</h1>
        <nav class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/quests">Quests</a>
            <a href="/profile">Profile</a>
            <a href="/auth/logout">Logout</a>
        </nav>
    </div>
    
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
            <span style="background: #667eea; color: white; padding: 4px 12px; border-radius: 12px; font-size: 14px;">{{ quest.category }}</span>
            <span style="color: #667eea; font-weight: bold; font-size: 1.2em;">🏆 {{ quest.xp_reward }} XP</span>
        </div>
        
        <p style="font-size: 1.1em; margin-bottom: 24px; line-height: 1.6;">{{ quest.description }}</p>
        
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
            <h4 style="margin-bottom: 12px;">Quest Details:</h4>
            <ul style="margin-left: 20px; color: #666;">
                <li>Difficulty: {{ quest.difficulty }} out of 5</li>
                <li>Reward: {{ quest.xp_reward }} experience points</li>
                <li>Type: {{ quest.category.title() }}</li>
            </ul>
        </div>
        
        <form action="/quests/{{ quest.id }}/complete" method="POST">
            <button type="submit" class="btn" style="width: 100%; font-size: 1.2em;">
                ✅ Complete Quest
            </button>
        </form>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add src/oneorg/api/templates/dashboard.html src/oneorg/api/templates/quests.html src/oneorg/api/templates/quest_detail.html
git commit -m "feat: add dashboard and quest templates"
```

### Task 4.4: Create UI Routes

- [ ] **Step 1: Create src/oneorg/api/routes/ui.py**

```python
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from oneorg.db.database import get_db
from oneorg.services.auth import get_current_user
from oneorg.services.quest_engine import get_available_quests, get_quest, get_student_progress

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

async def require_auth(request: Request, db: AsyncSession = Depends(get_db)):
    """Require authentication, return student info."""
    from sqlalchemy import select
    from oneorg.db.models import Student
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return student

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to dashboard if logged in, otherwise login."""
    if request.cookies.get("access_token"):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Student dashboard."""
    progress = await get_student_progress(db, student.id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        **progress
    })

@router.get("/quests", response_class=HTMLResponse)
async def quests_list(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """List available quests."""
    available = await get_available_quests(db, student.id)
    return templates.TemplateResponse("quests.html", {
        "request": request,
        "quests": [{"id": q.quest_id, **q.__dict__} for q in available]
    })

@router.get("/quests/{quest_id}", response_class=HTMLResponse)
async def quest_detail(request: Request, quest_id: str, db: AsyncSession = Depends(get_db)):
    """Quest detail page."""
    quest = await get_quest(db, quest_id)
    if not quest:
        return RedirectResponse("/quests?error=not_found", status_code=302)
    
    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": {
            "id": quest.quest_id,
            "title": quest.title,
            "description": quest.description,
            "xp_reward": quest.xp_reward,
            "difficulty": quest.difficulty,
            "category": quest.category
        }
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Profile page (redirects to dashboard for now)."""
    return RedirectResponse("/dashboard", status_code=302)
```

- [ ] **Step 2: Commit**

```bash
git add src/oneorg/api/routes/ui.py
git commit -m "feat: add UI routes for all pages"
```

---

## Chunk 5: Wire Everything Together

**Files:**
- Modify: `src/oneorg/api/main.py`
- Modify: `src/oneorg/db/__init__.py`

### Task 5.1: Update Main API File

- [ ] **Step 1: Modify src/oneorg/api/main.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from oneorg.api.routes import auth, quests, ui

app = FastAPI(
    title="OneEmployeeOrg Academy",
    description="Edu-tainment platform for K-12 students",
    version="2.0.0",
)

# Include routers
app.include_router(auth.router)
app.include_router(quests.router)
app.include_router(ui.router)

# Static files (for future use)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    from oneorg.db.database import engine, Base
    from oneorg.db.models import User, Student, Quest, QuestCompletion, Badge, StudentBadge
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed quests if needed
    from oneorg.db.database import AsyncSessionLocal
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Quest).limit(1))
        if not result.scalar():
            sample_quests = [
                Quest(
                    quest_id="intro_welcome",
                    title="Welcome to the Academy",
                    description="Complete your first quest and learn how the platform works.",
                    xp_reward=50,
                    difficulty=1,
                    category="onboarding"
                ),
                Quest(
                    quest_id="math_addition",
                    title="Addition Explorer",
                    description="Master basic addition with fun challenges.",
                    xp_reward=100,
                    difficulty=2,
                    category="math"
                ),
                Quest(
                    quest_id="sci_lab",
                    title="Virtual Lab Assistant",
                    description="Help clean up the science lab and learn about lab safety.",
                    xp_reward=75,
                    difficulty=1,
                    category="science"
                ),
            ]
            for quest in sample_quests:
                session.add(quest)
            await session.commit()
            print("Seeded sample quests")
```

- [ ] **Step 2: Update src/oneorg/db/__init__.py**

```python
from oneorg.db.database import Base, engine, get_db, AsyncSessionLocal
from oneorg.db.models import User, Student, Quest, QuestCompletion, Badge, StudentBadge

__all__ = [
    "Base",
    "engine",
    "get_db",
    "AsyncSessionLocal",
    "User",
    "Student",
    "Quest",
    "QuestCompletion",
    "Badge",
    "StudentBadge",
]
```

- [ ] **Step 3: Create src/oneorg/services/__init__.py**

```python
from oneorg.services.auth import (
    create_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
)
from oneorg.services.quest_engine import (
    get_available_quests,
    get_quest,
    complete_quest,
    get_student_progress,
)

__all__ = [
    "create_user",
    "authenticate_user",
    "create_access_token",
    "get_current_user",
    "verify_password",
    "get_password_hash",
    "get_available_quests",
    "get_quest",
    "complete_quest",
    "get_student_progress",
]
```

- [ ] **Step 4: Create src/oneorg/api/routes/__init__.py**

```python
from oneorg.api.routes import auth, quests, ui

__all__ = ["auth", "quests", "ui"]
```

- [ ] **Step 5: Integration test**

Create `tests/test_api.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from oneorg.api.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_login_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/login")
        assert response.status_code == 200
        assert "Sign In" in response.text
```

Run: `pytest tests/test_api.py -v`

Expected: 2 tests pass

- [ ] **Step 6: Commit**

```bash
git add src/oneorg/api/main.py src/oneorg/db/__init__.py src/oneorg/services/__init__.py src/oneorg/api/routes/__init__.py tests/test_api.py
git commit -m "feat: wire all routes together and add startup database initialization"
```

---

## Final Verification

### Task 6.1: Run All Tests

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v
```

Expected: All tests pass

### Task 6.2: Manual Smoke Test

- [ ] **Step 1: Start the server**

```bash
uvicorn oneorg.api.main:app --reload
```

- [ ] **Step 2: Test in browser**

1. Visit http://localhost:8000 - should redirect to login
2. Visit http://localhost:8000/register - should show registration form
3. Register a test user
4. Should redirect to dashboard with stats
5. Visit http://localhost:8000/quests - should show available quests
6. Click on a quest - should show quest detail
7. Complete quest - should return to dashboard with updated XP

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "feat: complete MVP with auth, quests, and UI"
```

---

## Summary

This plan creates a complete MVP with:
- **Database**: SQLite with SQLAlchemy async, all models migrated from JSON
- **Auth**: Email/password with bcrypt, JWT tokens, session cookies
- **Quests**: Database-stored quests, completion tracking, XP awards
- **Progress**: Level calculation, streaks, badges, completion history
- **UI**: HTMX + Jinja2 templates, responsive design, full page flow

**Independent domains for parallel execution:**
1. Chunk 1: Database (models + engine)
2. Chunk 2: Auth (service + routes)
3. Chunk 3: Quest system (engine + routes)
4. Chunk 4: UI (templates + routes)
5. Chunk 5: Integration (wiring + tests)
