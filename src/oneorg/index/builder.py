import json
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

from oneorg.index.parser import parse_category
from oneorg.models.agent import QuestMaster

CATEGORIES = [
    "engineering", "design", "marketing", "paid-media", "sales",
    "product", "project-management", "testing", "support",
    "spatial-computing", "specialized", "strategy", "game-development",
]

class IndexConfig(BaseModel):
    agency_agents_path: Path
    output_path: Path
    include_categories: Optional[list[str]] = None

class IndexStats(BaseModel):
    total_agents: int = 0
    categories: int = 0
    by_domain: dict[str, int] = {}
    generated_at: str = ""

def build_index(config: IndexConfig) -> dict:
    categories = config.include_categories or CATEGORIES
    quest_masters = []
    
    for category in categories:
        category_dir = config.agency_agents_path / category
        if not category_dir.is_dir():
            continue
        
        agents = parse_category(category_dir)
        for agent_data in agents:
            master = QuestMaster.from_frontmatter(
                frontmatter=agent_data,
                category=category,
                file_path=agent_data["file_path"],
            )
            quest_masters.append(master.model_dump())
    
    stats = IndexStats(
        total_agents=len(quest_masters),
        categories=len(set(m["category"] for m in quest_masters)),
        by_domain=_count_by_domain(quest_masters),
        generated_at=datetime.now().isoformat(),
    )
    
    index = {
        "version": 1,
        "quest_masters": quest_masters,
        "stats": stats.model_dump(),
    }
    
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config.output_path, "w") as f:
        json.dump(index, f, indent=2)
    
    return index

def _count_by_domain(masters: list[dict]) -> dict[str, int]:
    counts = {}
    for m in masters:
        domain = m.get("skill_domain", "unknown")
        counts[domain] = counts.get(domain, 0) + 1
    return counts
