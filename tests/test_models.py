import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from oneorg.db.models import User, Student, Quest
from oneorg.db.database import AsyncSessionLocal
from oneorg.db.init_db import init_db

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncSessionLocal() as session:
        user = User(email="test@example.com", hashed_password="hashed")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_student():
    async with AsyncSessionLocal() as session:
        user = User(email="student@example.com", hashed_password="hashed")
        session.add(user)
        await session.flush()
        
        student = Student(
            user_id=user.id,
            student_id="stu_001",
            name="Test Student",
            grade_level=5
        )
        session.add(student)
        await session.commit()
        
        assert student.id is not None
        assert student.name == "Test Student"
