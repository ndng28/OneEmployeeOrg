# TODO

## High Priority (Next 2 Weeks)
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
