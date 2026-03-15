import asyncio
from oneorg.db.database import engine, Base
from oneorg.db.models import User, Student, Quest, QuestCompletion, Badge, StudentBadge

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

async def seed_quests():
    from oneorg.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Check if quests already exist
        from sqlalchemy import select
        result = await session.execute(select(Quest).limit(1))
        if result.scalar():
            print("Quests already seeded")
            return
        
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
        print(f"Seeded {len(sample_quests)} quests")

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_quests())
