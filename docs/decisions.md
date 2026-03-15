# Decisions

## 2024-03-12: Badge Artwork Strategy
**Context:** Need to choose between emoji-only, custom artwork, or hybrid for badge system
**Decision:** Hybrid approach - Emoji for Common/Uncommon, Custom artwork for Epic/Legendary
**Rationale:** 
- Zero cost for MVP with emoji
- Cultural accessibility (Unicode universal)
- Custom artwork for high-value achievements creates differentiation
- Defers design spend until validated
**Alternatives:** 
- Custom artwork only (high cost, slow)
- Emoji only (low differentiation)

## 2024-03-12: Authentication Strategy for K-12
**Context:** COPPA compliance requirements for under-13 users, need low friction
**Decision:** Class codes + Google SSO (MVP), add Clever later
**Rationale:**
- Schools act as parent agents (COPPA school consent model)
- No email required for under-13s
- 30-second teacher setup time
- Defer OAuth complexity until multi-tenant SaaS
**Alternatives:**
- Full OAuth from day one (too complex for single classroom)
- Email-based auth (violates COPPA for under-13)

## 2024-03-12: Frontend Architecture
**Context:** Need to choose frontend stack - React SPA vs HTMX vs hybrid
**Decision:** HTMX + Alpine.js + PWA (no React for MVP)
**Rationale:**
- Fastest time to market (2-3 weeks vs 6-8)
- HTML-first natural accessibility advantage
- Progressive enhancement works on school Chromebooks
- One developer owns full stack
**Alternatives:**
- React SPA (3x dev time, higher complexity)
- Vue/Svelte (smaller hiring pool)

## 2024-03-12: Subagent Execution Mode
**Context:** How to execute OpenCode/AI quest masters - CLI vs API
**Decision:** Hybrid architecture (CLI for dev, SDK for production, Ollama fallback)
**Rationale:**
- CLI fastest for MVP validation
- SDK enables multi-tenant tracking
- Local model (Ollama) provides resilience
- Graceful degradation chain
**Alternatives:**
- CLI only (no production scalability)
- API only (longer time to validate)

## 2024-03-12: Database Evolution Path
**Context:** Current JSON file-based persistence, need to plan for scale
**Decision:** JSON files → SQLite now → PostgreSQL at SaaS transition
**Rationale:**
- JSON sufficient for 50 students (MVP)
- SQLite handles 10K users with zero config
- Migration path clear: StateTracker → Repository pattern
- Defer PostgreSQL until multi-tenant needs
**Alternatives:**
- PostgreSQL from day one (overkill for MVP)
- MongoDB (adds complexity without benefit)

## 2024-03-12: Monetization Model
**Context:** Need revenue model for sustainable platform
**Decision:** Freemium (Parent Pro) + School B2B licensing
**Rationale:**
- Free tier drives viral spread
- Parent subscription generates immediate revenue
- B2B high LTV but 6-12 month sales cycle
- Ethical constraints prevent dark patterns
**Ethical Constraints:**
1. No pay-to-win (no XP advantages)
2. No dark patterns targeting children
3. Transparent data practices

## 2024-03-12: Competitive Positioning
**Context:** Competing with Khan Academy, Duolingo, Google Classroom
**Decision:** Position as "AI Quest Masters as Co-Teachers"
**Rationale:**
- Own upper-right quadrant: High engagement + High teacher control
- Living curriculum adapts in real-time (impossible for static competitors)
- Teachers prompt AI, maintain control
- Compete on depth, not breadth
**Key Differentiator:** Teachers assign, AI adapts, you see the journey
