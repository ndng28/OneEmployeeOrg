import pytest
from pathlib import Path
from oneorg.index.parser import parse_agent_file, parse_category

def test_parse_agent_file_with_full_frontmatter(tmp_path):
    agent_file = tmp_path / "test-agent.md"
    agent_file.write_text("""---
name: Test Agent
description: A test agent for parsing
color: blue
emoji: 🧪
vibe: Tests everything thoroughly
---

# Test Agent Content

This is the body content.
""")
    
    result = parse_agent_file(agent_file)
    
    assert result["name"] == "Test Agent"
    assert result["description"] == "A test agent for parsing"
    assert result["color"] == "blue"
    assert result["emoji"] == "🧪"
    assert result["vibe"] == "Tests everything thoroughly"
    assert "body" in result
    assert "# Test Agent Content" in result["body"]

def test_parse_agent_file_with_minimal_frontmatter(tmp_path):
    agent_file = tmp_path / "minimal-agent.md"
    agent_file.write_text("""---
name: Minimal Agent
description: Just the basics
color: red
---

Content here.
""")
    
    result = parse_agent_file(agent_file)
    
    assert result["name"] == "Minimal Agent"
    assert result.get("emoji") is None
    assert result.get("vibe") is None

def test_parse_category_discovers_all_agents(tmp_path):
    category_dir = tmp_path / "engineering"
    category_dir.mkdir()
    
    (category_dir / "engineering-frontend.md").write_text("---\nname: Frontend\ndescription: Front\ncolor: blue\n---\nBody")
    (category_dir / "engineering-backend.md").write_text("---\nname: Backend\ndescription: Back\ncolor: green\n---\nBody")
    (category_dir / "README.md").write_text("# Engineering Agents")
    
    results = parse_category(category_dir)
    
    assert len(results) == 2
    assert results[0]["name"] in ["Frontend", "Backend"]
