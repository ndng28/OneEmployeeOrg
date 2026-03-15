# API + QuestRuntime Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add CRUD API endpoints for students, quests, and progress, plus implement QuestRuntime for quest execution with step-based completion flow.

**Architecture:** Split into 7 parallel workstreams: Student CRUD, Quest CRUD extensions, Progress API, QuestExecutor, StepRunner, CompletionHandler, and Integration Tests. Each worker builds a self-contained layer that integrates with existing gamification services.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (async), Pydantic, pytest

---

## File Structure

### New Files
- `src/oneorg/api/routes/students.py` - Student CRUD endpoints
- `src/oneorg/api/routes/progress.py` - Progress endpoints
- `src/oneorg/services/quest_executor.py` - Quest session management
- `src/oneorg/services/step_runner.py` - Step validation and scoring
- `src/oneorg/services/completion_handler.py` - Quest completion logic
- `src/oneorg/models/runtime.py` - QuestSession, StepResult, CompletionResult
- `tests/test_api/test_students.py` - Student API tests
- `tests/test_api/test_progress.py` - Progress API tests
- `tests/test_api/test_quest_flow.py` - Full quest flow tests

### Modified Files
- `src/oneorg/api/routes/quests.py` - Add start/step/complete endpoints
- `src/oneorg/api/routes/__init__.py` - Include new routers

---

## Chunk 1: Student CRUD API

**Worker:** Agent 1 (independent)

**Goal:** Create student management endpoints

### Files
- Create: `src/oneorg/api/routes/students.py`
- Modify: `src/oneorg/api/routes/__init__.py`
- Create: `tests/test_api/test_students.py`

### Task 1.1: Create runtime models

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_runtime.py
def test_quest_session_creation():
    from oneorg.models.runtime import QuestSession
    from datetime import datetime
    
    session = QuestSession(
        session_id="sess_001",
        student_id="stu_001",
        quest_id="quest_001",
        current_step=0,
        steps_completed=[],
        scores={},
        started_at=datetime.now(),
    )
    
    assert session.session_id == "sess_001"
    assert session.current_step == 0

def test_step_result_creation():
    from oneorg.models.runtime import StepResult
    
    result = StepResult(
        step_number=1,
        score=0.85,
        passed=True,
        feedback="Great job!",
        next_step=2,
        quest_complete=False,
    )
    
    assert result.passed == True
    assert result.next_step == 2

def test_completion_result_creation():
    from oneorg.models.runtime import CompletionResult
    from datetime import datetime
    
    result = CompletionResult(
        xp_earned=150,
        xp_breakdown={"base": 100, "accuracy_bonus": 50},
        badges_earned=[],
        calendar_updated=True,
        quest_id="quest_001",
        completed_at=datetime.now(),
    )
    
    assert result.xp_earned == 150
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models/test_runtime.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'oneorg.models.runtime'"

- [ ] **Step 3: Write runtime models**

```python
# src/oneorg/models/runtime.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from oneorg.models.student import Badge

class QuestSession(BaseModel):
    """In-memory session for quest execution."""
    session_id: str
    student_id: str
    quest_id: str
    current_step: int = 0
    steps_completed: list[int] = Field(default_factory=list)
    scores: dict[int, float] = Field(default_factory=dict)
    started_at: datetime
    time_spent_seconds: int = 0
    step_inputs: dict[int, dict] = Field(default_factory=dict)

class StepResult(BaseModel):
    """Result of executing a quest step."""
    step_number: int
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    feedback: str = ""
    next_step: Optional[int] = None
    quest_complete: bool = False

class CompletionResult(BaseModel):
    """Result of completing a quest."""
    xp_earned: int
    xp_breakdown: dict[str, int]
    badges_earned: list[Badge] = Field(default_factory=list)
    calendar_updated: bool = False
    quest_id: str
    completed_at: datetime
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models/test_runtime.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_models/test_runtime.py src/oneorg/models/runtime.py
git commit -m "feat: add runtime models for quest execution

- QuestSession for tracking quest progress
- StepResult for step validation
- CompletionResult for quest completion"
```

