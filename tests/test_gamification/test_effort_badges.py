"""Tests for effort-based badges that reward the learning process."""


def test_effort_badges_recognize_persistence():
    """Badges should reward effort, not just achievements."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Before meeting criteria - no badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0

    # Simulate multiple attempts (persistence) - 10 attempts
    student.total_attempts = 10

    # Should earn "persistent" badge
    badges = checker.check_effort_badges(student)
    assert any(b.badge_id == "persistent" for b in badges)


def test_time_spent_badges():
    """Badges for time spent learning (not speed)."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Before meeting criteria - no badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0

    # Simulate significant time spent - 1 hour (3600 seconds)
    student.total_time_spent = 3600

    # Should earn "thorough" badge
    badges = checker.check_effort_badges(student)
    assert any(b.badge_id == "thorough" for b in badges)


def test_curious_badges():
    """Badges for trying different categories."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Before meeting criteria - no badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0

    # Simulate category exploration - 3 categories
    student.categories_attempted = {"math", "science", "history"}

    # Should earn "curious" badge
    badges = checker.check_effort_badges(student)
    assert any(b.badge_id == "curious" for b in badges)


def test_reflective_badges():
    """Badges for revisiting completed quests."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Before meeting criteria - no badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0

    # Simulate revisiting quests - 3 revisits
    student.revisits = 3

    # Should earn "reflective" badge
    badges = checker.check_effort_badges(student)
    assert any(b.badge_id == "reflective" for b in badges)


def test_collaborative_badges():
    """Badges for helping others."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Before meeting criteria - no badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0

    # Simulate collaborations - 5 collaborations
    student.collaborations = 5

    # Should earn "collaborative" badge
    badges = checker.check_effort_badges(student)
    assert any(b.badge_id == "collaborative" for b in badges)


def test_badge_not_repeated():
    """Already earned badges should not be awarded again."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress, Badge

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Meet criteria
    student.total_attempts = 10

    # First check - earn the badge
    badges = checker.check_effort_badges(student)
    assert len(badges) == 1
    assert badges[0].badge_id == "persistent"

    # Award the badge
    student.award_badge(badges[0])

    # Second check - should not earn again
    badges = checker.check_effort_badges(student)
    assert len(badges) == 0


def test_multiple_badges_at_once():
    """Can earn multiple badges in one check."""
    from oneorg.gamification.effort_badges import EffortBadgeChecker
    from oneorg.models.student import StudentProgress

    checker = EffortBadgeChecker()

    student = StudentProgress(
        student_id="stu_001",
        name="Test",
        grade_level=5,
    )

    # Meet multiple criteria at once
    student.total_attempts = 10
    student.total_time_spent = 3600
    student.categories_attempted = {"math", "science", "history"}

    # Should earn multiple badges
    badges = checker.check_effort_badges(student)
    badge_ids = {b.badge_id for b in badges}
    assert "persistent" in badge_ids
    assert "thorough" in badge_ids
    assert "curious" in badge_ids
