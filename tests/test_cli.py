import pytest
from click.testing import CliRunner
from oneorg.cli import main


def test_progress_command_exists_and_not_leaderboard():
    """Test that 'oneorg progress' command exists and doesn't show leaderboard."""
    runner = CliRunner()
    result = runner.invoke(main, ['progress', 'nonexistent_student'])
    
    # Command should exist (not "No such command" error)
    assert "No such command 'progress'" not in result.output
    
    # Should not show leaderboard
    assert 'Leaderboard' not in result.output
    
    # Should show error for non-existent student
    assert 'not found' in result.output or 'Error' in result.output