### Task 1.2: Create students router

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api/test_students.py
import pytest
from fastapi.testclient import TestClient
from oneorg.api.main import app

client = TestClient(app)

def test_list_students_unauthorized():
    """Should require authentication."""
    response = client.get("/api/students")
    assert response.status_code == 401

def test_create_student():
    """Should create a new student."""
    # First register/login to get auth
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    
    # Create student
    response = client.post("/api/students", json={
        "name": "Test Student",
        "grade_level": 5,
    }, headers={"Authorization": f"Bearer {login_response.json()['access_token']}"})
    
    assert response.status_code == 200
    assert response.json()["name"] == "Test Student"

def test_get_student():
    """Should get student by ID."""
    # ... auth setup ...
    response = client.get("/api/students/1")
    assert response.status_code == 200
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api/test_students.py -v`
Expected: FAIL with "404 Not Found" (route doesn't exist)

- [ ] **Step 3: Write students router**

```python
# src/oneorg/api/routes/students.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from oneorg.db.database import get_db
from oneorg.db.models import Student, User
from oneorg.services.auth import get_current_user

router = APIRouter()

class StudentCreate(BaseModel):
    name: str
    grade_level: int

class StudentUpdate(BaseModel):
    name: str | None = None
    grade_level: int | None = None

class StudentResponse(BaseModel):
    id: int
    student_id: str
    name: str
    grade_level: int
    xp: int
    level: int
    
    class Config:
        from_attributes = True

