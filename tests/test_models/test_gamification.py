import pytest
from oneorg.models.gamification import BadgeCriteria, BadgeCategory

def test_badge_criteria_has_no_rarity():
    badge = BadgeCriteria(
        badge_id="test_badge",
        name="Test Badge",
        description="A test",
        icon="🌟",
        category=BadgeCategory.MILESTONE,
        criteria_type="quest_count",
        criteria_threshold=5,
    )
    
    # Should NOT have rarity attribute
    assert not hasattr(badge, 'rarity')

def test_no_badge_rarity_enum():
    # BadgeRarity should not exist
    with pytest.raises(ImportError):
        from oneorg.models.gamification import BadgeRarity
