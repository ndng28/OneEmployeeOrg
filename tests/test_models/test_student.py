import pytest
from datetime import datetime
from oneorg.models.student import StudentProgress, QuestCompletion, Badge

def test_student_progress_initialization():
    student = StudentProgress(
        student_id="stu_001",
        name="Alex Chen",
        grade_level=10,
    )
    
    assert student.xp == 0
    assert student.level == 1
    assert student.quests_completed == []
    assert student.badges == []

def test_student_add_quest_completion():
    student = StudentProgress(
        student_id="stu_001",
        name="Alex Chen",
        grade_level=10,
    )
    
    completion = QuestCompletion(
        quest_id="frontend-basics",
        quest_master="frontend-developer",
        xp_earned=150,
        completed_at=datetime.now(),
        score=0.92,
    )
    
    student.add_quest_completion(completion)
    
    assert student.xp == 150
    assert len(student.quests_completed) == 1
    assert student.level == 1

def test_student_level_up():
    student = StudentProgress(
        student_id="stu_001",
        name="Alex Chen",
        grade_level=10,
        xp=450,
    )
    
    student.add_xp(100)
    
    assert student.xp == 550
    assert student.level == 2

def test_badge_award():
    student = StudentProgress(
        student_id="stu_001",
        name="Alex Chen",
        grade_level=10,
    )
    
    badge = Badge(
        badge_id="first-quest",
        name="First Steps",
        description="Complete your first quest",
        icon="🎬",
    )
    
    student.award_badge(badge)
    
    assert len(student.badges) == 1
    assert student.has_badge("first-quest")
