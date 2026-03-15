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
    """Student dashboard with age-appropriate gamification display."""
    # Import StudentProgress model for dashboard data
    from oneorg.models.student import StudentProgress, QuestCompletion, Badge
    from datetime import datetime
    
    # Convert database student to StudentProgress model
    # This assumes student has the necessary fields from the DB model
    student_progress = StudentProgress(
        student_id=str(student.student_id) if hasattr(student, 'student_id') else str(student.id),
        name=student.name,
        grade_level=student.grade_level if hasattr(student, 'grade_level') else 5,
        xp=student.xp if hasattr(student, 'xp') else 0,
    )
    
    # Add quests completed if available
    if hasattr(student, 'quest_completions'):
        for qc in student.quest_completions:
            completion = QuestCompletion(
                quest_id=str(qc.quest_id),
                quest_master="system",
                xp_earned=qc.xp_earned if hasattr(qc, 'xp_earned') else 10,
                completed_at=qc.completed_at if hasattr(qc, 'completed_at') else datetime.now(),
                score=qc.score if hasattr(qc, 'score') else 1.0,
            )
            student_progress.quests_completed.append(completion)
    
    # Add badges if available
    if hasattr(student, 'student_badges'):
        for sb in student.student_badges:
            if hasattr(sb, 'badge'):
                badge = Badge(
                    badge_id=str(sb.badge.badge_id) if hasattr(sb.badge, 'badge_id') else str(sb.badge.id),
                    name=sb.badge.name,
                    description=sb.badge.description if hasattr(sb.badge, 'description') else "",
                    icon=sb.badge.icon if hasattr(sb.badge, 'icon') else "🏅",
                )
                student_progress.badges.append(badge)
    
    # Prepare dashboard data with new gamification system
    dashboard_data = {
        "student": student_progress,
        "age_mode": student_progress.age_mode,
        "calendar_summary": student_progress.calendar.get_recent_month_summary(),
        "week_view": student_progress.calendar.get_recent_week(),
        "badges": student_progress.badges,
        # Don't show leaderboard by default - opt-in only
        "show_leaderboard_prompt": not student_progress.leaderboard_settings.show_on_leaderboard,
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        **dashboard_data
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


@router.post("/leaderboard/opt-in")
async def opt_in_leaderboard(request: Request, student = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    """Allow students to opt-in to leaderboard visibility."""
    try:
        # Update student's leaderboard settings
        if hasattr(student, 'leaderboard_opt_in'):
            student.leaderboard_opt_in = True
        elif hasattr(student, 'show_on_leaderboard'):
            student.show_on_leaderboard = True
        
        # Set display name if not already set
        if hasattr(student, 'leaderboard_display_name') and not student.leaderboard_display_name:
            student.leaderboard_display_name = student.name
        
        await db.commit()
        
        # Return success message that replaces the prompt
        return HTMLResponse(
            content='<div class="success">🎉 You\'re now visible on the leaderboard! <a href="/leaderboard">View Leaderboard</a></div>'
        )
    except Exception as e:
        return HTMLResponse(
            content=f'<div class="error">Could not opt-in: {str(e)}</div>',
            status_code=500
        )
