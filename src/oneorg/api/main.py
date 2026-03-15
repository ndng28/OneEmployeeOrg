from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from oneorg.api.routes import auth, quests, ui

app = FastAPI(
    title="OneEmployeeOrg Academy",
    description="Edu-tainment platform for K-12 students",
    version="2.0.0",
)

# Include routers
app.include_router(auth.router)
app.include_router(quests.router)
app.include_router(ui.router)

# Static files (for future use)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    from oneorg.db.database import engine, Base
    from oneorg.db.models import User, Student, Quest, QuestCompletion, Badge, StudentBadge
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed quests if needed
    from oneorg.db.database import AsyncSessionLocal
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Quest).limit(1))
        if not result.scalar():
            sample_quests = [
                Quest(
                    quest_id="intro_welcome",
                    title="Welcome to the Academy",
                    description="Complete your first quest and learn how the platform works.",
                    xp_reward=50,
                    difficulty=1,
                    category="onboarding"
                ),
                Quest(
                    quest_id="math_addition",
                    title="Addition Explorer",
                    description="Master basic addition with fun challenges.",
                    xp_reward=100,
                    difficulty=2,
                    category="math"
                ),
                Quest(
                    quest_id="sci_lab",
                    title="Virtual Lab Assistant",
                    description="Help clean up the science lab and learn about lab safety.",
                    xp_reward=75,
                    difficulty=1,
                    category="science"
                ),
            ]
            for quest in sample_quests:
                session.add(quest)
            await session.commit()
            print("Seeded sample quests")
