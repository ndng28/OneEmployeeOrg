from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

try:
    from oneorg.db.models import Quest, QuestCompletion, Student, StudentBadge, Badge
except ImportError:
    # Models not available yet - will be integrated in Chunk 5
    Quest = None
    QuestCompletion = None
    Student = None
    StudentBadge = None
    Badge = None


async def get_available_quests(db: AsyncSession, student_id: int) -> List[Quest]:
    """Get quests not yet completed by student."""
    if Quest is None or QuestCompletion is None:
        return []
    
    # Get completed quest IDs
    result = await db.execute(
        select(QuestCompletion.quest_id)
        .where(QuestCompletion.student_id == student_id)
    )
    completed_ids = {row[0] for row in result.all()}
    
    # Get available quests
    result = await db.execute(
        select(Quest)
        .where(and_(
            Quest.is_active == True,
            ~Quest.id.in_(completed_ids) if completed_ids else True
        ))
    )
    return result.scalars().all()


async def get_quest(db: AsyncSession, quest_id: str) -> Optional[Quest]:
    """Get quest by ID."""
    if Quest is None:
        return None
    
    result = await db.execute(
        select(Quest).where(Quest.quest_id == quest_id)
    )
    return result.scalar()


async def complete_quest(
    db: AsyncSession,
    student_id: int,
    quest_id: int,
    score: float = 1.0,
    feedback: Optional[str] = None
) -> dict:
    """Complete a quest and award XP."""
    if Quest is None or QuestCompletion is None or Student is None:
        raise ValueError("Database models not available")
    
    # Get quest
    result = await db.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar()
    if not quest:
        raise ValueError(f"Quest {quest_id} not found")
    
    # Check if already completed
    result = await db.execute(
        select(QuestCompletion)
        .where(and_(
            QuestCompletion.student_id == student_id,
            QuestCompletion.quest_id == quest_id
        ))
    )
    if result.scalar():
        raise ValueError("Quest already completed")
    
    # Create completion
    xp_earned = int(quest.xp_reward * score)
    completion = QuestCompletion(
        student_id=student_id,
        quest_id=quest_id,
        score=score,
        xp_earned=xp_earned,
        feedback=feedback
    )
    db.add(completion)
    
    # Update student XP
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar()
    student.xp += xp_earned
    student.updated_at = datetime.utcnow()
    
    # Update streak
    today = datetime.utcnow().date()
    if student.last_activity_date:
        last_date = student.last_activity_date.date() if isinstance(student.last_activity_date, datetime) else student.last_activity_date
        if last_date == today - timedelta(days=1):
            student.current_streak += 1
        elif last_date != today:
            student.current_streak = 1
    else:
        student.current_streak = 1
    
    student.last_activity_date = datetime.utcnow()
    student.longest_streak = max(student.longest_streak, student.current_streak)
    
    await db.commit()
    
    return {
        "xp_earned": xp_earned,
        "total_xp": student.xp,
        "level": (student.xp // 500) + 1,
        "streak": student.current_streak
    }


async def get_student_progress(db: AsyncSession, student_id: int) -> dict:
    """Get comprehensive progress for a student."""
    if Student is None or QuestCompletion is None or Quest is None or StudentBadge is None or Badge is None:
        raise ValueError("Database models not available")
    
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar()
    if not student:
        raise ValueError("Student not found")
    
    # Get completions with quest info
    result = await db.execute(
        select(QuestCompletion, Quest)
        .join(Quest, QuestCompletion.quest_id == Quest.id)
        .where(QuestCompletion.student_id == student_id)
        .order_by(QuestCompletion.completed_at.desc())
    )
    completions = result.all()
    
    # Get badges
    result = await db.execute(
        select(StudentBadge, Badge)
        .join(Badge, StudentBadge.badge_id == Badge.id)
        .where(StudentBadge.student_id == student_id)
    )
    badges = result.all()
    
    level = (student.xp // 500) + 1
    xp_to_next = 500 - (student.xp % 500)
    
    return {
        "student_id": student.student_id,
        "name": student.name,
        "grade": student.grade_level,
        "xp": student.xp,
        "level": level,
        "xp_to_next": xp_to_next,
        "streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "quests_completed": len(completions),
        "recent_completions": [
            {
                "quest_title": quest.title,
                "xp": completion.xp_earned,
                "date": completion.completed_at.isoformat()
            }
            for completion, quest in completions[:5]
        ],
        "badges": [
            {"name": badge.name, "icon": badge.icon}
            for _, badge in badges
        ]
    }
