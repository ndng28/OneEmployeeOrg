from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from oneorg.db.database import get_db
from oneorg.services.quest_engine import (
    get_available_quests, get_quest, complete_quest, get_student_progress
)
from oneorg.services.auth import get_current_user

router = APIRouter()


async def get_current_student_id(request: Request, db: AsyncSession = Depends(get_db)):
    """Get current student ID from session cookie."""
    from sqlalchemy import select
    from oneorg.db.models import Student
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_current_user(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    result = await db.execute(select(Student).where(Student.user_id == user.id))
    student = result.scalar()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return student.id


@router.get("/api/quests")
async def list_quests(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """List available quests for current student."""
    quests = await get_available_quests(db, student_id)
    return {
        "quests": [
            {
                "id": q.quest_id,
                "title": q.title,
                "description": q.description,
                "xp_reward": q.xp_reward,
                "difficulty": q.difficulty,
                "category": q.category
            }
            for q in quests
        ]
    }


@router.get("/api/quests/{quest_id}")
async def get_quest_detail(
    quest_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get quest details."""
    quest = await get_quest(db, quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    return {
        "id": quest.quest_id,
        "title": quest.title,
        "description": quest.description,
        "xp_reward": quest.xp_reward,
        "difficulty": quest.difficulty,
        "category": quest.category
    }


@router.post("/api/quests/{quest_id}/complete")
async def complete_quest_api(
    quest_id: str,
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Complete a quest via API."""
    from sqlalchemy import select
    from oneorg.db.models import Quest
    
    result = await db.execute(select(Quest).where(Quest.quest_id == quest_id))
    quest = result.scalar()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    try:
        result = await complete_quest(db, student_id, quest.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/progress")
async def get_progress_api(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Get student progress."""
    progress = await get_student_progress(db, student_id)
    return progress


@router.post("/quests/{quest_id}/complete")
async def complete_quest_form(
    quest_id: str,
    request: Request,
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Complete quest via form submission."""
    from sqlalchemy import select
    from oneorg.db.models import Quest
    
    result = await db.execute(select(Quest).where(Quest.quest_id == quest_id))
    quest = result.scalar()
    if not quest:
        return RedirectResponse("/quests?error=not_found", status_code=302)
    
    try:
        await complete_quest(db, student_id, quest.id)
        return RedirectResponse("/dashboard?success=quest_completed", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/quests/{quest_id}?error={str(e)}", status_code=302)
