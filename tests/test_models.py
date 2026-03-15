import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from oneorg.db.models import User, Student, Quest
from oneorg.db.database import AsyncSessionLocal
from oneorg.db.init_db import init_db

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncSessionLocal() as session:
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        user = User(email=unique_email, hashed_password="hashed")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.email == unique_email

@pytest.mark.asyncio
async def test_create_student():
    async with AsyncSessionLocal() as session:
        unique_email = f"student_{uuid.uuid4().hex[:8]}@example.com"
        user = User(email=unique_email, hashed_password="hashed")
        session.add(user)
        await session.flush()
        
        unique_student_id = f"stu_{uuid.uuid4().hex[:8]}"
        student = Student(
            user_id=user.id,
            student_id=unique_student_id,
            name="Test Student",
            grade_level=5
        )
        session.add(student)
        await session.commit()
        
        assert student.id is not None
        assert student.name == "Test Student"
