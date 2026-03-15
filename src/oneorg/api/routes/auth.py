from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from oneorg.db.database import get_db
from oneorg.services.auth import (
    create_user, authenticate_user, create_access_token, get_current_user
)

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    grade_level: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/api/auth/register", response_model=dict)
async def register_api(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """API endpoint for registration."""
    from sqlalchemy import select
    from oneorg.db.models import User
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = await create_user(db, data.email, data.password)
    
    # Create student profile
    from oneorg.db.models import Student
    import uuid
    student = Student(
        user_id=user.id,
        student_id=f"stu_{uuid.uuid4().hex[:8]}",
        name=data.name,
        grade_level=data.grade_level
    )
    db.add(student)
    await db.commit()
    
    return {"message": "User created successfully", "student_id": student.student_id}


@router.post("/api/auth/login")
async def login_api(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """API endpoint for login, returns token."""
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/register")
async def register_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    grade_level: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Form handler for registration."""
    from sqlalchemy import select
    from oneorg.db.models import User, Student
    import uuid
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar():
        return RedirectResponse("/register?error=email_exists", status_code=302)
    
    # Create user
    user = await create_user(db, email, password)
    
    # Create student
    student = Student(
        user_id=user.id,
        student_id=f"stu_{uuid.uuid4().hex[:8]}",
        name=name,
        grade_level=grade_level
    )
    db.add(student)
    await db.commit()
    
    # Login and redirect
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=604800)
    return response


@router.post("/auth/login")
async def login_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Form handler for login."""
    user = await authenticate_user(db, email, password)
    if not user:
        return RedirectResponse("/login?error=invalid", status_code=302)
    
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=604800)
    return response


@router.get("/auth/logout")
async def logout():
    """Logout and clear session."""
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("access_token")
    return response
