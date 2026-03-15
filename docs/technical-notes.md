# Technical Notes

## HTMX + Alpine.js Integration
- HTMX handles server communication (hx-get, hx-post)
- Alpine.js handles client-side interactivity (forms, toggles)
- No build step required - both load from CDN
- Progressive enhancement: works without JavaScript

## Class Code Authentication
- Format: `XXX-####` (3 letters + 4 digits)
- Avoid ambiguous characters (0/O, 1/l/I)
- 7-day expiration for security
- Max 50 students per code
- Teacher notification on each join

## Badge System Implementation
- YAML-based definitions in `data/badges/`
- Categories: milestone, streak, mastery, social, exploration
- Rarity tiers: common, uncommon, rare, epic, legendary
- Criteria types: quest_count, level, streak_days, xp_total
- Check achievements after quest completion

## State Persistence
- Current: JSON files per student in `data/state/students/`
- Planned: SQLite migration for concurrent writes
- Repository pattern abstracts storage (JsonStudentRepository → SqliteStudentRepository)

## WebSocket Progress Updates
- FastAPI native WebSocket support
- ConnectionManager tracks active connections per student
- Notify on: xp_gained, level_up, badge_earned
- Client: `new WebSocket('/ws/progress/{student_id}')`

## QuestRuntime Architecture
- Async subprocess execution via `asyncio.create_subprocess_exec`
- Prompt construction from QuestMaster metadata (name, vibe, description, keywords)
- Error handling: retry with exponential backoff
- Output parsing: try JSON first, fall back to markdown sections

## COPPA Compliance
- School consent model (school acts as parent agent)
- No student email for under-13
- Anonymous display names optional
- Data export/delete on parent request

## Performance Considerations
- JSON files: O(n) leaderboard scan (fine for <100 students)
- SQLite: handles 10K users, 100s concurrent reads
- PostgreSQL: needed at >50 concurrent writes
- Redis: consider for leaderboard cache at scale
