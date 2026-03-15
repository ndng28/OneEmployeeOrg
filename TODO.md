# TODO

## Phase 0: Remove Harmful Mechanics (Week 1) - CRITICAL
- [ ] Remove badge rarity tiers (Common → Legendary) - variable reward mechanics
- [ ] Remove longest_streak field - loss aversion trigger
- [ ] Remove Team competition mechanics
- [ ] Make leaderboard opt-in by default (currently public)
- [ ] Replace CLI leaderboard command with personal progress command

## Phase 1: Age Modes + Healthy Gamification (Weeks 2-3) - HIGH PRIORITY
- [ ] Create AgeMode enum with 3 profiles: 5-8, 9-12, 13-18
- [ ] Add AgeMode computed field to StudentProgress
- [ ] Implement predictable XP system (no randomness)
- [ ] Create effort-based badge criteria (replaces achievement-only)
- [ ] Build consistency calendar (positive framing, no streak shaming)
- [ ] Update CLI progress command for age-appropriate display

## Phase 2: AI Quest Masters (Weeks 4-5) - HIGH PRIORITY
- [ ] Create AI Quest Master schema with new fields:
  - relationship_model: "senior_apprentice" (not "expert")
  - knowledge_stance: transparent limitations
  - failure_modeling: True (shows mistakes)
  - ai_disclosure: mandatory transparency
  - human_bridge_prompts: connects to humans
- [ ] Rewrite 3 pilot Quest Masters with new personas
- [ ] Implement AI transparency reminders (periodic)
- [ ] Add failure normalization prompts
- [ ] Build boundary enforcement when attachment detected

## Phase 3: Family Integration (Weeks 6-7) - MEDIUM PRIORITY
- [ ] Create parent dashboard with weekly stories (not metrics)
- [ ] Implement conversation starter engine
- [ ] Build family quest system (optional, solo-capable)
- [ ] Add screen time management (platform enforces)
- [ ] Create wind-down mode before sleep
- [ ] Add multilingual support (12+ languages)
- [ ] Implement "Ask someone" help button

## Phase 4: Polish + i18n (Weeks 8-9) - LOW PRIORITY
- [ ] Add personalized conversation starters
- [ ] Expand family quest variety
- [ ] Advanced time scheduling
- [ ] Cultural adaptation engine

## High Priority (Next 2 Weeks) - Pre-Expert
- [ ] Wire gamification logic to API endpoints (CRUD for students, quests, progress)
- [ ] Implement class code authentication (teacher PIN, student codes, session cookies)
- [ ] Create HTMX dashboard templates (leaderboard, student profile, badge gallery)
- [ ] Migrate StateTracker to SQLite (concurrent writes, better queries)
- [ ] Build basic QuestRuntime MVP (quest execution, XP awarding, completion flow)

## Medium Priority (Next Month)
- [ ] WebSocket real-time progress updates (live leaderboard, quest notifications)
- [ ] Quest authoring system for teachers (YAML-based with UI)
- [ ] Daily engagement features (login spinner, flash quests)
- [ ] Social features (team quest wars, squad configuration)
- [ ] Parent portal (progress reports, weekly summaries)

## Long Term (3+ Months)
- [ ] Multi-tenancy foundation (class isolation, teacher accounts)
- [ ] PostgreSQL migration for SaaS scale
- [ ] OAuth/SSO integration (Google, Clever, Microsoft)
- [ ] Payment integration (Stripe for subscriptions)
- [ ] Advanced personalization (adaptive difficulty, learning style detection)

## Known Issues
- [ ] JSON file persistence breaks with concurrent writes (migrate to SQLite)
- [ ] No error handling for OpenCode CLI not found
- [ ] WebSocket auth needs token validation implementation
- [ ] Missing parent email recovery flow

## Research & Strategy
- [ ] Validate pricing tiers with 10-20 pilot teachers
- [ ] Design viral growth loop (squad quests requiring 4 players)
- [ ] Create teacher ambassador program
- [ ] Develop 20 exceptional quest experiences for launch
