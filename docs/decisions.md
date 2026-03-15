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

## 2024-03-13: Gamification Mechanics - Expert-Informed Revision
**Context:** Child psychologist, neuroscientist, and ethics experts identified harmful mechanics in current design
**Decision:** Remove variable rewards, loss aversion, and social pressure; implement age-appropriate modes
**Rationale:**
- Variable rewards (rarity tiers) = gambling mechanics, damage dopaminergic system
- Loss aversion (longest streak) creates anxiety, undermines intrinsic motivation
- Social pressure (default leaderboards) toxic for developing self-concept
- Age modes: 5-8 minimal, 9-12 careful, 13-18 optional respects developmental stages
**Changes:**
- REMOVE: Badge rarity tiers, longest_streak tracking, Team competition, default leaderboards
- ADD: Predictable XP, effort-based badges, consistency calendar (positive framing), age-specific modes

## 2024-03-13: AI Quest Master Relationship Model
**Context:** Philosophers and child psychologists raised concerns about AI-student relationships
**Decision:** Shift from "expert agents" to "senior apprentice guides"
**Rationale:**
- Socratic model (guide, midwife) NOT Platonic (embodies wisdom) - AI cannot be good
- Risk of false intimacy without reciprocity - children form attachments to AI
- Transparency about AI nature required with periodic reminders
- Every AI interaction should deepen human connection (human bridge prompts)
**New Schema:**
- relationship_model: "senior_apprentice" (NOT "expert")
- knowledge_stance: transparent about limitations
- failure_modeling: True - shows mistakes and recovery
- ai_disclosure: mandatory transparency statement

## 2024-03-13: Family Integration Design
**Context:** Family systems expert identified risks to family dynamics from screen-based learning
**Decision:** Parents are learning partners, not enforcement police; platform enforces limits
**Rationale:**
- Platform as "bad guy" for time limits prevents parent-child battles
- Parent dashboard shows weekly stories (not surveillance metrics)
- Family quests optional but earn offline value (streak freezes)
- Multilingual support from day one for diverse families
**Key Features:**
- Wind-down mode before sleep (neuroscience-informed)
- Conversation starter engine ("what did you wonder about?")
- "Ask someone" help button (not "ask parent")
- 12+ language support
