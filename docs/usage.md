# Usage

## CLI Commands

### Student Management
```bash
# Create student
oneorg student stu_001 --name "Alex Chen" --grade 10

# View student progress
oneorg student stu_001

# Complete quest and award XP
oneorg complete stu_001 frontend-basics frontend-developer --xp 150 --score 0.92
```

### Quest Masters
```bash
# Build quest master index from agency-agents
oneorg index

# Search quest masters
oneorg search "frontend"

# View leaderboard
oneorg leaderboard --limit 20
```

### Decision Gates
```bash
# Evaluate decision confidence
oneorg evaluate "Start new quest" --confidence 0.92 --domain operations
```

## FastAPI Server

### Start Server
```bash
uvicorn oneorg.api.main:app --reload
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Create class (teacher)
curl -X POST http://localhost:8000/auth/create-class \
  -H "Content-Type: application/json" \
  -d '{"teacher_name": "Ms. Johnson", "subject": "Math"}'

# Student join with class code
curl -X POST http://localhost:8000/auth/join \
  -H "Content-Type: application/json" \
  -d '{"class_code": "ABC-1234", "student_name": "Alex", "grade_level": 10}' \
  -c cookies.txt

# Get student progress
curl http://localhost:8000/api/students/{student_id} \
  -b cookies.txt

# Complete quest
curl -X POST http://localhost:8000/api/students/{student_id}/quests/complete \
  -H "Content-Type: application/json" \
  -d '{"quest_id": "frontend-basics", "quest_master": "frontend-developer", "xp_earned": 150}' \
  -b cookies.txt

# Search quests
curl "http://localhost:8000/api/quests/search?q=frontend"

# Get leaderboard
curl http://localhost:8000/api/leaderboard?limit=10
```

### WebSocket Progress
```javascript
const studentId = "stu_001";
const ws = new WebSocket(`ws://localhost:8000/ws/progress/${studentId}?token=${getToken()}`);

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.event_type === "xp_gained") {
        console.log(`XP gained: ${msg.data.xp_earned}`);
    } else if (msg.event_type === "level_up") {
        console.log(`Level up! Now level ${msg.data.new_level}`);
    }
};
```

## Dashboard

### Teacher Dashboard
Access teacher dashboard at: `http://localhost:8000/dashboard/{class_code}`

Features:
- Real-time class pulse (engagement, at-risk students)
- Quest assignment dispatcher
- Individual student progress tracking
- Weekly progress reports

### Student Dashboard
Students access their dashboard after joining via class code.

Features:
- XP progress bar
- Quest completion history
- Badge gallery
- Current streak display
- Leaderboard position

## Configuration

### Environment Variables
```bash
# OpenCode path for quest execution
export OPENCODE_PATH="opencode"

# State directory (default: data/state)
export ONEORG_STATE_DIR="/path/to/state"

# Badge definitions directory (default: data/badges)
export ONEORG_BADGES_DIR="/path/to/badges"
```

### Class Code Settings
- Expiration: 7 days default
- Max students per code: 50
- Rate limit: 10 attempts per 15 minutes

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Install in Development Mode
```bash
pip install -e .
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```
