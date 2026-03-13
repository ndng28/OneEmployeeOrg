import re
from pathlib import Path
from typing import Optional

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n(.*)$",
    re.DOTALL
)

def parse_frontmatter(content: str) -> tuple[dict, str]:
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content
    
    fm_str, body = match.groups()
    frontmatter = {}
    
    for line in fm_str.strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    
    return frontmatter, body

def parse_agent_file(file_path: Path) -> dict:
    content = file_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)
    
    return {
        **frontmatter,
        "body": body,
        "file_path": str(file_path),
    }

def parse_category(category_dir: Path) -> list[dict]:
    if not category_dir.is_dir():
        return []
    
    results = []
    for file_path in sorted(category_dir.glob("*.md")):
        if file_path.name.lower() in ("readme.md", "index.md"):
            continue
        try:
            result = parse_agent_file(file_path)
            results.append(result)
        except Exception:
            continue
    
    return results
