from oneorg.models.gamification import LeaderboardVisibility

def test_leaderboard_is_opt_out_by_default():
    """Test that leaderboard visibility defaults to opt-out (private)."""
    settings = LeaderboardVisibility()
    
    # Should be opt-out (private) by default
    assert settings.show_on_leaderboard == False
