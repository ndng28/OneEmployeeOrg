from pathlib import Path
from oneorg.state.tracker import StateTracker
from oneorg.gamification.badges import BadgeManager
from oneorg.gamification.leaderboard import LeaderboardManager

DEFAULT_STATE_DIR = Path("data/state")

def get_tracker() -> StateTracker:
    return StateTracker(DEFAULT_STATE_DIR)

def get_badge_manager() -> BadgeManager:
    return BadgeManager()

def get_leaderboard_manager(tracker: StateTracker = None) -> LeaderboardManager:
    if tracker is None:
        tracker = get_tracker()
    return LeaderboardManager(tracker)
