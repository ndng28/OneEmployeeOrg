import pytest
from datetime import datetime
from oneorg.models.student import StudentProgress, QuestCompletion, Badge


def test_age_mode_enum_values():
    from oneorg.models.age_mode import AgeMode

    assert AgeMode.YOUNG.value == "5-8"
    assert AgeMode.MIDDLE.value == "9-12"
    assert AgeMode.TEEN.value == "13-18"


def test_age_mode_computed_field():
    from oneorg.models.age_mode import AgeMode

    student = StudentProgress(
        student_id="stu_test",
        name="Test",
        grade_level=10,
    )

    assert student.age_mode == AgeMode.MIDDLE
