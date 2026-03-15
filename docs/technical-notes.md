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

## Neuroscience-Informed Design

### Dopaminergic System Protection
- **Variable rewards prohibited**: Loot boxes, random drops damage developing prefrontal cortex
- **Predictable XP formula**: `time_minutes × 5 XP/min × difficulty_multiplier` - never random
- **Effort bonuses only**: 10% per retry (max 50%), rewards persistence not luck
- **No loss aversion**: Remove streaks with punishment, celebrate consistency without fear

### Age-Appropriate Feature Gating
- **5-8 years (Young Child)**: No XP/levels/streaks visible, minimal gamification
- **9-12 years (Preteen)**: XP visible but no leaderboards, introduce carefully
- **13-18 years (Teen)**: Optional features, self-directed, can disable entirely

### Social Evaluation Sensitivity
- Adolescents hypersensitive to social ranking (amygdala response to exclusion)
- Private progress default, public comparison opt-in only
- No zero-sum competition, cooperative structures preferred
- Celebration language: "You completed this!" not "You're ranked #47"

## AI Quest Master Design

### Persona Requirements
- **Senior apprentice model**: "I'm a few steps ahead on this path" not "I'm an expert"
- **Failure modeling**: Show mistakes, wrong turns, recovery process
- **Transparency**: "I'm an AI tool" reminders every ~10 interactions
- **Boundary enforcement**: Decline relationship-building attempts, redirect to humans

### Socratic Dialogue Pattern
1. **QUESTION**: Start with curiosity ("What do you think?")
2. **GUIDE**: Offer hints, not answers
3. **STRUGGLE**: Narrate thinking process including mistakes
4. **VALIDATE**: Acknowledge effort and thinking process
5. **BRIDGE**: Connect to human teachers/family

### Required Disclosures
- Onboarding: "I'm an AI, not a person. Teachers and family are your real guides."
- Periodic: "Quick reminder: I'm an AI guide."
- Before personal disclosure: "I'm an AI, so I can't really understand feelings..."

## Family Integration Patterns

### Screen Time Management
- Platform enforces, parent sets preferences (parent never "bad guy")
- Wind-down mode: 6-8pm calmer content, 8pm+ rest mode
- No hard cutoff mid-quest: complete current, then graceful ending
- Streak freezes earnable through offline family activities

### Conversation Starters (Not Progress Bars)
- "What did you wonder about this week?"
- "Show me something you got better at"
- "What was tricky? How did you figure it out?"
- "Can you teach me something you learned?"

### Red Lines (Never Implement)
- Real-time activity feed (surveillance)
- "You played X hours today" (time policing)
- Leaderboard position in parent dashboard (comparison pressure)
- "Help with homework" framing (assumes parent expertise)
