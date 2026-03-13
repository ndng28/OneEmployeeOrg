import pytest
from oneorg.models.agent import QuestMaster, SkillDomain
from oneorg.index.search import QuestIndex, SearchQuery

@pytest.fixture
def sample_masters():
    return [
        QuestMaster(
            slug="frontend-dev",
            name="Frontend Developer",
            description="Expert in React, Vue, and UI development",
            category="engineering",
            skill_domain=SkillDomain.TECHNOLOGY,
            color="#00FFFF",
            emoji="🖥️",
            vibe="Builds responsive web apps",
            keywords=["react", "vue", "ui", "frontend", "javascript"],
            file_path="engineering/engineering-frontend.md",
        ),
        QuestMaster(
            slug="compliance-auditor",
            name="Compliance Auditor",
            description="SOC 2, ISO 27001, HIPAA certification expert",
            category="specialized",
            skill_domain=SkillDomain.LIFE_SKILLS,
            color="#FFA500",
            emoji="📋",
            vibe="Walks you through certification",
            keywords=["soc2", "compliance", "audit", "security", "hipaa"],
            file_path="specialized/compliance-auditor.md",
        ),
    ]

def test_search_by_keywords(sample_masters):
    index = QuestIndex(quest_masters=sample_masters)
    
    results = index.search(SearchQuery(keywords=["react", "ui"]))
    
    assert len(results) == 1
    assert results[0].slug == "frontend-dev"

def test_search_by_domain(sample_masters):
    index = QuestIndex(quest_masters=sample_masters)
    
    results = index.search(SearchQuery(skill_domain=SkillDomain.TECHNOLOGY))
    
    assert len(results) == 1
    assert results[0].slug == "frontend-dev"

def test_search_by_category(sample_masters):
    index = QuestIndex(quest_masters=sample_masters)
    
    results = index.search(SearchQuery(category="specialized"))
    
    assert len(results) == 1
    assert results[0].slug == "compliance-auditor"

def test_search_fuzzy_match(sample_masters):
    index = QuestIndex(quest_masters=sample_masters)
    
    results = index.search_fuzzy("security certification")
    
    assert len(results) >= 1
    assert any(r.slug == "compliance-auditor" for r in results)
