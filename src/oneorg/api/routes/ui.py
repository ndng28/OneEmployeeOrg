from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from oneorg.db.database import get_db
from oneorg.services.auth import get_current_user
from oneorg.services.quest_engine import get_available_quests, get_quest, get_student_progress

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

async def require_auth(request: Request, db: AsyncSession = Depends(get_db)):
    """Require authentication, return student info."""
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
    
    return student

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect to dashboard if logged in, otherwise login."""
    if request.cookies.get("access_token"):
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Student dashboard."""
    progress = await get_student_progress(db, student.id)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        **progress
    })

@router.get("/quests", response_class=HTMLResponse)
async def quests_list(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """List available quests."""
    available = await get_available_quests(db, student.id)
    return templates.TemplateResponse("quests.html", {
        "request": request,
        "quests": [{"id": q.quest_id, **q.__dict__} for q in available]
    })

@router.get("/quests/{quest_id}", response_class=HTMLResponse)
async def quest_detail(request: Request, quest_id: str, db: AsyncSession = Depends(get_db)):
    """Quest detail page."""
    quest = await get_quest(db, quest_id)
    if not quest:
        return RedirectResponse("/quests?error=not_found", status_code=302)
    
    return templates.TemplateResponse("quest_detail.html", {
        "request": request,
        "quest": {
            "id": quest.quest_id,
            "title": quest.title,
            "description": quest.description,
            "xp_reward": quest.xp_reward,
            "difficulty": quest.difficulty,
            "category": quest.category
        }
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Profile page (redirects to dashboard for now)."""
    return RedirectResponse("/dashboard", status_code=302)
