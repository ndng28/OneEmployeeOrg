from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from oneorg.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    student_id = Column(String, unique=True, index=True)  # public-facing ID
    name = Column(String, nullable=False)
    grade_level = Column(Integer, nullable=False)
    age_mode = Column(String, default="middle")  # young, middle, teen
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)
    current_quest_id = Column(Integer, ForeignKey("quests.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="student")
    completions = relationship("QuestCompletion", back_populates="student")
    badges = relationship("StudentBadge", back_populates="student")

class Quest(Base):
    __tablename__ = "quests"
    
    id = Column(Integer, primary_key=True, index=True)
    quest_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    xp_reward = Column(Integer, default=100)
    difficulty = Column(Integer, default=1)  # 1-5
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    completions = relationship("QuestCompletion", back_populates="quest")

class QuestCompletion(Base):
    __tablename__ = "quest_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    quest_id = Column(Integer, ForeignKey("quests.id"))
    score = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)
    feedback = Column(Text)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="completions")
    quest = relationship("Quest", back_populates="completions")

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    badge_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String, default="🏆")
    criteria = Column(Text)  # JSON string for criteria
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student_badges = relationship("StudentBadge", back_populates="badge")

class StudentBadge(Base):
    __tablename__ = "student_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="badges")
    badge = relationship("Badge", back_populates="student_badges")
