import click
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table

from oneorg.index.builder import build_index, IndexConfig
from oneorg.index.search import QuestIndex, SearchQuery
from oneorg.gates.evaluator import DecisionEvaluator, Decision
from oneorg.gates.thresholds import ThresholdConfig
from oneorg.state.tracker import StateTracker
from oneorg.models.student import StudentProgress, QuestCompletion, Badge
from oneorg.gamification.leaderboard import LeaderboardManager

console = Console()

DEFAULT_AGENCY_PATH = Path("vendor/agency-agents")
DEFAULT_OUTPUT_PATH = Path("data/index/quest-masters.json")
DEFAULT_STATE_DIR = Path("data/state")
DEFAULT_CONFIG_PATH = Path("data/config/thresholds.yaml")

@click.group()
def main():
    """OneEmployeeOrg Edu-tainment Platform CLI."""
    pass

@main.command()
@click.option("--agency-path", type=click.Path(), default=str(DEFAULT_AGENCY_PATH))
@click.option("--output", type=click.Path(), default=str(DEFAULT_OUTPUT_PATH))
def index(agency_path, output):
    """Build quest master capability index from agency-agents."""
    config = IndexConfig(
        agency_agents_path=Path(agency_path),
        output_path=Path(output),
    )
    
    result = build_index(config)
    
    console.print(f"[green]✓[/green] Built index with {result['stats']['total_agents']} quest masters")
    console.print(f"  Output: {output}")

@main.command()
@click.argument("query")
@click.option("--domain", "-d", help="Filter by skill domain")
@click.option("--category", "-c", help="Filter by category")
def search(query, domain, category):
    """Search for quest masters matching query."""
    index_path = DEFAULT_OUTPUT_PATH
    if not index_path.exists():
        console.print("[red]Error:[/red] Index not found. Run `oneorg index` first.")
        return
    
    with open(index_path) as f:
        data = json.load(f)
    
    quest_index = QuestIndex.from_dict(data["quest_masters"])
    
    results = quest_index.search_fuzzy(query)
    
    if not results:
        console.print("[yellow]No matching quest masters found[/yellow]")
        return
    
    table = Table(title=f"Quest Masters matching '{query}'")
    table.add_column("Name")
    table.add_column("Domain")
    table.add_column("Category")
    table.add_column("Vibe")
    
    for master in results[:10]:
        table.add_row(
            f"{master.emoji or '•'} {master.name}",
            master.skill_domain.value,
            master.category,
            (master.vibe or "")[:40],
        )
    
    console.print(table)

@main.command()
@click.argument("decision")
@click.option("--confidence", "-c", type=float, required=True)
@click.option("--domain", "-d", default="operations")
@click.option("--risks", "-r", multiple=True, help="Risk factors")
def evaluate(decision, confidence, domain, risks):
    """Evaluate a decision against confidence thresholds."""
    config = ThresholdConfig.load(DEFAULT_CONFIG_PATH)
    evaluator = DecisionEvaluator(config)
    
    dec = Decision(
        decision_id=f"cli_{hash(decision) % 10000:04d}",
        description=decision,
        confidence=confidence,
        domain=domain,
        requester="cli_user",
        risk_factors=list(risks),
    )
    
    result = evaluator.evaluate(dec)
    
    level_colors = {
        "fully_autonomous": "green",
        "autonomous_notify": "yellow",
        "escalate_approval": "orange1",
        "escalate_urgent": "red",
    }
    color = level_colors.get(result.autonomy_level.value, "white")
    
    console.print(f"\nDecision: [bold]{decision}[/bold]")
    console.print(f"Confidence: {confidence:.0%} → {result.effective_confidence:.0%} (effective)")
    console.print(f"Level: [{color}]{result.autonomy_level.value}[/{color}]")
    console.print(f"Can execute: {'[green]Yes[/green]' if result.can_execute else '[red]No[/red]'}")
    
    if result.escalate_to:
        console.print(f"Escalate to: [bold]{result.escalate_to}[/bold]")

@main.command()
@click.argument("student_id")
@click.option("--name", "-n", help="Student name")
@click.option("--grade", "-g", type=int, help="Grade level (1-16)")
def student(student_id, name, grade):
    """Show or create student progress."""
    tracker = StateTracker(DEFAULT_STATE_DIR)
    
    if not tracker.exists(student_id):
        if not name or not grade:
            console.print("[red]Error:[/red] New student requires --name and --grade")
            return
        
        student = StudentProgress(
            student_id=student_id,
            name=name,
            grade_level=grade,
        )
        tracker.save(student)
        console.print(f"[green]✓[/green] Created student {name} (Grade {grade})")
    
    student = tracker.load(student_id)
    
    console.print(f"\n[bold]{student.name}[/bold] (Grade {student.grade_level})")
    console.print(f"Level {student.level} • {student.xp} XP • {student.xp_to_next_level} XP to next level")
    console.print(f"Quests completed: {len(student.quests_completed)}")
    console.print(f"Badges: {len(student.badges)}")
    
    if student.badges:
        badge_str = " ".join(f"{b.icon} {b.name}" for b in student.badges[:5])
        console.print(f"  {badge_str}")

@main.command()
@click.argument("student_id")
@click.argument("quest_id")
@click.argument("quest_master")
@click.option("--xp", "-x", type=int, default=100)
@click.option("--score", "-s", type=float, default=0.85)
def complete(student_id, quest_id, quest_master, xp, score):
    """Mark a quest as completed for a student."""
    from datetime import datetime
    
    tracker = StateTracker(DEFAULT_STATE_DIR)
    
    if not tracker.exists(student_id):
        console.print(f"[red]Error:[/red] Student {student_id} not found")
        return
    
    completion = QuestCompletion(
        quest_id=quest_id,
        quest_master=quest_master,
        xp_earned=xp,
        completed_at=datetime.now(),
        score=score,
    )
    
    old_student = tracker.load(student_id)
    student = tracker.add_quest_completion(student_id, completion)
    
    level_up = student.level - old_student.level
    
    console.print(f"[green]✓[/green] Quest completed: {quest_id}")
    console.print(f"  XP earned: +{xp}")
    if level_up > 0:
        console.print(f"  [bold yellow]LEVEL UP! Now level {student.level}[/bold yellow]")

@main.command()
@click.option("--limit", "-l", default=10)
def leaderboard(limit):
    """Show top students on the leaderboard."""
    tracker = StateTracker(DEFAULT_STATE_DIR)
    manager = LeaderboardManager(tracker)
    
    entries = manager.get_leaderboard(limit=limit)
    
    table = Table(title="Leaderboard")
    table.add_column("Rank", style="bold")
    table.add_column("Student")
    table.add_column("Level")
    table.add_column("XP")
    table.add_column("Streak")
    
    for entry in entries:
        table.add_row(
            f"#{entry.rank}",
            entry.display_name,
            str(entry.level),
            str(entry.xp),
            f"🔥{entry.current_streak}" if entry.current_streak > 0 else "",
        )
    
    console.print(table)

if __name__ == "__main__":
    main()
