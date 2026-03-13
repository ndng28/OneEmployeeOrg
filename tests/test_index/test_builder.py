import pytest
from pathlib import Path
import json
from oneorg.index.builder import build_index, IndexConfig

def test_build_index_from_agency_agents(tmp_path):
    agency_dir = tmp_path / "vendor" / "agency-agents"
    
    eng_dir = agency_dir / "engineering"
    eng_dir.mkdir(parents=True)
    (eng_dir / "engineering-frontend.md").write_text(
        "---\nname: Frontend Dev\ndescription: UI expert\ncolor: cyan\nemoji: 🖥️\n---\nBody"
    )
    
    design_dir = agency_dir / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "design-ux.md").write_text(
        "---\nname: UX Designer\ndescription: User experience\ncolor: pink\nemoji: 🎨\n---\nBody"
    )
    
    config = IndexConfig(
        agency_agents_path=agency_dir,
        output_path=tmp_path / "index" / "quest-masters.json",
    )
    
    index = build_index(config)
    
    assert len(index["quest_masters"]) == 2
    assert any(m["slug"] == "frontend-dev" for m in index["quest_masters"])
    assert any(m["slug"] == "ux-designer" for m in index["quest_masters"])
    assert index["stats"]["total_agents"] == 2
    assert index["stats"]["categories"] == 2

def test_index_output_file_created(tmp_path):
    agency_dir = tmp_path / "vendor" / "agency-agents"
    eng_dir = agency_dir / "engineering"
    eng_dir.mkdir(parents=True)
    (eng_dir / "engineering-test.md").write_text(
        "---\nname: Test Agent\ndescription: Testing\ncolor: blue\n---\nBody"
    )
    
    output_path = tmp_path / "output" / "quest-masters.json"
    config = IndexConfig(
        agency_agents_path=agency_dir,
        output_path=output_path,
    )
    
    build_index(config)
    
    assert output_path.exists()
    with open(output_path) as f:
        data = json.load(f)
    assert "quest_masters" in data
