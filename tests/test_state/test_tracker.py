import pytest
from pathlib import Path
from oneorg.state.tracker import StateTracker
from oneorg.models.student import StudentProgress, QuestCompletion
from datetime import datetime

def test_state_tracker_save_and_load(tmp_path):
    tracker = StateTracker(state_dir=tmp_path)
    
    student = StudentProgress(
        student_id="stu_001",
        name="Alex Chen",
        grade_level=10,
    )
    
    tracker.save(student)
    
    loaded = tracker.load("stu_001")
    
    assert loaded.student_id == "stu_001"
    assert loaded.name == "Alex Chen"
    assert loaded.grade_level == 10

def test_state_tracker_update_progress(tmp_path):
    tracker = StateTracker(state_dir=tmp_path)
    
    student = StudentProgress(
        student_id="stu_002",
        name="Jordan Lee",
        grade_level=8,
    )
    tracker.save(student)
    
    completion = QuestCompletion(
        quest_id="python-basics",
        quest_master="backend-developer",
        xp_earned=200,
        completed_at=datetime.now(),
        score=0.95,
    )
    
    tracker.add_quest_completion("stu_002", completion)
    
    updated = tracker.load("stu_002")
    
    assert updated.xp == 200
    assert len(updated.quests_completed) == 1

def test_state_tracker_list_students(tmp_path):
    tracker = StateTracker(state_dir=tmp_path)
    
    for i in range(3):
        student = StudentProgress(
            student_id=f"stu_{i:03d}",
            name=f"Student {i}",
            grade_level=9 + i,
        )
        tracker.save(student)
    
    students = tracker.list_all()
    
    assert len(students) == 3
    assert "stu_000" in students
    assert "stu_001" in students
    assert "stu_002" in students

def test_state_tracker_delete(tmp_path):
    tracker = StateTracker(state_dir=tmp_path)
    
    student = StudentProgress(
        student_id="stu_delete",
        name="To Delete",
        grade_level=10,
    )
    tracker.save(student)
    
    assert tracker.exists("stu_delete")
    
    tracker.delete("stu_delete")
    
    assert not tracker.exists("stu_delete")
