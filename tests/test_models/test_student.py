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


def test_student_has_computed_age_mode():
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )

    from oneorg.models.age_mode import AgeMode
    assert student.age_mode == AgeMode.YOUNG


def test_age_mode_from_grade_10():
    student = StudentProgress(
        student_id="stu_002",
        name="Bob",
        grade_level=10,
    )

    from oneorg.models.age_mode import AgeMode
    assert student.age_mode == AgeMode.MIDDLE


def test_student_has_activity_calendar():
    from oneorg.models.calendar import ActivityCalendar
    
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )
    
    assert isinstance(student.calendar, ActivityCalendar)


def test_student_no_longest_streak():
    student = StudentProgress(
        student_id="stu_001",
        name="Alice",
        grade_level=5,
    )
    
    # Should not have longest_streak attribute
    assert not hasattr(student, 'longest_streak')
    
    # Calendar should not have it either
    assert not hasattr(student.calendar, 'longest_streak')
