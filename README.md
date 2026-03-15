# OneEmployeeOrg Academy

Quest-based learning platform for K-12 students. Students complete interactive quests, earn XP, badges, and levels while learning through personalized experiences.

## Features

- **Student Accounts** - Email/password authentication with secure sessions
- **Quest System** - Complete quests to earn XP and progress
- **Gamification** - Levels, XP tracking, streaks, badges
- **Progress Tracking** - Dashboard showing stats, recent completions, achievements
- **Responsive UI** - Beautiful web interface with HTMX

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/ndng28/OneEmployeeOrg.git
cd OneEmployeeOrg

# Set up environment
cp .env.example .env
# Edit .env and set a secure SECRET_KEY

# Start with Docker Compose
docker compose up --build -d

# Visit http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env and set SECRET_KEY

# Start the server
uvicorn oneorg.api.main:app --reload

# Visit http://localhost:8000
```

## Docker Development

### Development Mode (Hot Reload)

```bash
# Start with hot reload and exposed PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Changes to src/ are reflected immediately
```

### Production Mode

```bash
# Start production stack
docker compose up --build -d

# View logs
docker compose logs -f app

# Stop
docker compose down

# Reset database (⚠️ deletes all data)
docker compose down -v
```

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (required) | - |
| `DATABASE_URL` | Database connection string | SQLite |
| `DEBUG` | Debug mode | false |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Session lifetime | 7 |

### Database Options

**SQLite (Local Development):**
```
DATABASE_URL=sqlite+aiosqlite:///data/oneorg.db
```

**PostgreSQL (Docker/Production):**
```
DATABASE_URL=postgresql+asyncpg://oneorg:oneorg@db:5432/oneorg
```

## Project Structure

```
OneEmployeeOrg/
├── src/oneorg/
│   ├── api/              # FastAPI routes and templates
│   │   ├── routes/       # Auth, quests, UI routes
│   │   └── templates/    # Jinja2 HTML templates
│   ├── db/               # Database models and connection
│   ├── services/         # Business logic (auth, quests)
│   └── config.py         # Pydantic settings
├── tests/                # Test suite
├── Dockerfile            # Production container
├── docker-compose.yml    # Docker orchestration
├── .env.example          # Environment template
└── docs/                 # Documentation
```

## Documentation

- **[docs/decisions.md](docs/decisions.md)** - Architecture decisions
- **[docs/technical-notes.md](docs/technical-notes.md)** - Implementation details
- **[docs/usage.md](docs/usage.md)** - CLI usage guide
- **[TODO.md](TODO.md)** - Development roadmap

## Development

### Running Tests

```bash
pytest tests/ -v
```

### CLI Commands

```bash
# View leaderboard
oneorg leaderboard

# Check student progress
oneorg student stu_001

# Complete a quest
oneorg complete stu_001 quest_001 "Quest Master"
```

## Architecture

### Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Jinja2 + HTMX
- **Auth**: JWT tokens + bcrypt
- **Containerization**: Docker + Docker Compose

### Docker Services

```
┌─────────────────────────────────────┐
│         Docker Compose              │
│                                     │
│  ┌──────────┐      ┌────────────┐  │
│  │   App    │      │ PostgreSQL │  │
│  │ FastAPI  │──────│   16       │  │
│  │ Port 8000│      │ Port 5432  │  │
│  └──────────┘      └────────────┘  │
└─────────────────────────────────────┘
```

## License

MIT