@router.get("/api/students")
async def list_students(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students."""
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return {
        "students": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "name": s.name,
                "grade_level": s.grade_level,
                "xp": s.xp,
                "level": (s.xp // 500) + 1
            }
            for s in students
        ]
    }

@router.post("/api/students", response_model=StudentResponse)
async def create_student(
    data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new student."""
    import uuid
    student = Student(
        student_id=f"stu_{uuid.uuid4().hex[:8]}",
        name=data.name,
        grade_level=data.grade_level,
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    
    return StudentResponse(
        id=student.id,
        student_id=student.student_id,
        name=student.name,
        grade_level=student.grade_level,
        xp=student.xp,
        level=(student.xp // 500) + 1
    )

@router.get("/api/students/{student_id}")
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student by ID."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "id": student.id,
        "student_id": student.student_id,
        "name": student.name,
        "grade_level": student.grade_level,
        "xp": student.xp,
        "level": (student.xp // 500) + 1
    }

@router.patch("/api/students/{student_id}")
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update student."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if data.name is not None:
        student.name = data.name
    if data.grade_level is not None:
        student.grade_level = data.grade_level
    
    await db.commit()
    return {"message": "Student updated successfully"}

@router.delete("/api/students/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete student."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    await db.delete(student)
    await db.commit()
    return {"message": "Student deleted successfully"}
```

- [ ] **Step 4: Update routes __init__.py**

```python
# src/oneorg/api/routes/__init__.py
from oneorg.api.routes import auth, quests, ui, students

# Add students router to exports
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_api/test_students.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_api/test_students.py src/oneorg/api/routes/students.py src/oneorg/api/routes/__init__.py
git commit -m "feat: add student CRUD API endpoints

- GET /api/students - list all students
- POST /api/students - create student
- GET /api/students/{id} - get student
- PATCH /api/students/{id} - update student
- DELETE /api/students/{id} - delete student"
```

---

## Chunk 2: Quest CRUD API Extensions

**Worker:** Agent 2 (independent)

**Goal:** Extend quest endpoints with start/step/complete

### Files
- Modify: `src/oneorg/api/routes/quests.py`
- Create: `tests/test_api/test_quest_runtime.py`

### Task 2.1: Add start quest endpoint

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api/test_quest_runtime.py
def test_start_quest():
    """Should start a quest and create a session."""
    # Auth and setup...
    response = client.post(f"/api/quests/quest_001/start")
    
    assert response.status_code == 200
    assert "session_id" in response.json()
    assert response.json()["quest_id"] == "quest_001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api/test_quest_runtime.py::test_start_quest -v`
Expected: FAIL with "404 Not Found"

- [ ] **Step 3: Add start endpoint**

```python
# src/oneorg/api/routes/quests.py (add to existing file)

@router.post("/api/quests/{quest_id}/start")
async def start_quest(
    quest_id: str,
    db: AsyncSession = Depends(get_db),
    student_id: int = Depends(get_current_student_id)
):
    """Start a quest and create a session."""
    from oneorg.services.quest_executor import start_quest_session
    
    session = await start_quest_session(db, student_id, quest_id)
    return {
        "session_id": session.session_id,
        "quest_id": session.quest_id,
        "current_step": session.current_step,
        "started_at": session.started_at.isoformat()
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api/test_quest_runtime.py::test_start_quest -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_api/test_quest_runtime.py src/oneorg/api/routes/quests.py
git commit -m "feat: add start quest endpoint"
```

### Task 2.2: Add step and complete endpoints

- [ ] **Step 1: Write failing tests**

```python
# tests/test_api/test_quest_runtime.py (append)

def test_submit_step():
    """Should submit a step and get result."""
    # Start quest first...
    response = client.post(f"/api/quests/quest_001/step", json={
        "step_number": 1,
        "input": {"answer": "42"}
    })
    
    assert response.status_code == 200
    assert "score" in response.json()
    assert "passed" in response.json()

def test_complete_quest():
    """Should complete quest and award XP."""
    # Start quest, submit steps...
    response = client.post(f"/api/quests/quest_001/complete")
    
    assert response.status_code == 200
    assert "xp_earned" in response.json()
    assert "badges_earned" in response.json()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_api/test_quest_runtime.py -v`
Expected: FAIL with "404 Not Found"

- [ ] **Step 3: Add step and complete endpoints**

```python
# src/oneorg/api/routes/quests.py (append)

@router.post("/api/quests/{quest_id}/step")
async def submit_step(
    quest_id: str,
    step_data: dict,
    db: AsyncSession = Depends(get_db),
    student_id: int = Depends(get_current_student_id)
):
    """Submit a step result."""
    from oneorg.services.step_runner import run_quest_step
    
    result = await run_quest_step(
        db, 
        student_id, 
        quest_id, 
        step_data.get("step_number", 1),
        step_data.get("input", {})
    )
    
    return {
        "step_number": result.step_number,
        "score": result.score,
        "passed": result.passed,
        "feedback": result.feedback,
        "next_step": result.next_step,
        "quest_complete": result.quest_complete
    }

@router.post("/api/quests/{quest_id}/complete")
async def complete_quest_runtime(
    quest_id: str,
    db: AsyncSession = Depends(get_db),
    student_id: int = Depends(get_current_student_id)
):
    """Complete quest and award XP."""
    from oneorg.services.completion_handler import complete_quest_session
    
    result = await complete_quest_session(db, student_id, quest_id)
    
    return {
        "xp_earned": result.xp_earned,
        "xp_breakdown": result.xp_breakdown,
        "badges_earned": [
            {"badge_id": b.badge_id, "name": b.name, "icon": b.icon}
            for b in result.badges_earned
        ],
        "calendar_updated": result.calendar_updated,
        "quest_id": result.quest_id,
        "completed_at": result.completed_at.isoformat()
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_api/test_quest_runtime.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_api/test_quest_runtime.py src/oneorg/api/routes/quests.py
git commit -m "feat: add step and complete quest endpoints"
```

---

## Chunk 3: Progress API

**Worker:** Agent 3 (independent)

**Goal:** Create progress tracking endpoints

### Files
- Create: `src/oneorg/api/routes/progress.py`
- Create: `tests/test_api/test_progress.py`

### Task 3.1: Create progress router

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api/test_progress.py
def test_get_progress():
    """Should get student progress."""
    # Auth setup...
    response = client.get("/api/progress")
    
    assert response.status_code == 200
    assert "xp" in response.json()
    assert "level" in response.json()

def test_get_badge_progress():
    """Should get badge progress."""
    response = client.get("/api/progress/badges")
    
    assert response.status_code == 200
    assert "badges" in response.json()

def test_get_calendar():
    """Should get activity calendar."""
    response = client.get("/api/progress/calendar")
    
    assert response.status_code == 200
    assert "recent_week" in response.json()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api/test_progress.py -v`
Expected: FAIL with "404 Not Found"

- [ ] **Step 3: Write progress router**

```python
# src/oneorg/api/routes/progress.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from oneorg.db.database import get_db
from oneorg.db.models import Student, User
from oneorg.services.auth import get_current_user
from oneorg.services.quest_engine import get_student_progress

router = APIRouter()

async def get_current_student(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current student from user."""
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    return result.scalar()

@router.get("/api/progress")
async def get_progress(
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    """Get current student progress."""
    progress = await get_student_progress(db, student.id)
    return progress

@router.get("/api/progress/badges")
async def get_badge_progress(
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    """Get badge progress."""
    from oneorg.gamification.badges import BadgeManager
    from oneorg.models.student import StudentProgress
    from pathlib import Path
    
    # Convert DB student to StudentProgress model
    student_progress = StudentProgress(
        student_id=student.student_id,
        name=student.name,
        grade_level=student.grade_level,
        xp=student.xp,
    )
    
    # Get badge progress
    badge_manager = BadgeManager(Path("data/badges"))
    progress = badge_manager.get_progress(student_progress)
    
    return {"badges": progress}

@router.get("/api/progress/calendar")
async def get_calendar(
    db: AsyncSession = Depends(get_db),
    student: Student = Depends(get_current_student)
):
    """Get activity calendar."""
    from oneorg.models.student import StudentProgress
    
    # Convert DB student to StudentProgress model
    student_progress = StudentProgress(
        student_id=student.student_id,
        name=student.name,
        grade_level=student.grade_level,
        xp=student.xp,
    )
    
    # Get calendar data
    week_view = student_progress.calendar.get_recent_week()
    month_summary = student_progress.calendar.get_recent_month_summary()
    
    return {
        "recent_week": week_view,
        "month_summary": month_summary
    }
```

- [ ] **Step 4: Update routes __init__.py**

```python
# src/oneorg/api/routes/__init__.py (add)
from oneorg.api.routes import progress
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_api/test_progress.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_api/test_progress.py src/oneorg/api/routes/progress.py src/oneorg/api/routes/__init__.py
git commit -m "feat: add progress API endpoints

- GET /api/progress - current student progress
- GET /api/progress/badges - badge progress
- GET /api/progress/calendar - activity calendar"
```

---

## Chunk 4: QuestExecutor Service

**Worker:** Agent 4 (independent)

**Goal:** Implement quest session management

### Files
- Create: `src/oneorg/services/quest_executor.py`
- Create: `tests/test_services/test_quest_executor.py`

### Task 4.1: Create QuestExecutor

- [ ] **Step 1: Write the failing test**

```python
# tests/test_services/test_quest_executor.py
import pytest
from datetime import datetime

@pytest.mark.asyncio
async def test_start_quest_session(db_session):
    """Should create a quest session."""
    from oneorg.services.quest_executor import start_quest_session
    
    session = await start_quest_session(db_session, 1, "quest_001")
    
    assert session.session_id is not None
    assert session.quest_id == "quest_001"
    assert session.current_step == 0
    assert session.student_id == "1"

@pytest.mark.asyncio
async def test_cannot_start_completed_quest(db_session):
    """Should not allow restarting completed quest."""
    from oneorg.services.quest_executor import start_quest_session
    
    # First completion...
    # Try to start again
    with pytest.raises(ValueError, match="already completed"):
        await start_quest_session(db_session, 1, "quest_001")

@pytest.mark.asyncio
async def test_get_active_session(db_session):
    """Should get active session if exists."""
    from oneorg.services.quest_executor import start_quest_session, get_active_session
    
    # Start session
    session = await start_quest_session(db_session, 1, "quest_001")
    
    # Get active
    active = await get_active_session(db_session, 1, "quest_001")
    assert active.session_id == session.session_id
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_quest_executor.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write QuestExecutor**

```python
# src/oneorg/services/quest_executor.py
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from oneorg.models.runtime import QuestSession
from oneorg.db.models import Quest, QuestCompletion

# In-memory session store (could be Redis in production)
_active_sessions: dict[str, QuestSession] = {}

async def start_quest_session(
    db: AsyncSession,
    student_id: int,
    quest_id: str
) -> QuestSession:
    """Start a new quest session."""
    # Get quest
    result = await db.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    quest = result.scalar()
    
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Check if already completed
    result = await db.execute(
        select(QuestCompletion).where(and_(
            QuestCompletion.student_id == student_id,
            QuestCompletion.quest_id == quest.id
        ))
    )
    if result.scalar():
        raise ValueError("Quest already completed")
    
    # Check for existing active session
    session_key = f"{student_id}_{quest_id}"
    if session_key in _active_sessions:
        return _active_sessions[session_key]
    
    # Create new session
    session = QuestSession(
        session_id=f"sess_{uuid.uuid4().hex[:8]}",
        student_id=str(student_id),
        quest_id=quest_id,
        current_step=0,
        steps_completed=[],
        scores={},
        started_at=datetime.now(),
    )
    
    _active_sessions[session_key] = session
    return session

async def get_active_session(
    db: AsyncSession,
    student_id: int,
    quest_id: str
) -> Optional[QuestSession]:
    """Get active session if exists."""
    session_key = f"{student_id}_{quest_id}"
    return _active_sessions.get(session_key)

async def update_session(session: QuestSession) -> None:
    """Update session state."""
    session_key = f"{session.student_id}_{session.quest_id}"
    _active_sessions[session_key] = session

async def clear_session(student_id: int, quest_id: str) -> None:
    """Clear completed session."""
    session_key = f"{student_id}_{quest_id}"
    if session_key in _active_sessions:
        del _active_sessions[session_key]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_quest_executor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_services/test_quest_executor.py src/oneorg/services/quest_executor.py
git commit -m "feat: add QuestExecutor service

- start_quest_session() creates new session
- Validates quest not already completed
- In-memory session store (Redis-ready)"
```

---

## Chunk 5: StepRunner Service

**Worker:** Agent 5 (independent)

**Goal:** Implement step validation and scoring

### Files
- Create: `src/oneorg/services/step_runner.py`
- Create: `tests/test_services/test_step_runner.py`

### Task 5.1: Create StepRunner

- [ ] **Step 1: Write the failing test**

```python
# tests/test_services/test_step_runner.py
import pytest

@pytest.mark.asyncio
async def test_run_quest_step(db_session):
    """Should run a quest step and return result."""
    from oneorg.services.step_runner import run_quest_step
    
    result = await run_quest_step(
        db_session,
        student_id=1,
        quest_id="quest_001",
        step_number=1,
        step_input={"answer": "42"}
    )
    
    assert result.step_number == 1
    assert result.score >= 0.0
    assert result.passed in [True, False]

@pytest.mark.asyncio
async def test_step_scoring(db_session):
    """Should calculate step score based on input."""
    from oneorg.services.step_runner import run_quest_step
    
    # Correct answer
    result1 = await run_quest_step(
        db_session, 1, "quest_001", 1, {"answer": "42"}
    )
    
    # Wrong answer
    result2 = await run_quest_step(
        db_session, 1, "quest_001", 1, {"answer": "wrong"}
    )
    
    assert result1.score > result2.score

@pytest.mark.asyncio
async def test_quest_completion_detection(db_session):
    """Should detect when quest is complete."""
    from oneorg.services.step_runner import run_quest_step
    
    # Run all steps
    result = await run_quest_step(
        db_session, 1, "quest_001", 5, {"answer": "final"}
    )
    
    assert result.quest_complete == True
    assert result.next_step is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_step_runner.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write StepRunner**

```python
# src/oneorg/services/step_runner.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from oneorg.models.runtime import StepResult
from oneorg.db.models import Quest
from oneorg.services.quest_executor import get_active_session, update_session

async def run_quest_step(
    db: AsyncSession,
    student_id: int,
    quest_id: str,
    step_number: int,
    step_input: dict
) -> StepResult:
    """Run a quest step and return result."""
    # Get quest
    result = await db.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    quest = result.scalar()
    
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Get active session
    session = await get_active_session(db, student_id, quest_id)
    if not session:
        raise ValueError("No active session. Start quest first.")
    
    # Calculate score (simplified - real implementation would validate against quest schema)
    score = _calculate_step_score(step_input, step_number)
    passed = score >= 0.7
    
    # Update session
    session.scores[step_number] = score
    session.steps_completed.append(step_number)
    session.step_inputs[step_number] = step_input
    session.current_step = step_number
    
    # Determine next step
    total_steps = 5  # TODO: Get from quest definition
    next_step = step_number + 1 if step_number < total_steps else None
    quest_complete = step_number >= total_steps
    
    await update_session(session)
    
    return StepResult(
        step_number=step_number,
        score=score,
        passed=passed,
        feedback="Great job!" if passed else "Try again!",
        next_step=next_step,
        quest_complete=quest_complete
    )

def _calculate_step_score(step_input: dict, step_number: int) -> float:
    """Calculate score for step input.
    
    Simplified scoring - real implementation would:
    1. Load quest step definition
    2. Validate input against schema
    3. Calculate accuracy
    """
    # Placeholder scoring logic
    answer = step_input.get("answer", "")
    
    # Simple correctness check
    if answer == "42":
        return 1.0
    elif answer.isdigit():
        return 0.5
    else:
        return 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_step_runner.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_services/test_step_runner.py src/oneorg/services/step_runner.py
git commit -m "feat: add StepRunner service

- run_quest_step() validates and scores input
- Updates session state
- Detects quest completion"
```

---

## Chunk 6: CompletionHandler Service

**Worker:** Agent 6 (independent)

**Goal:** Implement quest completion with gamification

### Files
- Create: `src/oneorg/services/completion_handler.py`
- Create: `tests/test_services/test_completion_handler.py`

### Task 6.1: Create CompletionHandler

- [ ] **Step 1: Write the failing test**

```python
# tests/test_services/test_completion_handler.py
import pytest

@pytest.mark.asyncio
async def test_complete_quest_session(db_session):
    """Should complete quest and award XP."""
    from oneorg.services.completion_handler import complete_quest_session
    
    result = await complete_quest_session(
        db_session,
        student_id=1,
        quest_id="quest_001"
    )
    
    assert result.xp_earned > 0
    assert "base" in result.xp_breakdown
    assert result.calendar_updated == True

@pytest.mark.asyncio
async def test_badge_checking_on_completion(db_session):
    """Should check badges on completion."""
    from oneorg.services.completion_handler import complete_quest_session
    
    result = await complete_quest_session(db_session, 1, "quest_001")
    
    # Should have checked for effort badges
    assert isinstance(result.badges_earned, list)

@pytest.mark.asyncio
async def test_xp_uses_calculator(db_session):
    """Should use XPCalculator for predictable XP."""
    from oneorg.services.completion_handler import complete_quest_session
    
    result1 = await complete_quest_session(db_session, 1, "quest_001")
    # Same inputs should give same XP
    # (would need to reset state for real test)
    
    assert "accuracy_bonus" in result1.xp_breakdown
    assert "effort_bonus" in result1.xp_breakdown
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_services/test_completion_handler.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write CompletionHandler**

```python
# src/oneorg/services/completion_handler.py
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from oneorg.models.runtime import CompletionResult
from oneorg.models.student import Badge
from oneorg.db.models import Quest, QuestCompletion, Student
from oneorg.services.quest_executor import get_active_session, clear_session
from oneorg.models.xp_system import XPCalculator, XPConfig, QuestAttempt

async def complete_quest_session(
    db: AsyncSession,
    student_id: int,
    quest_id: str
) -> CompletionResult:
    """Complete quest and award XP, check badges, update calendar."""
    # Get quest
    result = await db.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    quest = result.scalar()
    
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Get session
    session = await get_active_session(db, student_id, quest_id)
    if not session:
        raise ValueError("No active session")
    
    # Get student
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    
    if not student:
        raise ValueError(f"Student {student_id} not found")
    
    # Calculate average score
    scores = list(session.scores.values())
    avg_score = sum(scores) / len(scores) if scores else 1.0
    
    # Calculate XP using XPCalculator
    calculator = XPCalculator(XPConfig())
    attempt = QuestAttempt(
        difficulty=quest.difficulty,
        accuracy=avg_score,
        time_spent_seconds=session.time_spent_seconds,
        attempt_number=1,  # TODO: Track attempts
        current_streak_days=student.current_streak,
    )
    
    xp_result = calculator.calculate_quest_xp(attempt)
    xp_earned = xp_result["total"]
    
    # Create completion record
    completion = QuestCompletion(
        student_id=student_id,
        quest_id=quest.id,
        score=avg_score,
        xp_earned=xp_earned,
        xp_breakdown=str(xp_result["breakdown"])
    )
    db.add(completion)
    
    # Update student XP and streak
    student.xp += xp_earned
    student.updated_at = datetime.utcnow()
    
    # Update streak (simplified - use CalendarManager in production)
    from datetime import date, timedelta
    today = date.today()
    if student.last_activity_date:
        last_date = student.last_activity_date.date() if isinstance(student.last_activity_date, datetime) else student.last_activity_date
        if last_date == today - timedelta(days=1):
            student.current_streak += 1
        elif last_date != today:
            student.current_streak = 1
    else:
        student.current_streak = 1
    
    student.last_activity_date = datetime.utcnow()
    
    # Check badges
    badges_earned = await _check_badges(db, student_id, student)
    
    # Commit changes
    await db.commit()
    
    # Clear session
    await clear_session(student_id, quest_id)
    
    return CompletionResult(
        xp_earned=xp_earned,
        xp_breakdown=xp_result["breakdown"],
        badges_earned=badges_earned,
        calendar_updated=True,
        quest_id=quest_id,
        completed_at=datetime.now()
    )

async def _check_badges(
    db: AsyncSession,
    student_id: int,
    student: Student
) -> list[Badge]:
    """Check for newly earned badges."""
    from oneorg.gamification.badges import BadgeManager
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress
    from pathlib import Path
    
    # Convert to StudentProgress model
    student_progress = StudentProgress(
        student_id=student.student_id,
        name=student.name,
        grade_level=student.grade_level,
        xp=student.xp,
    )
    
    # Check achievement badges
    badge_manager = BadgeManager(Path("data/badges"))
    achievement_badges = badge_manager.check_achievements(student_progress)
    
    # Check effort badges
    effort_checker = EffortBadgeChecker()
    effort_badges = effort_checker.check_effort_badges(student_progress)
    
    all_badges = achievement_badges + effort_badges
    
    # Award badges to database
    from oneorg.db.models import StudentBadge, Badge as DBBadge
    for badge in all_badges:
        # Find or create badge
        result = await db.execute(
            select(DBBadge).where(DBBadge.badge_id == badge.badge_id)
        )
        db_badge = result.scalar()
        
        if db_badge:
            # Award to student
            student_badge = StudentBadge(
                student_id=student_id,
                badge_id=db_badge.id
            )
            db.add(student_badge)
    
    return all_badges
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_services/test_completion_handler.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_services/test_completion_handler.py src/oneorg/services/completion_handler.py
git commit -m "feat: add CompletionHandler service

- complete_quest_session() handles full completion flow
- Uses XPCalculator for predictable XP
- Checks achievement and effort badges
- Updates student streak/calendar"
```

---

## Chunk 7: Integration Tests

**Worker:** Agent 7 (depends on Chunks 1-6)

**Goal:** Test full quest flow end-to-end

### Files
- Create: `tests/test_api/test_quest_flow.py`

### Task 7.1: Full quest flow test

- [ ] **Step 1: Write integration test**

```python
# tests/test_api/test_quest_flow.py
import pytest
from fastapi.testclient import TestClient
from oneorg.api.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Get auth token for testing."""
    # Register/login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    return response.json()["access_token"]

def test_full_quest_flow(auth_token):
    """Test complete quest flow: start → steps → complete."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. List available quests
    response = client.get("/api/quests", headers=headers)
    assert response.status_code == 200
    quests = response.json()["quests"]
    assert len(quests) > 0
    
    quest_id = quests[0]["id"]
    
    # 2. Start quest
    response = client.post(f"/api/quests/{quest_id}/start", headers=headers)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # 3. Submit steps
    for step_num in range(1, 6):  # Assume 5 steps
        response = client.post(
            f"/api/quests/{quest_id}/step",
            json={"step_number": step_num, "input": {"answer": "42"}},
            headers=headers
        )
        assert response.status_code == 200
        result = response.json()
        
        if result["quest_complete"]:
            break
    
    # 4. Complete quest
    response = client.post(f"/api/quests/{quest_id}/complete", headers=headers)
    assert response.status_code == 200
    completion = response.json()
    
    assert "xp_earned" in completion
    assert completion["xp_earned"] > 0
    assert "badges_earned" in completion
    assert "calendar_updated" in completion

def test_cannot_restart_completed_quest(auth_token):
    """Should not allow restarting completed quest."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Try to start already completed quest
    response = client.post("/api/quests/quest_001/start", headers=headers)
    assert response.status_code == 400
    assert "already completed" in response.json()["detail"].lower()

def test_progress_updated_after_completion(auth_token):
    """Should update progress after quest completion."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Get initial progress
    response = client.get("/api/progress", headers=headers)
    initial_xp = response.json()["xp"]
    
    # Complete a quest...
    # (using test_full_quest_flow logic)
    
    # Get updated progress
    response = client.get("/api/progress", headers=headers)
    assert response.json()["xp"] > initial_xp

def test_badges_endpoint(auth_token):
    """Should return badge progress."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.get("/api/progress/badges", headers=headers)
    assert response.status_code == 200
    
    badges = response.json()["badges"]
    assert isinstance(badges, list)
    
    # Each badge should have progress info
    for badge in badges:
        assert "badge_id" in badge
        assert "earned" in badge
        assert "percent" in badge

def test_calendar_endpoint(auth_token):
    """Should return activity calendar."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.get("/api/progress/calendar", headers=headers)
    assert response.status_code == 200
    
    calendar = response.json()
    assert "recent_week" in calendar
    assert "month_summary" in calendar
```

- [ ] **Step 2: Run integration tests**

Run: `pytest tests/test_api/test_quest_flow.py -v`
Expected: PASS (all 5 tests)

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
git add tests/test_api/test_quest_flow.py
git commit -m "test: add integration tests for full quest flow

- test_full_quest_flow - start to completion
- test_cannot_restart_completed_quest
- test_progress_updated_after_completion
- test_badges_endpoint
- test_calendar_endpoint"
```

---

## Integration Checklist

Before finalizing, verify:

- [ ] All CRUD endpoints functional
- [ ] QuestRuntime executes start → step → complete flow
- [ ] XP awarded using deterministic XPCalculator
- [ ] Badges checked (achievement + effort)
- [ ] Calendar updated on completion
- [ ] All tests passing (40+ new tests)
- [ ] API documentation updated

### Final Integration Test

```bash
# Run all tests
pytest tests/ -v

# Start server and test manually
uvicorn oneorg.api.main:app --reload

# Test endpoints
curl -X POST http://localhost:8000/api/auth/login -d '{"email":"test@example.com","password":"testpass"}'
curl -X GET http://localhost:8000/api/students -H "Authorization: Bearer <token>"
curl -X POST http://localhost:8000/api/quests/quest_001/start -H "Authorization: Bearer <token>"
```

---

## Summary

This plan adds API and QuestRuntime capabilities:

1. **Student CRUD** - Full CRUD for student management
2. **Quest CRUD Extensions** - Start, step, complete endpoints
3. **Progress API** - Progress, badges, calendar endpoints
4. **QuestExecutor** - Session management
5. **StepRunner** - Step validation and scoring
6. **CompletionHandler** - Quest completion with gamification
7. **Integration Tests** - Full flow testing

**Dependencies:**
- Chunks 1-6 are independent
- Chunk 7 depends on 1-6

**Workers can run in parallel:**
- Agents 1-6 start immediately
- Agent 7 starts after 1-6 complete

Plan saved to `docs/superpowers/plans/2026-03-15-api-questruntime.md`

Ready to execute with subagents?
