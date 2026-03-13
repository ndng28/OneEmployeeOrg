import pytest
from oneorg.models.agent import QuestMaster, SkillDomain

def test_quest_master_from_frontmatter():
    frontmatter = {
        "name": "Frontend Developer",
        "description": "Expert frontend developer",
        "color": "cyan",
        "emoji": "🖥️",
        "vibe": "Builds responsive web apps",
    }
    master = QuestMaster.from_frontmatter(
        frontmatter=frontmatter,
        category="engineering",
        file_path="engineering/engineering-frontend-developer.md"
    )
    
    assert master.name == "Frontend Developer"
    assert master.slug == "frontend-developer"
    assert master.category == "engineering"
    assert master.color == "#00FFFF"
    assert master.emoji == "🖥️"
    assert master.skill_domain == SkillDomain.TECHNOLOGY

def test_quest_master_keywords_extraction():
    frontmatter = {
        "name": "Compliance Auditor",
        "description": "SOC 2, ISO 27001, HIPAA audits",
        "color": "orange",
        "emoji": "📋",
        "vibe": "Walks you through certification",
    }
    master = QuestMaster.from_frontmatter(
        frontmatter=frontmatter,
        category="specialized",
        file_path="specialized/compliance-auditor.md"
    )
    
    assert "SOC" in master.keywords or "soc" in master.keywords
    assert "compliance" in master.keywords or "auditor" in master.keywords
