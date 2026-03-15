# API + QuestRuntime Design

## Summary
Add CRUD API endpoints for students, quests, and progress, plus implement QuestRuntime for quest execution with step-based completion flow.

## Requirements
- RESTful CRUD endpoints for students, quests, and progress
- QuestRuntime with start → step → complete flow
- Integration with existing gamification (XP, badges, calendar)
- Tests for all new endpoints and services

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ Student CRUD │ │ Quest CRUD   │ │ Progress/Badge APIs │ │
│  │  /api/students│ │  /api/quests │ │  /api/progress       │ │
│  └──────┬───────┘ └──────┬───────┘ └─────────┬────────────┘ │
└─────────┼────────────────┼───────────────────┼──────────────┘
          │                │                   │
┌─────────┴────────────────┴───────────────────┴──────────────┐
│                    QuestRuntime                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │QuestExecutor│ │ StepRunner  │ │ CompletionHandler       ││
│  │ start()     │ │ run_step()  │ │ award_xp(), check_badges││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
          │                │                   │
┌─────────┴────────────────┴───────────────────┴──────────────┐
│                    Service Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ XPCalculator│ │ BadgeChecker│ │ CalendarManager         ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

## Components

### API Layer

**Students API (`/api/students`)**
- GET / - List students (paginated)
- POST / - Create student
- GET /{id} - Get student details
- PATCH /{id} - Update student
- DELETE /{id} - Delete student

**Quests API (`/api/quests`)**
- GET / - List available quests
- POST / - Create quest (admin)
- GET /{id} - Get quest details
- POST /{id}/start - Start quest runtime
- POST /{id}/step - Submit step result
- POST /{id}/complete - Complete quest

**Progress API (`/api/progress`)**
- GET / - Current student progress
- GET /badges - Badge progress
- GET /calendar - Activity calendar

### QuestRuntime

**QuestExecutor**
- `start_quest(student_id, quest_id)` → QuestSession
- Validates quest exists and student hasn't completed it
- Creates in-memory session with step state

**StepRunner**
- `run_step(session_id, step_input)` → StepResult
- Validates step input against quest schema
- Calculates score for step
- Returns next step or completion signal

**CompletionHandler**
- `complete_quest(session_id, final_score)` → CompletionResult
- Awards XP using XPCalculator
- Checks badges using BadgeChecker
- Updates calendar via CalendarManager
- Persists QuestCompletion to database

### Data Models

**QuestSession**
```python
class QuestSession(BaseModel):
    session_id: str
    student_id: str
    quest_id: str
    current_step: int
    steps_completed: list[int]
    scores: dict[int, float]
    started_at: datetime
    time_spent_seconds: int = 0
```

**StepResult**
```python
class StepResult(BaseModel):
    step_number: int
    score: float
    passed: bool
    feedback: str
    next_step: Optional[int]
    quest_complete: bool
```

**CompletionResult**
```python
class CompletionResult(BaseModel):
    xp_earned: int
    xp_breakdown: dict
    badges_earned: list[Badge]
    calendar_updated: bool
    quest_id: str
    completed_at: datetime
```

## Error Handling

- 401 Unauthorized - Invalid or missing session token
- 404 Not Found - Quest/Student not found
- 400 Bad Request - Invalid step input or quest already completed
- 409 Conflict - Quest session already in progress
- 500 Internal Server Error - Database or service errors

## Testing Strategy

**Unit Tests**
- QuestExecutor.start_quest()
- StepRunner.run_step() with various inputs
- CompletionHandler.complete_quest()

**Integration Tests**
- Full quest flow (start → steps → complete)
- XP calculation integration
- Badge checking integration
- Calendar update integration

**API Tests**
- All CRUD endpoints
- Error responses
- Authentication/authorization

## Files to Create/Modify

**New Files**
- `src/oneorg/api/routes/students.py` - Student CRUD endpoints
- `src/oneorg/api/routes/progress.py` - Progress endpoints
- `src/oneorg/services/quest_executor.py` - Quest session management
- `src/oneorg/services/step_runner.py` - Step validation and scoring
- `src/oneorg/services/completion_handler.py` - Quest completion logic
- `src/oneorg/models/runtime.py` - QuestSession, StepResult, CompletionResult
- `tests/test_api/test_students.py` - Student API tests
- `tests/test_api/test_progress.py` - Progress API tests
- `tests/test_api/test_quest_flow.py` - Full quest flow tests

**Modified Files**
- `src/oneorg/api/routes/quests.py` - Add start/step/complete endpoints
- `src/oneorg/api/routes/__init__.py` - Include new routers
- `src/oneorg/services/quest_engine.py` - Extract completion logic

## Worker Decomposition

**7 Parallel Workers:**

| Agent | Task | Dependencies |
|-------|------|-------------|
| 1 | Student CRUD API | None |
| 2 | Quest CRUD API (extend) | None |
| 3 | Progress API | None |
| 4 | QuestExecutor | None |
| 5 | StepRunner | None |
| 6 | CompletionHandler | None |
| 7 | API Integration Tests | 1-6 |

**Execution Order:**
1. Agents 1-6 start in parallel
2. Agent 7 starts after 1-6 complete
3. Final integration test runs after all complete

## Success Criteria

- [ ] All CRUD endpoints functional with tests
- [ ] QuestRuntime executes quest flow end-to-end
- [ ] XP awarded using deterministic XPCalculator
- [ ] Badges checked and awarded correctly
- [ ] Calendar updated on quest completion
- [ ] All tests passing (35+ new tests)
